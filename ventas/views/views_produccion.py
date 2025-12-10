# ================================================================
# =                                                              =
# =           VISTAS PARA MÓDULO DE PRODUCCIÓN                 =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas para gestionar la producción
# propia de la Fornería (pan, pasteles, etc.)
#
# VISTAS INCLUIDAS:
# 1. produccion_list_view: Lista de lotes de producción propia
# 2. produccion_crear_view: Formulario para registrar nueva producción
# 3. produccion_detalle_view: Detalle de un lote específico

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.utils import timezone
from ventas.models import Lote, Productos, MovimientosInventario
from ventas.funciones.formularios_lotes import LoteProduccionForm
from datetime import date, timedelta


# ================================================================
# =              VISTA: LISTADO DE PRODUCCIÓN                    =
# ================================================================

@login_required
def produccion_list_view(request):
    """
    Muestra el listado de lotes de producción propia.
    
    Permite filtrar por:
    - Producto
    - Estado (activo, agotado, vencido)
    - Rango de fechas
    """
    # Obtener parámetros de filtro
    producto_id = request.GET.get('producto_id')
    estado = request.GET.get('estado', 'activo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    buscar = request.GET.get('buscar', '').strip()
    
    # Obtener lotes - SOLO producción propia
    # Si se filtra por producto_id, mostrar solo lotes de producción propia de ese producto
    # Si no hay filtro de producto, mostrar todos los lotes de producción propia
    if producto_id:
        lotes = Lote.objects.filter(
            productos_id=producto_id,
            origen='produccion_propia'  # Solo producción propia
        )
    else:
        # Solo lotes de producción propia
        lotes = Lote.objects.filter(origen='produccion_propia')
    
    # Aplicar otros filtros
    
    if estado and estado != 'todos':
        lotes = lotes.filter(estado=estado)
    
    if fecha_desde:
        try:
            fecha_desde_obj = date.fromisoformat(fecha_desde)
            lotes = lotes.filter(fecha_recepcion__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = date.fromisoformat(fecha_hasta)
            lotes = lotes.filter(fecha_recepcion__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    if buscar:
        lotes = lotes.filter(
            Q(productos__nombre__icontains=buscar) |
            Q(numero_lote__icontains=buscar)
        )
    
    # Ordenar por fecha de caducidad (más antiguos primero - FIFO)
    lotes = lotes.select_related('productos').order_by('fecha_caducidad', 'fecha_recepcion')
    
    # Calcular días hasta vencer para cada lote (para mostrar en template)
    # Convertir a lista para poder agregar atributos
    lotes_lista = list(lotes)
    for lote in lotes_lista:
        dias = lote.dias_hasta_vencer()
        lote.dias_hasta_vencer_abs = abs(dias) if dias is not None and dias < 0 else dias
    
    # Obtener productos para el filtro
    # Solo mostrar productos que tienen al menos un lote de producción propia
    # Esto evita mostrar productos que solo son comprados a proveedores
    productos = Productos.objects.filter(
        eliminado__isnull=True,
        lotes__origen='produccion_propia'  # Solo productos con lotes de producción propia (usar 'lotes' plural)
    ).distinct().order_by('nombre')
    
    # Estadísticas (usar el QuerySet original antes de convertirlo a lista)
    # Aplicar la misma lógica de filtrado que para los lotes mostrados
    # Solo producción propia
    if producto_id:
        lotes_qs = Lote.objects.filter(
            productos_id=producto_id,
            origen='produccion_propia'
        )
    else:
        lotes_qs = Lote.objects.filter(origen='produccion_propia')
    
    # Aplicar otros filtros a las estadísticas
    if estado and estado != 'todos':
        lotes_qs = lotes_qs.filter(estado=estado)
    if fecha_desde:
        try:
            fecha_desde_obj = date.fromisoformat(fecha_desde)
            lotes_qs = lotes_qs.filter(fecha_recepcion__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    if fecha_hasta:
        try:
            fecha_hasta_obj = date.fromisoformat(fecha_hasta)
            lotes_qs = lotes_qs.filter(fecha_recepcion__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    if buscar:
        lotes_qs = lotes_qs.filter(
            Q(productos__nombre__icontains=buscar) |
            Q(numero_lote__icontains=buscar)
        )
    
    total_lotes = lotes_qs.count()
    lotes_activos = lotes_qs.filter(estado='activo').count()
    lotes_vencidos = lotes_qs.filter(estado='vencido').count()
    total_cantidad = lotes_qs.filter(estado='activo').aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    
    context = {
        'lotes': lotes_lista,
        'productos': productos,
        'producto_id': producto_id,
        'estado': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'buscar': buscar,
        'total_lotes': total_lotes,
        'lotes_activos': lotes_activos,
        'lotes_vencidos': lotes_vencidos,
        'total_cantidad': total_cantidad,
    }
    
    return render(request, 'produccion_list.html', context)


# ================================================================
# =              VISTA: CREAR LOTE DE PRODUCCIÓN                 =
# ================================================================

@login_required
def produccion_crear_view(request):
    """
    Formulario para registrar un nuevo lote de producción propia.
    """
    if request.method == 'POST':
        form = LoteProduccionForm(request.POST)
        if form.is_valid():
            # El formulario ya actualiza el producto y crea el movimiento en su método save()
            lote = form.save()
            
            messages.success(
                request,
                f'Lote de producción registrado exitosamente. '
                f'Se agregaron {lote.cantidad} unidad(es) de {lote.productos.nombre} al inventario.'
            )
            return redirect('produccion_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = LoteProduccionForm()
    
    # Obtener productos para mostrar en el selector (con sus unidades para el JavaScript)
    productos = Productos.objects.filter(
        eliminado__isnull=True,
        estado_merma='activo'  # Solo productos activos
    ).order_by('nombre')
    
    context = {
        'form': form,
        'productos': productos,
    }
    
    return render(request, 'produccion_crear.html', context)


# ================================================================
# =              VISTA: DETALLE DE LOTE                          =
# ================================================================

@login_required
def produccion_detalle_view(request, lote_id):
    """
    Muestra el detalle de un lote específico.
    """
    lote = get_object_or_404(Lote, pk=lote_id)
    
    # Obtener movimientos relacionados con este lote
    movimientos = MovimientosInventario.objects.filter(
        productos=lote.productos,
        tipo_referencia='lote',
        referencia_id=lote.id
    ).order_by('-fecha')[:10]
    
    # Calcular estadísticas
    dias_hasta_vencer = lote.dias_hasta_vencer()
    dias_hasta_vencer_abs = abs(dias_hasta_vencer) if dias_hasta_vencer is not None else None
    porcentaje_consumido = ((lote.cantidad_inicial - lote.cantidad) / lote.cantidad_inicial * 100) if lote.cantidad_inicial > 0 else 0
    
    context = {
        'lote': lote,
        'movimientos': movimientos,
        'dias_hasta_vencer': dias_hasta_vencer,
        'dias_hasta_vencer_abs': dias_hasta_vencer_abs,
        'porcentaje_consumido': porcentaje_consumido,
    }
    
    return render(request, 'produccion_detalle.html', context)

