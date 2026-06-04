from django.contrib import admin
from .models import Prestamo, Sancion, Notificacion

admin.site.register(Prestamo)
admin.site.register(Sancion)
admin.site.register(Notificacion)
