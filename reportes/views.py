#---------------- IMPORTACIONES -----------#
# LIBRERIAS ESTANDAR
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
import base64
import os
# IMPORTACIONES LOCALES
from .utils import render_to_pdf, generar_y_registrar_reporte
from catalogo.models import Ejemplar
from prestamos.models import Prestamo

#------------------------ VISTAS --------------#
#PORTAL PRINCIPAL
def portal_reportes(request):
    return render(request, 'reportes/portal.html')

#INVENTARIO POR ESTANTE
def get_data_estante(estante_query):
    if not estante_query:
        return [], [], 0, 0
        
    base_query = Ejemplar.objects.filter(ubicacion__estante__icontains=estante_query)
    
    # Resumen por Categoría (Cutter o Dewey)
    resumen = base_query.values('libro__cutter').annotate(total=Count('id')).order_by('libro__cutter')
    
    # Listado Detallado (Select *)
    detallado = base_query.select_related('libro', 'ubicacion').order_by('ubicacion__estante')
    
    total_libros = base_query.values('libro').distinct().count()
    total_ejemplares = base_query.count()
    
    return resumen, detallado, total_libros, total_ejemplares

def inventario_estante(request):
    estante = request.GET.get('estante', '')
    resumen, detallado, total_libros, total_ejemplares = get_data_estante(estante)
    
    return render(request, 'reportes/rep_estante.html', {
        'estante': estante,
        'resumen': resumen,
        'detallada': detallado,
        'total_libros': total_libros,
        'total_ejemplares': total_ejemplares
    })

def pdf_inventario_estante(request):
    estante = request.GET.get('estante', '')
    resumen, detallado, total_libros, total_ejemplares = get_data_estante(estante)
    
    logo_izq_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo1.png')
    logo_der_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_carnet.png')

    logo_izq_64 = ""
    if os.path.exists(logo_izq_path):
        with open(logo_izq_path, "rb") as f:
            logo_izq_64 = base64.b64encode(f.read()).decode('utf-8')
            
    logo_der_64 = ""
    if os.path.exists(logo_der_path):
        with open(logo_der_path, "rb") as f:
            logo_der_64 = base64.b64encode(f.read()).decode('utf-8')

    context = {
        'titulo': f'Inventario Estante: {estante}',
        'resumen': resumen,
        'detallada': detallado,
        'total_libros': total_libros,
        'total_ejemplares': total_ejemplares,
        'fecha': timezone.now(),
        'admin_nombre': request.user.get_full_name() or request.user.username,
        'logo_izq_64': logo_izq_64,
        'logo_der_64': logo_der_64,
    }
    return generar_y_registrar_reporte(
        'reportes/pdf_base_estante.html', 
        context,
        'INVENTARIO',
        request.user)

# PRÉSTAMOS MENSUALES 
def get_data_mensual(mes_anio):
    if not mes_anio:
        return []

    year, month = mes_anio.split('-')
    return Prestamo.objects.filter(
        fecha_aprobacion__year=year, 
        fecha_aprobacion__month=month
    ).select_related('ejemplar__libro', 'usuario')

def prestamos_mensual(request):
    mes = request.GET.get('mes', '') 
    prestamos = get_data_mensual(mes)
    
    return render(request, 'reportes/rep_mensual.html', {
        'mes': mes,
        'prestamos': prestamos,
        'total': prestamos.count() if prestamos else 0
    })

def pdf_prestamos_mensual(request):
    mes = request.GET.get('mes', '')
    prestamos = get_data_mensual(mes)
    
    context = {
        'titulo': f'Reporte Mensual: {mes}',
        'prestamos': prestamos,
        'fecha': timezone.now()
    }
    return generar_y_registrar_reporte(
        'reportes/pdf_base_lista.html', 
        context,
        'INVENTARIO',
        request.user)


def get_data_retrasados(filtro_mes=None):
    hoy = timezone.now().date()

    query = Prestamo.objects.filter(
        estado='PRESTADO', 
        fecha_devolucion_esperada__lt=hoy  
    )
    
    if filtro_mes:
         year, month = filtro_mes.split('-')
         query = query.filter(fecha_aprobacion__year=year, fecha_aprobacion__month=month)
         
    return query.select_related('ejemplar__libro', 'usuario')

def prestamos_retrasados(request):
    mes = request.GET.get('mes', '')
    prestamos = get_data_retrasados(mes if mes else None)
    
    return render(request, 'reportes/rep_retrasados.html', {
        'mes': mes,
        'prestamos': prestamos,
        'total': prestamos.count()
    })

def pdf_prestamos_retrasados(request):
    mes = request.GET.get('mes', '')
    prestamos = get_data_retrasados(mes if mes else None)
    
    context = {
        'titulo': 'Reporte de Morosidad / Retrasos',
        'subtitulo': f'Filtrado por: {mes}' if mes else 'Reporte General',
        'prestamos': prestamos,
        'es_retraso': True, 
        'fecha': timezone.now()
    }
    return generar_y_registrar_reporte(
        'reportes/pdf_base_lista.html', 
        context,
        'INVENTARIO',
        request.user)
