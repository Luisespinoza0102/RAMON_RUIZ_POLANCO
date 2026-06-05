# ------------ IMPORTACIONES -----------#
# Librerias Estandar
import json
# Librerias de Django
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
# Librerias Extras
from xhtml2pdf import pisa
# Importaciones Locales
from .models import Libro, Ejemplar, Genero, Autor, Editorial, Ubicacion
from .forms import LibroForm, EjemplarForm, UbicacionForm
from .utils.generador_cutter import generador
# Importaciones Externas
from core.utils import guardar_archivo_sistema
from recomendacion.models import HistorialBusqueda

# ------------ VISTAS ------------------- #

# Interfaz Pública
def catalogo_publico(request):
    query = request.GET.get('q')
    # Capturamos TODOS los parámetros de la URL
    filtros = request.GET.dict()
    filtros.pop('q', None)
    filtros.pop('csrfmiddlewaretoken', None)
    
    if query:
        libros = Libro.objects.filter(
            Q(titulo__icontains=query) | 
            Q(autores__nombre_completo__icontains=query) | 
            Q(generos__nombre__icontains=query)
        ).distinct()
        
        # Guardar en el historial CON LOS FILTROS
        if request.user.is_authenticated:
            HistorialBusqueda.objects.create(
                usuario=request.user, 
                termino_busqueda=query,
                filtros_usados=filtros 
            )
    else:
        libros = Libro.objects.all()
    
    return render(request, 'catalogo/lista_publica.html', {'libros': libros})

def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    disponibles = libro.ejemplares.filter(estado='DISPONIBLE').count()
    prestamos_vencidos = False
    if request.user.is_authenticated:
        prestamos_vencidos = request.user.prestamos.filter(
            estado='APROBADO', 
            fecha_devolucion_esperada__lt=timezone.now().date()
        ).exists()
    puedo_solicitar = disponibles > 0 and not prestamos_vencidos
    context = {
        'libro': libro,
        'ejemplares': libro.ejemplares.all(),
        'disponibles': disponibles,
        'puedo_solicitar': puedo_solicitar,
        'prestamos_vencidos': prestamos_vencidos,
    }
    return render(request, 'catalogo/detalle_libro.html', context)

# Gestión Administrativa
# ----------- Gestión Libros ---------- #
@login_required
def gestion_libros(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')

    query = request.GET.get('q', '').strip() # Obtenemos parametros de busqueda
    filter_by = request.GET.get('filter_by', 'titulo')
    libros = Libro.objects.all().prefetch_related('autores', 'generos', 'ejemplares').order_by('-id') 
    if query: # Aplica la lógica de filtrado
        if filter_by == 'titulo':
            libros = libros.filter(titulo__icontains=query)
        
        elif filter_by == 'cutter':
            libros = libros.filter(cutter__icontains=query)
            
        elif filter_by == 'autor':
            libros = libros.filter(autores__nombre_completo__icontains=query).distinct()
            
        elif filter_by == 'genero':
            libros = libros.filter(generos__nombre__icontains=query).distinct()
            
        elif filter_by == 'estante':
            libros = libros.filter(ejemplares__ubicacion__estante__icontains=query).distinct()

    return render(request, 'catalogo/gestion_libros.html', {
        'libros': libros,
        'query': query,
        'filter_by': filter_by
    })

@login_required
def crear_libro(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
        
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            if request.FILES.get('imagen_portada'):
                libro.imagen_portada = guardar_archivo_sistema(request.FILES['imagen_portada'], 'libros')
            autores_seleccionados = request.POST.getlist('autores')
            if autores_seleccionados:
                primer_autor_id = autores_seleccionados[0]
                try:
                    autor_obj = Autor.objects.get(id=primer_autor_id)
                    libro.cutter = generador.generar_codigo(
                        autor_obj.nombre_completo, 
                        libro.titulo
                    )
                except Autor.DoesNotExist:
                    pass
            libro.save()
            form.save_m2m()

            messages.success(request, f"Libro '{libro.titulo}' registrado con Éxito. Cutter: {libro.cutter}")
            return redirect('gestion_libros')
    else:
        form = LibroForm()
    return render(request, 'catalogo/form_libro.html', {'form': form, 'titulo': 'Registrar Nuevo Libro'})

@login_required
def editar_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
        
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro) #Creamos un formulario asociado al libro existente
        if form.is_valid():
            libro_editado = form.save(commit=False)
            if request.FILES.get('imagen_portada'):
                libro_editado.imagen_portada = guardar_archivo_sistema(request.FILES['imagen_portada'], 'libros')
            libro_editado.save()
            form.save_m2m()
            return redirect('gestion_libros')
    else:
        form = LibroForm(instance=libro)
    return render(request, 'catalogo/form_libro.html', {'form': form, 'titulo': 'Editar Libro'})

@login_required
def eliminar_libro(request, pk):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
    
    libro = get_object_or_404(Libro, pk=pk)
    titulo = libro.titulo
    libro.delete()

    messages.error(request, f"El Libro '{titulo}' y todos sus ejemplares han sido removidos del sistema.")
    return redirect('gestion_libros')


# ----------------- Gestión Ejemplares ------------- #
@login_required
def crear_ejemplar(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
        
    if request.method == 'POST':
        form = EjemplarForm(request.POST)
        nombre_ed = request.POST.get('editorial_manual', '').strip()
        if form.is_valid():
            ejemplar = form.save(commit=False)
            
            if nombre_ed:
                editorial_obj, created = Editorial.objects.get_or_create(
                    nombre__iexact=nombre_ed,
                    defaults={'nombre': nombre_ed}
                )
                ejemplar.editorial = editorial_obj
                ejemplar.save()
                messages.success(request, f"Ejemplar registrado con la editorial: {editorial_obj.nombre}")
                return redirect('gestion_libros')
            else:
                messages.error(request, "Por favor, indique el nombre de la editorial.")
    else:
        form = EjemplarForm()
    editoriales = Editorial.objects.all()
    return render(request, 'catalogo/form_ejemplar.html', {
        'form': form, 
        'editoriales': editoriales
    })

@login_required
def lista_ejemplares(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    ejemplares = libro.ejemplares.all()
    return render(request, 'catalogo/lista_ejemplares.html', {
        'libro': libro,
        'ejemplares': ejemplares
    })

@login_required
def editar_ejemplar(request, ejemplar_id):
    ejemplar = get_object_or_404(Ejemplar, id=ejemplar_id)
    ubicaciones = Ubicacion.objects.all()
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        nueva_ubicacion_id = request.POST.get('ubicacion')
        if nuevo_estado:
            ejemplar.estado = nuevo_estado
            ejemplar.ubicacion_id = nueva_ubicacion_id
            ejemplar.save()
            
            messages.success(request, "Ejemplar actualizado con éxito.")
            return redirect('lista_ejemplares', libro_id=ejemplar.libro.id)
        else:
            messages.error(request, "El campo estado no puede estar vacío.")

    return render(request, 'catalogo/editar_ejemplar.html', {
        'ejemplar': ejemplar,
        'ubicaciones': ubicaciones
    })

@login_required
def eliminar_ejemplar(request, ejemplar_id):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
    
    ejemplar = get_object_or_404(Ejemplar, id=ejemplar_id)
    libro_id = ejemplar.libro.id
    titulo_libro = ejemplar.libro.titulo

    ejemplar.delete()
    messages.warning(request, f"Ejemplar del libro '{titulo_libro}' eliminado del inventario")
    return redirect('lista_ejemplares', libro_id=libro_id)


# API
@login_required
def api_crear_autor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nuevo = Autor.objects.create(nombre_completo=data.get('nombre'))
        return JsonResponse({'id': nuevo.id, 'nombre': nuevo.nombre_completo})

@login_required
def api_crear_genero(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Aquí integramos el Sistema Dewey
        nuevo = Genero.objects.create(
            nombre=data.get('nombre'),
            codigo_dewey=data.get('dewey')
        )
        return JsonResponse({
            'id': nuevo.id, 
            'nombre': f"{nuevo.codigo_dewey} - {nuevo.nombre}"
        })

@login_required
def api_generar_cutter(request):
    autor = request.GET.get('autor', '')
    titulo = request.GET.get('titulo', '')

    codigo = generador.generar_codigo(autor, titulo)

    return JsonResponse({'cutter': codigo})

# Reportes
@login_required
def portal_reportes(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    # Obtenemos las salas y estantes únicos para el filtro
    salas = Ejemplar.objects.values('sala').distinct()
    # Una lista de tuplas (Sala, Estante) únicos
    estantes = Ejemplar.objects.values('sala', 'estante').distinct().order_by('sala', 'estante')
    
    return render(request, 'catalog/portal_reportes.html', {
        'salas': salas,
        'estantes': estantes
    })

@login_required
def generar_reporte_estante(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    
    ubicacion_id = request.GET.get('ubicacion_id')
    ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
    
    ejemplares = Ejemplar.objects.filter(ubicacion=ubicacion, estado='DISPONIBLE')
    total_general = ejemplares.count()
    
    desglose = {
        '000': {'n': 'Generalidades', 'c': 0}, '100': {'n': 'Filosofía', 'c': 0},
        '200': {'n': 'Religión', 'c': 0}, '300': {'n': 'Ciencias Sociales', 'c': 0},
        '400': {'n': 'Lenguas', 'c': 0}, '500': {'n': 'Ciencias Puras', 'c': 0},
        '600': {'n': 'Tecnología', 'c': 0}, '700': {'n': 'Artes', 'c': 0},
        '800': {'n': 'Literatura', 'c': 0}, '900': {'n': 'Historia/Geografía', 'c': 0},
        'PV': {'n': 'Poesía Venezolana', 'c': 0},
        'NV': {'n': 'Novela Venezolana', 'c': 0},
        'TV': {'n': 'Teatro Venezolano', 'c': 0},
        'CV': {'n': 'Cuento Venezolano', 'c': 0},
    }

    for ej in ejemplares:
        genero = ej.libro.generos.first()
        if genero and genero.codigo_dewey:
            cod = genero.codigo_dewey.upper().strip()
            if cod in desglose:
                desglose[cod]['c'] += 1
            elif cod[0].isdigit():
                clave = f"{cod[0]}00"
                if clave in desglose:
                    desglose[clave]['c'] += 1

    template_path = 'catalogo/reporte_estante_pdf.html' 
    context = {
        'ubicacion': ubicacion,
        'ejemplares': ejemplares,
        'total': total_general,
        'desglose': desglose,
        'fecha': timezone.now()
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Reporte_{ubicacion.estante}.pdf"'
    
    html = render_to_string(template_path, context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err: return HttpResponse('Error PDF')
    return response

@login_required
def gestion_ubicaciones(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    
    ubicaciones = Ubicacion.objects.all().order_by('estante')
    total_ubicaciones = ubicaciones.count()
    
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nueva ubicación registrada correctamente.")
            return redirect('gestion_ubicaciones')
    else:
        form = UbicacionForm()
        
    return render(request, 'catalogo/gestion_ubicaciones.html', {
        'ubicaciones': ubicaciones,
        'total_ubicaciones': total_ubicaciones,
        'form': form
    })
