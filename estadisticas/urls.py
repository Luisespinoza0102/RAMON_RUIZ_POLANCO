from django.urls import path
from . import views

urlpatterns = [
    path('panel/estadisticas/circulante/', views.reporte_mensual_circulante, name='reporte_circulante'),
]