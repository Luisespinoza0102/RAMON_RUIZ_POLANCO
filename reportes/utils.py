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
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        pdf_content = result.getvalue()
        
        # Crear nombre del archivo de respaldo
        fecha_str = timezone.now().strftime('%Y%m%d_%H&M%S')
        nombre_fichero = f"Respaldo_{tipo_reporte}_{fecha_str}.pdf"

        # Crear registro en la tabla Reistro Reporte
        registro = RegistroReporte(
            admin=usuario,
            tipo=tipo_reporte
        )

        # Guardar el archivo fisico
        registro.archivo_respaldo.save(nombre_fichero, ContentFile(pdf_content))
        registro.save()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nombre_fichero}"'
        return response
    return None