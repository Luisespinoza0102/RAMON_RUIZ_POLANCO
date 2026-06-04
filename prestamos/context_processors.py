from .models import Prestamo, Notificacion

def contadores_biblioteca(request):
    if request.user.is_authenticated:
        # Variables para el Admin
        if request.user.perfil.rol == 'ADMIN':
            return {
                'global_pendientes_count': Prestamo.objects.filter(estado='SOLICITADO').count(),
                'global_vencidos_count': sum(1 for p in Prestamo.objects.filter(estado='APROBADO') if p.esta_vencido)
            }
        
        # Variables para el Usuario (Aquí calculamos el conteo para el HTML)
        else:
            return {
                'global_notificaciones_count': Notificacion.objects.filter(usuario=request.user, leido=False).count()
            }
            
    return {}