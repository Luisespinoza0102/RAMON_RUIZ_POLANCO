from .models import Prestamo
from django.utils import timezone

def puede_solicitar_libro(user):
    # Regla: No puede solicitar si tiene préstamos vencidos
    vencidos = Prestamo.objects.filter(
        usuario=user,
        estado='APROBADO',
        fecha_devolucion_esperada__lt=timezone.now().date()
    ).exists()
    
    # Regla: Máximo 3 libros prestados simultáneamente
    activos = Prestamo.objects.filter(usuario=user, estado__in=['SOLICITADO', 'APROBADO']).count()
    
    if vencidos: return False, "Tienes libros vencidos sin devolver."
    if activos >= 3: return False, "Has alcanzado el límite de préstamos."
    
    return True, "OK"