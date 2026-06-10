#------------- IMPORTACIONES ------------------#
# lIBRERIAS ESTANDAR
from django.shortcuts import render, redirect, get_object_or_404
import os
import base64
import requests
import cloudinary.uploader
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.contrib.auth.views import PasswordChangeView 
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse_lazy 
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
# IMPORTACIONES LOCALES
from .forms import RegistroUsuarioForm
from .models import Perfil, Documento_Perfil, TIPOS_DOCUMENTOS
from .utils import guardar_archivo_sistema
from prestamos.models import Prestamo, Notificacion
from prestamos.views import link_callback
from catalogo.models import Libro
from recomendacion.engine import obtener_recomendaciones
from recomendacion.models import HistorialBusqueda


# ----------------------- VISTAS -------------------#

# AUTENTICACIÓN
def verificar_cedula(request):
    cedula = request.GET.get('dni', None)
    data = {'existe': False, 'nombre_completo': '', 'ya_activo': False}

    if cedula:
        user = User.objects.filter(username=cedula).first()
        if user:
            data['existe'] = True
            data['nombre_completo'] = f"{user.first_name} {user.last_name}"
            data['ya_activo'] = user.has_usable_password()

    return JsonResponse(data)

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            cedula_ingresada = form.cleaned_data['dni'] 
            nueva_clave = form.cleaned_data['password']
            nuevo_tel = form.cleaned_data.get('telefono')

            try:
                # Buscamos al usuario pre-creado
                user = User.objects.get(username=cedula_ingresada)
                if user.has_usable_password():
                    messages.warning(request, "Esta Cuenta ya está activa. Por Favor, inicia sesión")
                    return redirect('login')
                
                user.set_password(nueva_clave)
                user.save()

                perfil = user.perfil
                perfil.estado = 'ACTIVO'
                if nuevo_tel:
                    perfil.telefono = nuevo_tel
                perfil.save()

                messages.success(request, "¡Cuenta activada con éxito! Ya puedes Iniciar Sesión")
                return redirect('login')

            except User.DoesNotExist:
                messages.error(request, "No te encuentras pre-registrado en el sistema.")
        else:
            
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'core/registro.html', {'form': form})

# NAVEGACIÓN Y DASHBOARD
@login_required
def dispatch_dashboard(request):
    if request.user.perfil.rol == 'ADMIN': return redirect('dashboard_admin')
    return redirect('dashboard_usuario')

@login_required
def dashboard_usuario(request):
    # Lógica de Recomendación
    recomendados = obtener_recomendaciones(request.user)
    prestamos_activos = Prestamo.objects.filter(usuario=request.user, estado__in=['SOLICITADO', 'APROBADO'])
    
    return render(request, 'core/dashboard_usuario.html', {
        'recomendados': recomendados,
        'prestamos': prestamos_activos
    })

@login_required
def dashboard_admin(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    # Métricas para el admin
    pendientes = Prestamo.objects.filter(estado='SOLICITADO').count()
    vencidos_count = 0 
    for p in Prestamo.objects.filter(estado='APROBADO'):
        if p.esta_vencido: vencidos_count += 1
    # Buscamos libros que tengan 0 ejemplares DISPONIBLES
    libros_con_stock = Libro.objects.annotate(
        cantidad_disponible=Count(
            'ejemplares',
            filter=Q(ejemplares__estado='DISPONIBLE')
        )
    )
    # Filtramos solo los que están en 0 o nivel crítico (ej. menos de 2)
    libros_alerta = libros_con_stock.filter(cantidad_disponible__lte=1).order_by('cantidad_disponible')
    
    return render(request, 'core/dashboard_admin.html', {
        'libros_alerta': libros_alerta,
        'pendientes': pendientes,
        'vencidos': vencidos_count
    })

# CONFIGURACIÓN DE USUARIOS
@login_required
def gestion_usuarios(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    
    if request.method == 'POST':
        # Captura de datos básicos
        u_cedula = request.POST.get('cedula')
        u_carnet = request.POST.get('carnet')
        u_nombres = request.POST.get('nombres')
        u_apellidos = request.POST.get('apellidos')
        u_email = request.POST.get('email')
        u_dir = request.POST.get('direccion')
        u_tel = request.POST.get('telefono')

        try:
            with transaction.atomic():
                nuevo_user = User.objects.create_user(
                    username=u_cedula, 
                    email=u_email, 
                    first_name=u_nombres,
                    last_name=u_apellidos
                )
                
                u_foto = request.FILES.get('foto_perfil')
                if u_foto:
                    u_foto_procesada = guardar_archivo_sistema(u_foto, 'perfiles')
                else:
                    u_foto_procesada = None

                perfil = Perfil.objects.create(
                    usuario=nuevo_user,
                    cedula =u_cedula,
                    carnet=u_carnet,
                    direccion=u_dir,
                    telefono=u_tel,
                    foto_perfil=u_foto_procesada,
                    rol='USUARIO',
                    estado='ACTIVO'
                )

                #Bucle para guardar documentos
                for tipo_cod, tipo_nombre in TIPOS_DOCUMENTOS:
                    archivos = request.FILES.getlist(f'doc_{tipo_cod}')
                    for archivo in archivos:
                        archivo_procesado = guardar_archivo_sistema(archivo, f'documentos_usarios/{tipo_cod.lower()}')
                        Documento_Perfil.objects.create(
                            perfil=perfil,
                            tipo_documento=tipo_cod,
                            archivo=archivo_procesado
                        )

            messages.success(request, f"Usuario {u_nombres} {u_apellidos} registrado correctamente.")
            return redirect('gestion_usuarios')

        except IntegrityError:
            messages.error(request, f"Error: La Cédula {u_cedula} ya está en uso.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    usuarios = Perfil.objects.all().select_related('usuario')
    return render(request, 'core/gestion_usuarios.html', {'usuarios': usuarios, 'TIPOS_DOCUMENTOS': TIPOS_DOCUMENTOS})


@login_required
def editar_usuario(request, user_id):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')

    perfil = get_object_or_404(Perfil, id=user_id)
    usuario = perfil.usuario

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 1. Procesar eliminación de documentos seleccionados
                docs_a_eliminar = request.POST.getlist('eliminar_doc')
                for doc_id in docs_a_eliminar:
                    doc_obj = perfil.documentos.filter(id=doc_id).first()
                    if doc_obj:
                        # Se elimina el registro; Supabase maneja el ciclo de almacenamiento remoto
                        doc_obj.delete()

                # 2. Actualizar datos de la tabla User de Django
                usuario.first_name = request.POST.get('nombres')
                usuario.last_name = request.POST.get('apellidos')
                usuario.email = request.POST.get('email')
                usuario.save()

                # 3. Actualizar datos del Perfil del usuario
                perfil.telefono = request.POST.get('telefono')
                perfil.direccion = request.POST.get('direccion')
                perfil.rol = request.POST.get('rol')
                perfil.carnet = request.POST.get('carnet')
                perfil.estado = request.POST.get('estado', perfil.estado) 
                
                # Si subió una nueva foto de perfil, se procesa a Supabase
                if request.FILES.get('foto_perfil'):
                    perfil.foto_perfil = guardar_archivo_sistema(request.FILES.get('foto_perfil'), 'perfiles')
                perfil.save()

                # 4. Procesar la carga de nuevos documentos reglamentarios
                for tipo_cod, tipo_nombre in TIPOS_DOCUMENTOS:
                    archivos_nuevos = request.FILES.getlist(f'doc_{tipo_cod}')
                    
                    if archivos_nuevos:
                        # Si es un documento único como el carnet, limpiamos el anterior en BD
                        if tipo_cod == 'CARNET':
                            perfil.documentos.filter(tipo_documento='CARNET').delete()
                            
                        for archivo in archivos_nuevos:
                            archivo_procesado = guardar_archivo_sistema(archivo, f'documentos_usuarios/{tipo_cod.lower()}')
                            Documento_Perfil.objects.create(
                                perfil=perfil,
                                tipo_documento=tipo_cod,
                                archivo=archivo_procesado
                            )

                messages.success(request, f"Usuario {usuario.first_name} {usuario.last_name} actualizado correctamente.")
                return redirect('gestion_usuarios')

        except IntegrityError:
            messages.error(request, "Error de integridad: Verifique que el correo o documento no estén duplicados.")
        except Exception as e:
            messages.error(request, f"Error inesperado al actualizar: {str(e)}")

    return render(request, 'core/editar_usuario.html', {'perfil': perfil, 'TIPOS_DOCUMENTOS': TIPOS_DOCUMENTOS})

@login_required
def eliminar_usuario(request, user_id):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    
    perfil = get_object_or_404(Perfil, id=user_id)
    usuario = perfil.usuario

    if usuario == request.user:
        messages.error(request, "No Puedes Eliminar tu propia cuenta de Administrador")
        return redirect('gestion_usuarios')
    try:
        with transaction.atomic():
            if perfil.foto_perfil and "http" not in str(perfil.foto_perfil):
                if os.path.isfile(perfil.foto_perfil.path):
                   os.remove(perfil.foto_perfil.path)
            
            for doc in perfil.documentos.all():
                if doc.archivo and "http" not in str(doc.archivo):
                    if  os.path.isfile(doc.archivo.path):
                        os.remove(doc.archivo.path)
            nombre_completo = usuario.get_full_name()
            usuario.delete()

            messages.success(request, f"El usuario {nombre_completo} ha sido eliminado del sistema.")
    except Exception as e:
        messages.error(request, f"Error al intentar eliminar {str(e)}")
    return redirect('gestion_usuarios')

@login_required
def mi_perfil(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        if request.FILES.get('foto_perfil'):
            archivo_subido = request.FILES.get('foto_perfil')
            # El helper hace la validación de entorno automáticamente
            perfil.foto_perfil = guardar_archivo_sistema(archivo_subido, "perfiles")
            perfil.save()
            messages.success(request, "¡Tu foto de perfil ha sido actualizada!")
            return redirect('mi_perfil')
        else:
            messages.warning(request, "No seleccionaste ninguna imagen.")
    
    return render(request, 'core/perfil.html', {'perfil': perfil})

class CambiarPasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'core/cambiar_password.html'
    success_message = "¡Tu contraseña ha sido actualizada correctamente!"
    
    def get_success_url(self):
        if self.request.user.perfil.rol == 'ADMIN':
            return reverse_lazy('dashboard_admin')
        return reverse_lazy('dashboard_usuario')

# GESTIÓN DE NOTIFICACIONES
@login_required
def mis_notificaciones(request):
    notificaciones = request.user.notificaciones.all().order_by('-fecha')
    response = render(request, 'core/notificaciones.html', {'notificaciones': notificaciones})
    return response

@login_required
def marcar_leida(request, noti_id):
    noti = Notificacion.objects.get(id=noti_id, usuario=request.user)
    noti.leido = True
    noti.save()
    return redirect('mis_notificaciones')

@login_required
def mi_historial(request):
    busquedas = HistorialBusqueda.objects.filter(usuario=request.user).order_by('-fecha')[:20]
    prestamos_pasados = Prestamo.objects.filter(
        usuario=request.user, 
        estado__in=['DEVUELTO']
    ).order_by('-fecha_devolucion_real')

    return render(request, 'core/historial.html', {
        'busquedas': busquedas,
        'prestamos_pasados': prestamos_pasados
    })

# FAKE ADMIN
def vista_error_fake(request):
    return render(request, 'core/fake_404.html', status=404)

# GESTIÓN DE CARNET
@login_required
def previsualizar_carnet(request, user_id):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    
    perfil = get_object_or_404(Perfil, id=user_id)
    foto_carnet_doc = perfil.documentos.filter(tipo_documento='FOTO_CARNET').first()

    es_imagen = False
    foto_carnet_url = None

    if foto_carnet_doc and foto_carnet_doc.archivo:
        url_archivo = foto_carnet_doc.archivo.url.lower()
        if any(url_archivo.endswith(ext) for ext in ['.jpg', 'j.peg', '.png', '.webp']):
            es_imagen = True
            foto_carnet_url = foto_carnet_doc.archivo.url
        else:
            foto_carnet_url = foto_carnet_doc.archivo.url
    return render(request, 'core/vista_previa_carnet.html', {
        'perfil':perfil,
        'foto_carnet_url': foto_carnet_url,
        'es_imagen': es_imagen,})

@login_required
def enviar_carnet_usuario(request, user_id):
    if request.user.perfil.rol != 'ADMIN':
      return redirect('home')
    
    perfil = get_object_or_404(Perfil, id=user_id)
    try:
        url_descarga = reverse('descargar_pdf_carnet', args=[perfil.id])
    except:
        url_descarga = '#'
    
    Notificacion.objects.create(
        usuario=perfil.usuario,
        mensaje="¡Tu Carnet de la Biblioteca ha sido generado! Ya puedes descargarlo.",
        tipo='CARNET',
        enlace=url_descarga
    )
    messages.success(request, f"Carnet enviado exitosamente a {perfil.usuario.first_name} {perfil.usuario.last_name}.")
    return redirect('gestion_usuarios')

@login_required
def descargar_pdf_carnet(request, perfil_id):
    perfil = get_object_or_404(Perfil, id=perfil_id)
    foto_obj = perfil.documentos.filter(tipo_documento='FOTO_CARNET').first()

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_carnet.png')
    logo_64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_64 = base64.b64encode(f.read()).decode('utf-8')
    
    foto_64 = ""
    if foto_obj and foto_obj.archivo:
        url_archivo = foto_obj.archivo.url
        url_archivo_lower = url_archivo.lower()
        
        if any(url_archivo_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            try:
                if not url_archivo.startswith('http'):
                    if hasattr(settings, 'CLOUDINARY_STORAGE') or not settings.DEBUG:
                        url_archivo = cloudinary.uploader.build_url(foto_obj.archivo.name, secure=True)
                    else:
                        url_archivo = request.build_absolute_uri(url_archivo)

                response_url = requests.get(url_archivo, timeout=10)
                if response_url.status_code == 200:
                    foto_64 = base64.b64encode(response_url.content).decode('utf-8')
            except Exception as e:
                print(f"Error al descargar imagen: {e}")

    context = {
        'perfil': perfil,
        'logo_64': logo_64,
        'foto_64': foto_64,
    }

    template_path = 'core/carnet_pdf.html'
    html = render_to_string(template_path, context)
    response = HttpResponse(content_type='application/pdf')

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF')
    return response