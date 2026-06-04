from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.perfil.rol == 'ADMIN'):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder a esta área.")
            return redirect('home')
    return wrapper_func