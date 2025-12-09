# ================================================================
# =                                                              =
# =        VISTAS PARA PAGOS A PROVEEDORES                     =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas para gestionar pagos a proveedores.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime
from ventas.models.proveedores import FacturaProveedor, PagoProveedor, Proveedor
import logging

logger = logging.getLogger('ventas')


@login_required
def pagos_proveedores_list_view(request):
    """
    Vista para listar todos los pagos realizados a proveedores.
    """
    # Obtener parámetros de búsqueda
    q = request.GET.get('q', '').strip()
    factura_id = request.GET.get('factura_id', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Obtener pagos
    pagos = PagoProveedor.objects.all().select_related('factura_proveedor__proveedor')
    
    # Aplicar filtros
    if q:
        pagos = pagos.filter(
            Q(numero_comprobante__icontains=q) |
            Q(factura_proveedor__numero_factura__icontains=q) |
            Q(factura_proveedor__proveedor__nombre__icontains=q)
        )
    
    if factura_id:
        pagos = pagos.filter(factura_proveedor_id=factura_id)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            pagos = pagos.filter(fecha_pago__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            pagos = pagos.filter(fecha_pago__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha descendente
    pagos = pagos.order_by('-fecha_pago', '-id')
    
    # Calcular totales
    total_pagos = pagos.count()
    monto_total = pagos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
    
    contexto = {
        'pagos': pagos,
        'q': q,
        'factura_id': factura_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_pagos': total_pagos,
        'monto_total': monto_total,
    }
    
    return render(request, 'pagos_proveedores_list.html', contexto)


@login_required
def pago_proveedor_crear_view(request, factura_id=None):
    """
    Vista para crear un nuevo pago a un proveedor.
    Si se proporciona factura_id, se pre-selecciona esa factura.
    """
    facturas = FacturaProveedor.objects.filter(
        eliminado__isnull=True,
        estado_pago__in=['pendiente', 'parcial']
    ).select_related('proveedor').order_by('fecha_vencimiento', 'fecha_factura')
    
    if request.method == 'POST':
        try:
            factura_id_post = request.POST.get('factura_proveedor_id')
            monto = Decimal(request.POST.get('monto', '0.00'))
            fecha_pago_str = request.POST.get('fecha_pago', '')
            metodo_pago = request.POST.get('metodo_pago', 'efectivo')
            numero_comprobante = request.POST.get('numero_comprobante', '').strip() or None
            observaciones = request.POST.get('observaciones', '').strip() or None
            
            # Validaciones
            if not factura_id_post:
                messages.error(request, 'Debe seleccionar una factura.')
                return render(request, 'pago_proveedor_form.html', {
                    'modo': 'crear',
                    'facturas': facturas,
                    'factura_seleccionada': None
                })
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero.')
                facturas_con_saldo = [{'factura': f, 'saldo_pendiente': f.calcular_saldo_pendiente()} for f in facturas]
                return render(request, 'pago_proveedor_form.html', {
                    'modo': 'crear',
                    'facturas_con_saldo': facturas_con_saldo,
                    'factura_seleccionada': None,
                    'saldo_pendiente': None
                })
            
            if not fecha_pago_str:
                messages.error(request, 'La fecha de pago es obligatoria.')
                facturas_con_saldo = [{'factura': f, 'saldo_pendiente': f.calcular_saldo_pendiente()} for f in facturas]
                return render(request, 'pago_proveedor_form.html', {
                    'modo': 'crear',
                    'facturas_con_saldo': facturas_con_saldo,
                    'factura_seleccionada': None,
                    'saldo_pendiente': None
                })
            
            # Convertir fecha
            fecha_pago = datetime.strptime(fecha_pago_str, '%Y-%m-%d').date()
            
            # Obtener factura
            factura = get_object_or_404(FacturaProveedor, pk=factura_id_post, eliminado__isnull=True)
            
            # Verificar que el monto no exceda el saldo pendiente
            saldo_pendiente = factura.calcular_saldo_pendiente()
            if monto > saldo_pendiente:
                messages.error(request, f'El monto excede el saldo pendiente (${saldo_pendiente:,.0f}).')
                facturas_con_saldo = [{'factura': f, 'saldo_pendiente': f.calcular_saldo_pendiente()} for f in facturas]
                return render(request, 'pago_proveedor_form.html', {
                    'modo': 'crear',
                    'facturas_con_saldo': facturas_con_saldo,
                    'factura_seleccionada': factura,
                    'saldo_pendiente': saldo_pendiente
                })
            
            # Crear el pago
            pago = PagoProveedor.objects.create(
                factura_proveedor=factura,
                monto=monto,
                fecha_pago=fecha_pago,
                metodo_pago=metodo_pago,
                numero_comprobante=numero_comprobante,
                observaciones=observaciones
            )
            
            # Actualizar estado de pago de la factura
            factura.actualizar_estado_pago_automatico()
            
            messages.success(request, f'Pago de ${monto:,.0f} registrado exitosamente.')
            logger.info(f'Pago creado: {pago.id} - Factura {factura.numero_factura} - ${monto}')
            return redirect('factura_proveedor_detalle', factura_id=factura.id)
            
        except ValueError as e:
            logger.error(f'Error de validación al crear pago: {str(e)}', exc_info=True)
            messages.error(request, f'Error en los datos: {str(e)}')
            facturas_con_saldo = [{'factura': f, 'saldo_pendiente': f.calcular_saldo_pendiente()} for f in facturas]
            return render(request, 'pago_proveedor_form.html', {
                'modo': 'crear',
                'facturas_con_saldo': facturas_con_saldo,
                'factura_seleccionada': None,
                'saldo_pendiente': None
            })
        except Exception as e:
            logger.error(f'Error al crear pago: {str(e)}', exc_info=True)
            messages.error(request, f'Error al crear el pago: {str(e)}')
            facturas_con_saldo = [{'factura': f, 'saldo_pendiente': f.calcular_saldo_pendiente()} for f in facturas]
            return render(request, 'pago_proveedor_form.html', {
                'modo': 'crear',
                'facturas_con_saldo': facturas_con_saldo,
                'factura_seleccionada': None,
                'saldo_pendiente': None
            })
    
    # GET: Mostrar formulario
    factura_seleccionada = None
    saldo_pendiente = None
    if factura_id:
        try:
            factura_seleccionada = FacturaProveedor.objects.get(pk=factura_id, eliminado__isnull=True)
            saldo_pendiente = factura_seleccionada.calcular_saldo_pendiente()
        except FacturaProveedor.DoesNotExist:
            pass
    
    # Calcular saldo pendiente para cada factura y filtrar solo las que tienen saldo > 0
    facturas_con_saldo = []
    for factura in facturas:
        saldo = factura.calcular_saldo_pendiente()
        if saldo > 0:  # Solo incluir facturas con saldo pendiente
            facturas_con_saldo.append({
                'factura': factura,
                'saldo_pendiente': saldo
            })
    
    return render(request, 'pago_proveedor_form.html', {
        'modo': 'crear',
        'facturas_con_saldo': facturas_con_saldo,
        'factura_seleccionada': factura_seleccionada,
        'saldo_pendiente': saldo_pendiente
    })


@login_required
def pago_proveedor_eliminar_view(request, pago_id):
    """
    Vista para eliminar (borrado lógico) un pago.
    """
    pago = get_object_or_404(PagoProveedor, pk=pago_id)
    factura = pago.factura_proveedor
    
    if request.method == 'POST':
        try:
            # Guardar ID antes de eliminar para el log
            pago_id_log = pago.id
            
            # Eliminación física (no hay campo eliminado en la BD)
            pago.delete()
            
            # Actualizar estado de pago de la factura
            factura.actualizar_estado_pago_automatico()
            
            messages.success(request, 'Pago eliminado exitosamente.')
            logger.info(f'Pago eliminado: {pago_id_log}')
            return redirect('factura_proveedor_detalle', factura_id=factura.id)
            
        except Exception as e:
            logger.error(f'Error al eliminar pago: {str(e)}', exc_info=True)
            messages.error(request, f'Error al eliminar el pago: {str(e)}')
            return redirect('factura_proveedor_detalle', factura_id=factura.id)
    
    # GET: Mostrar confirmación
    return render(request, 'pago_proveedor_eliminar.html', {
        'pago': pago
    })

