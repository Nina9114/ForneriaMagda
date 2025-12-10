# ================================================================
# =                                                              =
# =        VISTA: REPORTE DE VENTAS CON FILTROS AVANZADOS       =
# =                                                              =
# ================================================================
#
# Este archivo implementa el reporte de ventas según RF-V4 del Jira:
# "Consultar ventas por rango/cliente/canal con totales"
#
# REQUISITOS JIRA:
# - RF-V4: Consultar ventas por rango/cliente/canal con totales
#
# FUNCIONALIDADES:
# - Filtro por rango de fechas
# - Filtro por cliente
# - Filtro por canal de venta (presencial/delivery)
# - Cálculo de totales agregados (neto, IVA, total)
# - Visualización clara de resultados
# - Exportación a CSV (opcional)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from datetime import datetime, time as dt_time
from decimal import Decimal
import csv

from ventas.models import Ventas, DetalleVenta, Clientes
from ventas.utils.exportadores import exportar_a_excel, exportar_a_pdf


# ================================================================
# =              VISTA: REPORTE DE VENTAS                        =
# ================================================================

@login_required
def reporte_ventas_view(request):
    """
    Vista para generar reporte de ventas con filtros avanzados.
    
    Cumple con RF-V4 del Jira:
    - Consultar ventas por rango de fechas
    - Filtrar por cliente
    - Filtrar por canal (presencial/delivery)
    - Mostrar totales agregados
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Página HTML con el reporte
    """
    
    # ============================================================
    # PASO 1: Inicializar variables
    # ============================================================
    reporte_generado = False
    ventas = Ventas.objects.none()  # QuerySet vacío inicial
    totales = {
        'total_neto': Decimal('0.00'),
        'total_iva': Decimal('0.00'),
        'total_con_iva': Decimal('0.00'),
        'cantidad_ventas': 0,
        'promedio_venta': Decimal('0.00'),
    }
    
    # Valores por defecto para filtros
    fecha_desde = None
    fecha_hasta = None
    cliente_id = None
    canal_venta = None
    
    # ============================================================
    # PASO 2: Procesar filtros del formulario
    # ============================================================
    if request.method == 'GET' and 'generar' in request.GET:
        reporte_generado = True
        
        # Obtener fechas
        fecha_desde_str = request.GET.get('fecha_desde')
        fecha_hasta_str = request.GET.get('fecha_hasta')
        
        try:
            if fecha_desde_str:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            if fecha_hasta_str:
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Si hay error, usar mes actual
            hoy = timezone.now().date()
            fecha_desde = hoy.replace(day=1)
            fecha_hasta = hoy
        
        # Obtener filtros adicionales
        cliente_id = request.GET.get('cliente_id')
        canal_venta = request.GET.get('canal_venta')
        
        # ============================================================
        # PASO 3: Construir query con filtros
        # ============================================================
        ventas = Ventas.objects.select_related('clientes').all()
        
        # Filtro por fecha
        if fecha_desde:
            # Incluir desde el inicio del día (00:00:00)
            fecha_desde_datetime = timezone.make_aware(
                datetime.combine(fecha_desde, dt_time.min)
            )
            ventas = ventas.filter(fecha__gte=fecha_desde_datetime)
        if fecha_hasta:
            # Incluir hasta el final del día (23:59:59.999999)
            fecha_hasta_datetime = timezone.make_aware(
                datetime.combine(fecha_hasta, dt_time.max)
            )
            ventas = ventas.filter(fecha__lte=fecha_hasta_datetime)
        
        # Filtro por cliente
        if cliente_id and cliente_id != '':
            ventas = ventas.filter(clientes_id=cliente_id)
        
        # Filtro por canal
        if canal_venta and canal_venta != '':
            ventas = ventas.filter(canal_venta=canal_venta)
        
        # Ordenar por fecha descendente
        ventas = ventas.order_by('-fecha')
        
        # ============================================================
        # PASO 4: Calcular totales agregados
        # ============================================================
        cantidad_ventas = ventas.count()
        
        if cantidad_ventas > 0:
            # Calcular totales usando agregación
            totales_calculados = ventas.aggregate(
                total_neto=Sum('total_sin_iva'),
                total_iva=Sum('total_iva'),
                total_con_iva=Sum('total_con_iva'),
            )
            
            totales['total_neto'] = totales_calculados['total_neto'] or Decimal('0.00')
            totales['total_iva'] = totales_calculados['total_iva'] or Decimal('0.00')
            totales['total_con_iva'] = totales_calculados['total_con_iva'] or Decimal('0.00')
            totales['cantidad_ventas'] = cantidad_ventas
            totales['promedio_venta'] = totales['total_con_iva'] / cantidad_ventas if cantidad_ventas > 0 else Decimal('0.00')
        
        # Limitar resultados para visualización (paginación opcional)
        ventas = ventas[:100]
    
    # ============================================================
    # PASO 5: Obtener lista de clientes para el filtro
    # ============================================================
    clientes = Clientes.objects.all().order_by('nombre')
    
    # ============================================================
    # PASO 6: Preparar contexto
    # ============================================================
    context = {
        'reporte_generado': reporte_generado,
        'ventas': ventas,
        'totales': totales,
        'clientes': clientes,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cliente_seleccionado': cliente_id,
        'canal_seleccionado': canal_venta,
        'canales': [
            ('presencial', 'Presencial'),
            ('delivery', 'Delivery'),
        ],
    }
    
    # ============================================================
    # PASO 7: Renderizar template
    # ============================================================
    return render(request, 'reporte_ventas.html', context)


# ================================================================
# =        VISTA: EXPORTAR REPORTE DE VENTAS A CSV              =
# ================================================================

def _obtener_ventas_filtradas(request):
    """
    Función auxiliar para obtener ventas con filtros aplicados.
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        QuerySet: Ventas filtradas
    """
    ventas = Ventas.objects.select_related('clientes').all()
    
    # Filtros desde GET
    fecha_desde_str = request.GET.get('fecha_desde')
    fecha_hasta_str = request.GET.get('fecha_hasta')
    cliente_id = request.GET.get('cliente_id')
    canal_venta = request.GET.get('canal_venta')
    
    # Aplicar filtros de fecha
    if fecha_desde_str:
        try:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            # Incluir desde el inicio del día (00:00:00)
            fecha_desde_datetime = timezone.make_aware(
                datetime.combine(fecha_desde, dt_time.min)
            )
            ventas = ventas.filter(fecha__gte=fecha_desde_datetime)
        except ValueError:
            pass
    
    if fecha_hasta_str:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
            # Incluir hasta el final del día (23:59:59.999999)
            fecha_hasta_datetime = timezone.make_aware(
                datetime.combine(fecha_hasta, dt_time.max)
            )
            ventas = ventas.filter(fecha__lte=fecha_hasta_datetime)
        except ValueError:
            pass
    
    if cliente_id and cliente_id != '':
        ventas = ventas.filter(clientes_id=cliente_id)
    
    if canal_venta and canal_venta != '':
        ventas = ventas.filter(canal_venta=canal_venta)
    
    return ventas.order_by('-fecha')


@login_required
def exportar_ventas_csv(request):
    """
    Exporta el reporte de ventas a formato CSV.
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Archivo CSV descargable
    """
    ventas = _obtener_ventas_filtradas(request)
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    # Escribir CSV
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow([
        'Folio', 'Fecha', 'Cliente', 'Canal', 
        'Total Neto', 'IVA', 'Total con IVA', 'Descuento'
    ])
    
    # Datos
    for venta in ventas:
        writer.writerow([
            venta.folio or f'VENTA-{venta.id}',
            venta.fecha.strftime('%d/%m/%Y %H:%M'),
            venta.clientes.nombre if venta.clientes else 'Cliente Genérico',
            venta.canal_venta,
            float(venta.total_sin_iva),
            float(venta.total_iva),
            float(venta.total_con_iva),
            float(venta.descuento),
        ])
    
    return response


@login_required
def exportar_ventas_excel(request):
    """
    Exporta el reporte de ventas a formato Excel (XLSX).
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Archivo Excel descargable
    """
    ventas = _obtener_ventas_filtradas(request)
    
    # Preparar datos
    datos = []
    for venta in ventas:
        datos.append({
            'Folio': venta.folio or f'VENTA-{venta.id}',
            'Fecha': venta.fecha.strftime('%d/%m/%Y %H:%M'),
            'Cliente': venta.clientes.nombre if venta.clientes else 'Cliente Genérico',
            'Canal': venta.canal_venta,
            'Total Neto': venta.total_sin_iva,
            'IVA': venta.total_iva,
            'Total con IVA': venta.total_con_iva,
            'Descuento': venta.descuento,
        })
    
    # Generar título con filtros
    titulo = "Reporte de Ventas"
    fecha_desde_str = request.GET.get('fecha_desde')
    fecha_hasta_str = request.GET.get('fecha_hasta')
    if fecha_desde_str and fecha_hasta_str:
        titulo += f" ({fecha_desde_str} a {fecha_hasta_str})"
    
    return exportar_a_excel(datos, 'reporte_ventas', titulo)


@login_required
def exportar_ventas_pdf(request):
    """
    Exporta el reporte de ventas a formato PDF.
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Archivo PDF descargable
    """
    ventas = _obtener_ventas_filtradas(request)
    
    # Preparar datos
    datos = []
    for venta in ventas:
        datos.append({
            'Folio': venta.folio or f'VENTA-{venta.id}',
            'Fecha': venta.fecha.strftime('%d/%m/%Y %H:%M'),
            'Cliente': venta.clientes.nombre if venta.clientes else 'Cliente Genérico',
            'Canal': venta.canal_venta,
            'Total Neto': venta.total_sin_iva,
            'IVA': venta.total_iva,
            'Total con IVA': venta.total_con_iva,
        })
    
    # Generar título con filtros
    titulo = "Reporte de Ventas"
    fecha_desde_str = request.GET.get('fecha_desde')
    fecha_hasta_str = request.GET.get('fecha_hasta')
    if fecha_desde_str and fecha_hasta_str:
        titulo += f" ({fecha_desde_str} a {fecha_hasta_str})"
    
    encabezados = ['Folio', 'Fecha', 'Cliente', 'Canal', 'Total Neto', 'IVA', 'Total con IVA']
    
    return exportar_a_pdf(datos, 'reporte_ventas', titulo, encabezados)

