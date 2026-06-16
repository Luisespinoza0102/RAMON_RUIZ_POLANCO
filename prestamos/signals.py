from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prestamo

@receiver(post_save, sender=Prestamo)
def control_flujo_prestamo_y_ejemplar(sender, instance, created, **kwargs):
    ejemplar = instance.ejemplar
    if created:
        ejemplar.estado = 'NO DISPONIBLE'
        ejemplar.save()
    else:
        if instance.estado == 'DEVUELTO':
            ejemplar.estado = 'DISPONIBLE'
            ejemplar.save()

        elif instance.estado == 'RECHAZADO':
            ejemplar.estado = 'DISPONIBLE'
            ejemplar.save()
        
        elif instance.estado == 'APROBADO':
            ejemplar.estado = 'PRESTADO'
            ejemplar.save()