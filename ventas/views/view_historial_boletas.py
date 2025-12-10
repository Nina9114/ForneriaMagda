# ================================================================
# =                                                              =
# =        VISTAS: HISTORIAL DE BOLETAS                         =
# =                                                              =
# ================================================================
#
# Este archivo contiene las vistas para gestionar el historial
# de boletas emitidas (auditoría y revisión).

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from ventas.models import HistorialBoletas, Ventas
from decimal import Decimal
import json
import logging

logger = logging.getLogger('ventas')


@login_required
def historial_boletas_list_view(request):
    """
    Muestra el listado de boletas emitidas (historial).
    
    Permite:
    - Ver todas las boletas emitidas
    - Buscar por folio, cliente, fecha
    - Filtrar por fecha
    - Ver detalles de cada boleta
    - Regenerar PDFs
    
    Args:
        request: HttpRequest
    
    Returns:
        HttpResponse: Página HTML con el listado
    """
    
    # Obtener parámetros de búsqueda y filtros
    busqueda = request.GET.get('q', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    pagina = request.GET.get('page', 1)
    
    # Obtener todas las boletas del historial
    boletas = HistorialBoletas.objects.select_related('venta').all()
    
    # Aplicar filtros de búsqueda
    if busqueda:
        boletas = boletas.filter(
            Q(folio__icontains=busqueda) |
            Q(cliente_nombre__icontains=busqueda) |
            Q(usuario_emisor__icontains=busqueda)
        )
    
    # Aplicar filtros de fecha
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            boletas = boletas.filter(fecha_emision__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            boletas = boletas.filter(fecha_emision__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha más reciente primero
    boletas = boletas.order_by('-fecha_emision')
    
    # Paginación
    paginador = Paginator(boletas, 20)  # 20 boletas por página
    try:
        boletas_pagina = paginador.page(pagina)
    except:
        boletas_pagina = paginador.page(1)
    
    # Calcular estadísticas
    total_boletas = boletas.count()
    total_ingresos = sum(b.total_con_iva for b in boletas)
    
    context = {
        'boletas': boletas_pagina,
        'busqueda': busqueda,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_boletas': total_boletas,
        'total_ingresos': total_ingresos,
    }
    
    return render(request, 'historial_boletas_list.html', context)


@login_required
def historial_boleta_detalle_view(request, historial_id):
    """
    Muestra los detalles de una boleta del historial.
    
    Args:
        request: HttpRequest
        historial_id: ID del registro en HistorialBoletas
    
    Returns:
        HttpResponse: Página HTML con los detalles
    """
    
    historial = get_object_or_404(HistorialBoletas, pk=historial_id)
    datos_boleta = historial.get_datos_boleta_dict()
    
    context = {
        'historial': historial,
        'datos_boleta': datos_boleta,
        'venta': historial.venta,
    }
    
    return render(request, 'historial_boleta_detalle.html', context)


@login_required
def historial_boleta_regenerar_pdf_view(request, historial_id):
    """
    Regenera el PDF de una boleta desde el historial.
    
    Usa los datos guardados en el historial para generar el PDF,
    incluso si la venta original fue modificada.
    
    Args:
        request: HttpRequest
        historial_id: ID del registro en HistorialBoletas
    
    Returns:
        HttpResponse: Archivo PDF descargable
    """
    
    historial = get_object_or_404(HistorialBoletas, pk=historial_id)
    
    # Usar la vista de PDF normal, pero con la venta del historial
    from ventas.views.view_comprobante import comprobante_pdf_view
    return comprobante_pdf_view(request, historial.venta.id)

