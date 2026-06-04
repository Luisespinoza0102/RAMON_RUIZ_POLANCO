from django.urls import path
from . import views

urlpatterns = [
    path('gestion/', views.gestion_repositorio, name='gestion_repositorio'),
    path('gestion/nuevo/', views.crear_documento, name='crear_documento'),
    path('gestion/editar/<uuid:id>/', views.editar_documento, name='editar_documento'),
    path('gestion/eliminar/<uuid:id>/', views.eliminar_documento, name='eliminar_documento'),
    path('gestion/categorias/', views.lista_categorias, name='lista_categorias'),
    
    path('biblioteca-virtual/', views.catalogo_digital, name='catalogo_digital'),
    path('visor/<uuid:id>/', views.detalle_digital, name='detalle_digital'),
]