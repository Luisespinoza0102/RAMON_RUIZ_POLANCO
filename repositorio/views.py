from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DocumentoDigital, CategoriaDigital
from .forms import DocumentoForm, CategoriaForm

# --------- VISTAS DE ADMIN -----------------

# Gestión de categorías
@login_required
def lista_categorias(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    categorias = CategoriaDigital.objects.all()
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'repositorio/admin_categorias.html', {'categorias': categorias, 'form': form})

# Gestión de Documentos
@login_required
def gestion_repositorio(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    documentos = DocumentoDigital.objects.all().order_by('-fecha_subida')
    return render(request, 'repositorio/admin_gestion.html', {'documentos': documentos})

@login_required
def crear_documento(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.subido_por = request.user
            doc.save()
            return redirect('gestion_repositorio')
    else:
        form = DocumentoForm()

    return render(request, 'repositorio/admin_form.html', {'form': form, 'titulo_vista': 'Cargar Nuevo Documento'})

@login_required
def editar_documento(request, id):
    doc = get_object_or_404(DocumentoDigital, id=id)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
           form.save()
           return redirect('gestion_repositorio')
    else: 
        form = DocumentoForm(instance=doc)
    return render(request, 'repositorio/admin_form.html', {'form': form, 'titulo_vista': 'Editar Documento'})

@login_required
def eliminar_documento(request, id):
    doc = get_object_or_404(DocumentoDigital, id=id)
    doc.delete()
    return redirect('gestion_repositorio')

# Vistas del usuario
def catalogo_digital(request):
    query = request.GET.get('q', '')
    documentos = DocumentoDigital.objects.all()

    if query:
        documentos = documentos.filter(titulo__icontains=query) | documentos.filter(autor__icontains=query)
    
    return render(request, 'repositorio/usuario_catalogo.html', {
        'documentos': documentos,
        'query': query
    })

def detalle_digital(request, id):
    documento = get_object_or_404(DocumentoDigital, id=id)
    documento.descargas += 1
    documento.save()
    return render(request, 'repositorio/usuario_detalle.html', {'documento': documento})