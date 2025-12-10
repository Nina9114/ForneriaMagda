from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from ventas.funciones.formularios_productos import ProductoForm, NutricionalForm
from ventas.models.productos import Productos, Nutricional
from ventas.models.movimientos import MovimientosInventario
from ventas.models.ventas import DetalleVenta
from ventas.models.alertas import Alertas
from django.utils import timezone

def inventario_view(request):
    q = (request.GET.get('q') or '').strip()
    # Filtro para mostrar inactivos
    mostrar_inactivos = request.GET.get('mostrar_inactivos', 'false').lower() == 'true'
    
    qs = Productos.objects.select_related('categorias').filter(eliminado__isnull=True)
    
    # Por defecto, mostrar productos activos Y productos en merma (para que se vean en inventario)
    # Si mostrar_inactivos=True, mostrar activos, inactivos y en_merma
    if mostrar_inactivos:
        qs = qs.filter(estado_merma__in=['activo', 'inactivo', 'en_merma'])
    else:
        # Mostrar productos activos Y productos en merma (estos deben permanecer visibles)
        qs = qs.filter(estado_merma__in=['activo', 'en_merma'])
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(marca__icontains=q) |
            Q(tipo__icontains=q) |
            Q(formato__icontains=q) |
            Q(categorias__nombre__icontains=q)
        )

    # Deduplicar: clave por (nombre, marca)
    productos = []
    seen = set()
    for p in qs.order_by('nombre', 'marca'):
        key = (p.nombre.strip().lower(), (p.marca or '').strip().lower())
        if key in seen:
            continue
        seen.add(key)
        
        # Calcular cantidad desde lotes si existen
        p.cantidad_desde_lotes = p.calcular_cantidad_desde_lotes()
        
        # Contar lotes activos
        try:
            from ventas.models import Lote
            lotes_activos = Lote.objects.filter(
                productos=p,
                estado='activo',
                cantidad__gt=0
            )
            p.numero_lotes_activos = lotes_activos.count()
            
            # Si el producto está en merma pero tiene lotes activos (no inactivos), reactivarlo automáticamente
            # PERO solo si NO tiene registros activos en HistorialMerma
            if p.estado_merma == 'en_merma' and p.numero_lotes_activos > 0:
                try:
                    from ventas.models import HistorialMerma
                    tiene_historial_activo = HistorialMerma.objects.filter(
                        producto=p,
                        activo=True
                    ).exists()
                    
                    # Solo reactivar si NO tiene historial activo (es decir, fue reactivado manualmente)
                    if not tiene_historial_activo:
                        p.estado_merma = 'activo'
                        # Actualizar fecha de caducidad con la del lote más antiguo (FIFO)
                        lote_mas_antiguo = lotes_activos.order_by('fecha_caducidad', 'fecha_recepcion').first()
                        if lote_mas_antiguo:
                            p.caducidad = lote_mas_antiguo.fecha_caducidad
                            if lote_mas_antiguo.fecha_elaboracion:
                                p.elaboracion = lote_mas_antiguo.fecha_elaboracion
                        p.save(update_fields=['estado_merma', 'caducidad', 'elaboracion'])
                except Exception:
                    # Si HistorialMerma no existe, usar el comportamiento anterior
                    p.estado_merma = 'activo'
                    lote_mas_antiguo = lotes_activos.order_by('fecha_caducidad', 'fecha_recepcion').first()
                    if lote_mas_antiguo:
                        p.caducidad = lote_mas_antiguo.fecha_caducidad
                        if lote_mas_antiguo.fecha_elaboracion:
                            p.elaboracion = lote_mas_antiguo.fecha_elaboracion
                    p.save(update_fields=['estado_merma', 'caducidad', 'elaboracion'])
        except Exception:
            p.numero_lotes_activos = 0
        
        productos.append(p)

    return render(request, 'inventario.html', {
        'productos': productos, 
        'q': q,
        'mostrar_inactivos': mostrar_inactivos
    })

def editar_producto_view(request, producto_id):
    producto = get_object_or_404(Productos, pk=producto_id)
    nutri_inst = producto.nutricional or Nutricional()

    if request.method == 'POST':
        # IMPORTANTE: Obtener la cantidad anterior DIRECTAMENTE de la BD antes de crear el formulario
        # porque el formulario puede modificar el objeto producto
        cantidad_anterior_bd = Productos.objects.filter(pk=producto_id).values_list('cantidad', flat=True).first()
        cantidad_anterior = int(cantidad_anterior_bd) if cantidad_anterior_bd is not None else 0
        
        # También obtener los valores de merma directamente de la BD
        producto_bd = Productos.objects.get(pk=producto_id)
        motivo_merma_anterior = producto_bd.motivo_merma
        fecha_merma_anterior = producto_bd.fecha_merma
        cantidad_merma_anterior = producto_bd.cantidad_merma
        estado_merma_anterior = producto_bd.estado_merma
        
        form = ProductoForm(request.POST, instance=producto)
        nutricional_form = NutricionalForm(request.POST, instance=nutri_inst)
        if form.is_valid() and nutricional_form.is_valid():
            # PRESERVAR el historial de merma antes de guardar (el formulario no incluye estos campos)
            # IMPORTANTE: Guardar estos valores ANTES de llamar a form.save() porque el formulario
            # podría limpiar estos campos si no están incluidos en el formulario
            
            # Obtener la nueva cantidad del formulario ANTES de hacer save(commit=False)
            # porque después el objeto puede tener valores modificados
            cantidad_nueva_raw = form.cleaned_data.get('cantidad')
            cantidad_nueva = int(cantidad_nueva_raw) if cantidad_nueva_raw is not None else 0
            
            # Debug inmediato
            import logging
            logger = logging.getLogger('ventas')
            logger.info(f'[EDITAR PRODUCTO] ANTES DE GUARDAR - Producto ID: {producto.id}, Cantidad Anterior (BD): {cantidad_anterior}, Cantidad Nueva (Form): {cantidad_nueva}')
            
            nutri = nutricional_form.save()  # crea/actualiza nutricional
            form.instance.nutricional = nutri
            producto_guardado = form.save(commit=False)  # NO guardar aún, necesitamos restaurar el historial primero
            
            # Verificar que la cantidad del objeto guardado coincide con la del formulario
            cantidad_guardada = int(producto_guardado.cantidad) if producto_guardado.cantidad is not None else 0
            logger.info(f'[EDITAR PRODUCTO] DESPUÉS DE save(commit=False) - Cantidad en objeto guardado: {cantidad_guardada}')
            
            # Asegurar que usamos la cantidad del formulario (más confiable)
            if cantidad_guardada != cantidad_nueva:
                logger.warning(f'[EDITAR PRODUCTO] ⚠️ Discrepancia: Form={cantidad_nueva}, Objeto={cantidad_guardada}, usando Form')
                cantidad_nueva = cantidad_guardada  # Usar la del objeto por si acaso
            
            # RESTAURAR SIEMPRE el historial de merma si existía (independientemente del estado)
            # Esto asegura que el historial se mantenga incluso si el producto ya está activo
            if motivo_merma_anterior is not None:
                producto_guardado.motivo_merma = motivo_merma_anterior
            if fecha_merma_anterior is not None:
                producto_guardado.fecha_merma = fecha_merma_anterior
            if cantidad_merma_anterior is not None:
                producto_guardado.cantidad_merma = cantidad_merma_anterior
            
            # LÓGICA DE REABASTECIMIENTO: Si el producto estaba en merma y ahora tiene stock y caducidad
            # entonces reactivarlo automáticamente, pero MANTENER el historial de merma
            if estado_merma_anterior == 'en_merma':
                caducidad = form.cleaned_data.get('caducidad')
                
                # Si tiene cantidad > 0 y caducidad, reactivar el producto (pero mantener historial)
                if cantidad_nueva > 0 and caducidad:
                    producto_guardado.estado_merma = 'activo'  # Reactivar producto
                    # El historial ya fue restaurado arriba
                    producto_guardado.save()
                    messages.success(request, 'Producto reabastecido y reactivado. El historial de merma se mantiene.')
                else:
                    producto_guardado.save()  # Guardar con historial restaurado
                    messages.success(request, 'Producto actualizado exitosamente.')
            else:
                # Producto ya estaba activo, solo guardar con historial preservado
                producto_guardado.save()  # Guardar con historial restaurado
                messages.success(request, 'Producto actualizado exitosamente.')
            
            # CREAR MOVIMIENTO DE INVENTARIO si la cantidad cambió
            # IMPORTANTE: Esto debe hacerse DESPUÉS de guardar el producto para tener el ID correcto
            diferencia_cantidad = cantidad_nueva - cantidad_anterior
            
            # Debug: verificar valores finales
            logger.info(f'[EDITAR PRODUCTO] CÁLCULO FINAL - Anterior: {cantidad_anterior}, Nueva: {cantidad_nueva}, Diferencia: {diferencia_cantidad}')
            
            if diferencia_cantidad != 0:
                logger.info(f'[EDITAR PRODUCTO] ✅ Diferencia detectada: {diferencia_cantidad}, procediendo a crear movimiento...')
                try:
                    # Asegurarse de que el producto esté guardado antes de crear el movimiento
                    if not producto_guardado.pk:
                        producto_guardado.save()
                        logger.info(f'[EDITAR PRODUCTO] Producto guardado con ID: {producto_guardado.id}')
                    
                    if diferencia_cantidad > 0:
                        # Aumentó la cantidad = ENTRADA
                        # Crear un lote nuevo para mantener trazabilidad
                        from ventas.models import Lote
                        from django.utils import timezone
                        from datetime import timedelta, date
                        from decimal import Decimal
                        
                        # Usar fecha de caducidad del producto o fecha por defecto
                        fecha_caducidad_lote = producto_guardado.caducidad if producto_guardado.caducidad else (date.today() + timedelta(days=30))
                        
                        # Generar número de lote automático
                        numero_lote = f"EDIT-{producto_guardado.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                        
                        # Crear lote para la edición
                        lote_edicion = Lote.objects.create(
                            productos=producto_guardado,
                            numero_lote=numero_lote,
                            cantidad=Decimal(str(abs(diferencia_cantidad))),
                            cantidad_inicial=Decimal(str(abs(diferencia_cantidad))),
                            fecha_elaboracion=date.today(),
                            fecha_caducidad=fecha_caducidad_lote,
                            fecha_recepcion=timezone.now(),
                            origen='ajuste_manual',
                            estado='activo'
                        )
                        
                        # Actualizar cantidad del producto desde lotes
                        producto_guardado.cantidad = producto_guardado.calcular_cantidad_desde_lotes() if hasattr(producto_guardado, 'calcular_cantidad_desde_lotes') else producto_guardado.cantidad
                        
                        # Actualizar fecha de caducidad del producto con la del lote más antiguo
                        lote_mas_antiguo = Lote.objects.filter(
                            productos=producto_guardado,
                            estado='activo',
                            cantidad__gt=0
                        ).order_by('fecha_caducidad', 'fecha_recepcion').first()
                        
                        if lote_mas_antiguo and lote_mas_antiguo.fecha_caducidad:
                            producto_guardado.caducidad = lote_mas_antiguo.fecha_caducidad
                        
                        producto_guardado.save(update_fields=['cantidad', 'caducidad'])
                        
                        # Crear movimiento de inventario
                        movimiento = MovimientosInventario.objects.create(
                            tipo_movimiento='entrada',
                            cantidad=abs(diferencia_cantidad),
                            productos=producto_guardado,
                            origen='edicion_manual',
                            referencia_id=lote_edicion.id,
                            tipo_referencia='lote'
                        )
                        logger.info(f'[EDITAR PRODUCTO] ✅ Lote y movimiento ENTRADA creados: Lote ID={lote_edicion.id}, Movimiento ID={movimiento.id}, Cantidad={abs(diferencia_cantidad)}, Producto={producto_guardado.id}')
                        unidad = producto_guardado.get_unidad_stock_display()
                        messages.info(request, f'Se registró una entrada de {abs(diferencia_cantidad)} {unidad} en el inventario. Se creó un nuevo lote para mantener la trazabilidad.')
                    else:
                        # Disminuyó la cantidad = SALIDA
                        movimiento = MovimientosInventario.objects.create(
                            tipo_movimiento='salida',
                            cantidad=abs(diferencia_cantidad),
                            productos=producto_guardado,
                            origen='edicion_manual',
                            referencia_id=producto_guardado.id,
                            tipo_referencia='edicion_producto'
                        )
                        logger.info(f'[EDITAR PRODUCTO] ✅ Movimiento SALIDA creado: ID={movimiento.id}, Cantidad={abs(diferencia_cantidad)}, Producto={producto_guardado.id}')
                        unidad = producto_guardado.get_unidad_stock_display()
                        messages.info(request, f'Se registró una salida de {abs(diferencia_cantidad)} {unidad} en el inventario.')
                except Exception as e:
                    # Si falla la creación del movimiento, registrar pero no fallar la edición
                    logger.error(f'[EDITAR PRODUCTO] ❌ Error al crear movimiento: {str(e)}', exc_info=True)
                    import traceback
                    logger.error(f'[EDITAR PRODUCTO] Traceback completo: {traceback.format_exc()}')
                    messages.warning(request, f'Producto actualizado, pero no se pudo registrar el movimiento de inventario. Error: {str(e)}')
            else:
                logger.info(f'[EDITAR PRODUCTO] ⚠️ No se creó movimiento porque la cantidad no cambió (anterior={cantidad_anterior}, nueva={cantidad_nueva}, diferencia={diferencia_cantidad})')
            
            return render(request, 'editar_producto.html', {
                'form': form, 'nutricional_form': nutricional_form, 'producto': producto_guardado
            })
        messages.error(request, 'Corrige los campos marcados e inténtalo de nuevo.')
    else:
        form = ProductoForm(instance=producto)
        nutricional_form = NutricionalForm(instance=nutri_inst)

    return render(request, 'editar_producto.html', {
        'form': form, 'nutricional_form': nutricional_form, 'producto': producto
    })

def eliminar_producto_view(request, producto_id):
    """
    Desactiva un producto (no lo elimina físicamente).
    Cambia el estado_merma a 'inactivo' en vez de usar eliminado.
    """
    producto = get_object_or_404(Productos, pk=producto_id, eliminado__isnull=True)
    if request.method == 'POST':
        # Desactivar producto cambiando estado_merma a 'inactivo'
        producto.estado_merma = 'inactivo'
        producto.save(update_fields=['estado_merma'])
        messages.success(request, f'Producto "{producto.nombre}" desactivado correctamente. Puede reactivarlo desde el inventario.')
        return redirect('inventario')
    return render(request, 'confirmar_eliminar.html', {'producto': producto})

@login_required
def reactivar_producto_view(request, producto_id):
    """
    Reactiva un producto que estaba inactivo.
    Cambia el estado_merma de 'inactivo' a 'activo'.
    """
    producto = get_object_or_404(Productos, pk=producto_id, eliminado__isnull=True)
    if request.method == 'POST':
        if producto.estado_merma == 'inactivo':
            producto.estado_merma = 'activo'
            producto.save(update_fields=['estado_merma'])
            messages.success(request, f'Producto "{producto.nombre}" reactivado correctamente.')
        else:
            messages.info(request, f'El producto "{producto.nombre}" no está inactivo.')
        return redirect('inventario')
    return render(request, 'confirmar_reactivar.html', {'producto': producto})

def agregar_producto_view(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Producto agregado exitosamente!')
            messages.info(request, 'Puedes completar la información nutricional y la categoría desde Inventario.')
            # Mantener en la misma página para seguir agregando
            form = ProductoForm()
            return render(request, 'agregar_producto.html', {'form': form})
        else:
            messages.error(request, 'Por favor corrige los campos marcados y vuelve a intentar.')
    else:
        form = ProductoForm()
    
    return render(request, 'agregar_producto.html', {'form': form})

@login_required
def detalle_producto_view(request, producto_id):
    """
    Muestra el detalle completo de un producto, incluyendo:
    - Información básica del producto
    - Información nutricional
    - Movimientos recientes de inventario
    - Historial de ventas
    - Alertas relacionadas
    """
    producto = get_object_or_404(Productos, pk=producto_id, eliminado__isnull=True)
    
    # Obtener información nutricional
    nutricional = producto.nutricional
    
    # Obtener TODOS los movimientos para cálculos precisos
    todos_los_movimientos = MovimientosInventario.objects.filter(
        productos=producto
    ).order_by('-fecha')
    
    # Obtener movimientos recientes (últimos 10) para mostrar en la tabla
    movimientos = todos_los_movimientos[:10]
    
    # Contar total de movimientos
    total_movimientos = todos_los_movimientos.count()
    total_entradas_count = todos_los_movimientos.filter(tipo_movimiento='entrada').count()
    total_salidas_count = todos_los_movimientos.filter(tipo_movimiento='salida').count()
    
    # Obtener ventas recientes (últimos 10) y calcular subtotales
    ventas_recientes_raw = DetalleVenta.objects.filter(
        productos=producto
    ).select_related('ventas', 'ventas__clientes').order_by('-ventas__fecha')[:10]
    
    # Agregar subtotal calculado a cada detalle
    ventas_recientes = []
    for detalle in ventas_recientes_raw:
        detalle.subtotal = detalle.cantidad * detalle.precio_unitario
        ventas_recientes.append(detalle)
    
    # Calcular estadísticas de ventas
    detalles_ventas = DetalleVenta.objects.filter(productos=producto)
    total_cantidad_vendida = detalles_ventas.aggregate(total=Sum('cantidad'))['total'] or 0
    total_ingresos = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles_ventas)
    
    # Obtener alertas relacionadas
    alertas = Alertas.objects.filter(
        productos=producto,
        estado='activa'
    ).order_by('-fecha_generada')[:5]
    
    # Calcular estadísticas de movimientos (usando todos los movimientos, no solo los recientes)
    # IMPORTANTE: Usar aggregate con Sum para obtener el total correcto
    entradas = todos_los_movimientos.filter(
        tipo_movimiento='entrada'
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    salidas = todos_los_movimientos.filter(
        tipo_movimiento='salida'
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Calcular suma manual de movimientos recientes para comparación
    suma_entradas_recientes = sum(m.cantidad for m in movimientos if m.tipo_movimiento == 'entrada')
    suma_salidas_recientes = sum(m.cantidad for m in movimientos if m.tipo_movimiento == 'salida')
    
    # Obtener lotes del producto (si existen)
    try:
        from ventas.models import Lote
        lotes = Lote.objects.filter(productos=producto).order_by('fecha_caducidad', 'fecha_recepcion')
        cantidad_desde_lotes = producto.calcular_cantidad_desde_lotes()
        
        # Calcular días hasta vencer para cada lote (para mostrar en template)
        for lote in lotes:
            dias = lote.dias_hasta_vencer()
            lote.dias_hasta_vencer_abs = abs(dias) if dias is not None and dias < 0 else dias
    except Exception:
        lotes = []
        cantidad_desde_lotes = producto.cantidad or 0
    
    context = {
        'producto': producto,
        'nutricional': nutricional,
        'movimientos': movimientos,
        'ventas_recientes': ventas_recientes,
        'alertas': alertas,
        'total_ventas_cantidad': total_cantidad_vendida,
        'total_ingresos': total_ingresos,
        'entradas_totales': entradas,
        'salidas_totales': salidas,
        'cantidad_desde_lotes': cantidad_desde_lotes,
        'lotes': lotes,
        # Información adicional para depuración
        'total_movimientos': total_movimientos,
        'total_entradas_count': total_entradas_count,
        'total_salidas_count': total_salidas_count,
        'suma_entradas_recientes': suma_entradas_recientes,
        'suma_salidas_recientes': suma_salidas_recientes,
    }
    
    return render(request, 'detalle_producto.html', context)


@login_required
@require_POST
def cambiar_estado_producto_ajax(request, producto_id):
    """
    Cambia el estado de un producto individual (activo/inactivo).
    
    Args:
        request: HttpRequest con JSON body conteniendo {'estado': 'activo' o 'inactivo'}
        producto_id: ID del producto a modificar
    
    Returns:
        JsonResponse con el resultado de la operación
    """
    try:
        producto = get_object_or_404(Productos, pk=producto_id, eliminado__isnull=True)
        
        # Parsear el JSON del body de la petición
        data = json.loads(request.body)
        nuevo_estado = data.get('estado', '').strip()
        
        # Validar el estado
        if nuevo_estado not in ['activo', 'inactivo']:
            return JsonResponse({
                'success': False,
                'message': 'Estado inválido. Debe ser "activo" o "inactivo".'
            }, status=400)
        
        # Cambiar el estado
        producto.estado_merma = nuevo_estado
        producto.save()
        
        # Mensaje según el cambio
        if nuevo_estado == 'activo':
            mensaje = f'Producto "{producto.nombre}" activado exitosamente. Ahora está disponible para venta.'
        else:
            mensaje = f'Producto "{producto.nombre}" desactivado exitosamente. Ya no está disponible para venta.'
        
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
            'message': f'Error al cambiar el estado del producto: {str(e)}'
        }, status=500)


@login_required
def eliminar_registro_merma_view(request, producto_id):
    """
    Desactiva el registro de merma de un producto (no lo elimina).
    Cambia el estado de activo a inactivo en HistorialMerma.
    Si la tabla HistorialMerma no existe, limpia los campos del producto directamente.
    """
    import logging
    logger = logging.getLogger('ventas')
    
    producto = get_object_or_404(Productos, pk=producto_id)
    
    if request.method == 'POST':
        try:
            # Intentar usar HistorialMerma si la tabla existe
            from ventas.models import HistorialMerma
            
            # Obtener registros activos de merma para este producto
            registros_activos = HistorialMerma.objects.filter(
                producto=producto,
                activo=True
            )
            
            if registros_activos.exists():
                # Desactivar todos los registros activos (no eliminar)
                cantidad_desactivados = registros_activos.update(activo=False)
                
                # Si el producto está en merma, cambiar estado a activo para que no aparezca en la lista de merma
                # PERO NO restaurar la cantidad (debe permanecer en 0)
                # Mantener los campos motivo_merma, fecha_merma, cantidad_merma para historial
                if producto.estado_merma == 'en_merma':
                    producto.estado_merma = 'activo'
                    # NO restaurar cantidad - debe permanecer en 0
                    # El producto quedará activo pero con cantidad 0, listo para reabastecer
                    producto.save(update_fields=['estado_merma'])
                
                messages.success(
                    request, 
                    f'Se desactivaron {cantidad_desactivados} registro(s) de merma para "{producto.nombre}". '
                    f'El producto ha sido reactivado y ya no aparece en la lista de merma. '
                    f'Los datos históricos se mantienen en la base de datos para reportes.'
                )
            else:
                # Si no hay registros en HistorialMerma pero el producto está en merma, solo cambiar estado
                # Mantener los campos históricos (motivo_merma, fecha_merma, cantidad_merma)
                if producto.estado_merma == 'en_merma':
                    producto.estado_merma = 'activo'
                    producto.save(update_fields=['estado_merma'])
                    messages.success(
                        request, 
                        f'Producto reactivado para "{producto.nombre}". '
                        f'Los datos históricos de merma se mantienen en la base de datos.'
                    )
                else:
                    messages.info(request, f'El producto "{producto.nombre}" no tiene registros activos de merma.')
        
        except Exception as e:
            # Si HistorialMerma no existe o hay error, limpiar campos del producto directamente
            logger.warning(f'No se pudo usar HistorialMerma (tabla puede no existir): {str(e)}')
            
            # Solo cambiar estado del producto (mantener campos históricos)
            if producto.estado_merma == 'en_merma':
                producto.estado_merma = 'activo'
                producto.save(update_fields=['estado_merma'])
                messages.success(
                    request, 
                    f'Producto reactivado para "{producto.nombre}". '
                    f'Los datos históricos de merma se mantienen en la base de datos. '
                    f'Nota: Ejecuta el script SQL para habilitar el historial completo de merma.'
                )
            else:
                messages.info(request, f'El producto "{producto.nombre}" no tiene registros activos de merma.')
        
        # Redirigir a la lista de merma (no al detalle del producto)
        return redirect('merma_list')
    
    # GET: Mostrar confirmación
    try:
        from ventas.models import HistorialMerma
        registros_activos = HistorialMerma.objects.filter(producto=producto, activo=True).count()
    except Exception:
        # Si la tabla no existe, verificar campos del producto
        registros_activos = 1 if (producto.motivo_merma or producto.fecha_merma or (producto.cantidad_merma and producto.cantidad_merma > 0)) else 0
    
    return render(request, 'eliminar_registro_merma.html', {
        'producto': producto,
        'registros_activos': registros_activos
    })