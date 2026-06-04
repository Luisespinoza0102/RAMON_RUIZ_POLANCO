import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core.views import dispatch_dashboard, vista_error_fake

urlpatterns = [
    # Administración de Django
    path('ramon_ruiz_2026/', admin.site.urls),
    path('admin_django/', vista_error_fake),

    # Módulos de la App
    path('', include('core.urls')),
    path('catalogo/', include('catalogo.urls')),
    path('prestamos/', include('prestamos.urls')),
    path('reportes/', include('reportes.urls')),
    path('auditoria/', include('auditoria.urls')),
    path('repositorio/', include('repositorio.urls')),
    path('estadisticas/', include('estadisticas.urls')),
    path("__reload__/", include("django_browser_reload.urls")),

    # Dashboard
    path('dashboard/', dispatch_dashboard, name='dispatch_dashboard'),
]

if settings.DEBUG:
    # 1. Servir archivos estáticos (CSS, JS, Imágenes de diseño)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
    # 2. Servir archivos multimedia (Fotos de libros)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += staticfiles_urlpatterns()