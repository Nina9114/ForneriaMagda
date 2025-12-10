# ================================================================
# =                                                              =
# =              URLS PRINCIPALES DEL PROYECTO FORNERIA          =
# =                                                              =
# ================================================================
#
# Este archivo define todas las rutas (URLs) del proyecto.
# Cada path() conecta una URL con una vista (función) que la maneja.
#
# Ejemplo:
# path('login/', login_view, name='login')
#       ↑ URL        ↑ Función    ↑ Nombre para usar en templates
#
# En los templates podemos usar: {% url 'login' %}
# En las vistas podemos usar: redirect('login')

from django.contrib import admin
from django.urls import path

# Importar todas las vistas necesarias
from ventas.views import (
    # Vistas de autenticación y navegación
    home, login_view, register_view, dashboard_view, logout_view,
    proximamente_view, recuperar_contrasena_view,
    
    # Vistas de productos e inventario
    agregar_producto_view, inventario_view, editar_producto_view, 
    eliminar_producto_view, detalle_producto_view, eliminar_registro_merma_view,
    reactivar_producto_view,
    cambiar_estado_producto_ajax,
    
    # Vistas de gestión de usuarios (admin)
    usuarios_list_view, usuario_editar_view, usuario_eliminar_view,
    
    # Vistas del sistema POS (Punto de Venta)
    pos_view, agregar_cliente_ajax, validar_producto_ajax, procesar_venta_ajax,
    
    # Vistas del sistema de Alertas
    alertas_list_view, alerta_crear_view, alerta_editar_view, alerta_eliminar_view,
    alerta_cambiar_estado_ajax, generar_alertas_automaticas_view, 
    generar_alerta_desde_producto,
    
    # Vistas de Movimientos de Inventario (NUEVO)
    movimientos_view,
    
    # Vistas de Gestión de Merma
    merma_list_view, mover_a_merma_ajax,
    
    # Vistas de Sistema de Reportes (NUEVO)
    reportes_view,
    
    # Vistas de Acciones Masivas (NUEVO)
    crear_alertas_masivo, mover_merma_masivo, activar_desactivar_masivo, eliminar_masivo,
    
    # Vistas de Métricas del Dashboard (NUEVO)
    ventas_del_dia_api, stock_bajo_api, alertas_pendientes_api, top_producto_api,
    ventas_del_dia_lista_api, merma_lista_api,
    
    # Vistas de Historial de Boletas (NUEVO)
    historial_boletas_list_view, historial_boleta_detalle_view, historial_boleta_regenerar_pdf_view,
    
    # Vistas de Proveedores y Facturas (NUEVO)
    proveedores_list_view, proveedor_crear_view, proveedor_editar_view, proveedor_eliminar_view,
    facturas_proveedores_list_view, factura_proveedor_crear_view, factura_proveedor_detalle_view,
    factura_proveedor_editar_view, factura_proveedor_eliminar_view,
    agregar_detalle_factura_ajax, eliminar_detalle_factura_ajax, recibir_factura_ajax, quitar_recepcion_factura_ajax,
    pagos_proveedores_list_view, pago_proveedor_crear_view, pago_proveedor_eliminar_view,
    
    # Vistas de Producción (NUEVO)
    produccion_list_view, produccion_crear_view, produccion_detalle_view,
)

# Vistas de APIs para el dashboard
from ventas.views.views_vencimientos import (
    productos_por_vencer_api,
    productos_por_vencer_14_dias_api,
    productos_por_vencer_30_dias_api
)
from ventas.views.view_dashboard import (
    perdida_siete_dias,
    perdida_catorce_dias,
    perdida_treinta_dias
)

# Vistas de reportes avanzados (RF-V4, RF-V5, RF-I5)
from ventas.views.view_reportes_ventas import (
    reporte_ventas_view,
    exportar_ventas_csv,
    exportar_ventas_excel,
    exportar_ventas_pdf
)
from ventas.views.view_top_productos import (
    top_productos_view,
    exportar_top_productos_csv,
    exportar_top_productos_excel,
    exportar_top_productos_pdf
)
from ventas.views.view_reportes_inventario import (
    reporte_inventario_view,
    exportar_inventario_csv,
    exportar_inventario_excel,
    exportar_inventario_pdf
)

# Vista de comprobante PDF (RF-V3)
from ventas.views.view_comprobante import (
    comprobante_pdf_view,
    comprobante_html_view
)

# Vista de ajustes de stock (RF-I2)
from ventas.views.view_ajustes_stock import (
    ajustes_stock_view,
    procesar_ajuste_stock_ajax
)

# Vista de lotes
from ventas.views.view_lotes import (
    obtener_lotes_producto_api
)

# ================================================================
# =                     DEFINICIÓN DE RUTAS                      =
# ================================================================

urlpatterns = [
    # ============================================================
    # ADMINISTRACIÓN DE DJANGO
    # ============================================================
    # Panel de administración de Django (para superusuarios)
    path('admin/', admin.site.urls),
    
    # ============================================================
    # PÁGINAS PRINCIPALES Y AUTENTICACIÓN
    # ============================================================
    # Página de inicio (home) - Visible sin autenticar
    path('', home, name='home'),
    
    # Sistema de autenticación
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('recuperar-contrasena/', recuperar_contrasena_view, name='recuperar_contrasena'),
    
    # Dashboard principal (requiere autenticación)
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # ============================================================
    # GESTIÓN DE PRODUCTOS E INVENTARIO
    # ============================================================
    # Agregar nuevo producto
    path('productos/agregar/', agregar_producto_view, name='agregar_producto'),
    
    # Ver inventario completo
    path('inventario/', inventario_view, name='inventario'),
    
    # Ver detalle de un producto
    path('inventario/detalle/<int:producto_id>/', detalle_producto_view, name='detalle_producto'),
    
    # Editar un producto existente
    path('inventario/editar/<int:producto_id>/', editar_producto_view, name='editar_producto'),
    
    # Desactivar un producto (cambia estado a inactivo)
    path('inventario/eliminar/<int:producto_id>/', eliminar_producto_view, name='eliminar_producto'),
    
    # Reactivar un producto inactivo
    path('inventario/reactivar/<int:producto_id>/', reactivar_producto_view, name='reactivar_producto'),
    
    # Eliminar registro de merma de un producto
    path('inventario/detalle/<int:producto_id>/eliminar-merma/', eliminar_registro_merma_view, name='eliminar_registro_merma'),
    
    # Cambiar estado de producto (activo/inactivo) - API
    path('api/productos/<int:producto_id>/cambiar-estado/', cambiar_estado_producto_ajax, name='api_cambiar_estado_producto'),
    
    # API para obtener lotes de un producto
    path('api/productos/<int:producto_id>/lotes/', obtener_lotes_producto_api, name='api_obtener_lotes_producto'),
    
    # ============================================================
    # SISTEMA DE PUNTO DE VENTA (POS) - NUEVO
    # ============================================================
    # Página principal del POS
    path('pos/', pos_view, name='pos'),
    
    # APIs del POS (llamadas AJAX desde JavaScript)
    path('api/agregar-cliente/', agregar_cliente_ajax, name='api_agregar_cliente'),
    path('api/validar-producto/<int:producto_id>/', validar_producto_ajax, name='api_validar_producto'),
    path('api/procesar-venta/', procesar_venta_ajax, name='api_procesar_venta'),
    
    # Comprobante de venta (RF-V3)
    path('ventas/comprobante/<int:venta_id>/pdf/', comprobante_pdf_view, name='comprobante_pdf'),
    path('ventas/comprobante/<int:venta_id>/', comprobante_html_view, name='comprobante_html'),
    
    # ============================================================
    # GESTIÓN DE USUARIOS (SOLO ADMINISTRADORES)
    # ============================================================
    # Listar todos los usuarios
    path('usuarios/', usuarios_list_view, name='usuarios_list'),
    
    # Editar un usuario
    path('usuarios/editar/<int:user_id>/', usuario_editar_view, name='usuario_editar'),
    
    # Eliminar un usuario
    path('usuarios/eliminar/<int:user_id>/', usuario_eliminar_view, name='usuario_eliminar'),
    
    # ============================================================
    # APIs PARA EL DASHBOARD
    # ============================================================
    # APIs de métricas principales
    path('api/ventas-del-dia/', ventas_del_dia_api, name='api_ventas_del_dia'),
    path('api/ventas-del-dia/lista/', ventas_del_dia_lista_api, name='api_ventas_del_dia_lista'),
    path('api/stock-bajo/', stock_bajo_api, name='api_stock_bajo'),
    path('api/alertas-pendientes/', alertas_pendientes_api, name='api_alertas_pendientes'),
    path('api/top-producto/', top_producto_api, name='api_top_producto'),
    path('api/merma/lista/', merma_lista_api, name='api_merma_lista'),
    
    # APIs de productos próximos a vencer
    path('api/proximos-vencimientos/', productos_por_vencer_api, name='api_proximos_vencimientos'),
    path('api/proximos-vencimientos-14/', productos_por_vencer_14_dias_api, name='api_proximos_vencimientos_14'),
    path('api/proximos-vencimientos-30/', productos_por_vencer_30_dias_api, name='api_proximos_vencimientos_30'),
    
    # APIs de pérdida potencial por vencimiento
    path('api/perdida-potencial/', perdida_siete_dias, name='api_perdida_potencial'),
    path('api/perdida-potencial-14/', perdida_catorce_dias, name='api_perdida_potencial_14'),
    path('api/perdida-potencial-30/', perdida_treinta_dias, name='api_perdida_potencial_30'),
    
    # ============================================================
    # SISTEMA DE ALERTAS (NUEVO)
    # ============================================================
    # Lista de alertas con filtros
    path('alertas/', alertas_list_view, name='alertas_list'),
    
    # Crear nueva alerta
    path('alertas/crear/', alerta_crear_view, name='alerta_crear'),
    
    # Editar una alerta existente
    path('alertas/editar/<int:alerta_id>/', alerta_editar_view, name='alerta_editar'),
    
    # Eliminar una alerta
    path('alertas/eliminar/<int:alerta_id>/', alerta_eliminar_view, name='alerta_eliminar'),
    
    # Crear alerta desde un producto específico (desde inventario)
    path('alertas/producto/<int:producto_id>/', generar_alerta_desde_producto, name='alerta_desde_producto'),
    
    # APIs para alertas (llamadas AJAX)
    path('api/alerta/<int:alerta_id>/cambiar-estado/', alerta_cambiar_estado_ajax, name='api_alerta_cambiar_estado'),
    path('api/generar-alertas-automaticas/', generar_alertas_automaticas_view, name='api_generar_alertas'),
    
    # ============================================================
    # HISTORIAL DE MOVIMIENTOS DE INVENTARIO (NUEVO)
    # ============================================================
    # Página que muestra el historial completo de movimientos
    path('movimientos/', movimientos_view, name='movimientos'),
    
    # ============================================================
    # GESTIÓN DE MERMA (NUEVO)
    # ============================================================
    # Página que muestra productos en merma (vencidos, deteriorados, dañados)
    path('merma/', merma_list_view, name='merma_list'),
    
    # API para mover productos a merma (llamada AJAX desde inventario)
    path('api/mover-a-merma/', mover_a_merma_ajax, name='api_mover_merma'),
    
    # ============================================================
    # SISTEMA DE REPORTES (NUEVO)
    # ============================================================
    # Página principal de reportes con filtros y visualización
    path('reportes/', reportes_view, name='reportes'),
    
    # Reporte de ventas con filtros avanzados (RF-V4)
    path('reportes/ventas/', reporte_ventas_view, name='reporte_ventas'),
    path('reportes/ventas/exportar/csv/', exportar_ventas_csv, name='exportar_ventas_csv'),
    path('reportes/ventas/exportar/excel/', exportar_ventas_excel, name='exportar_ventas_excel'),
    path('reportes/ventas/exportar/pdf/', exportar_ventas_pdf, name='exportar_ventas_pdf'),
    
    # Reporte top productos (RF-V5)
    path('reportes/top-productos/', top_productos_view, name='top_productos'),
    path('reportes/top-productos/exportar/csv/<str:tipo>/', exportar_top_productos_csv, name='exportar_top_productos_csv'),
    path('reportes/top-productos/exportar/excel/<str:tipo>/', exportar_top_productos_excel, name='exportar_top_productos_excel'),
    path('reportes/top-productos/exportar/pdf/<str:tipo>/', exportar_top_productos_pdf, name='exportar_top_productos_pdf'),
    
    # Reporte de inventario con valorización (RF-I5)
    path('reportes/inventario/', reporte_inventario_view, name='reporte_inventario'),
    path('reportes/inventario/exportar/csv/', exportar_inventario_csv, name='exportar_inventario_csv'),
    path('reportes/inventario/exportar/excel/', exportar_inventario_excel, name='exportar_inventario_excel'),
    path('reportes/inventario/exportar/pdf/', exportar_inventario_pdf, name='exportar_inventario_pdf'),
    
    # ============================================================
    # HISTORIAL DE BOLETAS (NUEVO)
    # ============================================================
    # Lista de boletas emitidas (auditoría)
    path('historial-boletas/', historial_boletas_list_view, name='historial_boletas_list'),
    
    # Detalle de una boleta del historial
    path('historial-boletas/<int:historial_id>/', historial_boleta_detalle_view, name='historial_boleta_detalle'),
    
    # Regenerar PDF de una boleta del historial
    path('historial-boletas/<int:historial_id>/pdf/', historial_boleta_regenerar_pdf_view, name='historial_boleta_pdf'),
    
    # Ajustes manuales de stock (RF-I2)
    path('inventario/ajustes/', ajustes_stock_view, name='ajustes_stock'),
    path('api/ajustes-stock/', procesar_ajuste_stock_ajax, name='api_ajustes_stock'),
    
    # ============================================================
    # ACCIONES MASIVAS EN INVENTARIO (NUEVO)
    # ============================================================
    # APIs para ejecutar acciones sobre múltiples productos
    path('api/acciones-masivas/crear-alertas/', crear_alertas_masivo, name='api_crear_alertas_masivo'),
    path('api/acciones-masivas/mover-merma/', mover_merma_masivo, name='api_mover_merma_masivo'),
    path('api/acciones-masivas/activar-desactivar/', activar_desactivar_masivo, name='api_activar_desactivar_masivo'),
    path('api/acciones-masivas/eliminar/', eliminar_masivo, name='api_eliminar_masivo'),
    
    # ============================================================
    # GESTIÓN DE PROVEEDORES Y FACTURAS (NUEVO)
    # ============================================================
    # Proveedores
    path('proveedores/', proveedores_list_view, name='proveedores_list'),
    path('proveedores/crear/', proveedor_crear_view, name='proveedor_crear'),
    path('proveedores/editar/<int:proveedor_id>/', proveedor_editar_view, name='proveedor_editar'),
    path('proveedores/eliminar/<int:proveedor_id>/', proveedor_eliminar_view, name='proveedor_eliminar'),
    
    # Facturas de Proveedores
    path('facturas-proveedores/', facturas_proveedores_list_view, name='facturas_proveedores_list'),
    path('facturas-proveedores/crear/', factura_proveedor_crear_view, name='factura_proveedor_crear'),
    path('facturas-proveedores/<int:factura_id>/', factura_proveedor_detalle_view, name='factura_proveedor_detalle'),
    path('facturas-proveedores/editar/<int:factura_id>/', factura_proveedor_editar_view, name='factura_proveedor_editar'),
    path('facturas-proveedores/eliminar/<int:factura_id>/', factura_proveedor_eliminar_view, name='factura_proveedor_eliminar'),
    
    # APIs para detalles de facturas
    path('api/factura/<int:factura_id>/agregar-producto/', agregar_detalle_factura_ajax, name='api_agregar_detalle_factura'),
    path('api/detalle-factura/<int:detalle_id>/eliminar/', eliminar_detalle_factura_ajax, name='api_eliminar_detalle_factura'),
    path('api/factura/<int:factura_id>/recibir/', recibir_factura_ajax, name='api_recibir_factura'),
    path('api/factura/<int:factura_id>/quitar-recepcion/', quitar_recepcion_factura_ajax, name='api_quitar_recepcion_factura'),
    
    # Pagos a Proveedores
    path('pagos-proveedores/', pagos_proveedores_list_view, name='pagos_proveedores_list'),
    path('pagos-proveedores/crear/', pago_proveedor_crear_view, name='pago_proveedor_crear'),
    path('pagos-proveedores/crear/<int:factura_id>/', pago_proveedor_crear_view, name='pago_proveedor_crear_factura'),
    path('pagos-proveedores/eliminar/<int:pago_id>/', pago_proveedor_eliminar_view, name='pago_proveedor_eliminar'),
    
    # ============================================================
    # URLs de Producción (NUEVO)
    # ============================================================
    path('produccion/', produccion_list_view, name='produccion_list'),
    path('produccion/crear/', produccion_crear_view, name='produccion_crear'),
    path('produccion/detalle/<int:lote_id>/', produccion_detalle_view, name='produccion_detalle'),
    
    # ============================================================
    # PÁGINA "PRÓXIMAMENTE" (FUNCIONES EN DESARROLLO)
    # ============================================================
    # Página genérica para funcionalidades que aún no están listas
    path("proximamente/", proximamente_view, name="proximamente"),
    path("proximamente/<slug:feature>/", proximamente_view, name="proximamente_feature"),
]

# ================================================================
# NOTA: ¿Qué hace cada parte?
# ================================================================
#
# 1. path('url/', vista, name='nombre'):
#    - 'url/': Es lo que el usuario escribe en el navegador
#    - vista: La función Python que maneja esa URL
#    - name='nombre': Un identificador para usar en templates y redirects
#
# 2. <int:producto_id>: Es un parámetro dinámico
#    - Captura un número de la URL y lo pasa a la vista
#    - Ejemplo: /inventario/editar/5/ → producto_id = 5
#
# 3. <slug:feature>: Es un parámetro de texto
#    - Captura texto con guiones
#    - Ejemplo: /proximamente/reportes/ → feature = 'reportes'
