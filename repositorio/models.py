import uuid
from django.db import models
from auditlog.registry import auditlog
from django.conf import settings

# MODELO PARA LOS DOCUMENTOS DIGITALES

class CategoriaDigital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría Digital"
        verbose_name_plural = "Categorías Digitales"

class DocumentoDigital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    categoria = models.ForeignKey(CategoriaDigital, on_delete=models.CASCADE, related_name='documentos')
    descripcion = models.TextField(blank=True)
    archivo_pdf = models.CharField(max_length=500)
    portada = models.CharField(max_length=500, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descargas = models.PositiveIntegerField(default=0)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo

auditlog.register(DocumentoDigital)