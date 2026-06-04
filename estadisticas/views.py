from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
from prestamos.models import Prestamo

# VISTAS DE ESTADÍSTICAS
@login_required
def reporte_mensual_circulante(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
    
    hoy = timezone.now()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))

    prestamos_mes = Prestamo.objects.filter(
        fecha_solicitud__year=anio,
        fecha_solicitud__month=mes,
        estado__in=['APROBADO', 'DEVUELTO']
    )

    estadisticas = prestamos_mes.aggregate(
        # Clases Dewey principales
        dewey_000=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='0')),
        dewey_100=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='1')),
        dewey_200=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='2')),
        dewey_300=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='3')),
        dewey_400=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='4')),
        dewey_500=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='5')),
        dewey_600=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='6')),
        dewey_700=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='7')),
        dewey_800=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='8')),
        dewey_900=Count('id', filter=Q(ejemplar__libro__generos__codigo_dewey__startswith='9')),
        
        # Cuentos Infantiles (X)
        cuentos_x=Count('id', filter=Q(ejemplar__libro__es_infantil=True)),
        
        # Literatura (Filtramos por nombre de género e identificador de origen)
        lit_universal=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Literatura') & Q(ejemplar__libro__origen='UNI')),
        lit_venezolana=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Literatura') & Q(ejemplar__libro__origen='VNZ')),
        
        # Novelas
        nov_internacional=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Novela') & Q(ejemplar__libro__origen='INT')),
        nov_venezolana=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Novela') & Q(ejemplar__libro__origen='VNZ')),
        
        # Poesía
        poe_internacional=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Poesía') & Q(ejemplar__libro__origen='INT')),
        poe_venezolana=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Poesía') & Q(ejemplar__libro__origen='VNZ')),
        
        # Biografías
        bio_internacional=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Biografía') & Q(ejemplar__libro__origen='INT')),
        bio_venezolana=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Biografía') & Q(ejemplar__libro__origen='VNZ')),
        
        # Teatro
        tea_internacional=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Teatro') & Q(ejemplar__libro__origen='INT')),
        tea_venezolana=Count('id', filter=Q(ejemplar__libro__generos__nombre__icontains='Teatro') & Q(ejemplar__libro__origen='VNZ')),
        
        # Colección Bolivariana 
        bolivariana=Count('id', filter=Q(ejemplar__libro__es_bolivariano=True)),
    )

    total_circulante = prestamos_mes.count()
    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]

    anios_rango = range(hoy.year - 3, hoy.year + 1 )

    context = {
        'estadisticas': estadisticas,
        'total_circulante': total_circulante,
        'mes_sel': mes,
        'anio_sel': anio,
        'meses': meses,
        'anios_rango': anios_rango,
    }
    return render(request, 'estadisticas/reporte_mensual.html', context)
