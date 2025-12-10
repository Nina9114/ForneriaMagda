# ================================================================
# =     IMPORTACIÓN DE TODAS LAS VISTAS DE LA APP VENTAS        =
# ================================================================
# 
# Este archivo centraliza todas las vistas para facilitar su importación.

# --- Vistas de Autenticación y Usuarios ---
from .views_autentication import home, login_view, register_view, dashboard_view
from .views_autentication import proximamente_view, recuperar_contrasena_view
from .views_autentication import logout_view
from .views_autentication import usuarios_list_view, usuario_editar_view, usuario_eliminar_view

# --- Vistas de Productos e Inventario ---
from .views_productos import (
    agregar_producto_view, 
    inventario_view, 
    editar_producto_view, 
    eliminar_producto_view,
    detalle_producto_view,
    eliminar_registro_merma_view,
    cambiar_estado_producto_ajax,
    reactivar_producto_view
)

# --- Vistas del Sistema POS (Punto de Venta) ---
from .views_pos import pos_view, agregar_cliente_ajax, validar_producto_ajax, procesar_venta_ajax

# --- Vistas del Sistema de Alertas ---
from .views_alertas import (
    alertas_list_view,
    alerta_crear_view,
    alerta_editar_view,
    alerta_eliminar_view,
    alerta_cambiar_estado_ajax,
    generar_alertas_automaticas_view,
    generar_alerta_desde_producto
)

# --- Vistas de Movimientos de Inventario (NUEVO) ---
from .view_movimientos import movimientos_view

# --- Vistas de Gestión de Merma ---
from .view_merma import merma_list_view, mover_a_merma_ajax

# --- Vistas de Sistema de Reportes (NUEVO) ---
from .view_reportes import reportes_view

# --- Vistas de Reportes Avanzados (RF-V4, RF-V5, RF-I5) ---
from .view_reportes_ventas import (
    reporte_ventas_view, 
    exportar_ventas_csv,
    exportar_ventas_excel,
    exportar_ventas_pdf
)
from .view_top_productos import (
    top_productos_view, 
    exportar_top_productos_csv,
    exportar_top_productos_excel,
    exportar_top_productos_pdf
)
from .view_reportes_inventario import (
    reporte_inventario_view,
    exportar_inventario_csv,
    exportar_inventario_excel,
    exportar_inventario_pdf
)

# --- Vistas de Comprobante (RF-V3) ---
from .view_comprobante import comprobante_pdf_view, comprobante_html_view

# --- Vistas de Ajustes de Stock (RF-I2) ---
from .view_ajustes_stock import ajustes_stock_view, procesar_ajuste_stock_ajax

# --- Vistas de Acciones Masivas (NUEVO) ---
from .view_acciones_masivas import crear_alertas_masivo, mover_merma_masivo, activar_desactivar_masivo, eliminar_masivo

# --- Vistas de Métricas del Dashboard (NUEVO) ---
from .view_dashboard_metrics import (
    ventas_del_dia_api,
    stock_bajo_api,
    alertas_pendientes_api,
    top_producto_api,
    ventas_del_dia_lista_api,
    merma_lista_api
)

# --- Vistas de Proveedores y Facturas (NUEVO) ---
from .views_proveedores import (
    proveedores_list_view,
    proveedor_crear_view,
    proveedor_editar_view,
    proveedor_eliminar_view
)
from .views_facturas_proveedores import (
    facturas_proveedores_list_view,
    factura_proveedor_crear_view,
    factura_proveedor_detalle_view,
    factura_proveedor_editar_view,
    factura_proveedor_eliminar_view
)
from .views_detalles_factura import (
    agregar_detalle_factura_ajax,
    eliminar_detalle_factura_ajax,
    recibir_factura_ajax,
    quitar_recepcion_factura_ajax
)
from .views_pagos_proveedores import (
    pagos_proveedores_list_view,
    pago_proveedor_crear_view,
    pago_proveedor_eliminar_view
)

# --- Vistas de Producción (NUEVO) ---
from .views_produccion import (
    produccion_list_view,
    produccion_crear_view,
    produccion_detalle_view
)

# --- Vistas de Lotes (NUEVO) ---
from .view_lotes import obtener_lotes_producto_api

# --- Vistas de Historial de Boletas (NUEVO) ---
from .view_historial_boletas import (
    historial_boletas_list_view,
    historial_boleta_detalle_view,
    historial_boleta_regenerar_pdf_view
)