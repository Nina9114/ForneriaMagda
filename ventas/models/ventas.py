# ================================================================
# =                                                              =
# =              MODELOS PARA EL SISTEMA DE VENTAS              =
# =                                                              =
# ================================================================
# 
# Este archivo contiene los modelos (estructuras de datos) necesarios
# para manejar las ventas en la Forneria. Incluye:
# 
# 1. Clientes: Personas que compran en la forneria
# 2. Ventas: Registro de cada transacción de venta
# 3. DetalleVenta: Los productos específicos incluidos en cada venta
# 
# Estos modelos se conectan con las tablas que ya existen en la base de datos MySQL.

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .productos import Productos

# ================================================================
# =                    MODELO: CLIENTES                          =
# ================================================================
# 
# Este modelo representa a los clientes de la forneria.
# Puede ser un cliente registrado con RUT, o un cliente genérico
# para ventas rápidas sin registro.

class Clientes(models.Model):
    # --- Campo: RUT del cliente ---
    # El RUT es el identificador único de personas en Chile (como 12.345.678-9)
    # Es opcional (null=True, blank=True) porque podemos tener ventas sin cliente registrado
    rut = models.CharField(
        max_length=12,              # Máximo 12 caracteres para incluir puntos y guión (12.345.678-9)
        blank=True,                 # Permite que el formulario lo deje vacío
        null=True                   # Permite que la base de datos lo guarde como NULL
    )
    
    # --- Campo: Nombre del cliente ---
    # Nombre completo del cliente. Este campo SÍ es obligatorio.
    nombre = models.CharField(
        max_length=150,             # Hasta 150 caracteres para el nombre
        blank=False,                # NO puede estar vacío
        null=False                  # NO puede ser NULL en la base de datos
    )
    
    # --- Campo: Correo electrónico ---
    # Email del cliente, es opcional
    correo = models.EmailField(
        max_length=100,             # Hasta 100 caracteres
        blank=True,                 # Puede estar vacío
        null=True                   # Puede ser NULL
    )
    
    # --- Método para mostrar el cliente como texto ---
    # Cuando imprimimos un cliente, mostrará su nombre (útil en el admin y formularios)
    def __str__(self):
        return self.nombre
    
    # --- Configuración del modelo ---
    class Meta:
        managed = False             # Django NO creará/modificará esta tabla (ya existe en MySQL)
        db_table = 'clientes'       # Nombre de la tabla en la base de datos MySQL
        verbose_name = 'Cliente'    # Nombre singular en el admin de Django
        verbose_name_plural = 'Clientes'  # Nombre plural en el admin de Django


# ================================================================
# =                    MODELO: VENTAS                            =
# ================================================================
# 
# Este modelo representa una venta completa (como un ticket o boleta).
# Contiene información general de la transacción: fecha, totales, cliente, etc.

class Ventas(models.Model):
    # --- Opciones para el canal de venta ---
    # Definimos las dos formas en que se puede vender: presencial o delivery
    CANAL_CHOICES = [
        ('presencial', 'Presencial'),   # Venta en el local
        ('delivery', 'Delivery'),       # Venta con entrega a domicilio
    ]
    
    # --- Campo: Fecha y hora de la venta ---
    # Se guarda automáticamente cuando se crea la venta
    fecha = models.DateTimeField(
        auto_now_add=True           # Django lo llena automáticamente con la fecha/hora actual
    )
    
    # --- Campo: Total sin IVA ---
    # El monto total de la venta SIN incluir el impuesto (IVA en Chile es 19%)
    total_sin_iva = models.DecimalField(
        max_digits=10,              # Hasta 10 dígitos en total
        decimal_places=2,           # 2 decimales (ejemplo: 12345.67)
        validators=[MinValueValidator(Decimal('0.00'))]  # No puede ser negativo
    )
    
    # --- Campo: Monto del IVA ---
    # Cuánto es solo el impuesto (19% del total sin IVA)
    total_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Campo: Descuento aplicado ---
    # Si se aplicó algún descuento a la venta
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),    # Por defecto, sin descuento
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Campo: Total CON IVA ---
    # El monto final que el cliente debe pagar (total_sin_iva + total_iva - descuento)
    total_con_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Campo: Canal de venta ---
    # ¿La venta fue presencial o por delivery?
    canal_venta = models.CharField(
        max_length=20,
        choices=CANAL_CHOICES,      # Solo puede ser 'presencial' o 'delivery'
        default='presencial'        # Por defecto es venta presencial
    )
    
    # --- Campo: Folio ---
    # Número único de boleta/factura (como "BOL-0001234")
    folio = models.CharField(
        max_length=20,
        blank=True,                 # Puede estar vacío
        null=True                   # Puede ser NULL
    )
    
    # --- Opciones para el medio de pago ---
    MEDIO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta_debito', 'Tarjeta Débito'),
        ('tarjeta_credito', 'Tarjeta Crédito'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro'),
    ]
    
    # --- Campo: Medio de pago ---
    # Forma en que el cliente pagó la venta
    medio_pago = models.CharField(
        max_length=20,
        choices=MEDIO_PAGO_CHOICES,
        default='efectivo',
        help_text='Método de pago utilizado por el cliente'
    )
    
    # --- Campo: Monto pagado por el cliente ---
    # Cuánto dinero entregó el cliente (puede ser más que el total)
    monto_pagado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,                 # Opcional
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Campo: Vuelto ---
    # Si el cliente pagó de más, cuánto debemos devolverle
    # Ejemplo: Total $1.500, cliente paga con $2.000, vuelto = $500
    # Nota: Solo aplica para pagos en efectivo
    vuelto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Relación: Cliente asociado a esta venta ---
    # Cada venta pertenece a UN cliente
    # ForeignKey = "Clave foránea" = conexión con la tabla de clientes
    clientes = models.ForeignKey(
        Clientes,                   # Se conecta con el modelo Clientes
        on_delete=models.CASCADE,   # Si se borra el cliente, se borran sus ventas
        related_name='ventas'       # Permite hacer cliente.ventas.all() para ver sus compras
    )
    
    # --- Método para mostrar la venta como texto ---
    def __str__(self):
        return f"Venta {self.folio or self.id} - {self.fecha.strftime('%d/%m/%Y')}"
    
    # --- Configuración del modelo ---
    class Meta:
        managed = False             # La tabla ya existe en MySQL
        db_table = 'ventas'         # Nombre de la tabla en la BD
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']       # Por defecto, ordenar por fecha más reciente primero


# ================================================================
# =                  MODELO: DETALLE DE VENTA                    =
# ================================================================
# 
# Este modelo representa cada producto individual dentro de una venta.
# Por ejemplo, si alguien compra 2 panes y 3 croissants, habrá 2 registros
# de DetalleVenta: uno para los panes y otro para los croissants.

class DetalleVenta(models.Model):
    # --- Relación: Venta a la que pertenece este detalle ---
    # Cada detalle está asociado a UNA venta específica
    ventas = models.ForeignKey(
        Ventas,                     # Se conecta con el modelo Ventas
        on_delete=models.CASCADE,   # Si se borra la venta, se borran sus detalles
        related_name='detalles'     # Permite hacer venta.detalles.all() para ver todos los productos
    )
    
    # --- Relación: Producto que se vendió ---
    # Cada detalle está asociado a UN producto específico
    productos = models.ForeignKey(
        Productos,                  # Se conecta con el modelo Productos
        on_delete=models.PROTECT,   # NO se puede borrar un producto si tiene ventas registradas
        related_name='detalles_venta'
    )
    
    # --- Campo: Cantidad vendida ---
    # Cuántas unidades de este producto se vendieron
    # Ejemplo: si se vendieron 3 panes, cantidad = 3
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)]  # Mínimo 1 unidad
    )
    
    # --- Campo: Precio unitario ---
    # El precio de UNA unidad del producto al momento de la venta
    # Guardamos este dato porque el precio puede cambiar con el tiempo,
    # y necesitamos saber a qué precio se vendió EN ESE MOMENTO
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Campo: Porcentaje de descuento ---
    # Si este producto específico tiene descuento (0 a 100%)
    # Ejemplo: 10.00 significa 10% de descuento
    descuento_pct = models.DecimalField(
        max_digits=5,               # Hasta 999.99%
        decimal_places=2,
        blank=True,
        null=True,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # --- Método para calcular el subtotal de esta línea ---
    # Retorna: (cantidad × precio_unitario) - descuento
    def calcular_subtotal(self):
        """
        Calcula el subtotal de esta línea de venta.
        
        Ejemplo:
        - Cantidad: 2 panes
        - Precio unitario: $1.000
        - Descuento: 10%
        - Subtotal = (2 × $1.000) × 0.90 = $1.800
        """
        subtotal = self.cantidad * self.precio_unitario
        
        # Si hay descuento, lo aplicamos
        if self.descuento_pct and self.descuento_pct > 0:
            descuento = subtotal * (self.descuento_pct / 100)
            subtotal = subtotal - descuento
        
        return subtotal
    
    # --- Método para mostrar el detalle como texto ---
    def __str__(self):
        return f"{self.cantidad}x {self.productos.nombre} - ${self.calcular_subtotal()}"
    
    # --- Configuración del modelo ---
    class Meta:
        managed = False                 # La tabla ya existe en MySQL
        db_table = 'detalle_venta'      # Nombre de la tabla en la BD
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

