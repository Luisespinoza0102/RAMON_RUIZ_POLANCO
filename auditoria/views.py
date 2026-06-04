# ---- IMPORTACIONES DE DJANGO 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from auditlog.models import LogEntry
from django.contrib.auth.models import User
# ---- IMPORTACIONES LOCALES
from .models import RegistroReporte

# ----------- VISTAS ----------- #

# Gestión de Actividad
@login_required
def seguimiento_actividad(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    
    logs = LogEntry.objects.select_related('actor', 'content_type').all().order_by('-timestamp')

    admin_id = request.GET.get('admin')
    fecha = request.GET.get('fecha')
    if admin_id:
        logs = logs.filter(actor_id=admin_id)
    if fecha:
        logs = logs.filter(timestamp__date=fecha)
    
    administradores = User.objects.filter(perfil__rol='ADMIN')

    context = {
        'logs': logs,
        'administradores': administradores,
    }

    return render(request, 'auditoria/seguimiento_actividad.html', context)

@login_required
def historial_reportes(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    
    reportes = RegistroReporte.objects.all().order_by('-fecha_generacion')

    tipo = request.GET.get('tipo')
    if tipo:
        reportes = reportes.filter(tipo=tipo)
    
    context = {
        'reportes': reportes, 
        'tipos': RegistroReporte.TIPO_REPORTE
    }

    return render(request, 'auditoria/historial_reportes.html', context)