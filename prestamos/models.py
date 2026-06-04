from django.db import models
from django.conf import settings
from catalogo.models import Ejemplar
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from auditlog.registry import auditlog
import uuid

# --------------- Modelos para los Préstamos -------------#
class Prestamo(models.Model):
    ESTADOS = (
        ('SOLICITADO', 'Solicitado'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('DEVUELTO', 'Devuelto'),
        ('VENCIDO', 'Vencido'),
        ('RENOVADO', 'Renovado'),
        ('RENOVACION_SOLICITADA', 'Renovacion Solicitada')
    )

    DURACIONES = (
        (7, '7 días'),
        (15, '15 días')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prestamos')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_devolucion_esperada = models.DateField(null=True, blank=True)
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=25, choices=ESTADOS, default='SOLICITADO')
    duracion_dias = models.IntegerField(choices=DURACIONES, default=7, help_text="Duración inicial del Préstamo")
    es_renovado = models.BooleanField(default=False)

    def __str__(self):
        return f"Préstamo de {self.usuario.username} - {self.ejemplar.libro.titulo}"
    
    @property
    def esta_vencido(self):
        # Lógica para determinar si bloquea al usuario
        if self.estado == 'APROBADO' and self.fecha_devolucion_esperada:
            return timezone.now().date() >  self.fecha_devolucion_esperada
        return False
    
    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

class Sancion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sanciones')
    prestamo_origen = models.ForeignKey(Prestamo, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField()
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Sanción a {self.usuario.username} - {self.motivo}"

class Notificacion(models.Model):
    TIPOS = (
        ('INFO', 'Información General'),
        ('APROBADO', 'Solicitud Aprobada'),
        ('Rechazado', 'Solicitud Rechazada'),
        ('ALERTA', 'Alerta / Vencimiento'),
        ('CARENT', 'Carnet de Usuario')
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='INFO')
    leido = models.BooleanField(default=False)
    enlace = models.CharField(max_length=200, blank=True, null=True, help_text="Link de acción (ej. descargar pdf)")
    fecha_creacion = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()} para {self.usuario.username}"

# Registro de Auditoria
auditlog.register(Prestamo)