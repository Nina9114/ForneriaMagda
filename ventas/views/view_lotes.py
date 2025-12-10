# ================================================================
# =                                                              =
# =              VISTAS API PARA LOTES                           =
# =                                                              =
# ================================================================

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from ventas.models import Productos, Lote
from datetime import date


@login_required
@require_http_methods(["GET"])
def obtener_lotes_producto_api(request, producto_id):
    """
    API que retorna los lotes activos de un producto.
    
    Returns:
        JSON con lista de lotes activos del producto
    """
    try:
        producto = get_object_or_404(Productos, pk=producto_id, eliminado__isnull=True)
        
        # Obtener lotes activos del producto
        lotes = Lote.objects.filter(
            productos=producto,
            estado='activo',
            cantidad__gt=0
        ).order_by('fecha_caducidad', 'fecha_recepcion')
        
        lotes_data = []
        for lote in lotes:
            # Calcular días hasta vencer
            dias_hasta_vencer = None
            if lote.fecha_caducidad:
                dias_hasta_vencer = (lote.fecha_caducidad - date.today()).days
            
            lotes_data.append({
                'id': lote.id,
                'numero_lote': lote.numero_lote or f'Lote-{lote.id}',
                'cantidad': float(lote.cantidad),
                'cantidad_inicial': float(lote.cantidad_inicial),
                'fecha_elaboracion': lote.fecha_elaboracion.isoformat() if lote.fecha_elaboracion else None,
                'fecha_caducidad': lote.fecha_caducidad.isoformat() if lote.fecha_caducidad else None,
                'fecha_recepcion': lote.fecha_recepcion.strftime('%Y-%m-%d %H:%M:%S') if lote.fecha_recepcion else None,
                'origen': lote.origen,
                'dias_hasta_vencer': dias_hasta_vencer,
                'estado': lote.estado
            })
        
        return JsonResponse({
            'success': True,
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'unidad_stock': producto.get_unidad_stock_display()
            },
            'lotes': lotes_data,
            'total_lotes': len(lotes_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener lotes: {str(e)}'
        }, status=500)

