from django.db import models
from django.conf import settings

# ------- Modelo para alimentar el sistema de recomendación ------------#

class HistorialBusqueda(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} buscó '{self.termini_busqueda}'"
