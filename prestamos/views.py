from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db import transaction
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import Prestamo, Notificacion
from catalogo.models import Libro, Ejemplar

@login_required
def solicitar_prestamo(request, libro_id):
    if request.method == 'POST':
        libro = get_object_or_404(Libro, id=libro_id)
        
        #Restricción 
        if libro.es_infantil or libro.es_bolivariano:
            messages.error(
                request, 
                f"El libro {libro.titulo} pertenece a la colección infantil o estadal."
                f"Solo está permitido para lectura en la sala interna de la biblioteca."
            )
            return redirect('detalle_libro', libro_id=libro.id)
        
        ejemplar = libro.ejemplares.filter(estado='DISPONIBLE').first()
        
        duracion = int(request.POST.get('duracion_dias', 7))
        if duracion not in [7, 15]:
            duracion = 7

        if not ejemplar:
            messages.error(request, "Ya no hay copias disponibles.")
            return redirect('detalle_libro', libro_id=libro.id)

        try:
            with transaction.atomic():
                fecha_vencimiento = datetime.now() + timedelta(days=7)
                Prestamo.objects.create(
                    usuario=request.user,
                    ejemplar=ejemplar,
                    estado='SOLICITADO',
                    fecha_devolucion_esperada=fecha_vencimiento
                )

            messages.success(request, f"Solicitud enviada con éxito.")
            return redirect('dashboard_usuario')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('detalle_libro', libro_id=libro.id)
    return redirect('catalogo_publico')

@login_required
def mis_prestamos(request):
    prestamos = Prestamo.objects.filter(usuario=request.user).order_by('-fecha_solicitud')
    return render(request, 'prestamos/mis_pedidos.html', {'prestamos': prestamos})

@login_required
def admin_prestamos(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('dashboard_usuario')
    if request.method == 'POST':
        accion = request.POST.get('accion')
        prestamo_id = request.POST.get('id')
        
        if accion == 'aprobar':
            return redirect('revisar_solicitud', prestamo_id=prestamo_id)

    prestamos = Prestamo.objects.all().order_by('-fecha_solicitud')
    return render(request, 'prestamos/admin_lista.html', {'prestamos': prestamos})

# Vista Previa
@login_required
def revisar_solicitud_admin(request, prestamo_id):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    
    return render(request, 'prestamos/vista_previa_aprobacion.html', {'prestamo': prestamo})

@login_required
def rechazar_prestamo(request, prestamo_id):
    if request.user.perfil.rol != 'ADMIN': 
        return redirect('catalogo_publico') 
    
    if request.method == 'POST':
        prestamo = get_object_or_404(Prestamo, id=prestamo_id)
        
        if prestamo.estado == 'SOLICITADO':
            nombre_usuario = prestamo.usuario.get_full_name()
            titulo_libro = prestamo.ejemplar.libro.titulo
            prestamo.estado = 'RECHAZADO'
            prestamo.save()

            Notificacion.objects.create(
                usuario=prestamo.usuario,
                mensaje=f"Tu solicitud para el libro '{titulo_libro}' ha sido RECHAZADA.",
                tipo='RECHAZADO'
            )
            
            messages.warning(request, f"Has cancelado el préstamo de {nombre_usuario}.")
        
    return redirect('admin_prestamos')

@login_required
def devolver_libro(request, prestamo_id):

    if request.user.perfil.rol != 'ADMIN': return redirect('catalogo_publico')
    
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    prestamo.estado = 'DEVUELTO'
    prestamo.fecha_devolucion_real = timezone.now()
    prestamo.save()
    
    messages.success(request, f"Devolución registrada. Stock actualizado automáticamente.")
    return redirect('admin_prestamos')

@login_required
def confirmar_aprobacion(request, prestamo_id):
    if request.user.perfil.rol != 'ADMIN': return redirect('catalogo_publico')
    
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    
    if prestamo.estado == 'SOLICITADO':
        
        prestamo.estado = 'APROBADO'
        prestamo.fecha_aprobacion = timezone.now()
        prestamo.fecha_devolucion_esperada = (timezone.now() + timedelta(days=prestamo.duracion_dias)).date()

        prestamo.save() 
        
        # Generar la URL de descarga del PDF
        try:
            url_pdf = reverse('descargar_pdf_usuario', args=[prestamo.id])
        except:
            url_pdf = "#"

        # Notificar
        Notificacion.objects.create(
            usuario=prestamo.usuario,
            mensaje=f"Solicitud aprobada para '{prestamo.ejemplar.libro.titulo}'.",
            tipo='APROBADO',
            enlace=url_pdf
        )
        
        messages.success(request, f"Préstamo aprobado para {prestamo.usuario.get_full_name()}.")
    
    return redirect('admin_prestamos')

@login_required
def solicitar_renovacion(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id, usuario=request.user)
    if prestamo.estado == 'APROBADO':
        if prestamo.es_renovado:
            messages.error(request, "Este préstamo ya ha sido renovado previamente.")
        else:
            prestamo.estado = 'RENOVACION_SOLICITADA'
            prestamo.save()
            messages.success(request, "Tu solicitud de renovación ha sido enviada al administrador.")
    else:
        messages.error(request, "No se puede solicitar renovación para este préstamo.")

    return redirect('mis_prestamos')

@login_required
def procesar_renovacion_admin(request, prestamo_id):
    if request.user.perfil.rol != 'ADMIN': return redirect('catalogo_publico')

    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if request.method == 'POST' and prestamo.estado == 'RENOVACION_SOLICITADA':
        accion = request.POST.get('accion_renovacion')

        if accion == 'aprobar':
            dias_extra = int(request.POST.get('dias_renovacion', 7))
            if dias_extra not in [7, 15]: dias_extra = 7

            prestamo.fecha_devolucion_esperada = prestamo.fecha_devolucion_esperada + timedelta(days=dias_extra)
            prestamo.estado = 'APROBADO'
            prestamo.es_renovado = True
            prestamo.save()

            Notificacion.objects.create(
                usuario=prestamo.usuario,
                mensaje=f"Tu renovación para '{prestamo.ejemplar.libro.titulo}' fue APROBADA por {dias_extra} días adicionales.",
                tipo='APROBADO'
            )
            messages.success(request, f"Renovación aprobada por {dias_extra} días extras.")
        
        elif accion == 'rechazar':
            prestamo.estado = 'APROBADO'
            prestamo.save()

            Notificacion.objects.create(
                usuario=prestamo.usuario,
                mensaje=f"Tu solicitud de renovación para '{prestamo.ejemplar.libro.titulo}' ha sido RECHAZADA.",
                tipo='Rechazado'
            )
            messages.warning(request, "Solicitud de renovación rechazada.")
    return redirect('admin_prestamos')

def link_callback(uri, rel):

    if uri.startswith(settings.STATIC_URL):

        relative_path = uri.replace(settings.STATIC_URL, "").lstrip('/')
    elif uri.startswith(settings.MEDIA_URL):
        relative_path = uri.replace(settings.MEDIA_URL, "").lstrip('/')
    else:
        relative_path = uri.lstrip('/')

    for static_dir in settings.STATICFILES_DIRS:
        full_path = os.path.join(static_dir, relative_path)
        if os.path.exists(full_path):
            return full_path

    return uri

@login_required
def descargar_pdf_usuario(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    
    if request.user != prestamo.usuario and request.user.perfil.rol != 'ADMIN':
        return redirect('home')

    template_path = 'prestamos/pdf_formal.html'
    context = {'prestamo': prestamo, 'hoy': timezone.now()}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Comprobante_{prestamo.id}.pdf"'
    
    html = render_to_string(template_path, context)

    pisa_status = pisa.CreatePDF(
        html, 
        dest=response, 
        link_callback=link_callback
    )
    
    if pisa_status.err: return HttpResponse('Error generando PDF')
    return response

@login_required
def mis_notificaciones(request):
    notificaciones = request.user.notificaciones.all()
    request.user.notificaciones.filter(leido=False).update(leido=True)
    
    return render(request, 'prestamos/mis_notificaciones.html', {
        'notificaciones': notificaciones
    })

@login_required
def borrar_notificacion(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.delete()
    messages.success(request, "Notificación eliminada.")
    return redirect('mis_notificaciones')

@login_required
def marcar_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    
    if not notificacion.leido:
        notificacion.leido = True
        notificacion.save()

    if notificacion.enlace:
        return redirect(notificacion.enlace)

    return redirect('mis_notificaciones')