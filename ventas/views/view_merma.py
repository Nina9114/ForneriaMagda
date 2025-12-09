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
import json


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
    # - eliminado__isnull=True: Productos no eliminados
    # - estado_merma='en_merma': Productos en estado de merma
    # - O productos con historial de merma (motivo_merma, fecha_merma o cantidad_merma)
    #   Esto incluye productos que fueron reabastecidos pero aún tienen historial
    productos_merma = Productos.objects.filter(
        eliminado__isnull=True
    ).filter(
        Q(estado_merma='en_merma') | 
        Q(motivo_merma__isnull=False) |
        Q(fecha_merma__isnull=False) |
        (Q(cantidad_merma__isnull=False) & Q(cantidad_merma__gt=0))
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
        
        # Importar Alertas para resolver alertas automáticamente
        from ventas.models import Alertas
        
        # Buscar los productos por sus IDs
        productos = Productos.objects.filter(id__in=producto_ids)
        
        # NUEVA LÓGICA: Limpiar "contenido" del producto (cantidad, caducidad, elaboración)
        # El SKU permanece pero sin stock ni fechas (ese lote ya no existe)
        contador = 0
        for producto in productos:
            # Guardar la cantidad que se va a merma antes de ponerla en 0
            producto.cantidad_merma = producto.cantidad if producto.cantidad > 0 else 0
            producto.cantidad = 0  # Reducir cantidad a 0
            producto.caducidad = None  # Limpiar caducidad (ese lote ya no existe)
            producto.elaboracion = None  # Limpiar elaboración (ese lote ya no existe)
            producto.estado_merma = 'en_merma'  # Estado especial para productos en merma
            producto.motivo_merma = motivo_merma  # Registrar motivo
            producto.fecha_merma = timezone.now()  # Registrar fecha
            producto.save()
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
        mensaje = f'Se movieron {contador} producto(s) a merma. Cantidad reducida a 0. Puedes reabastecer editando el producto.'
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
