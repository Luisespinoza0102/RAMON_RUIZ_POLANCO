from django.db import models
from auditlog.registry import auditlog
import uuid

# --------- Modelos para el Registro de Libros ---------- #

# Modelo Autor
class Autor(models.Model):
    nombre_completo = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_completo

# Modelo Editorial
class Editorial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Modelo Género
class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_dewey = models.CharField(max_length=20, help_text="Ej: 800, Literatura")

    def __str__(self):
        return f"{self.codigo_dewey} - {self.nombre}"

# Modelo Ubicación
class Ubicacion(models.Model):
    estante = models.CharField(max_length=100, help_text="Ej: Referencias 1")

    class Meta:
        verbose_name_plural = "Ubicaciones"

    def __str__(self):
            return f"Estante: {self.estante}"

# Modelo Libros
class Libro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    cutter = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(verbose_name="Sinopsis")
    imagen_portada = models.ImageField(upload_to='libros/', blank=True, null=True)
    autores = models.ManyToManyField(Autor, related_name='libros')
    generos = models.ManyToManyField(Genero, related_name='libros')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # Atributos para las estadisticas
    ORIGEN_CHOICES = [
        ('VNZ', 'Venezolana'),
        ('INT', 'Internacional'), 
        ('UNI', 'Universal'),
    ]

    origen = models.CharField(
        max_length=3, choices=ORIGEN_CHOICES, 
        help_text="Necesario para el desglose de Novela, Poesía, etc."
    )

    es_infantil = models.BooleanField(
        default=False, verbose_name="¿Es cuento Infantil?",
        help_text="Marca esto para clasificarlo como cuentos (X)"
        )

    es_bolivariano = models.BooleanField(
        default=False, verbose_name="¿Pertenece a la sección Bolivariana?",
        help_text="Marca esto para clasificarlo en la sección bolivariana")

    def __str__(self):
        return self.titulo
    
    @property
    def stock_real(self):
        return self.ejemplares.exclude(estado__in=['DONADO', 'PERDIDO']).count()
    
    @property
    def unidades_disponibles(self):
        return self.ejemplares.filter(estado='DISPONIBLE').count()
    
    class Meta:
        ordering = ['-fecha_creacion']

# Modelo Ejemplar
class Ejemplar(models.Model):
    ESTADOS_FISICOS = (
        ('DISPONIBLE', 'Disponible'),
        ('PRESTADO', 'Prestado'),
        ('DONADO', 'DONADO'),
        ('PERDIDO', 'Perdido'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_inventario = models.CharField(max_length=50, unique=True, blank=True, default='', verbose_name='Código de Inventario' )
    anio_publicacion = models.IntegerField(verbose_name='Año de Publicación')
    estado = models.CharField(max_length=20, choices=ESTADOS_FISICOS, default='DISPONIBLE')
    # Claves Foráneas
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='ejemplares')

    def save(self, *args, **kwargs):
        if not self.codigo_inventario:
            genero = self.libro.generos.first()
            dewey = genero.codigo_dewey if genero and genero.codigo_dewey else "000"
            cutter = self.libro.cutter if getattr(self.libro, 'cutter', None) else "SC"
            cantidad_existente = Ejemplar.objects.filter(libro=self.libro).count()
            correlativo = cantidad_existente + 1

            self.codigo_inventario = f"{dewey}-{cutter}-{self.anio_publicacion}-{correlativo:02d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.libro.titulo} ({self.anio_publicacion}) - {self.codigo_inventario}"

# Registro de Auditoria
auditlog.register(Libro)
auditlog.register(Ejemplar)
auditlog.register(Genero)