from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.files.base import ContentFile
from django.utils import timezone
from auditoria.models import RegistroReporte

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def generar_y_registrar_reporte(template_src, context_dict, tipo_reporte, usuario):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # 🌟 Usamos el link_callback por si las plantillas de reporte llaman imágenes de portadas o firmas
    from prestamos.views import link_callback
    
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        link_callback=link_callback
    )

    if not pdf.err:
        pdf_content = result.getvalue()
        
        fecha_str = timezone.now().strftime('%Y%m%d_%H%M%S')
        nombre_fichero = f"Respaldo_{tipo_reporte}_{fecha_str}.pdf"

        # Crear registro en la tabla RegistroReporte
        registro = RegistroReporte(
            admin=usuario,
            tipo=tipo_reporte
        )

        registro.archivo_respaldo.save(nombre_fichero, ContentFile(pdf_content))
        registro.save()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nombre_fichero}"'
        return response
        
    return HttpResponse('Error generando los flujos internos del PDF', status=500)