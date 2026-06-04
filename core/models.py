from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from auditlog.registry import auditlog
import uuid

# ---------------- MODELOS PARA LOS USUARIOS ----------------- #

# Opciones para selectores Enums

ROLES = (
    ('ADMIN', 'Administrador'),
    ('USUARIO', 'Usuario'), 
)

ESTADOS_USUARIOS = (
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
    ('BLOQUEADO', 'Bloqueado'),
    ('PENDIENTE', 'Pendiente de Activación')
)

TIPOS_DOCUMENTOS = (
    ('CEDULA', 'Cedula de Identidad'),
    ('RIF', 'Registro de Información Fiscal'),
    ('REFERENCIAS', 'Referencia Personal'),
    ('FOTO_CARNET', 'Foto tipo Carnet'),
    ('OTRO', 'Otro Documento')
)

class Perfil(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula/DNI")
    carnet = models.CharField(max_length=20, unique=True, verbose_name="Carnet")
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES, default='USUARIO')
    estado = models.CharField(max_length=20, choices=ESTADOS_USUARIOS, default='PENDIENTE')

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

class Documento_Perfil(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=20, choices=TIPOS_DOCUMENTOS)
    archivo = models.FileField(
        upload_to='documentos_usuarios/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Formatos permitidos: PDF, JPG, PNG")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_documento_display()} de {self.perfil.usuario.username}"
    
    class Meta:
        verbose_name = "Documento de Perfil"
        verbose_name_plural = "Documentos de Perfiles"
        ordering = ['-fecha_subida']

# Registro de Audtoria
auditlog.register(Perfil)
auditlog.register(Documento_Perfil)