# ================================================================
# =                                                              =
# =           APIS PARA MÉTRICAS DEL DASHBOARD                  =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas API que proveen datos en tiempo real
# para las métricas principales del dashboard.

from django.http import JsonResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, date, timedelta, timezone as dt_timezone
from decimal import Decimal
from ventas.models.ventas import Ventas, DetalleVenta
from ventas.models.productos import Productos
from ventas.models.alertas import Alertas
import logging

logger = logging.getLogger('ventas')


def ventas_del_dia_api(request):
    """
    API que retorna las ventas del día actual.
    
    Returns:
        JSON con:
        - total_ventas: Monto total vendido hoy
        - num_transacciones: Número de ventas realizadas
    """
    try:
        # Obtener fecha de hoy en la zona horaria local (America/Santiago)
        ahora = timezone.now()
        ahora_local = timezone.localtime(ahora)  # Convertir a hora local
        hoy_local = ahora_local.date()  # Obtener solo la fecha local
        
        logger.info(f'Fecha/hora actual del sistema (UTC): {ahora}')
        logger.info(f'Fecha/hora local (America/Santiago): {ahora_local}')
        logger.info(f'Fecha local calculada: {hoy_local}')
        
        # Las ventas están guardadas en UTC
        # Necesitamos convertir el día local completo a UTC
        # Inicio del día local (00:00:00 en hora local)
        inicio_dia_local = datetime.combine(hoy_local, datetime.min.time())
        # Fin del día local (23:59:59.999999 en hora local)
        fin_dia_local = datetime.combine(hoy_local, datetime.max.time()) + timedelta(microseconds=999999)
        
        # Convertir a zona horaria aware usando la zona horaria configurada
        inicio_dia_aware = timezone.make_aware(inicio_dia_local)
        fin_dia_aware = timezone.make_aware(fin_dia_local)
        
        # Convertir a UTC para comparar con las fechas guardadas en la BD
        inicio_dia_utc = inicio_dia_aware.astimezone(dt_timezone.utc)
        fin_dia_utc = fin_dia_aware.astimezone(dt_timezone.utc)
        
        logger.info(f'Buscando ventas del día local {hoy_local}')
        logger.info(f'Rango local: desde {inicio_dia_aware} hasta {fin_dia_aware}')
        logger.info(f'Rango UTC: desde {inicio_dia_utc} hasta {fin_dia_utc}')
        
        # Obtener todas las ventas de hoy usando rango de fechas en UTC
        ventas_hoy = Ventas.objects.filter(
            fecha__gte=inicio_dia_utc,
            fecha__lte=fin_dia_utc
        )
        
        # Calcular el total vendido
        total_ventas = ventas_hoy.aggregate(
            total=Sum('total_con_iva')
        )['total'] or Decimal('0.00')
        
        # Contar número de transacciones
        num_transacciones = ventas_hoy.count()
        
        logger.info(f'Ventas del día encontradas: {num_transacciones} transacciones, total: ${total_ventas}')
        
        return JsonResponse({
            'total_ventas': float(total_ventas),
            'num_transacciones': num_transacciones
        })
    except Exception as e:
        logger.error(f'Error en ventas_del_dia_api: {str(e)}', exc_info=True)
        return JsonResponse({
            'total_ventas': 0,
            'num_transacciones': 0,
            'error': str(e)
        }, status=500)


def stock_bajo_api(request):
    """
    API que retorna productos con stock bajo.
    
    Un producto tiene stock bajo cuando:
    - cantidad <= stock_minimo (si stock_minimo está definido)
    - cantidad <= 5 (si stock_minimo no está definido)
    
    Returns:
        JSON con:
        - num_productos: Número de productos con stock bajo
        - productos: Lista de productos con stock bajo
    """
    try:
        # Obtener productos activos (no eliminados, no en merma, no inactivos)
        productos = Productos.objects.filter(
            eliminado__isnull=True,
            estado_merma='activo'  # Solo productos activos (excluye inactivos y en_merma)
        )
        
        logger.info(f'Productos activos encontrados: {productos.count()}')
        
        # Filtrar productos con stock bajo
        productos_stock_bajo = []
        for producto in productos:
            stock_minimo = producto.stock_minimo if producto.stock_minimo is not None else 5
            cantidad_actual = producto.cantidad or 0
            
            if cantidad_actual <= stock_minimo:
                productos_stock_bajo.append({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'cantidad': cantidad_actual,
                    'stock_minimo': stock_minimo
                })
        
        logger.info(f'Productos con stock bajo: {len(productos_stock_bajo)}')
        
        return JsonResponse({
            'num_productos': len(productos_stock_bajo),
            'productos': productos_stock_bajo
        })
    except Exception as e:
        logger.error(f'Error en stock_bajo_api: {str(e)}', exc_info=True)
        return JsonResponse({
            'num_productos': 0,
            'productos': [],
            'error': str(e)
        }, status=500)


def alertas_pendientes_api(request):
    """
    API que retorna el número de alertas activas.
    
    Returns:
        JSON con:
        - num_alertas: Número total de alertas activas
        - por_tipo: Desglose por tipo (roja, amarilla, verde)
    """
    # Contar alertas activas (solo de productos activos, no en merma, no inactivos)
    alertas_activas = Alertas.objects.filter(
        estado='activa',
        productos__estado_merma='activo'  # Solo productos activos (excluye inactivos y en_merma)
    )
    
    # Contar por tipo
    alertas_rojas = alertas_activas.filter(tipo_alerta='roja').count()
    alertas_amarillas = alertas_activas.filter(tipo_alerta='amarilla').count()
    alertas_verdes = alertas_activas.filter(tipo_alerta='verde').count()
    
    total_alertas = alertas_activas.count()
    
    return JsonResponse({
        'num_alertas': total_alertas,
        'por_tipo': {
            'roja': alertas_rojas,
            'amarilla': alertas_amarillas,
            'verde': alertas_verdes
        }
    })


def top_producto_api(request):
    """
    API que retorna el producto más vendido del día.
    
    Returns:
        JSON con:
        - nombre: Nombre del producto más vendido
        - unidades: Cantidad de unidades vendidas
        - total_vendido: Monto total generado por ese producto
    """
    try:
        # Obtener fecha de hoy en la zona horaria local (America/Santiago)
        ahora = timezone.now()
        ahora_local = timezone.localtime(ahora)  # Convertir a hora local
        hoy_local = ahora_local.date()  # Obtener solo la fecha local
        
        logger.info(f'Fecha/hora actual del sistema (UTC): {ahora}')
        logger.info(f'Fecha/hora local (America/Santiago): {ahora_local}')
        logger.info(f'Fecha local calculada: {hoy_local}')
        
        # Las ventas están guardadas en UTC
        # Necesitamos convertir el día local completo a UTC
        # Inicio del día local (00:00:00 en hora local)
        inicio_dia_local = datetime.combine(hoy_local, datetime.min.time())
        # Fin del día local (23:59:59.999999 en hora local)
        fin_dia_local = datetime.combine(hoy_local, datetime.max.time()) + timedelta(microseconds=999999)
        
        # Convertir a zona horaria aware usando la zona horaria configurada
        inicio_dia_aware = timezone.make_aware(inicio_dia_local)
        fin_dia_aware = timezone.make_aware(fin_dia_local)
        
        # Convertir a UTC para comparar con las fechas guardadas en la BD
        inicio_dia_utc = inicio_dia_aware.astimezone(dt_timezone.utc)
        fin_dia_utc = fin_dia_aware.astimezone(dt_timezone.utc)
        
        logger.info(f'Buscando top producto del día local {hoy_local}')
        logger.info(f'Rango local: desde {inicio_dia_aware} hasta {fin_dia_aware}')
        logger.info(f'Rango UTC: desde {inicio_dia_utc} hasta {fin_dia_utc}')
        
        # Obtener detalles de ventas de hoy y agrupar por producto
        detalles_hoy = DetalleVenta.objects.filter(
            ventas__fecha__gte=inicio_dia_utc,
            ventas__fecha__lte=fin_dia_utc
        )
        
        logger.info(f'Detalles de venta encontrados hoy: {detalles_hoy.count()}')
        
        if detalles_hoy.exists():
            top_producto = detalles_hoy.values(
                'productos__nombre'
            ).annotate(
                total_unidades=Sum('cantidad'),
                total_vendido=Sum(F('cantidad') * F('precio_unitario'))
            ).order_by('-total_unidades').first()
            
            if top_producto:
                logger.info(f'Top producto del día: {top_producto["productos__nombre"]} - {top_producto["total_unidades"]} unidades')
                return JsonResponse({
                    'nombre': top_producto['productos__nombre'],
                    'unidades': top_producto['total_unidades'],
                    'total_vendido': float(top_producto['total_vendido'] or 0)
                })
        
        # Si no hay ventas hoy
        logger.info('No hay ventas hoy para calcular top producto')
        return JsonResponse({
            'nombre': 'Sin ventas',
            'unidades': 0,
            'total_vendido': 0
        })
    except Exception as e:
        logger.error(f'Error en top_producto_api: {str(e)}', exc_info=True)
        return JsonResponse({
            'nombre': 'Error',
            'unidades': 0,
            'total_vendido': 0,
            'error': str(e)
        }, status=500)


def ventas_del_dia_lista_api(request):
    """
    API que retorna la lista detallada de ventas del día actual.
    
    Returns:
        JSON con:
        - ventas: Lista de ventas con detalles (folio, fecha, total, cliente, etc.)
    """
    try:
        # Obtener fecha de hoy en la zona horaria local
        ahora = timezone.now()
        ahora_local = timezone.localtime(ahora)
        hoy_local = ahora_local.date()
        
        # Calcular rango del día en UTC
        inicio_dia_local = datetime.combine(hoy_local, datetime.min.time())
        fin_dia_local = datetime.combine(hoy_local, datetime.max.time()) + timedelta(microseconds=999999)
        
        inicio_dia_aware = timezone.make_aware(inicio_dia_local)
        fin_dia_aware = timezone.make_aware(fin_dia_local)
        
        inicio_dia_utc = inicio_dia_aware.astimezone(dt_timezone.utc)
        fin_dia_utc = fin_dia_aware.astimezone(dt_timezone.utc)
        
        # Obtener todas las ventas de hoy
        ventas_hoy = Ventas.objects.filter(
            fecha__gte=inicio_dia_utc,
            fecha__lte=fin_dia_utc
        ).select_related('clientes').order_by('-fecha')
        
        # Formatear ventas para el JSON
        ventas_lista = []
        for venta in ventas_hoy:
            fecha_local = timezone.localtime(venta.fecha)
            ventas_lista.append({
                'id': venta.id,
                'folio': venta.folio or f'BOL-{venta.id}',
                'fecha': fecha_local.strftime('%d/%m/%Y'),
                'hora': fecha_local.strftime('%H:%M:%S'),
                'total': float(venta.total_con_iva),
                'cliente': venta.clientes.nombre if venta.clientes else 'Cliente Genérico',
                'canal': venta.canal_venta,
                'num_productos': venta.detalles.count()
            })
        
        return JsonResponse({
            'ventas': ventas_lista,
            'total_ventas': len(ventas_lista)
        })
    except Exception as e:
        logger.error(f'Error en ventas_del_dia_lista_api: {str(e)}', exc_info=True)
        return JsonResponse({
            'ventas': [],
            'total_ventas': 0,
            'error': str(e)
        }, status=500)


def merma_lista_api(request):
    """
    API que retorna la lista detallada de productos en merma.
    
    Returns:
        JSON con:
        - productos: Lista de productos en merma con detalles
    """
    try:
        from ventas.models import HistorialMerma
        from django.db.models import Q
        
        # Obtener IDs de productos con registros activos en HistorialMerma
        productos_con_historial_activo = HistorialMerma.objects.filter(
            activo=True
        ).values_list('producto_id', flat=True).distinct()
        
        # Obtener productos en merma
        productos_merma = Productos.objects.filter(
            eliminado__isnull=True
        ).filter(
            Q(id__in=productos_con_historial_activo) | Q(estado_merma='en_merma')
        ).distinct()
        
        # Formatear productos para el JSON
        productos_lista = []
        for producto in productos_merma:
            cantidad_merma = producto.cantidad_merma if (producto.cantidad_merma and producto.cantidad_merma > 0) else producto.cantidad
            perdida_producto = float(cantidad_merma * producto.precio) if cantidad_merma > 0 else 0.0
            
            productos_lista.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'cantidad_merma': float(cantidad_merma),
                'precio': float(producto.precio),
                'perdida': perdida_producto,
                'motivo': producto.motivo_merma or 'No especificado',
                'fecha_merma': producto.fecha_merma.strftime('%d/%m/%Y %H:%M') if producto.fecha_merma else 'N/A',
                'unidad': producto.get_unidad_stock_display()
            })
        
        return JsonResponse({
            'productos': productos_lista,
            'total_productos': len(productos_lista)
        })
    except Exception as e:
        logger.error(f'Error en merma_lista_api: {str(e)}', exc_info=True)
        return JsonResponse({
            'productos': [],
            'total_productos': 0,
            'error': str(e)
        }, status=500)
