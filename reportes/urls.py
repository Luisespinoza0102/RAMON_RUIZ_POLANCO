from django.urls import path
from . import views

urlpatterns = [
    # Portal Principal
    path('', views.portal_reportes, name='portal_reportes'),

    # 1. Inventario por Estante
    path('inventario/estante/', views.inventario_estante, name='rep_inventario_estante'),
    path('inventario/estante/pdf/', views.pdf_inventario_estante, name='pdf_inventario_estante'),

    # 2. Préstamos Mensuales
    path('prestamos/mensual/', views.prestamos_mensual, name='rep_prestamos_mensual'),
    path('prestamos/mensual/pdf/', views.pdf_prestamos_mensual, name='pdf_prestamos_mensual'),

    # 3. Préstamos Retrasados
    path('prestamos/retrasados/', views.prestamos_retrasados, name='rep_prestamos_retrasados'),
    path('prestamos/retrasados/pdf/', views.pdf_prestamos_retrasados, name='pdf_prestamos_retrasados'),
]