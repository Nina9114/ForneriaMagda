# ================================================================
# =                                                              =
# =              VISTA PARA SISTEMA DE REPORTES                 =
# =                                                              =
# ================================================================
#
# Este archivo contiene la vista principal del sistema de reportes.
#
# PROPÓSITO:
# - Generar reportes personalizados por rango de fechas
# - Mostrar datos de múltiples tablas (Ventas, Productos, Merma, etc.)
# - Presentar información de forma clara y organizada
#
# FUNCIONALIDADES:
# - Filtro por rango de fechas (desde - hasta)
# - Selección de tablas a incluir en el reporte
# - Cálculos automáticos (totales, promedios, pérdidas)
# - Visualización en pantalla (no genera archivos)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from ventas.models import (
    Productos, Ventas, DetalleVenta, Clientes,
    MovimientosInventario, Alertas
)
from django.db.models import Sum, Count, Q


# ================================================================
# =                    VISTA: REPORTES                           =
# ================================================================

@login_required
def reportes_view(request):
    """
    Vista principal del sistema de reportes.
    
    Permite al usuario:
    1. Seleccionar un rango de fechas
    2. Elegir qué tablas incluir en el reporte
    3. Ver el reporte generado en pantalla
    
    Args:
        request: Objeto HttpRequest con los parámetros del formulario
        
    Returns:
        HttpResponse: Página HTML con el reporte generado
    """
    
    # ============================================================
    # PASO 1: Inicializar variables
    # ============================================================
    reporte_generado = False  # Indica si se generó un reporte
    datos_reporte = {}        # Diccionario con los datos del reporte
    
    # ============================================================
    # PASO 2: Verificar si se envió el formulario
    # ============================================================
    if request.method == 'GET' and 'generar' in request.GET:
        # El usuario hizo clic en "Generar Reporte"
        
        # ------------------------------------------------------------
        # Obtener fechas del formulario
        # ------------------------------------------------------------
        fecha_desde_str = request.GET.get('fecha_desde')
        fecha_hasta_str = request.GET.get('fecha_hasta')
        
        # Convertir strings a objetos date
        try:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Si hay error en las fechas, usar el mes actual
            hoy = timezone.now().date()
            fecha_desde = hoy.replace(day=1)  # Primer día del mes
            fecha_hasta = hoy
        
        # ------------------------------------------------------------
        # Obtener tablas seleccionadas
        # ------------------------------------------------------------
        incluir_ventas = 'incluir_ventas' in request.GET
        incluir_productos = 'incluir_productos' in request.GET
        incluir_merma = 'incluir_merma' in request.GET
        incluir_movimientos = 'incluir_movimientos' in request.GET
        incluir_alertas = 'incluir_alertas' in request.GET
        
        # ============================================================
        # PASO 3: Generar datos del reporte
        # ============================================================
        
        # ------------------------------------------------------------
        # REPORTE DE VENTAS
        # ------------------------------------------------------------
        if incluir_ventas:
            # Filtrar ventas por rango de fechas
            ventas = Ventas.objects.filter(
                fecha__date__gte=fecha_desde,
                fecha__date__lte=fecha_hasta
            ).select_related('clientes')
            
            # Calcular totales
            total_ventas = ventas.aggregate(
                total=Sum('total_con_iva')
            )['total'] or 0
            
            cantidad_ventas = ventas.count()
            
            # Calcular promedio
            promedio_venta = total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0
            
            # Guardar datos
            datos_reporte['ventas'] = {
                'lista': ventas[:50],  # Limitar a 50 registros
                'total': total_ventas,
                'cantidad': cantidad_ventas,
                'promedio': promedio_venta,
            }
        
        # ------------------------------------------------------------
        # REPORTE DE PRODUCTOS
        # ------------------------------------------------------------
        if incluir_productos:
            # Obtener productos activos (no en merma, no inactivos, no eliminados)
            productos = Productos.objects.filter(
                eliminado__isnull=True,
                estado_merma='activo'  # Solo productos activos (excluye inactivos y en_merma)
            ).select_related('categorias')
            
            # Calcular totales
            total_productos = productos.count()
            total_stock = productos.aggregate(
                total=Sum('cantidad')
            )['total'] or 0
            
            # Calcular valor total del inventario
            valor_inventario = sum(
                p.precio * p.cantidad for p in productos
            )
            
            # Productos con stock bajo (menos de 10 unidades)
            productos_bajo_stock = productos.filter(cantidad__lt=10).count()
            
            # Guardar datos
            datos_reporte['productos'] = {
                'lista': productos[:50],  # Limitar a 50 registros
                'total': total_productos,
                'total_stock': total_stock,
                'valor_inventario': valor_inventario,
                'bajo_stock': productos_bajo_stock,
            }
        
        # ------------------------------------------------------------
        # REPORTE DE MERMA
        # ------------------------------------------------------------
        if incluir_merma:
            # Obtener productos en merma
            productos_merma = Productos.objects.filter(
                eliminado__isnull=True
            ).exclude(estado_merma='activo')
            
            # Calcular totales por tipo de merma
            merma_vencido = productos_merma.filter(estado_merma='vencido').count()
            merma_deteriorado = productos_merma.filter(estado_merma='deteriorado').count()
            merma_danado = productos_merma.filter(estado_merma='dañado').count()
            
            # Calcular pérdida económica total
            perdida_total = sum(
                p.precio * p.cantidad for p in productos_merma
            )
            
            # Guardar datos
            datos_reporte['merma'] = {
                'lista': productos_merma[:50],  # Limitar a 50 registros
                'total': productos_merma.count(),
                'vencido': merma_vencido,
                'deteriorado': merma_deteriorado,
                'danado': merma_danado,
                'perdida_total': perdida_total,
            }
        
        # ------------------------------------------------------------
        # REPORTE DE MOVIMIENTOS
        # ------------------------------------------------------------
        if incluir_movimientos:
            # Filtrar movimientos por rango de fechas
            movimientos = MovimientosInventario.objects.filter(
                fecha__date__gte=fecha_desde,
                fecha__date__lte=fecha_hasta
            ).select_related('productos')
            
            # Calcular totales por tipo
            total_entradas = movimientos.filter(
                tipo_movimiento='entrada'
            ).aggregate(total=Sum('cantidad'))['total'] or 0
            
            total_salidas = movimientos.filter(
                tipo_movimiento='salida'
            ).aggregate(total=Sum('cantidad'))['total'] or 0
            
            # Guardar datos
            datos_reporte['movimientos'] = {
                'lista': movimientos[:50],  # Limitar a 50 registros
                'total': movimientos.count(),
                'entradas': total_entradas,
                'salidas': total_salidas,
                'diferencia': total_entradas - total_salidas,
            }
        
        # ------------------------------------------------------------
        # REPORTE DE ALERTAS
        # ------------------------------------------------------------
        if incluir_alertas:
            # Filtrar alertas por rango de fechas
            alertas = Alertas.objects.filter(
                fecha_generada__date__gte=fecha_desde,
                fecha_generada__date__lte=fecha_hasta
            ).select_related('productos')
            
            # Calcular totales por tipo
            alertas_rojas = alertas.filter(tipo_alerta='roja').count()
            alertas_amarillas = alertas.filter(tipo_alerta='amarilla').count()
            alertas_verdes = alertas.filter(tipo_alerta='verde').count()
            
            # Guardar datos
            datos_reporte['alertas'] = {
                'lista': alertas[:50],  # Limitar a 50 registros
                'total': alertas.count(),
                'rojas': alertas_rojas,
                'amarillas': alertas_amarillas,
                'verdes': alertas_verdes,
            }
        
        # ============================================================
        # PASO 4: Marcar que el reporte fue generado
        # ============================================================
        reporte_generado = True
        
        # Guardar fechas en el contexto
        datos_reporte['fecha_desde'] = fecha_desde
        datos_reporte['fecha_hasta'] = fecha_hasta
        datos_reporte['fecha_generacion'] = timezone.now()
    
    # ============================================================
    # PASO 5: Preparar contexto para el template
    # ============================================================
    context = {
        'reporte_generado': reporte_generado,
        'datos_reporte': datos_reporte,
    }
    
    # ============================================================
    # PASO 6: Renderizar el template
    # ============================================================
    return render(request, 'reportes.html', context)
