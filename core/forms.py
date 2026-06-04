from django import forms
from django.core.exceptions import ValidationError
from .models import Perfil, Documento_Perfil

class RegistroUsuarioForm(forms.Form):
    carnet = forms.CharField(max_length=100, required=False)

    dni = forms.CharField(
        max_length=20,
        label="Cédula de Identidad",
        widget=forms.TextInput(attrs={'class': 'w-full bg-slate-900 border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none' })
    )

    nombres = forms.CharField(max_length=100, required=False)
    apellidos = forms.CharField(max_length=100, required=False)

    password = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'w-full bg-slate-900 border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none' })
    )

    confirm_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'w-full bg-slate-900 border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none' })
    )

    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full bg-slate-900 border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none' })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto_perfil']