from django import forms
from .models import Libro, Ejemplar, Ubicacion

# Formulario de libros
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'cutter', 'descripcion', 'imagen_portada', 'autores', 'generos',
                  'origen', 'es_infantil', 'es_bolivariano']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'w-full p-2 text-slate-300 border rounded'}),
            'cutter': forms.TextInput(attrs={'class': 'w-full p-2 text-slate-300 border rounded'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full p-2 border text-slate-300 rounded', 'rows': 3}),
            'autores': forms.SelectMultiple(attrs={'class': 'w-full p-2 border text-slate-300 rounded'}),
            'generos': forms.SelectMultiple(attrs={'class': 'w-full p-2 border text-slate-300 rounded'}),
            'imagen_portada': forms.FileInput(attrs={'class': 'hidden', 'id': 'input-portada', 'accept': 'image/*'}),
            'origen': forms.Select(attrs={'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-white outline-none focus:ring-2 focus:ring-blue-500 transition cursor-pointer'}),
            'es_infantil': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900'}),
            'es_bolivariano': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900'}),
        }

# Formularios de Ejemplares
class EjemplarForm(forms.ModelForm):
    class Meta:
        model = Ejemplar
        fields = ['libro', 'ubicacion', 'codigo_inventario', 'anio_publicacion']
        widgets = {
            'libro': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'ubicacion': forms.Select(attrs={'class': 'w-full bg-slate-900 border-slate-700 text-white p-3 rounded-lg'}),
            'codigo_inventario': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'anio_publicacion': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# Formularios de Ubicaciones
class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['estante']
        widgets = {
            'estante': forms.TextInput(attrs={'class': 'w-full bg-white border-slate-900 text-slate-900 rounded-lg p-3', 'placeholder': 'Ej: Referencia 1'}),
        }