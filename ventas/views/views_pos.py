# ================================================================
# =                                                              =
# =           VISTAS PARA EL SISTEMA POS (PUNTO DE VENTA)       =
# =                                                              =
# ================================================================
# 
# Este archivo contiene todas las funciones (vistas) que controlan
# el sistema de Punto de Venta (POS) de la Forneria.
# 
# ¿Qué es una VISTA en Django?
# Una vista es una función Python que:
# 1. Recibe una petición HTTP del navegador (request)
# 2. Procesa la información (busca datos, valida, calcula, etc.)
# 3. Retorna una respuesta HTTP (página HTML o datos JSON)
# 
# En este archivo manejaremos:
# - Mostrar la interfaz del POS
# - Agregar productos al carrito
# - Quitar productos del carrito
# - Calcular totales
# - Finalizar la venta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import json
import logging

# Importamos los modelos que necesitamos
from ventas.models import Productos, Clientes, Ventas, DetalleVenta
from ventas.funciones.formularios_ventas import ClienteRapidoForm, FinalizarVentaForm


# ================================================================
# =                VISTA: MOSTRAR EL POS                         =
# ================================================================
# 
# Esta vista muestra la página principal del Punto de Venta (POS)
# donde el usuario puede buscar productos, agregarlos al carrito
# y procesar ventas.

@login_required  # Solo usuarios autenticados pueden acceder
def pos_view(request):
    """
    Vista principal del Punto de Venta (POS).
    
    Muestra:
    - Lista de productos disponibles
    - Formulario para agregar cliente
    - Carrito de compras (manejado con JavaScript en el navegador)
    
    Args:
        request: Objeto con la información de la petición HTTP
        
    Returns:
        Una página HTML con la interfaz del POS
    """
    
    # --- Paso 1: Obtener todos los productos activos (no eliminados) ---
    # Filtramos solo los productos que:
    # - No han sido eliminados (eliminado__isnull=True)
    # - Están en estado activo (no en merma, no inactivos) (estado_merma='activo')
    # - Tienen stock disponible (cantidad > 0)
    # - Están ordenados alfabéticamente por nombre
    # IMPORTANTE: Productos en merma o inactivos NO se muestran en POS
    productos_disponibles = Productos.objects.filter(
        eliminado__isnull=True,    # Solo productos no eliminados
        estado_merma='activo',     # Solo productos activos (excluye inactivos y en_merma)
        cantidad__gt=0             # Solo con stock disponible
    ).select_related('categorias').order_by('nombre')
    
    # --- Paso 2: Obtener todos los clientes para el selector ---
    # Los ordenamos alfabéticamente por nombre
    clientes = Clientes.objects.all().order_by('nombre')
    
    # --- Paso 3: Crear el formulario para agregar nuevos clientes ---
    form_cliente = ClienteRapidoForm()
    
    # --- Paso 4: Preparar el contexto (datos que enviamos al template) ---
    # El "contexto" es un diccionario con todas las variables que
    # el template HTML necesita para mostrar la información
    contexto = {
        'productos': productos_disponibles,  # Lista de productos
        'clientes': clientes,                # Lista de clientes
        'form_cliente': form_cliente,        # Formulario de cliente
        'IVA_RATE': 0.19,                   # Tasa de IVA en Chile (19%)
    }
    
    # --- Paso 5: Renderizar (generar) la página HTML ---
    # Django toma el template 'pos.html' y lo llena con los datos del contexto
    return render(request, 'pos.html', contexto)


# ================================================================
# =        VISTA API: AGREGAR CLIENTE RÁPIDO (JSON)              =
# ================================================================
# 
# Esta vista se llama desde JavaScript (AJAX) para agregar un
# nuevo cliente sin recargar la página.

@login_required
@require_http_methods(["POST"])  # Solo acepta peticiones POST
def agregar_cliente_ajax(request):
    """
    API para agregar un cliente nuevo desde el POS usando AJAX.
    
    Recibe datos JSON del cliente y los guarda en la base de datos.
    Retorna el ID del cliente creado para poder seleccionarlo automáticamente.
    
    Args:
        request: Petición HTTP con los datos del cliente en formato JSON
        
    Returns:
        JsonResponse con el resultado (éxito o error)
    """
    
    try:
        # --- Paso 1: Obtener los datos enviados desde JavaScript ---
        # JavaScript nos envía los datos en formato JSON
        datos = json.loads(request.body)  # Convertimos JSON a diccionario Python
        
        # --- Paso 2: Crear el formulario con los datos recibidos ---
        form = ClienteRapidoForm(datos)
        
        # --- Paso 3: Validar el formulario ---
        if form.is_valid():
            # Si el formulario es válido, guardamos el cliente en la BD
            cliente = form.save()  # Django automáticamente crea el registro
            
            # --- Paso 4: Retornar respuesta exitosa ---
            return JsonResponse({
                'success': True,                    # Indica que todo salió bien
                'mensaje': 'Cliente agregado correctamente',
                'cliente': {
                    'id': cliente.id,               # ID del cliente creado
                    'nombre': cliente.nombre,       # Nombre del cliente
                    'rut': cliente.rut or '',       # RUT (o vacío si no tiene)
                }
            })
        else:
            # Si el formulario tiene errores, los retornamos
            # form.errors es un diccionario con los errores de cada campo
            return JsonResponse({
                'success': False,
                'mensaje': 'Datos inválidos',
                'errores': form.errors  # Diccionario con los errores
            }, status=400)  # Código HTTP 400 = Bad Request
            
    except json.JSONDecodeError:
        # Si el JSON enviado está mal formado
        return JsonResponse({
            'success': False,
            'mensaje': 'Error al procesar los datos JSON'
        }, status=400)
        
    except Exception as e:
        # Cualquier otro error inesperado
        return JsonResponse({
            'success': False,
            'mensaje': f'Error del servidor: {str(e)}'
        }, status=500)  # Código HTTP 500 = Internal Server Error


# ================================================================
# =        VISTA API: VALIDAR DISPONIBILIDAD DE PRODUCTO         =
# ================================================================
# 
# Esta vista verifica si un producto tiene stock suficiente
# antes de agregarlo al carrito.

@login_required
@require_http_methods(["GET"])  # Solo acepta peticiones GET
def validar_producto_ajax(request, producto_id):
    """
    API para validar si un producto está disponible y tiene stock.
    
    Verifica:
    - Que el producto exista
    - Que no esté eliminado
    - Que tenga stock disponible
    - Que no esté vencido
    
    Args:
        request: Petición HTTP
        producto_id: ID del producto a validar
        
    Returns:
        JsonResponse con la información del producto y su disponibilidad
    """
    
    try:
        # --- Paso 1: Buscar el producto ---
        # get_object_or_404 busca el producto, si no existe retorna error 404
        producto = get_object_or_404(Productos, pk=producto_id)
        
        # --- Paso 2: Verificar que el producto no esté eliminado ---
        if producto.eliminado is not None:
            return JsonResponse({
                'disponible': False,
                'mensaje': 'Este producto ya no está disponible'
            })
        
        # --- Paso 3: Verificar que el producto esté activo (no en merma ni inactivo) ---
        if producto.estado_merma != 'activo':
            estado_display = dict(Productos.ESTADO_MERMA_CHOICES).get(
                producto.estado_merma, 
                producto.estado_merma
            )
            mensaje = f'Producto no disponible: {estado_display}'
            if producto.estado_merma == 'inactivo':
                mensaje = f'Producto inactivo: {estado_display}'
            elif producto.estado_merma == 'en_merma':
                mensaje = f'Producto en merma: {estado_display}'
            return JsonResponse({
                'disponible': False,
                'mensaje': mensaje
            })
        
        # --- Paso 4: Verificar que tenga stock ---
        from decimal import Decimal
        if producto.cantidad <= Decimal('0'):
            return JsonResponse({
                'disponible': False,
                'mensaje': 'Producto sin stock'
            })
        
        # --- Paso 5: Verificar fecha de caducidad ---
        # Comparamos la fecha de hoy con la fecha de caducidad del producto
        hoy = timezone.now().date()
        if producto.caducidad < hoy:
            return JsonResponse({
                'disponible': False,
                'mensaje': 'Producto vencido'
            })
        
        # --- Paso 5: Todo está bien, retornar información del producto ---
        return JsonResponse({
            'disponible': True,
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),          # Convertimos Decimal a float para JSON
                'stock_disponible': producto.cantidad,      # Stock actual
                'caducidad': producto.caducidad.strftime('%Y-%m-%d'),  # Fecha en formato ISO
                'descripcion': producto.descripcion or '',
                'marca': producto.marca or '',
            }
        })
        
    except Productos.DoesNotExist:
        return JsonResponse({
            'disponible': False,
            'mensaje': 'Producto no encontrado'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'disponible': False,
            'mensaje': f'Error: {str(e)}'
        }, status=500)


# ================================================================
# =           VISTA API: PROCESAR VENTA COMPLETA                 =
# ================================================================
# 
# Esta es la vista más importante: procesa la venta completa.
# Recibe el carrito, crea los registros en la base de datos
# y actualiza el stock de los productos.

@login_required
@require_http_methods(["POST"])
def procesar_venta_ajax(request):
    # Configurar logger
    logger = logging.getLogger('ventas')
    """
    API para procesar una venta completa.
    
    Recibe:
    - ID del cliente
    - Canal de venta (presencial/delivery)
    - Carrito con los productos (array de objetos)
    - Monto pagado
    - Descuento (opcional)
    
    Realiza:
    1. Valida que todos los productos tengan stock
    2. Calcula los totales (subtotal, IVA, total)
    3. Crea el registro de la Venta
    4. Crea los registros de DetalleVenta
    5. Actualiza el stock de cada producto
    6. Retorna el resultado
    
    Args:
        request: Petición HTTP con los datos de la venta en JSON
        
    Returns:
        JsonResponse con el resultado de la venta (ID, folio, etc.)
    """
    
    try:
        # --- Paso 1: Obtener los datos enviados desde JavaScript ---
        datos = json.loads(request.body)
        
        # Extraemos cada campo del JSON
        cliente_id = datos.get('cliente_id')
        canal_venta = datos.get('canal_venta', 'presencial')
        carrito = datos.get('carrito', [])  # Array con los productos
        medio_pago = datos.get('medio_pago', 'efectivo')  # Por defecto efectivo
        monto_pagado = Decimal(str(datos.get('monto_pagado', 0)))
        descuento_global = Decimal(str(datos.get('descuento', 0)))
        
        # --- Paso 2: Validaciones básicas ---
        if not cliente_id:
            return JsonResponse({
                'success': False,
                'mensaje': 'Debe seleccionar un cliente'
            }, status=400)
        
        if not carrito or len(carrito) == 0:
            return JsonResponse({
                'success': False,
                'mensaje': 'El carrito está vacío'
            }, status=400)
        
        # Verificar que el cliente existe
        try:
            cliente = Clientes.objects.get(pk=cliente_id)
        except Clientes.DoesNotExist:
            return JsonResponse({
                'success': False,
                'mensaje': 'Cliente no encontrado'
            }, status=404)
        
        # --- Paso 3: Validar stock de todos los productos ---
        # Antes de procesar, verificamos que TODOS los productos tengan stock
        for item in carrito:
            producto_id = item.get('producto_id')
            cantidad_solicitada = Decimal(str(item.get('cantidad', 0)))
            
            try:
                producto = Productos.objects.get(pk=producto_id)
                
                # Verificar que no esté eliminado
                if producto.eliminado is not None:
                    return JsonResponse({
                        'success': False,
                        'mensaje': f'El producto "{producto.nombre}" ya no está disponible'
                    }, status=400)
                
                # Verificar stock (permite decimales)
                if producto.cantidad < cantidad_solicitada:
                    return JsonResponse({
                        'success': False,
                        'mensaje': f'Stock insuficiente para "{producto.nombre}". Disponible: {producto.cantidad}'
                    }, status=400)
                    
            except Productos.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'mensaje': f'Producto con ID {producto_id} no encontrado'
                }, status=404)
        
        # --- Paso 4: Calcular totales ---
        # IMPORTANTE: El precio del producto YA INCLUYE IVA (precio final al consumidor)
        # Por lo tanto, debemos calcular:
        # 1. Total con IVA incluido (precio mostrado × cantidad)
        # 2. Subtotal sin IVA (total / 1.19)
        # 3. IVA (subtotal sin IVA × 0.19)
        # 4. Total final = precio original (con IVA incluido)
        
        total_con_iva_incluido = Decimal('0.00')
        
        # Sumamos el precio de cada producto del carrito (precio ya incluye IVA)
        for item in carrito:
            producto_id = item.get('producto_id')
            cantidad = Decimal(str(item.get('cantidad', 0)))  # Permite decimales
            precio_unitario = Decimal(str(item.get('precio_unitario', 0)))  # Precio con IVA incluido
            descuento_item = Decimal(str(item.get('descuento', 0)))
            
            # Calcular subtotal de este item (precio con IVA incluido)
            subtotal_item_con_iva = cantidad * precio_unitario
            
            # Aplicar descuento si existe
            if descuento_item > 0:
                subtotal_item_con_iva = subtotal_item_con_iva - (subtotal_item_con_iva * descuento_item / 100)
            
            total_con_iva_incluido += subtotal_item_con_iva
        
        # Aplicar descuento global (si existe)
        total_con_iva_incluido = total_con_iva_incluido - descuento_global
        
        # Calcular subtotal sin IVA (desglosar el IVA del precio)
        # Subtotal sin IVA = Total con IVA / 1.19
        IVA_RATE = Decimal('0.19')
        total_sin_iva = total_con_iva_incluido / (Decimal('1') + IVA_RATE)
        
        # Calcular IVA (19% del subtotal sin IVA)
        total_iva = total_sin_iva * IVA_RATE
        
        # Total final = precio original (con IVA incluido)
        total_con_iva = total_con_iva_incluido
        
        # Redondear a 2 decimales
        from decimal import ROUND_HALF_UP
        total_sin_iva = total_sin_iva.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_iva = total_iva.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_con_iva = total_con_iva.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calcular vuelto
        vuelto = monto_pagado - total_con_iva
        
        # Verificar que el monto pagado sea suficiente
        if vuelto < 0:
            return JsonResponse({
                'success': False,
                'mensaje': f'Monto insuficiente. Total: ${total_con_iva:.2f}, Pagado: ${monto_pagado:.2f}'
            }, status=400)
        
        # --- Paso 4.5: VALIDAR STOCK ANTES DE PROCESAR VENTA ---
        # Verificar que todos los productos tengan stock suficiente
        for item in carrito:
            producto_id = item.get('producto_id')
            cantidad = Decimal(str(item.get('cantidad', 0)))  # Permite decimales
            
            try:
                producto = Productos.objects.get(pk=producto_id, eliminado__isnull=True)
                stock_disponible = producto.cantidad if producto.cantidad else Decimal('0')
                
                if stock_disponible < cantidad:
                    return JsonResponse({
                        'success': False,
                        'mensaje': f'Stock insuficiente para {producto.nombre}. Disponible: {stock_disponible}, Solicitado: {cantidad}'
                    }, status=400)
            except Productos.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'mensaje': f'Producto con ID {producto_id} no encontrado'
                }, status=404)
        
        # --- Paso 5: Crear la venta en la base de datos ---
        # Usamos una TRANSACCIÓN para asegurar que todo se guarde correctamente
        # o NADA se guarde si hay un error (atomicidad)
        with transaction.atomic():
            
            # Generar folio único (puedes mejorarlo con un sistema más robusto)
            folio = f"BOL-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # Calcular vuelto (solo para pagos en efectivo)
            # Para otros métodos de pago, el vuelto es 0
            vuelto_calculado = Decimal('0.00')
            if medio_pago == 'efectivo':
                vuelto_calculado = vuelto
            else:
                # Para otros métodos, el monto pagado debe ser exactamente el total
                if monto_pagado != total_con_iva:
                    # Si hay diferencia, ajustar monto_pagado al total
                    monto_pagado = total_con_iva
            
            # Crear el registro de Venta
            venta = Ventas.objects.create(
                clientes=cliente,
                canal_venta=canal_venta,
                total_sin_iva=total_sin_iva,
                total_iva=total_iva,
                descuento=descuento_global,
                total_con_iva=total_con_iva,
                folio=folio,
                medio_pago=medio_pago,
                monto_pagado=monto_pagado,
                vuelto=vuelto_calculado,
            )
            
            # --- Paso 6: Crear los detalles de venta y actualizar stock ---
            for item in carrito:
                producto_id = item.get('producto_id')
                cantidad = Decimal(str(item.get('cantidad', 0)))  # Permite decimales
                precio_unitario = Decimal(str(item.get('precio_unitario', 0)))
                descuento_pct = Decimal(str(item.get('descuento', 0)))
                
                # Obtener el producto
                producto = Productos.objects.get(pk=producto_id)
                
                # Crear el detalle de venta
                DetalleVenta.objects.create(
                    ventas=venta,
                    productos=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    descuento_pct=descuento_pct,
                )
                
                # Validar stock disponible antes de actualizar
                stock_disponible = producto.calcular_cantidad_desde_lotes() if hasattr(producto, 'calcular_cantidad_desde_lotes') else producto.cantidad
                if stock_disponible < cantidad:
                    raise ValueError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {stock_disponible}, Solicitado: {cantidad}'
                    )
                
                # Reducir cantidad de lotes usando FIFO (First In First Out)
                # Vender primero los lotes más antiguos (los que vencen primero)
                from ventas.models import Lote
                cantidad_restante = Decimal(str(cantidad))  # Asegurar que sea Decimal
                
                # Obtener lotes activos ordenados por fecha de caducidad (más antiguos primero)
                lotes_activos = Lote.objects.filter(
                    productos=producto,
                    estado='activo',
                    cantidad__gt=0
                ).order_by('fecha_caducidad', 'fecha_recepcion')
                
                for lote in lotes_activos:
                    if cantidad_restante <= Decimal('0'):
                        break
                    
                    # Asegurar que lote.cantidad sea Decimal
                    cantidad_lote = Decimal(str(lote.cantidad))
                    
                    # Calcular cuánto tomar de este lote
                    cantidad_a_tomar = min(cantidad_restante, cantidad_lote)
                    
                    logger.info(f'[VENTA FIFO] Lote {lote.id}: cantidad antes={cantidad_lote}, tomando={cantidad_a_tomar}')
                    
                    # Reducir la cantidad del lote
                    nueva_cantidad_lote = cantidad_lote - cantidad_a_tomar
                    lote.cantidad = nueva_cantidad_lote
                    
                    # Si el lote se agotó, marcarlo como agotado
                    if nueva_cantidad_lote <= Decimal('0'):
                        lote.estado = 'agotado'
                        lote.cantidad = Decimal('0')
                        logger.info(f'[VENTA FIFO] Lote {lote.id} agotado')
                    
                    lote.save(update_fields=['cantidad', 'estado'])
                    logger.info(f'[VENTA FIFO] Lote {lote.id}: cantidad después={lote.cantidad}, estado={lote.estado}')
                    cantidad_restante = cantidad_restante - cantidad_a_tomar
                
                # Si aún queda cantidad por vender (no debería pasar si la validación fue correcta)
                if cantidad_restante > Decimal('0'):
                    raise ValueError(
                        f'Error: No se pudo reducir completamente el stock. '
                        f'Quedan {cantidad_restante} unidades sin asignar a lotes.'
                    )
                
                # Refrescar el producto desde la BD para obtener datos actualizados
                producto.refresh_from_db()
                
                # Actualizar la cantidad total del producto desde lotes
                # Siempre recalcular desde lotes si el producto tiene lotes
                if hasattr(producto, 'calcular_cantidad_desde_lotes'):
                    nueva_cantidad_producto = producto.calcular_cantidad_desde_lotes()
                    logger.info(f'[VENTA] Recalculando cantidad desde lotes: {nueva_cantidad_producto}')
                else:
                    nueva_cantidad_producto = producto.cantidad - cantidad
                    logger.info(f'[VENTA] Reduciendo cantidad directamente: {nueva_cantidad_producto}')
                
                producto.cantidad = nueva_cantidad_producto
                logger.info(f'[VENTA] Cantidad del producto actualizada a: {producto.cantidad}')
                
                # Actualizar fecha de caducidad del producto con la del lote más antiguo activo
                lote_mas_antiguo = Lote.objects.filter(
                    productos=producto,
                    estado='activo',
                    cantidad__gt=0
                ).order_by('fecha_caducidad', 'fecha_recepcion').first()
                
                if lote_mas_antiguo and lote_mas_antiguo.fecha_caducidad:
                    producto.caducidad = lote_mas_antiguo.fecha_caducidad
                elif not lote_mas_antiguo:
                    # Si no hay lotes activos, limpiar fecha de caducidad
                    producto.caducidad = None
                
                # Guardar cambios en el producto
                producto.save(update_fields=['cantidad', 'caducidad'])
                
                # Log para debugging
                logger.info(f'[VENTA] Producto {producto.nombre}: cantidad actualizada a {producto.cantidad} después de vender {cantidad} unidades')
                
                # Crear movimiento de inventario para trazabilidad
                try:
                    from ventas.models import MovimientosInventario
                    MovimientosInventario.objects.create(
                        tipo_movimiento='salida',
                        cantidad=cantidad,
                        productos=producto,
                        origen='venta',
                        referencia_id=venta.id,
                        tipo_referencia='venta'
                    )
                except Exception as e:
                    # Si falla la creación del movimiento, registrar pero no fallar la venta
                    logger.warning(f'Error al crear movimiento de inventario: {e}')
            
            # --- Paso 6.5: Guardar historial de boleta (sin afectar la transacción principal) ---
            try:
                from ventas.funciones.historial_boletas import guardar_historial_boleta
                usuario_emisor = request.user.username if request.user.is_authenticated else None
                guardar_historial_boleta(venta, usuario_emisor=usuario_emisor)
            except Exception as e:
                # Si falla el guardado del historial, registrar pero no fallar la venta
                logger.warning(f'Error al guardar historial de boleta: {e}')
        
        # --- Paso 7: Retornar respuesta exitosa ---
        return JsonResponse({
            'success': True,
            'mensaje': 'Venta procesada correctamente',
            'venta': {
                'id': venta.id,
                'folio': venta.folio,
                'total': float(total_con_iva),
                'vuelto': float(vuelto),
                'fecha': venta.fecha.strftime('%d/%m/%Y %H:%M'),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'mensaje': 'Error al procesar los datos JSON'
        }, status=400)
        
    except Exception as e:
        # Si hay cualquier error, la transacción se revierte automáticamente
        logger.error(f'Error al procesar venta: {e}', exc_info=True)
        
        # En producción, no exponer detalles del error al usuario
        if settings.DEBUG:
            mensaje_error = f'Error al procesar la venta: {str(e)}'
        else:
            mensaje_error = 'Error al procesar la venta. Contacte al administrador.'
        
        return JsonResponse({
            'success': False,
            'mensaje': mensaje_error
        }, status=500)

