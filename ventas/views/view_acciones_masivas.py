# ================================================================
# =                                                              =
# =           VISTAS PARA ACCIONES MASIVAS EN INVENTARIO        =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas que manejan las acciones masivas
# sobre múltiples productos en el inventario.
#
# ACCIONES DISPONIBLES:
# 1. Crear alertas para múltiples productos
# 2. Mover múltiples productos a merma
# 3. Eliminar múltiples productos (borrado lógico)
#
# SEGURIDAD:
# - Todas las vistas requieren autenticación (@login_required)
# - Solo aceptan peticiones POST
# - Validan el token CSRF automáticamente

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import date
import json

# Importar los modelos necesarios
from ..models import Productos, Alertas


# ================================================================
# =                  ACCIÓN: CREAR ALERTAS                       =
# ================================================================

@login_required
@require_POST
def crear_alertas_masivo(request):
    """
    Crea alertas de vencimiento para múltiples productos.
    
    Esta función recibe una lista de IDs de productos y genera
    alertas automáticas según los días hasta su vencimiento:
    - ROJA: 0-13 días (urgente)
    - AMARILLA: 14-29 días (precaución)
    - VERDE: 30+ días (informativo)
    
    Args:
        request: HttpRequest con JSON body conteniendo {'ids': [1, 2, 3, ...]}
    
    Returns:
        JsonResponse con el resultado de la operación
    """
    try:
        # Parsear el JSON del body de la petición
        data = json.loads(request.body)
        ids_productos = data.get('ids', [])
        
        # Validar que se enviaron IDs
        if not ids_productos:
            return JsonResponse({
                'success': False,
                'message': 'No se seleccionaron productos'
            }, status=400)
        
        # Obtener los productos seleccionados
        productos = Productos.objects.filter(
            id__in=ids_productos,
            eliminado__isnull=True  # Solo productos no eliminados
        )
        
        # Contador de alertas creadas
        alertas_creadas = 0
        hoy = date.today()
        
        # Crear una alerta para cada producto
        for producto in productos:
            # Calcular días hasta vencer
            dias_hasta_vencer = (producto.caducidad - hoy).days
            
            # Determinar el tipo de alerta según los días
            if dias_hasta_vencer < 0:
                # Producto ya vencido
                tipo = 'roja'
                mensaje = f"{producto.nombre} YA VENCIÓ hace {abs(dias_hasta_vencer)} días"
            elif dias_hasta_vencer <= 13:
                # Alerta ROJA: 0-13 días
                tipo = 'roja'
                mensaje = f"{producto.nombre} vence en {dias_hasta_vencer} días - URGENTE"
            elif dias_hasta_vencer <= 29:
                # Alerta AMARILLA: 14-29 días
                tipo = 'amarilla'
                mensaje = f"{producto.nombre} vence en {dias_hasta_vencer} días - PRECAUCIÓN"
            else:
                # Alerta VERDE: 30+ días
                tipo = 'verde'
                mensaje = f"{producto.nombre} vence en {dias_hasta_vencer} días - OK"
            
            # Verificar si ya existe una alerta activa para este producto
            alerta_existente = Alertas.objects.filter(
                productos=producto,
                estado='activa'
            ).first()
            
            if alerta_existente:
                # Actualizar la alerta existente
                alerta_existente.tipo_alerta = tipo
                alerta_existente.mensaje = mensaje
                alerta_existente.fecha_generada = timezone.now()
                alerta_existente.save()
            else:
                # Crear nueva alerta
                Alertas.objects.create(
                    tipo_alerta=tipo,
                    mensaje=mensaje,
                    productos=producto,
                    estado='activa'
                )
            
            alertas_creadas += 1
        
        # Respuesta exitosa
        return JsonResponse({
            'success': True,
            'message': f'Se crearon/actualizaron {alertas_creadas} alerta(s) exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error al procesar los datos enviados'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear alertas: {str(e)}'
        }, status=500)


# ================================================================
# =                  ACCIÓN: MOVER A MERMA                       =
# ================================================================

@login_required
@require_POST
def mover_merma_masivo(request):
    """
    Mueve múltiples productos al estado de merma.
    
    Esta función cambia el estado_merma de los productos seleccionados
    a 'vencido'. Los productos en merma no aparecen en el inventario
    normal, sino en la sección de merma.
    
    Args:
        request: HttpRequest con JSON body conteniendo {'ids': [1, 2, 3, ...]}
    
    Returns:
        JsonResponse con el resultado de la operación
    """
    try:
        # Parsear el JSON del body de la petición
        data = json.loads(request.body)
        ids_productos = data.get('ids', [])
        motivo_merma = data.get('motivo_merma', '').strip()
        
        # Validar que se enviaron IDs
        if not ids_productos:
            return JsonResponse({
                'success': False,
                'message': 'No se seleccionaron productos'
            }, status=400)
        
        # Validar que se proporcionó un motivo
        if not motivo_merma:
            return JsonResponse({
                'success': False,
                'message': 'Debe proporcionar un motivo para mover el producto a merma'
            }, status=400)
        
        # Importar timezone para fecha_merma
        from django.utils import timezone
        from django.db import transaction
        from decimal import Decimal
        import logging
        
        logger = logging.getLogger('ventas')
        
        # Importar Alertas y HistorialMerma
        from ventas.models import Alertas, HistorialMerma
        
        # Actualizar el estado de los productos seleccionados
        productos_actualizados = Productos.objects.filter(
            id__in=ids_productos,
            eliminado__isnull=True  # Solo productos no eliminados
        )
        
        # NUEVA LÓGICA: Crear registro en HistorialMerma y actualizar producto
        cantidad_actualizados = 0
        historial_creado = False
        
        with transaction.atomic():
            for producto in productos_actualizados:
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
                    logger.info(f'Registro de merma creado: ID {registro_merma.id} para producto {producto.id} - Cantidad: {cantidad_merma_historial}')
                except Exception as e:
                    # Si hay error, registrar pero continuar
                    logger.error(f'Error al crear registro en HistorialMerma: {str(e)}', exc_info=True)
                    # Continuar de todas formas para actualizar el producto
                
                # Actualizar producto: limpiar "contenido" pero mantener SKU
                producto.cantidad = 0  # Reducir cantidad a 0
                producto.caducidad = None  # Limpiar caducidad (ese lote ya no existe)
                producto.elaboracion = None  # Limpiar elaboración (ese lote ya no existe)
                producto.estado_merma = 'en_merma'  # Estado especial para productos en merma
                producto.motivo_merma = motivo_merma  # Registrar motivo
                producto.fecha_merma = timezone.now()  # Registrar fecha
                producto.cantidad_merma = cantidad_original  # Guardar cantidad original (puede ser 0)
                producto.save()
                cantidad_actualizados += 1
        
        # Resolver automáticamente todas las alertas activas de estos productos
        # ya que están en merma y no necesitan alertas
        alertas_resueltas = Alertas.objects.filter(
            productos_id__in=ids_productos,
            estado='activa'
        ).update(estado='resuelta')
        
        # Respuesta exitosa
        mensaje = f'Se movieron {cantidad_actualizados} producto(s) a merma'
        if alertas_resueltas > 0:
            mensaje += f' y se resolvieron {alertas_resueltas} alerta(s) automáticamente'
        
        return JsonResponse({
            'success': True,
            'message': mensaje
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error al procesar los datos enviados'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al mover productos a merma: {str(e)}'
        }, status=500)


# ================================================================
# =            ACCIÓN: ACTIVAR/DESACTIVAR PRODUCTOS             =
# ================================================================

@login_required
@require_POST
def activar_desactivar_masivo(request):
    """
    Activa o desactiva múltiples productos.
    
    Si un producto está activo, lo desactiva (estado_merma='inactivo').
    Si un producto está inactivo, lo activa (estado_merma='activo').
    
    Args:
        request: HttpRequest con JSON body conteniendo {'ids': [1, 2, 3, ...]}
    
    Returns:
        JsonResponse con el resultado de la operación
    """
    try:
        # Parsear el JSON del body de la petición
        data = json.loads(request.body)
        ids_productos = data.get('ids', [])
        
        # Validar que se enviaron IDs
        if not ids_productos:
            return JsonResponse({
                'success': False,
                'message': 'No se seleccionaron productos'
            }, status=400)
        
        # Obtener los productos seleccionados
        productos = Productos.objects.filter(
            id__in=ids_productos,
            eliminado__isnull=True  # Solo productos no eliminados
        )
        
        activados = 0
        desactivados = 0
        
        # Cambiar el estado de cada producto
        for producto in productos:
            if producto.estado_merma == 'activo':
                producto.estado_merma = 'inactivo'
                producto.save()
                desactivados += 1
            elif producto.estado_merma == 'inactivo':
                producto.estado_merma = 'activo'
                producto.save()
                activados += 1
        
        # Construir mensaje
        mensaje_parts = []
        if activados > 0:
            mensaje_parts.append(f'{activados} producto(s) activado(s)')
        if desactivados > 0:
            mensaje_parts.append(f'{desactivados} producto(s) desactivado(s)')
        
        mensaje = ' y '.join(mensaje_parts)
        
        return JsonResponse({
            'success': True,
            'message': mensaje
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error al procesar los datos enviados'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cambiar estado de productos: {str(e)}'
        }, status=500)


# ================================================================
# =                  ACCIÓN: ELIMINAR PRODUCTOS                  =
# ================================================================

@login_required
@require_POST
def eliminar_masivo(request):
    """
    Elimina múltiples productos (borrado lógico).
    
    Esta función NO borra físicamente los productos de la base de datos,
    sino que marca el campo 'eliminado' con la fecha actual. Esto permite
    mantener un historial y recuperar productos si es necesario.
    
    Args:
        request: HttpRequest con JSON body conteniendo {'ids': [1, 2, 3, ...]}
    
    Returns:
        JsonResponse con el resultado de la operación
    """
    try:
        # Parsear el JSON del body de la petición
        data = json.loads(request.body)
        ids_productos = data.get('ids', [])
        
        # Validar que se enviaron IDs
        if not ids_productos:
            return JsonResponse({
                'success': False,
                'message': 'No se seleccionaron productos'
            }, status=400)
        
        # Marcar los productos como eliminados (borrado lógico)
        productos_eliminados = Productos.objects.filter(
            id__in=ids_productos,
            eliminado__isnull=True  # Solo productos no eliminados previamente
        ).update(
            eliminado=timezone.now()  # Marcar con fecha de eliminación
        )
        
        # Respuesta exitosa
        return JsonResponse({
            'success': True,
            'message': f'Se eliminaron {productos_eliminados} producto(s) exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error al procesar los datos enviados'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar productos: {str(e)}'
        }, status=500)
