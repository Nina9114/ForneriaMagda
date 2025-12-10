# ================================================================
# =                                                              =
# =      VISTA: REPORTE DE INVENTARIO CON VALORIZACIÓN         =
# =                                                              =
# ================================================================
#
# Este archivo implementa el reporte de inventario según RF-I5 del Jira:
# "Reporte inventario por categoría y valorización"
#
# REQUISITOS JIRA:
# - RF-I5: Reporte inventario por categoría y valorización
#
# FUNCIONALIDADES:
# - Filtro por categoría
# - Cálculo de valorización (precio × stock)
# - Resumen por categoría con totales
# - Visualización clara
# - Exportación a CSV (opcional)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from decimal import Decimal
import csv

from ventas.models import Productos, Categorias
from ventas.utils.exportadores import exportar_a_excel, exportar_a_pdf


# ================================================================
# =          VISTA: REPORTE DE INVENTARIO                       =
# ================================================================

@login_required
def reporte_inventario_view(request):
    """
    Vista para generar reporte de inventario con valorización.
    
    Cumple con RF-I5 del Jira:
    - Reporte inventario por categoría
    - Cálculo de valorización (precio × stock)
    - Resumen por categoría con totales
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Página HTML con el reporte
    """
    
    # ============================================================
    # PASO 1: Inicializar variables
    # ============================================================
    reporte_generado = False
    productos = Productos.objects.none()
    resumen_categorias = []
    valorizacion_total = Decimal('0.00')
    categoria_id = None
    
    # ============================================================
    # PASO 2: Procesar filtros del formulario
    # ============================================================
    if request.method == 'GET' and 'generar' in request.GET:
        reporte_generado = True
        
        # Obtener filtro de categoría
        categoria_id = request.GET.get('categoria_id')
        
        # ============================================================
        # PASO 3: Obtener productos según filtros
        # ============================================================
        # Solo productos activos (excluye inactivos y en_merma)
        productos = Productos.objects.filter(
            eliminado__isnull=True,
            estado_merma='activo'
        ).select_related('categorias')
        
        # Filtrar por categoría si se especifica
        if categoria_id and categoria_id != '':
            productos = productos.filter(categorias_id=categoria_id)
        
        # ============================================================
        # PASO 4: Calcular valorización por producto
        # ============================================================
        productos_con_valorizacion = []
        for producto in productos:
            cantidad = producto.cantidad if producto.cantidad else 0
            precio = producto.precio if producto.precio else Decimal('0.00')
            valorizacion = cantidad * precio
            
            productos_con_valorizacion.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'valorizacion': valorizacion,
            })
        
        # ============================================================
        # PASO 5: Calcular resumen por categoría
        # ============================================================
        # Obtener todas las categorías
        categorias = Categorias.objects.all()
        
        resumen_categorias = []
        for categoria in categorias:
            productos_categoria = productos.filter(categorias_id=categoria.id)
            
            total_productos = productos_categoria.count()
            total_stock = sum(
                p.cantidad if p.cantidad else 0 
                for p in productos_categoria
            )
            valorizacion_categoria = sum(
                (p.cantidad if p.cantidad else 0) * (p.precio if p.precio else Decimal('0.00'))
                for p in productos_categoria
            )
            
            if total_productos > 0:  # Solo incluir categorías con productos
                resumen_categorias.append({
                    'categoria': categoria,
                    'total_productos': total_productos,
                    'total_stock': total_stock,
                    'valorizacion': valorizacion_categoria,
                })
        
        # Ordenar por valorización descendente
        resumen_categorias.sort(key=lambda x: x['valorizacion'], reverse=True)
        
        # Calcular valorización total
        valorizacion_total = sum(item['valorizacion'] for item in resumen_categorias)
        
        # Limitar productos para visualización
        productos_con_valorizacion = productos_con_valorizacion[:100]
    
    # ============================================================
    # PASO 6: Obtener lista de categorías para el filtro
    # ============================================================
    categorias = Categorias.objects.all().order_by('nombre')
    
    # ============================================================
    # PASO 7: Preparar contexto
    # ============================================================
    context = {
        'reporte_generado': reporte_generado,
        'productos': productos_con_valorizacion if reporte_generado else [],
        'resumen_categorias': resumen_categorias,
        'valorizacion_total': valorizacion_total,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
    }
    
    # ============================================================
    # PASO 8: Renderizar template
    # ============================================================
    return render(request, 'reporte_inventario.html', context)


# ================================================================
# =     VISTA: EXPORTAR REPORTE INVENTARIO A CSV               =
# ================================================================

def _obtener_productos_inventario(request):
    """
    Función auxiliar para obtener productos de inventario con filtros aplicados.
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        list: Lista de diccionarios con datos de productos
    """
    productos = Productos.objects.filter(
        eliminado__isnull=True,
        estado_merma='activo'
    ).select_related('categorias')
    
    categoria_id = request.GET.get('categoria_id')
    if categoria_id and categoria_id != '':
        productos = productos.filter(categorias_id=categoria_id)
    
    # Preparar datos
    datos = []
    for producto in productos:
        cantidad = producto.cantidad if producto.cantidad else 0
        precio = producto.precio if producto.precio else Decimal('0.00')
        valorizacion = cantidad * precio
        
        datos.append({
            'Producto': producto.nombre,
            'Categoría': producto.categorias.nombre if producto.categorias else 'Sin categoría',
            'Stock Actual': cantidad,
            'Precio': precio,
            'Valorización': valorizacion,
        })
    
    return datos


@login_required
def exportar_inventario_csv(request):
    """
    Exporta el reporte de inventario a formato CSV.
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Archivo CSV descargable
    """
    datos = _obtener_productos_inventario(request)
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.csv"'
    
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow([
        'Producto', 'Categoría', 'Stock Actual', 'Precio', 'Valorización'
    ])
    
    # Datos
    for item in datos:
        writer.writerow([
            item['Producto'],
            item['Categoría'],
            item['Stock Actual'],
            float(item['Precio']),
            float(item['Valorización']),
        ])
    
    return response


@login_required
def exportar_inventario_excel(request):
    """
    Exporta el reporte de inventario a formato Excel (XLSX).
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Archivo Excel descargable
    """
    datos = _obtener_productos_inventario(request)
    
    titulo = "Reporte de Inventario"
    categoria_id = request.GET.get('categoria_id')
    if categoria_id and categoria_id != '':
        try:
            categoria = Categorias.objects.get(id=categoria_id)
            titulo += f" - {categoria.nombre}"
        except Categorias.DoesNotExist:
            pass
    
    return exportar_a_excel(datos, 'reporte_inventario', titulo)


@login_required
def exportar_inventario_pdf(request):
    """
    Exporta el reporte de inventario a formato PDF.
    
    Args:
        request: HttpRequest con parámetros de filtro
        
    Returns:
        HttpResponse: Archivo PDF descargable
    """
    datos = _obtener_productos_inventario(request)
    
    titulo = "Reporte de Inventario"
    categoria_id = request.GET.get('categoria_id')
    if categoria_id and categoria_id != '':
        try:
            categoria = Categorias.objects.get(id=categoria_id)
            titulo += f" - {categoria.nombre}"
        except Categorias.DoesNotExist:
            pass
    
    encabezados = ['Producto', 'Categoría', 'Stock Actual', 'Precio', 'Valorización']
    
    return exportar_a_pdf(datos, 'reporte_inventario', titulo, encabezados)

