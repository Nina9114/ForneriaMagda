# ================================================================
# =     IMPORTACIÓN DE TODOS LOS MODELOS DE LA APP VENTAS       =
# ================================================================
# 
# Este archivo permite importar los modelos desde cualquier lugar con:
# from ventas.models import Productos, Ventas, Clientes, etc.
# 
# En lugar de tener que especificar el archivo completo:
# from ventas.models.productos import Productos

# --- Modelos de Usuarios ---
from .usuarios import Roles, Direccion, Usuarios

# --- Modelos de Productos ---
from .productos import Categorias, Nutricional, Productos

# --- Modelos de Ventas ---
from .ventas import Clientes, Ventas, DetalleVenta

# --- Modelos de Alertas ---
from .alertas import Alertas

# --- Modelos de Movimientos de Inventario (NUEVO) ---
from .movimientos import MovimientosInventario

# --- Modelos de Proveedores (NUEVO) ---
from .proveedores import Proveedor, FacturaProveedor, DetalleFacturaProveedor, PagoProveedor

# --- Modelos de Lotes (NUEVO) ---
from .lotes import Lote

# --- Modelos de Historial de Merma (NUEVO) ---
from .historial_merma import HistorialMerma

# --- Modelos de Historial de Boletas (NUEVO) ---
from .historial_boletas import HistorialBoletas