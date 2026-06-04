from django.utils import timezone
from datetime import timedelta
from .models import Notificacion

def procesar_devolucion(prestamo):
    prestamo.fecha_devolucion_real = timezone.now().date()
    prestamo.estado = 'DEVUELTO'
    # Bloqueo Automatico si hay retraso
    if prestamo.fecha_devolucion_real > prestamo.fecha_devolucion_esperada:
        perfil = prestamo.usuario.perfil
        perfil.estado = 'BLOQUEADO'
        perfil.save()
        Notificacion.objects.create(
            usuario=prestamo.usuario,
            mensaje=f"Tu cuenta ha sido bloqueada por devolver tarde: {prestamo.ejemplar.libro.titulo}"
        )
        prestamo.save()
        
        # Liberar ejemplar
        ejemplar = prestamo.ejemplar
        ejemplar.estado = 'DISPONIBLE'
        ejemplar.save()