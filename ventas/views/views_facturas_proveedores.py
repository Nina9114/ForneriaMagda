# ================================================================
# =                                                              =
# =        VISTAS PARA FACTURAS DE PROVEEDORES                 =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas para gestionar facturas de
# proveedores en el sistema.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from ventas.models.proveedores import Proveedor, FacturaProveedor, DetalleFacturaProveedor, PagoProveedor
from ventas.models.productos import Productos
from ventas.models.movimientos import MovimientosInventario
import logging

logger = logging.getLogger('ventas')


# ================================================================
# =                VISTAS DE FACTURAS DE PROVEEDORES            =
# ================================================================

@login_required
def facturas_proveedores_list_view(request):
    """
    Vista para listar todas las facturas de proveedores.
    
    Permite:
    - Ver todas las facturas
    - Buscar por número de factura, proveedor
    - Filtrar por estado de pago, estado de recepción
    - Filtrar por rango de fechas
    """
    # Obtener parámetros de búsqueda
    q = request.GET.get('q', '').strip()
    estado_pago_filter = request.GET.get('estado_pago', '')
    estado_recepcion_filter = request.GET.get('estado_recepcion', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Obtener facturas (solo no eliminadas)
    facturas = FacturaProveedor.objects.filter(eliminado__isnull=True).select_related('proveedor')
    
    # Aplicar filtros
    if q:
        facturas = facturas.filter(
            Q(numero_factura__icontains=q) |
            Q(proveedor__nombre__icontains=q) |
            Q(observaciones__icontains=q)
        )
    
    if estado_pago_filter:
        facturas = facturas.filter(estado_pago=estado_pago_filter)
    
    # Usar fecha_recepcion para determinar si está recibida
    if estado_recepcion_filter == 'recibida':
        facturas = facturas.filter(fecha_recepcion__isnull=False)
    elif estado_recepcion_filter == 'pendiente':
        facturas = facturas.filter(fecha_recepcion__isnull=True)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            facturas = facturas.filter(fecha_factura__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            facturas = facturas.filter(fecha_factura__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha descendente (más recientes primero)
    facturas = facturas.order_by('-fecha_factura', '-id')
    
    # Calcular totales
    total_facturas = facturas.count()
    total_monto = facturas.aggregate(Sum('total_con_iva'))['total_con_iva__sum'] or Decimal('0.00')
    facturas_pendientes = facturas.filter(estado_pago='pendiente').count()
    monto_pendiente = facturas.filter(estado_pago='pendiente').aggregate(Sum('total_con_iva'))['total_con_iva__sum'] or Decimal('0.00')
    
    contexto = {
        'facturas': facturas,
        'q': q,
        'estado_pago_filter': estado_pago_filter,
        'estado_recepcion_filter': estado_recepcion_filter,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_facturas': total_facturas,
        'total_monto': total_monto,
        'facturas_pendientes': facturas_pendientes,
        'monto_pendiente': monto_pendiente,
    }
    
    return render(request, 'facturas_proveedores_list.html', contexto)


@login_required
def factura_proveedor_crear_view(request):
    """
    Vista para crear una nueva factura de proveedor.
    """
    proveedores = Proveedor.objects.filter(eliminado__isnull=True, estado='activo').order_by('nombre')
    # Solo productos activos (excluye inactivos y en_merma)
    productos = Productos.objects.filter(eliminado__isnull=True, estado_merma='activo').order_by('nombre')
    
    if request.method == 'POST':
        try:
            # Obtener datos básicos de la factura
            proveedor_id = request.POST.get('proveedor_id')
            numero_factura = request.POST.get('numero_factura', '').strip()
            fecha_factura_str = request.POST.get('fecha_factura', '')
            fecha_vencimiento_str = request.POST.get('fecha_vencimiento', '') or None
            fecha_recepcion_str = request.POST.get('fecha_recepcion', '') or None
            estado_pago = request.POST.get('estado_pago', 'pendiente')
            # estado_recepcion ya no existe, se determina por fecha_recepcion
            # Si fecha_recepcion tiene valor, está recibida; si es NULL, está pendiente
            subtotal_sin_iva = Decimal(request.POST.get('subtotal_sin_iva', '0.00'))
            total_iva = Decimal(request.POST.get('total_iva', '0.00'))
            descuento = Decimal(request.POST.get('descuento', '0.00'))
            total_con_iva = Decimal(request.POST.get('total_con_iva', '0.00'))
            observaciones = request.POST.get('observaciones', '').strip() or None
            
            # Validaciones básicas
            if not proveedor_id:
                messages.error(request, 'Debe seleccionar un proveedor.')
                return render(request, 'factura_proveedor_form.html', {
                    'modo': 'crear',
                    'proveedores': proveedores,
                    'productos': productos,
                    'factura': None
                })
            
            if not numero_factura:
                messages.error(request, 'El número de factura es obligatorio.')
                return render(request, 'factura_proveedor_form.html', {
                    'modo': 'crear',
                    'proveedores': proveedores,
                    'productos': productos,
                    'factura': None
                })
            
            if not fecha_factura_str:
                messages.error(request, 'La fecha de factura es obligatoria.')
                return render(request, 'factura_proveedor_form.html', {
                    'modo': 'crear',
                    'proveedores': proveedores,
                    'productos': productos,
                    'factura': None
                })
            
            # Convertir fechas
            fecha_factura = datetime.strptime(fecha_factura_str, '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date() if fecha_vencimiento_str else None
            fecha_recepcion = datetime.strptime(fecha_recepcion_str, '%Y-%m-%d').date() if fecha_recepcion_str else None
            
            # Obtener proveedor
            proveedor = get_object_or_404(Proveedor, pk=proveedor_id, eliminado__isnull=True)
            
            # Crear la factura
            factura = FacturaProveedor.objects.create(
                proveedor=proveedor,
                numero_factura=numero_factura,
                fecha_factura=fecha_factura,
                fecha_vencimiento=fecha_vencimiento,
                fecha_recepcion=fecha_recepcion,
                estado_pago=estado_pago,
                subtotal_sin_iva=subtotal_sin_iva,
                total_iva=total_iva,
                descuento=descuento,
                total_con_iva=total_con_iva,
                observaciones=observaciones
            )
            
            # Procesar detalles de la factura (productos)
            # Los detalles se procesarán mediante AJAX o en una segunda vista
            
            messages.success(request, f'Factura "{factura.numero_factura}" creada exitosamente.')
            logger.info(f'Factura creada: {factura.id} - {factura.numero_factura}')
            return redirect('factura_proveedor_detalle', factura_id=factura.id)
            
        except ValueError as e:
            logger.error(f'Error de validación al crear factura: {str(e)}', exc_info=True)
            messages.error(request, f'Error en los datos: {str(e)}')
            return render(request, 'factura_proveedor_form.html', {
                'modo': 'crear',
                'proveedores': proveedores,
                'productos': productos,
                'factura': None
            })
        except Exception as e:
            logger.error(f'Error al crear factura: {str(e)}', exc_info=True)
            messages.error(request, f'Error al crear la factura: {str(e)}')
            return render(request, 'factura_proveedor_form.html', {
                'modo': 'crear',
                'proveedores': proveedores,
                'productos': productos,
                'factura': None
            })
    
    # GET: Mostrar formulario vacío
    return render(request, 'factura_proveedor_form.html', {
        'modo': 'crear',
        'proveedores': proveedores,
        'productos': productos,
        'factura': None
    })


@login_required
def factura_proveedor_detalle_view(request, factura_id):
    """
    Vista para ver el detalle completo de una factura de proveedor.
    """
    factura = get_object_or_404(
        FacturaProveedor.objects.select_related('proveedor'),
        pk=factura_id,
        eliminado__isnull=True
    )
    
    # Obtener detalles de la factura
    detalles = DetalleFacturaProveedor.objects.filter(
        factura_proveedor=factura
    ).select_related('productos').order_by('id')
    
    # Obtener productos disponibles para agregar (solo si no está recibida)
    # IMPORTANTE: Siempre pasar productos, incluso si está recibida (para evitar errores en template)
    productos = Productos.objects.filter(
        eliminado__isnull=True,
        estado_merma='activo'
    ).order_by('nombre')
    
    # Obtener pagos de la factura
    pagos = PagoProveedor.objects.filter(
        factura_proveedor=factura
    ).order_by('-fecha_pago', '-id')
    
    # Calcular totales de pagos
    total_pagado = sum(pago.monto for pago in pagos)
    saldo_pendiente = factura.total_con_iva - total_pagado
    
    contexto = {
        'factura': factura,
        'detalles': detalles,
        'productos': productos,
        'pagos': pagos,
        'total_pagado': total_pagado,
        'saldo_pendiente': saldo_pendiente,
    }
    
    return render(request, 'factura_proveedor_detalle.html', contexto)


@login_required
def factura_proveedor_editar_view(request, factura_id):
    """
    Vista para editar una factura de proveedor existente.
    """
    factura = get_object_or_404(
        FacturaProveedor.objects.select_related('proveedor'),
        pk=factura_id,
        eliminado__isnull=True
    )
    
    proveedores = Proveedor.objects.filter(eliminado__isnull=True, estado='activo').order_by('nombre')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            factura.numero_factura = request.POST.get('numero_factura', '').strip()
            fecha_factura_str = request.POST.get('fecha_factura', '')
            fecha_vencimiento_str = request.POST.get('fecha_vencimiento', '') or None
            fecha_recepcion_str = request.POST.get('fecha_recepcion', '') or None
            factura.estado_pago = request.POST.get('estado_pago', 'pendiente')
            # estado_recepcion eliminado - se determina por fecha_recepcion
            # Obtener totales del formulario (si están vacíos, mantener los valores existentes)
            subtotal_sin_iva_str = request.POST.get('subtotal_sin_iva', '').strip()
            total_iva_str = request.POST.get('total_iva', '').strip()
            total_con_iva_str = request.POST.get('total_con_iva', '').strip()
            descuento_str = request.POST.get('descuento', '0.00').strip()
            
            # Si los campos tienen valor, actualizarlos; si están vacíos, mantener los valores existentes
            # Esto evita que se borren los totales cuando el usuario solo edita otros campos
            if subtotal_sin_iva_str:
                factura.subtotal_sin_iva = Decimal(subtotal_sin_iva_str)
            # Si está vacío, mantener el valor existente (no cambiar)
            
            if total_iva_str:
                factura.total_iva = Decimal(total_iva_str)
            # Si está vacío, mantener el valor existente (no cambiar)
            
            if total_con_iva_str:
                factura.total_con_iva = Decimal(total_con_iva_str)
            # Si está vacío, mantener el valor existente (no cambiar)
            
            if descuento_str:
                factura.descuento = Decimal(descuento_str)
            # Si descuento está vacío, mantener el valor existente o usar 0.00
            elif not factura.descuento:
                factura.descuento = Decimal('0.00')
            # Si ya tiene valor, mantenerlo
            
            factura.observaciones = request.POST.get('observaciones', '').strip() or None
            
            # Convertir fechas
            if fecha_factura_str:
                factura.fecha_factura = datetime.strptime(fecha_factura_str, '%Y-%m-%d').date()
            if fecha_vencimiento_str:
                factura.fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
            else:
                factura.fecha_vencimiento = None
            
            # Permitir quitar la fecha de recepción (dejarla vacía)
            if fecha_recepcion_str:
                factura.fecha_recepcion = datetime.strptime(fecha_recepcion_str, '%Y-%m-%d').date()
            else:
                factura.fecha_recepcion = None  # Quitar fecha de recepción si se deja vacía
            
            factura.save()
            
            messages.success(request, f'Factura "{factura.numero_factura}" actualizada exitosamente.')
            logger.info(f'Factura actualizada: {factura.id} - {factura.numero_factura}')
            return redirect('factura_proveedor_detalle', factura_id=factura.id)
            
        except Exception as e:
            logger.error(f'Error al actualizar factura: {str(e)}', exc_info=True)
            messages.error(request, f'Error al actualizar la factura: {str(e)}')
            return render(request, 'factura_proveedor_form.html', {
                'modo': 'editar',
                'proveedores': proveedores,
                'factura': factura
            })
    
    # GET: Mostrar formulario con datos de la factura
    return render(request, 'factura_proveedor_form.html', {
        'modo': 'editar',
        'proveedores': proveedores,
        'factura': factura
    })


@login_required
def factura_proveedor_eliminar_view(request, factura_id):
    """
    Vista para eliminar (borrado lógico) una factura de proveedor.
    """
    factura = get_object_or_404(FacturaProveedor, pk=factura_id, eliminado__isnull=True)
    
    if request.method == 'POST':
        try:
            factura.eliminado = timezone.now()
            factura.save()
            
            messages.success(request, f'Factura "{factura.numero_factura}" eliminada exitosamente.')
            logger.info(f'Factura eliminada: {factura.id} - {factura.numero_factura}')
            return redirect('facturas_proveedores_list')
            
        except Exception as e:
            logger.error(f'Error al eliminar factura: {str(e)}', exc_info=True)
            messages.error(request, f'Error al eliminar la factura: {str(e)}')
            return redirect('facturas_proveedores_list')
    
    # GET: Mostrar confirmación
    return render(request, 'factura_proveedor_eliminar.html', {
        'factura': factura
    })

