# ================================================================
# =                                                              =
# =          VISTAS PARA EL SISTEMA DE ALERTAS                  =
# =                                                              =
# ================================================================
#
# Este archivo contiene todas las vistas (funciones) que controlan
# el sistema de alertas de vencimiento de productos.
#
# Funcionalidades:
# - Listar alertas con filtros
# - Crear nuevas alertas manualmente
# - Editar alertas existentes
# - Eliminar alertas
# - Cambiar estado de alertas
# - Generar alertas automáticamente

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

# Importar modelos y formularios
from ventas.models import Alertas, Productos
from ventas.funciones.formularios_alertas import (
    AlertaForm, 
    AlertaFiltroForm,
    CambiarEstadoAlertasForm
)


# ================================================================
# =          VISTA: LISTAR ALERTAS CON FILTROS                   =
# ================================================================

@login_required
def alertas_list_view(request):
    """
    Vista principal que muestra el historial de alertas.
    
    Funcionalidades:
    - Lista todas las alertas ordenadas por fecha (más recientes primero)
    - Permite filtrar por tipo, estado, producto y fecha
    - Muestra estadísticas (cantidad por tipo y estado)
    - Incluye barra de búsqueda similar al inventario
    
    Args:
        request: Objeto con la información de la petición HTTP
        
    Returns:
        Página HTML con la lista de alertas y filtros
    """
    
    # --- Paso 1: Obtener todas las alertas ---
    # Empezamos con todas las alertas, luego aplicaremos filtros
    # Incluir:
    # - Alertas de productos activos (no en merma)
    # - Alertas de facturas (donde productos=None y factura_proveedor no es None)
    from django.db.models import Q
    alertas = Alertas.objects.select_related('productos', 'factura_proveedor').filter(
        Q(productos__estado_merma='activo') |  # Alertas de productos activos
        Q(productos__isnull=True, factura_proveedor__isnull=False)  # Alertas de facturas
    )
    
    # --- Paso 2: Aplicar filtros si existen ---
    # Obtener parámetros de la URL (GET)
    tipo_filtro = request.GET.get('tipo_alerta', '')
    estado_filtro = request.GET.get('estado', '')
    producto_filtro = request.GET.get('producto', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Filtrar por tipo de alerta
    if tipo_filtro:
        alertas = alertas.filter(tipo_alerta=tipo_filtro)
    
    # Filtrar por estado
    if estado_filtro:
        alertas = alertas.filter(estado=estado_filtro)
    
    # Filtrar por nombre de producto o factura (búsqueda parcial)
    if producto_filtro:
        alertas = alertas.filter(
            Q(productos__nombre__icontains=producto_filtro) |
            Q(productos__marca__icontains=producto_filtro) |
            Q(factura_proveedor__numero_factura__icontains=producto_filtro) |
            Q(factura_proveedor__proveedor__nombre__icontains=producto_filtro) |
            Q(mensaje__icontains=producto_filtro)
        )
    
    # Filtrar por rango de fechas
    if fecha_desde:
        alertas = alertas.filter(fecha_generada__gte=fecha_desde)
    
    if fecha_hasta:
        # Agregar un día para incluir todo el día seleccionado
        alertas = alertas.filter(fecha_generada__lte=fecha_hasta + ' 23:59:59')
    
    # --- Paso 3: Ordenar las alertas ---
    # Primero por tipo (rojas primero), luego por fecha (más recientes primero)
    orden_tipo = {
        'roja': 1,
        'amarilla': 2,
        'verde': 3,
    }
    
    # Ordenar en Python (Django no puede ordenar por CASE directamente sin SQL raw)
    alertas_list = list(alertas)
    alertas_list.sort(
        key=lambda x: (orden_tipo.get(x.tipo_alerta, 4), -x.fecha_generada.timestamp())
    )
    
    # --- Paso 4: Calcular estadísticas ---
    # Contar alertas por tipo y estado para mostrar en cards
    stats_tipo = {
        'roja': alertas.filter(tipo_alerta='roja', estado='activa').count(),
        'amarilla': alertas.filter(tipo_alerta='amarilla', estado='activa').count(),
        'verde': alertas.filter(tipo_alerta='verde', estado='activa').count(),
    }
    
    stats_estado = {
        'activa': alertas.filter(estado='activa').count(),
        'resuelta': alertas.filter(estado='resuelta').count(),
        'ignorada': alertas.filter(estado='ignorada').count(),
    }
    
    # --- Paso 5: Crear el formulario de filtros ---
    form_filtro = AlertaFiltroForm(request.GET or None)
    
    # --- Paso 6: Preparar el contexto para el template ---
    contexto = {
        'alertas': alertas_list,
        'form_filtro': form_filtro,
        'stats_tipo': stats_tipo,
        'stats_estado': stats_estado,
        'total_alertas': len(alertas_list),
        # Mantener los valores de los filtros para la URL
        'tipo_actual': tipo_filtro,
        'estado_actual': estado_filtro,
        'producto_actual': producto_filtro,
    }
    
    return render(request, 'alertas_list.html', contexto)


# ================================================================
# =          VISTA: CREAR NUEVA ALERTA MANUALMENTE               =
# ================================================================

@login_required
def alerta_crear_view(request):
    """
    Vista para crear una nueva alerta manualmente.
    
    Muestra un formulario donde el usuario puede:
    - Seleccionar un producto
    - Elegir el tipo de alerta
    - Escribir un mensaje personalizado
    
    Args:
        request: Petición HTTP
        
    Returns:
        - GET: Formulario vacío
        - POST: Guarda la alerta y redirige a la lista
    """
    
    if request.method == 'POST':
        # Procesar el formulario enviado
        form = AlertaForm(request.POST)
        
        if form.is_valid():
            # Guardar la nueva alerta
            alerta = form.save()
            
            messages.success(
                request,
                f'Alerta creada exitosamente para {alerta.productos.nombre}'
            )
            
            # Redirigir a la lista de alertas
            return redirect('alertas_list')
        else:
            messages.error(
                request,
                'Por favor corrige los errores marcados en el formulario'
            )
    else:
        # Mostrar formulario vacío
        form = AlertaForm()
    
    contexto = {
        'form': form,
        'titulo': 'Crear Nueva Alerta',
        'boton_texto': 'Crear Alerta',
    }
    
    return render(request, 'alerta_form.html', contexto)


# ================================================================
# =          VISTA: EDITAR ALERTA EXISTENTE                      =
# ================================================================

@login_required
def alerta_editar_view(request, alerta_id):
    """
    Vista para editar una alerta existente.
    
    Permite modificar:
    - Tipo de alerta
    - Mensaje
    - Estado
    
    Args:
        request: Petición HTTP
        alerta_id: ID de la alerta a editar
        
    Returns:
        Formulario con los datos actuales de la alerta
    """
    
    # Obtener la alerta o mostrar error 404 si no existe
    alerta = get_object_or_404(Alertas, pk=alerta_id)
    
    if request.method == 'POST':
        form = AlertaForm(request.POST, instance=alerta)
        
        if form.is_valid():
            form.save()
            
            messages.success(
                request,
                f'Alerta actualizada correctamente'
            )
            
            return redirect('alertas_list')
        else:
            messages.error(
                request,
                'Por favor corrige los errores en el formulario'
            )
    else:
        # Mostrar formulario con los datos actuales
        form = AlertaForm(instance=alerta)
    
    contexto = {
        'form': form,
        'alerta': alerta,
        'titulo': 'Editar Alerta',
        'boton_texto': 'Guardar Cambios',
    }
    
    return render(request, 'alerta_form.html', contexto)


# ================================================================
# =          VISTA: ELIMINAR ALERTA                              =
# ================================================================

@login_required
def alerta_eliminar_view(request, alerta_id):
    """
    Vista para eliminar una alerta.
    
    Muestra una página de confirmación antes de eliminar.
    
    Args:
        request: Petición HTTP
        alerta_id: ID de la alerta a eliminar
        
    Returns:
        - GET: Página de confirmación
        - POST: Elimina la alerta y redirige a la lista
    """
    
    alerta = get_object_or_404(Alertas, pk=alerta_id)
    
    if request.method == 'POST':
        # Guardar información antes de eliminar
        producto_nombre = alerta.productos.nombre
        
        # Eliminar la alerta
        alerta.delete()
        
        messages.success(
            request,
            f'Alerta de "{producto_nombre}" eliminada correctamente'
        )
        
        return redirect('alertas_list')
    
    # Mostrar página de confirmación
    contexto = {
        'alerta': alerta,
    }
    
    return render(request, 'alerta_confirmar_eliminar.html', contexto)


# ================================================================
# =       VISTA API: CAMBIAR ESTADO DE UNA ALERTA (AJAX)         =
# ================================================================

@login_required
@require_http_methods(["POST"])
def alerta_cambiar_estado_ajax(request, alerta_id):
    """
    API para cambiar el estado de una alerta mediante AJAX.
    
    Se llama desde JavaScript para cambiar el estado sin recargar la página.
    
    Args:
        request: Petición HTTP con el nuevo estado
        alerta_id: ID de la alerta a modificar
        
    Returns:
        JsonResponse con el resultado
    """
    
    try:
        alerta = get_object_or_404(Alertas, pk=alerta_id)
        nuevo_estado = request.POST.get('estado')
        
        # Validar que el estado sea válido
        estados_validos = ['activa', 'resuelta', 'ignorada']
        
        if nuevo_estado not in estados_validos:
            return JsonResponse({
                'success': False,
                'mensaje': 'Estado inválido'
            }, status=400)
        
        # Actualizar el estado
        alerta.estado = nuevo_estado
        alerta.save(update_fields=['estado'])
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Estado cambiado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'mensaje': f'Error: {str(e)}'
        }, status=500)


# ================================================================
# =       VISTA API: GENERAR ALERTAS AUTOMÁTICAMENTE             =
# ================================================================

@login_required
@require_http_methods(["POST"])
def generar_alertas_automaticas_view(request):
    """
    Vista para generar alertas automáticamente.
    
    Llama al método estático del modelo Alertas que:
    - Revisa todos los productos activos
    - Calcula días hasta vencer
    - Verifica niveles de stock (stock_minimo)
    - Crea/actualiza alertas según corresponda
    
    Se puede llamar:
    - Manualmente desde un botón en la interfaz
    - Automáticamente con un cron job
    - Al iniciar el servidor
    
    Args:
        request: Petición HTTP
        
    Returns:
        JsonResponse con estadísticas de alertas generadas
    """
    
    try:
        # Llamar al método estático del modelo
        resultado = Alertas.generar_alertas_automaticas()
        
        # Preparar mensaje informativo
        stock_bajo = resultado.get('stock_bajo', 0)
        mensaje = (
            f"Alertas generadas: {resultado['total']} total "
            f"({resultado['roja']} rojas, "
            f"{resultado['amarilla']} amarillas, "
            f"{resultado['verde']} verdes"
        )
        if stock_bajo > 0:
            mensaje += f", {stock_bajo} de stock bajo"
        mensaje += ")"
        
        messages.success(request, mensaje)
        
        return JsonResponse({
            'success': True,
            'mensaje': mensaje,
            'estadisticas': resultado
        })
        
    except Exception as e:
        messages.error(request, f'Error al generar alertas: {str(e)}')
        
        return JsonResponse({
            'success': False,
            'mensaje': f'Error: {str(e)}'
        }, status=500)


# ================================================================
# =       VISTA: GENERAR ALERTA DESDE INVENTARIO                 =
# ================================================================

@login_required
def generar_alerta_desde_producto(request, producto_id):
    """
    Vista para crear una alerta directamente desde un producto.
    
    Se accede desde el botón "Crear Alerta" en la página de inventario.
    
    Args:
        request: Petición HTTP
        producto_id: ID del producto para crear la alerta
        
    Returns:
        Formulario pre-llenado con el producto seleccionado
    """
    
    producto = get_object_or_404(Productos, pk=producto_id)
    
    if request.method == 'POST':
        form = AlertaForm(request.POST)
        
        if form.is_valid():
            form.save()
            
            messages.success(
                request,
                f'Alerta creada para {producto.nombre}'
            )
            
            # Volver al inventario
            return redirect('inventario')
        
    else:
        # Pre-llenar el formulario con el producto
        # Calcular días hasta vencer para sugerir el tipo
        hoy = timezone.now().date()
        dias = (producto.caducidad - hoy).days
        
        # Determinar tipo sugerido
        if dias <= 13:
            tipo_sugerido = 'roja'
        elif dias <= 29:
            tipo_sugerido = 'amarilla'
        else:
            tipo_sugerido = 'verde'
        
        # Mensaje sugerido
        mensaje_sugerido = f"{producto.nombre} vence en {dias} días"
        
        form = AlertaForm(initial={
            'productos': producto,
            'tipo_alerta': tipo_sugerido,
            'mensaje': mensaje_sugerido,
            'estado': 'activa'
        })
    
    contexto = {
        'form': form,
        'producto': producto,
        'titulo': f'Crear Alerta para {producto.nombre}',
        'boton_texto': 'Crear Alerta',
    }
    
    return render(request, 'alerta_form.html', contexto)

