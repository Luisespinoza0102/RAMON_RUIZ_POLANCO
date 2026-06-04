from django.contrib import admin
from .models import Autor, Editorial, Ejemplar, Genero, Ubicacion, Libro

admin.site.register(Autor)
admin.site.register(Editorial)
admin.site.register(Ejemplar)
admin.site.register(Genero)
admin.site.register(Libro)
admin.site.register(Ubicacion)