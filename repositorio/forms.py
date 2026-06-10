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
    archivo_pdf = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf'})
    )
    portada = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )
    class Meta:
        model = DocumentoDigital
        fields = ['titulo', 'autor', 'descripcion', 'categoria']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows':3, 'class': 'input-modern'}),
            'titulo': forms.TextInput(attrs={'class': 'input-modern'}),
            'autor': forms.TextInput(attrs={'class': 'input-modern'}),
            'categoria': forms.Select(attrs={'class': 'input-modern'})
        }
    def clean_archivo_pdf(self):
        return self.cleaned_data.get('archivo_pdf')

    def clean_portada(self):
        return self.cleaned_data.get('portada')