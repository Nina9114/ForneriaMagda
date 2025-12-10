# ================================================================
# =                                                              =
# =        FUNCIONES PARA HISTORIAL DE BOLETAS                  =
# =                                                              =
# ================================================================
#
# Este archivo contiene funciones auxiliares para gestionar
# el historial de boletas emitidas.

from django.utils import timezone
from ventas.models import HistorialBoletas, Ventas, DetalleVenta
import json
import logging

logger = logging.getLogger('ventas')


def guardar_historial_boleta(venta, usuario_emisor=None):
    """
    Guarda un snapshot de la boleta en el historial.
    
    Esta función se llama automáticamente después de crear una venta
    para guardar todos los datos de la boleta en formato JSON.
    
    Args:
        venta: Objeto Ventas que se acaba de crear
        usuario_emisor: Usuario que emitió la boleta (opcional)
    
    Returns:
        HistorialBoletas: El objeto de historial creado, o None si hubo error
    """
    try:
        # Obtener todos los detalles de la venta
        detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
        
        # Construir el diccionario con todos los datos de la boleta
        datos_boleta = {
            'cabecera': {
                'folio': venta.folio,
                'fecha': venta.fecha.isoformat() if venta.fecha else None,
                'canal_venta': venta.canal_venta,
                'cliente': {
                    'id': venta.clientes.id if venta.clientes else None,
                    'nombre': venta.clientes.nombre if venta.clientes else 'Cliente Genérico',
                    'rut': venta.clientes.rut if venta.clientes and hasattr(venta.clientes, 'rut') else None,
                },
                'totales': {
                    'subtotal_sin_iva': str(venta.total_sin_iva),
                    'total_iva': str(venta.total_iva),
                    'descuento': str(venta.descuento),
                    'total_con_iva': str(venta.total_con_iva),
                },
                'pago': {
                    'medio_pago': venta.medio_pago if hasattr(venta, 'medio_pago') else 'efectivo',
                    'monto_pagado': str(venta.monto_pagado) if venta.monto_pagado else None,
                    'vuelto': str(venta.vuelto) if venta.vuelto else None,
                }
            },
            'detalles': []
        }
        
        # Agregar cada detalle de producto
        for detalle in detalles:
            datos_boleta['detalles'].append({
                'producto': {
                    'id': detalle.productos.id,
                    'nombre': detalle.productos.nombre,
                    'marca': detalle.productos.marca if hasattr(detalle.productos, 'marca') else None,
                },
                'cantidad': str(detalle.cantidad),
                'precio_unitario': str(detalle.precio_unitario),
                'descuento_pct': str(detalle.descuento_pct) if hasattr(detalle, 'descuento_pct') else '0.00',
                'subtotal': str(detalle.calcular_subtotal()) if hasattr(detalle, 'calcular_subtotal') else str(detalle.cantidad * detalle.precio_unitario),
            })
        
        # Crear el registro en el historial
        historial = HistorialBoletas.objects.create(
            venta=venta,
            folio=venta.folio or f'BOL-{venta.id}',
            fecha_venta=venta.fecha,
            cliente_nombre=venta.clientes.nombre if venta.clientes else 'Cliente Genérico',
            total_con_iva=venta.total_con_iva,
            num_productos=detalles.count(),
            canal_venta=venta.canal_venta,
            datos_boleta=datos_boleta,
            usuario_emisor=usuario_emisor or (venta.clientes.nombre if venta.clientes else 'Sistema'),
            modificado=False,
        )
        
        logger.info(f'Historial de boleta guardado: {historial.folio} (ID: {historial.id})')
        return historial
        
    except Exception as e:
        # Si hay un error, registrar pero no fallar la venta
        logger.error(f'Error al guardar historial de boleta para venta {venta.id}: {str(e)}', exc_info=True)
        return None


def reconstruir_boleta_desde_historial(historial):
    """
    Reconstruye los datos de una boleta desde el historial.
    
    Útil para regenerar PDFs o mostrar boletas históricas.
    
    Args:
        historial: Objeto HistorialBoletas
    
    Returns:
        dict: Diccionario con los datos reconstruidos de la boleta
    """
    return historial.get_datos_boleta_dict()

