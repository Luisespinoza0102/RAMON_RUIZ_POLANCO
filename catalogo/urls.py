from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.catalogo_publico, name='catalogo_publico'),
    path('libro/<uuid:libro_id>/', views.detalle_libro, name='detalle_libro'),
    
    # Gestión Admin
    path('gestion/', views.gestion_libros, name='gestion_libros'),
    path('nuevo/', views.crear_libro, name='crear_libro'),
    path('editar/<uuid:pk>/', views.editar_libro, name='editar_libro'),
    path('ejemplar/nuevo/', views.crear_ejemplar, name='crear_ejemplar'),
    path('api/crear-autor/', views.api_crear_autor, name='api_crear_autor'),
    path('api/crear-genero/', views.api_crear_genero, name='api_crear_genero'),
    
    path('reportes/portal/', views.portal_reportes, name='portal_reportes'),
    path('reportes/generar/inventario/', views.generar_reporte_estante, name='reporte_estante_pdf'),
    path('ubicaciones/gestion/', views.gestion_ubicaciones, name='gestion_ubicaciones'),
    path('libro/<uuid:libro_id>/ejemplares/', views.lista_ejemplares, name='lista_ejemplares'),
    path('libro/eliminar/<uuid:pk>/', views.eliminar_libro, name='eliminar_libro'),
    path('ejemplar/eliminar/<uuid:ejemplar_id>/', views.eliminar_ejemplar, name='eliminar_ejemplar'),
    path('ejemplar/<uuid:ejemplar_id>/editar/', views.editar_ejemplar, name='editar_ejemplar'),
    
]