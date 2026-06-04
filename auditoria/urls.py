from django.urls import path
from . import views

urlpatterns = [
    path('actividad/', views.seguimiento_actividad, name='seguimiento_actividad'),
    path('reportes/', views.historial_reportes, name='historial_reportes'),
]
