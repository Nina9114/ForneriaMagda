# ================================================================
# =                                                              =
# =              VISTA PARA PRODUCTOS EN MERMA                   =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas para gestionar productos en merma.
# La merma incluye productos vencidos, deteriorados o dañados.
#
# PROPÓSITO:
# - Mostrar listado de productos en merma
# - Permitir mover productos desde inventario activo a merma
# - Facilitar la gestión de productos que no se pueden vender
#
# VISTAS INCLUIDAS:
# 1. merma_list_view: Muestra el listado de productos en merma
# 2. mover_a_merma_ajax: API para mover productos a merma (llamada desde JavaScript)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from ventas.models import Productos
from decimal import Decimal
import json
import logging

logger = logging.getLogger('ventas')


# ================================================================
# =              VISTA: LISTADO DE MERMA                         =
# ================================================================

@login_required
def merma_list_view(request):
    """
    Muestra el listado de productos en estado de merma.
    
    Filtra y muestra todos los productos que NO están en estado 'activo',
    es decir, productos vencidos, deteriorados o dañados.
    
    Filtros disponibles:
    - Tipo de merma: vencido, deteriorado, dañado
    
    Args:
        request: Objeto HttpRequest con la información de la petición
        
    Returns:
        HttpResponse: Página HTML con el listado de productos en merma
    """
    
    # ============================================================
    # PASO 1: Obtener productos en merma
    # ============================================================
    # Criterios de búsqueda:
    # - Productos con registros activos en HistorialMerma (prioridad)
    # - O productos con estado_merma='en_merma' (compatibilidad con productos antiguos)
    try:
        from ventas.models import HistorialMerma
        # Obtener IDs de productos con registros activos en HistorialMerma
        productos_con_historial_activo = HistorialMerma.objects.filter(
            activo=True
        ).values_list('producto_id', flat=True).distinct()
        
        # Mostrar productos que tienen registros activos en HistorialMerma
        # O productos con estado_merma='en_merma' (para compatibilidad)
        # Usar Q() para combinar ambas condiciones con OR
        productos_merma = Productos.objects.filter(
            eliminado__isnull=True
        ).filter(
            Q(id__in=productos_con_historial_activo) | Q(estado_merma='en_merma')
        ).distinct()
    except Exception:
        # Si HistorialMerma no existe, usar el método anterior (compatibilidad)
        productos_merma = Productos.objects.filter(
            eliminado__isnull=True,
            estado_merma='en_merma'
        ).distinct()
    
    # ============================================================
    # PASO 2: Mostrar todos los productos en merma (sin filtro)
    # ============================================================
    # Ya no filtramos por tipo, mostramos todo por defecto
    
    # ============================================================
    # PASO 3: Calcular estadísticas de merma
    # ============================================================
    # Calcular pérdida total y total de unidades
    perdida_total = 0
    total_unidades = 0
    
    for producto in productos_merma:
        # Usar cantidad_merma si está disponible, sino usar cantidad
        cantidad_perdida = producto.cantidad_merma if (producto.cantidad_merma and producto.cantidad_merma > 0) else producto.cantidad
        # Calcular pérdida por producto (cantidad_merma × precio)
        perdida_producto = cantidad_perdida * producto.precio
        perdida_total += perdida_producto
        total_unidades += cantidad_perdida
    
    # ============================================================
    # PASO 4: Preparar el contexto para el template
    # ============================================================
    context = {
        'productos': productos_merma,    # Lista de productos en merma
        'perdida_total': perdida_total,  # Pérdida económica total
        'total_unidades': total_unidades, # Total de unidades en merma
    }
    
    # ============================================================
    # PASO 5: Renderizar el template
    # ============================================================
    return render(request, 'merma_list.html', context)


# ================================================================
# =              API: MOVER PRODUCTOS A MERMA                    =
# ================================================================

@login_required
def mover_a_merma_ajax(request):
    """
    API para mover productos seleccionados a estado de merma.
    
    Esta función se llama desde JavaScript (AJAX) cuando el usuario
    selecciona productos en el inventario y hace clic en "Mover a Merma".
    
    Recibe:
    - producto_ids: Lista de IDs de productos a mover
    - motivo: Razón de la merma ('vencido', 'deteriorado', 'dañado')
    
    Retorna:
    - JSON con el resultado de la operación
    
    Args:
        request: Objeto HttpRequest con los datos en formato JSON
        
    Returns:
        JsonResponse: Respuesta en formato JSON con el resultado
    """
    
    # ============================================================
    # PASO 1: Validar que sea una petición POST
    # ============================================================
    # Solo aceptamos peticiones POST (no GET)
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido. Usa POST.'
        })
    
    try:
        # ============================================================
        # PASO 2: Obtener los datos enviados desde JavaScript
        # ============================================================
        # Los datos vienen en formato JSON en el body de la petición
        data = json.loads(request.body)
        
        # Extraer la lista de IDs de productos
        producto_ids = data.get('producto_ids', [])
        
        # Extraer el motivo detallado de la merma
        motivo_merma = data.get('motivo_merma', '').strip()
        
        # Extraer lotes específicos (opcional - solo si se seleccionaron lotes específicos)
        lotes_seleccionados = data.get('lotes', [])  # Lista de {lote_id: int, cantidad: float}
        
        # ============================================================
        # PASO 3: Validar que se proporcionó un motivo
        # ============================================================
        # Ya no necesitamos validar estado_merma porque siempre será 'en_merma'
        if not motivo_merma:
            return JsonResponse({
                'success': False,
                'error': 'Debe proporcionar un motivo detallado para mover el producto a merma'
            })
        
        # ============================================================
        # PASO 4: Validar que se seleccionaron productos
        # ============================================================
        if not producto_ids or len(producto_ids) == 0:
            return JsonResponse({
                'success': False,
                'error': 'No se seleccionaron productos'
            })
        
        # ============================================================
        # PASO 5: Mover productos a merma
        # ============================================================
        # Importar timezone para fecha_merma
        from django.utils import timezone
        from django.db import transaction
        
        # Importar Alertas y HistorialMerma
        from ventas.models import Alertas, HistorialMerma
        
        # Buscar los productos por sus IDs
        productos = Productos.objects.filter(id__in=producto_ids)
        
        # NUEVA LÓGICA: Crear registro en HistorialMerma y actualizar producto
        contador = 0
        historial_creado = False
        
        with transaction.atomic():
            for producto in productos:
                # Guardar la cantidad que se va a merma antes de ponerla en 0
                cantidad_original = producto.cantidad if producto.cantidad else Decimal('0')
                
                # Para HistorialMerma, usar mínimo 0.001 si la cantidad es 0 (requisito del modelo)
                cantidad_merma_historial = cantidad_original if cantidad_original > 0 else Decimal('0.001')
                
                # Crear registro en HistorialMerma (siempre intentar crear)
                try:
                    registro_merma = HistorialMerma.objects.create(
                        producto=producto,
                        cantidad_merma=cantidad_merma_historial,
                        motivo_merma=motivo_merma,
                        fecha_merma=timezone.now(),
                        activo=True
                    )
                    historial_creado = True
                    logger.info(f'Registro de merma creado: ID {registro_merma.id} para producto {producto.id} ({producto.nombre}) - Cantidad: {cantidad_merma_historial}')
                except Exception as e:
                    # Si hay error, registrar pero continuar
                    logger.error(f'Error al crear registro en HistorialMerma para producto {producto.id}: {str(e)}', exc_info=True)
                    # Continuar de todas formas para actualizar el producto
                
                # Procesar lotes según si se especificaron lotes específicos o no
                lotes_procesados = 0
                cantidad_total_merma = Decimal('0')
                
                try:
                    from ventas.models import Lote
                    
                    # Si se especificaron lotes específicos, procesar solo esos
                    if lotes_seleccionados and len(lotes_seleccionados) > 0:
                        # Filtrar lotes del producto actual
                        lotes_del_producto = []
                        for lote_data in lotes_seleccionados:
                            lote_id = lote_data.get('lote_id')
                            if Lote.objects.filter(id=lote_id, productos=producto).exists():
                                lotes_del_producto.append(lote_data)
                        
                        for lote_data in lotes_del_producto:
                            lote_id = lote_data.get('lote_id')
                            cantidad_merma = Decimal(str(lote_data.get('cantidad', 0)))
                            
                            try:
                                lote = Lote.objects.get(id=lote_id, productos=producto, estado='activo')
                                
                                # Validar que la cantidad sea mayor a 0
                                if cantidad_merma <= Decimal('0'):
                                    logger.warning(f'Cantidad inválida para lote {lote_id}: {cantidad_merma}. Debe ser mayor a 0. Se omite este lote.')
                                    continue
                                
                                # Validar que no exceda la cantidad disponible del lote
                                if cantidad_merma > lote.cantidad:
                                    logger.warning(f'Cantidad excede lo disponible para lote {lote_id}: solicitado={cantidad_merma}, disponible={lote.cantidad}. Se ajusta al máximo disponible.')
                                    cantidad_merma = lote.cantidad
                                
                                # Validar que sea al menos 1
                                if cantidad_merma < Decimal('1'):
                                    logger.warning(f'Cantidad inválida para lote {lote_id}: {cantidad_merma}. Debe ser al menos 1. Se omite este lote.')
                                    continue
                                
                                # Si la cantidad es igual a la del lote, marcar todo el lote como en_merma
                                if cantidad_merma >= lote.cantidad:
                                    lote.estado = 'en_merma'
                                    cantidad_total_merma += lote.cantidad
                                    lote.cantidad = Decimal('0')
                                    lotes_procesados += 1
                                else:
                                    # Reducir solo la cantidad especificada
                                    cantidad_total_merma += cantidad_merma
                                    lote.cantidad = lote.cantidad - cantidad_merma
                                    lotes_procesados += 1
                                
                                lote.save(update_fields=['cantidad', 'estado'])
                                logger.info(f'Lote {lote_id} procesado: cantidad_merma={cantidad_merma}, nueva_cantidad={lote.cantidad}, estado={lote.estado}')
                                
                            except Lote.DoesNotExist:
                                logger.warning(f'Lote {lote_id} no encontrado o no pertenece al producto {producto.id}')
                                continue
                    else:
                        # Si no se especificaron lotes, procesar todos los lotes activos (comportamiento anterior)
                        lotes_activos = Lote.objects.filter(
                            productos=producto,
                            estado='activo',
                            cantidad__gt=0
                        )
                        lotes_procesados = lotes_activos.count()
                        if lotes_procesados > 0:
                            for lote in lotes_activos:
                                cantidad_total_merma += lote.cantidad
                            lotes_activos.update(estado='en_merma', cantidad=Decimal('0'))
                            logger.info(f'Marcados {lotes_procesados} lotes como en_merma para producto {producto.id}')
                    
                except Exception as e:
                    logger.error(f'Error al procesar lotes: {str(e)}', exc_info=True)
                
                # Actualizar cantidad del producto desde lotes activos restantes
                try:
                    from ventas.models import Lote
                    nueva_cantidad = producto.calcular_cantidad_desde_lotes() if hasattr(producto, 'calcular_cantidad_desde_lotes') else Decimal('0')
                    producto.cantidad = nueva_cantidad
                    
                    # Actualizar fecha de caducidad con la del lote más antiguo activo
                    lote_mas_antiguo = Lote.objects.filter(
                        productos=producto,
                        estado='activo',
                        cantidad__gt=0
                    ).order_by('fecha_caducidad', 'fecha_recepcion').first()
                    
                    if lote_mas_antiguo and lote_mas_antiguo.fecha_caducidad:
                        producto.caducidad = lote_mas_antiguo.fecha_caducidad
                        if lote_mas_antiguo.fecha_elaboracion:
                            producto.elaboracion = lote_mas_antiguo.fecha_elaboracion
                    elif nueva_cantidad == 0:
                        # Si no quedan lotes activos, limpiar fechas
                        producto.caducidad = None
                        producto.elaboracion = None
                except Exception as e:
                    logger.error(f'Error al actualizar cantidad desde lotes: {str(e)}', exc_info=True)
                    # Fallback: usar cantidad_total_merma
                    producto.cantidad = cantidad_original - cantidad_total_merma
                
                # Si la cantidad es 0, marcar como en_merma
                if producto.cantidad <= Decimal('0'):
                    producto.estado_merma = 'en_merma'
                else:
                    # Si aún hay stock, mantener activo
                    producto.estado_merma = 'activo'
                
                # Mantener motivo_merma y fecha_merma en producto para compatibilidad
                producto.motivo_merma = motivo_merma
                producto.fecha_merma = timezone.now()
                producto.cantidad_merma = cantidad_total_merma if cantidad_total_merma > 0 else cantidad_original
                producto.save(update_fields=['cantidad', 'caducidad', 'elaboracion', 'estado_merma', 'motivo_merma', 'fecha_merma', 'cantidad_merma'])
                logger.info(f'Producto {producto.id} ({producto.nombre}) actualizado: estado_merma={producto.estado_merma}, cantidad={producto.cantidad}')
                
                # Guardar información de lotes procesados para el mensaje
                producto._lotes_procesados = lotes_procesados
                producto._cantidad_merma_procesada = cantidad_total_merma
                contador += 1
            
            # Resolver automáticamente todas las alertas activas de estos productos
            # ya que están en merma y no necesitan alertas
            alertas_resueltas = Alertas.objects.filter(
                productos_id__in=producto_ids,
                estado='activa'
            ).update(estado='resuelta')
        
        # ============================================================
        # PASO 6: Retornar respuesta exitosa
        # ============================================================
        # Contar total de lotes procesados y cantidad total
        total_lotes = sum(getattr(p, '_lotes_procesados', 0) for p in productos)
        total_cantidad_merma = sum(getattr(p, '_cantidad_merma_procesada', 0) for p in productos)
        
        mensaje = f'Se movieron {contador} producto(s) a merma.'
        if total_lotes > 0:
            mensaje += f' Se procesaron {total_lotes} lote(s).'
        if total_cantidad_merma > 0:
            mensaje += f' Cantidad enviada a merma: {total_cantidad_merma}.'
        if any(p.cantidad > 0 for p in productos):
            mensaje += ' El producto aún tiene stock disponible.'
        else:
            mensaje += ' El producto quedó sin stock. Puedes reabastecer editándolo.'
        if alertas_resueltas > 0:
            mensaje += f' Se resolvieron {alertas_resueltas} alerta(s) automáticamente.'
        
        return JsonResponse({
            'success': True,
            'mensaje': mensaje
        })
        
    except json.JSONDecodeError:
        # Si hay error al decodificar el JSON
        return JsonResponse({
            'success': False,
            'error': 'Error al procesar los datos. Formato JSON inválido.'
        })
    
    except Exception as e:
        # Cualquier otro error inesperado
        return JsonResponse({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        })
