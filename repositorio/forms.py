from django import forms
from .models import DocumentoDigital, CategoriaDigital

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaDigital
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input-modern', 'placeholder': 'Ej. Revistas Científicas'})
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoDigital
        fields = ['titulo', 'autor', 'descripcion', 'categoria', 'archivo_pdf', 'portada']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows':3, 'class': 'input-modern'}),
            'titulo': forms.TextInput(attrs={'class': 'input-modern'}),
            'autor': forms.TextInput(attrs={'class': 'input-modern'}),
            'categoria': forms.Select(attrs={'class': 'input-modern'})
        }