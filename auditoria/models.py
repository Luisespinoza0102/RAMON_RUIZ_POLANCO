from django.db import models
from django.conf import settings

# ------------ Modelo para llevar el registro de los reportes ------#
class RegistroReporte(models.Model):
    TIPO_REPORTE = (
        ('EXCEL_MENSUAL', 'Reporte Estadístico Mensual'),
        ('ASISTENCIA', 'Formato de Asistencia'),
        ('INVENTARIO', 'Reporte de Inventario')
    )

    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Generado por")
    tipo = models.CharField(max_length=50, choices=TIPO_REPORTE)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    archivo_respaldo = models.FileField(upload_to='auditoria_reportes/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.admin.username} ({self.fecha_generacion.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Registro de Reporte"
        verbose_name_plural = "Historial de Reportes Generados"