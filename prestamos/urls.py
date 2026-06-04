from django.urls import path
from . import views

urlpatterns = [
    path('solicitar/<uuid:libro_id>/', views.solicitar_prestamo, name='solicitar_prestamo'),
    path('mis-pedidos/', views.mis_prestamos, name='mis_prestamos'),
    
    # Gestión Admin
    path('control-solicitudes/', views.admin_prestamos, name='admin_prestamos'),
    path('rechazar/<uuid:prestamo_id>/', views.rechazar_prestamo, name='rechazar_prestamo'),
    path('devolver/<uuid:prestamo_id>/', views.devolver_libro, name='devolver_libro'),
    path('comprobante/<uuid:prestamo_id>/descargar', views.descargar_pdf_usuario, name='descargar_pdf_usuario'),
    path('solicitud/<uuid:prestamo_id>/revisar/', views.revisar_solicitud_admin, name='revisar_solicitud'),
    path('solicitud/<uuid:prestamo_id>/confirmar/', views.confirmar_aprobacion, name='confirmar_aprobacion'),
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    path('notificaciones/borrar/<int:notificacion_id>/', views.borrar_notificacion, name='borrar_notificacion'),
    path('notificaciones/leer/<int:notificacion_id>/', views.marcar_leida, name='marcar_leida'),
    path('renovar/solicitar/<uuid:prestamo_id>/', views.solicitar_renovacion, name='solicitar_renovacion'),
    path('renovar/procesar/<uuid:prestamo_id>/', views.procesar_renovacion_admin, name='procesar_renovacion_admin'),
]