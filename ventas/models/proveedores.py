# ================================================================
# =                                                              =
# =         MODELOS PARA EL SISTEMA DE PROVEEDORES             =
# =                                                              =
# ================================================================
# 
# Este archivo contiene los modelos (estructuras de datos) necesarios
# para manejar los proveedores y facturas de compra en la Forneria. Incluye:
# 
# 1. Proveedor: Información de los proveedores de productos
# 2. FacturaProveedor: Registro de facturas de compra a proveedores
# 3. DetalleFacturaProveedor: Los productos específicos incluidos en cada factura
# 
# Estos modelos se conectan con las tablas que se crean en la base de datos MySQL.
#
# CARDINALIDADES:
# - Proveedor (1) ────< FacturaProveedor (N): Un proveedor puede tener muchas facturas
# - FacturaProveedor (1) ────< DetalleFacturaProveedor (N): Una factura puede tener muchos detalles
# - Productos (1) ────< DetalleFacturaProveedor (N): Un producto puede aparecer en muchos detalles
# - Relación N:M entre FacturaProveedor y Productos (a través de DetalleFacturaProveedor)

from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from .productos import Productos

# ================================================================
# =                    MODELO: PROVEEDOR                         =
# ================================================================
# 
# Este modelo representa a los proveedores de la fornería.
# Almacena información de contacto y datos comerciales del proveedor.

class Proveedor(models.Model):
    """
    Modelo que representa un proveedor de productos para la Fornería.
    
    Este modelo maneja toda la información de proveedores, incluyendo:
    - Información básica (nombre, RUT, contacto)
    - Datos de contacto (teléfono, email, dirección)
    - Estado del proveedor (activo/inactivo)
    """
    
    # ============================================================
    # OPCIONES DE ESTADO
    # ============================================================
    ESTADO_CHOICES = [
        ('activo', 'Activo'),       # Proveedor activo, puede recibir órdenes
        ('inactivo', 'Inactivo'),   # Proveedor inactivo, no se usa actualmente
    ]
    
    # ============================================================
    # CAMPOS BÁSICOS DEL PROVEEDOR
    # ============================================================
    nombre = models.CharField(
        max_length=150,
        help_text='Razón social o nombre del proveedor'
    )
    
    rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        help_text='RUT del proveedor (formato: 12345678-9)'
    )
    
    contacto = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Nombre de la persona de contacto'
    )
    
    # ============================================================
    # DATOS DE CONTACTO
    # ============================================================
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Teléfono de contacto'
    )
    
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        validators=[EmailValidator()],
        help_text='Correo electrónico del proveedor'
    )
    
    direccion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Dirección del proveedor'
    )
    
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Ciudad del proveedor'
    )
    
    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Región del proveedor'
    )
    
    # ============================================================
    # ESTADO Y NOTAS
    # ============================================================
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo',
        help_text='Estado del proveedor: activo o inactivo'
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales sobre el proveedor'
    )
    
    # ============================================================
    # TIMESTAMPS
    # ============================================================
    creado = models.DateTimeField(
        blank=True,
        null=True,
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    modificado = models.DateTimeField(
        blank=True,
        null=True,
        auto_now=True,
        help_text='Fecha de última modificación'
    )
    
    eliminado = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha de eliminación lógica'
    )
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    def __str__(self):
        return self.nombre
    
    def esta_activo(self):
        """
        Verifica si el proveedor está activo.
        
        Returns:
            bool: True si el proveedor está activo, False en caso contrario
        """
        return self.estado == 'activo' and self.eliminado is None
    
    def obtener_facturas_pendientes(self):
        """
        Obtiene todas las facturas pendientes de pago de este proveedor.
        
        Returns:
            QuerySet: Facturas con estado_pago='pendiente'
        """
        return self.facturas.filter(estado_pago='pendiente', eliminado__isnull=True)
    
    def obtener_total_pendiente(self):
        """
        Calcula el total de facturas pendientes de pago.
        
        Returns:
            Decimal: Suma de totales de facturas pendientes
        """
        facturas_pendientes = self.obtener_facturas_pendientes()
        return sum(factura.total for factura in facturas_pendientes)
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    class Meta:
        managed = False
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']


# ================================================================
# =                MODELO: FACTURA PROVEEDOR                     =
# ================================================================
# 
# Este modelo representa una factura de compra a un proveedor.
# Contiene información general de la transacción: fecha, totales, estado de pago, etc.

class FacturaProveedor(models.Model):
    """
    Modelo que representa una factura de compra a un proveedor.
    
    Este modelo maneja toda la información de facturas de compra, incluyendo:
    - Información de la factura (número, fechas)
    - Totales (subtotal, IVA, descuento, total)
    - Estado del pago
    - Relación con el proveedor
    """
    
    # ============================================================
    # OPCIONES DE ESTADO DE PAGO
    # ============================================================
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),     # Factura pendiente de pago
        ('pagado', 'Pagado'),           # Factura completamente pagada
        ('parcial', 'Pago Parcial'),    # Factura pagada parcialmente
        ('atrasado', 'Atrasado'),       # Factura vencida sin pagar
        ('cancelado', 'Cancelado'),     # Factura cancelada/anulada
    ]
    
    # ============================================================
    # INFORMACIÓN DE LA FACTURA
    # ============================================================
    numero_factura = models.CharField(
        max_length=50,
        help_text='Número de factura del proveedor'
    )
    
    fecha_factura = models.DateField(
        help_text='Fecha de emisión de la factura'
    )
    
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de vencimiento para pago'
    )
    
    fecha_recepcion = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha en que se recibió la factura (si es NULL, no se ha recibido)'
    )
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    def clean(self):
        """
        Validaciones personalizadas del modelo.
        """
        super().clean()
        
        # Validar que fecha_vencimiento sea posterior a fecha_factura
        if self.fecha_vencimiento and self.fecha_factura:
            if self.fecha_vencimiento < self.fecha_factura:
                raise ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior a la fecha de factura.'
                })
        
        # Validar que fecha_recepcion sea posterior o igual a fecha_factura
        if self.fecha_recepcion and self.fecha_factura:
            if self.fecha_recepcion < self.fecha_factura:
                raise ValidationError({
                    'fecha_recepcion': 'La fecha de recepción debe ser posterior o igual a la fecha de factura.'
                })
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para ejecutar validaciones.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ============================================================
    # TOTALES Y MONTOS
    # ============================================================
    # NOTA: Los nombres de campos coinciden con la estructura de la BD
    # Estos campos son nullable porque se calculan automáticamente
    subtotal_sin_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Subtotal sin IVA (se calcula automáticamente)',
        db_column='subtotal_sin_iva'
    )
    
    total_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Total de IVA (19%) (se calcula automáticamente)',
        db_column='total_iva'
    )
    
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Descuento aplicado'
    )
    
    total_con_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Total con IVA',
        db_column='total_con_iva'
    )
    
    # Propiedades para compatibilidad con código existente
    @property
    def subtotal(self):
        """Alias para subtotal_sin_iva"""
        return self.subtotal_sin_iva
    
    @subtotal.setter
    def subtotal(self, value):
        """Setter para subtotal_sin_iva"""
        self.subtotal_sin_iva = value
    
    @property
    def iva(self):
        """Alias para total_iva"""
        return self.total_iva
    
    @iva.setter
    def iva(self, value):
        """Setter para total_iva"""
        self.total_iva = value
    
    @property
    def total(self):
        """Alias para total_con_iva"""
        return self.total_con_iva
    
    @total.setter
    def total(self, value):
        """Setter para total_con_iva"""
        self.total_con_iva = value
    
    # ============================================================
    # ESTADO DE PAGO
    # ============================================================
    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO_CHOICES,
        default='pendiente',
        help_text='Estado del pago'
    )
    
    # NOTA: fecha_pago y metodo_pago están en la tabla pago_proveedor, no aquí
    
    # ============================================================
    # OBSERVACIONES
    # ============================================================
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones sobre la factura'
    )
    
    # ============================================================
    # RELACIÓN CON PROVEEDOR
    # ============================================================
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.RESTRICT,  # No se puede eliminar proveedor con facturas
        related_name='facturas',
        help_text='Proveedor que emitió la factura'
    )
    
    # ============================================================
    # TIMESTAMPS
    # ============================================================
    creado = models.DateTimeField(
        blank=True,
        null=True,
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    modificado = models.DateTimeField(
        blank=True,
        null=True,
        auto_now=True,
        help_text='Fecha de última modificación'
    )
    
    eliminado = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha de eliminación lógica'
    )
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.proveedor.nombre}"
    
    def calcular_total(self):
        """
        Calcula el total de la factura sumando todos los detalles.
        
        Returns:
            Decimal: Total calculado desde los detalles
        """
        total_detalles = sum(
            detalle.subtotal for detalle in self.detalles.all()
        )
        return total_detalles - self.descuento
    
    def actualizar_totales(self):
        """
        Actualiza los totales de la factura basándose en los detalles.
        Debe llamarse después de agregar, modificar o eliminar detalles.
        
        NOTA: En Chile, el IVA se calcula sobre el subtotal ANTES de descuentos,
        luego se aplica el descuento al total con IVA.
        """
        # Sumar todos los subtotales de los detalles (solo activos)
        subtotal_sin_descuento = sum(
            detalle.subtotal for detalle in self.detalles.all()
        )
        
        # Calcular IVA sobre el subtotal sin descuento (19% en Chile)
        # Redondear a 2 decimales
        from decimal import ROUND_HALF_UP
        self.total_iva = (subtotal_sin_descuento * Decimal('0.19')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Subtotal con IVA
        subtotal_con_iva = subtotal_sin_descuento + self.total_iva
        
        # Aplicar descuento al total con IVA y redondear a 2 decimales
        self.subtotal_sin_iva = subtotal_sin_descuento
        self.total_con_iva = (subtotal_con_iva - self.descuento).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Asegurar que el total no sea negativo
        if self.total_con_iva < 0:
            self.total_con_iva = Decimal('0.00')
        
        self.save()
    
    def esta_vencida(self):
        """
        Verifica si la factura está vencida (fecha_vencimiento pasada y no pagada).
        
        Returns:
            bool: True si está vencida, False en caso contrario
        """
        if not self.fecha_vencimiento:
            return False
        
        from datetime import date
        return (
            self.fecha_vencimiento < date.today() and
            self.estado_pago != 'pagado'
        )
    
    def dias_para_vencer(self):
        """
        Calcula cuántos días faltan para que la factura venza.
        
        Returns:
            int: Número de días (negativo si ya venció, None si no hay fecha)
        """
        if not self.fecha_vencimiento:
            return None
        
        from datetime import date
        delta = self.fecha_vencimiento - date.today()
        return delta.days
    
    def marcar_como_pagada(self, fecha_pago=None, metodo_pago=None):
        """
        Marca la factura como pagada.
        
        NOTA: Para registrar pagos, usar el modelo PagoProveedor.
        Este método solo cambia el estado.
        
        Args:
            fecha_pago: Fecha del pago (no se guarda aquí, usar PagoProveedor)
            metodo_pago: Método de pago (no se guarda aquí, usar PagoProveedor)
        """
        self.estado_pago = 'pagado'
        self.save()
    
    def marcar_como_recibida(self, fecha_recepcion=None):
        """
        Marca la factura como recibida físicamente.
        Esto permite actualizar el stock de productos.
        
        Args:
            fecha_recepcion: Fecha de recepción (default: hoy)
        """
        self.estado_recepcion = 'recibida'
        self.fecha_recepcion = fecha_recepcion or date.today()
        self.save()
        
        # Actualizar stock de todos los productos
        for detalle in self.detalles.all():
            detalle.actualizar_stock_producto()
    
    def cancelar_recepcion(self):
        """
        Cancela la recepción de una factura y revierte el stock.
        Solo funciona si la factura está en estado 'recibida'.
        """
        if self.estado_recepcion != 'recibida':
            raise ValueError(
                "Solo se pueden cancelar facturas que están en estado 'recibida'"
            )
        
        # Revertir stock de todos los productos
        for detalle in self.detalles.all():
            detalle.revertir_stock_producto()
        
        # Cambiar estado
        self.estado_recepcion = 'cancelada'
        self.save()
    
    def calcular_total_pagado(self):
        """
        Calcula el total pagado de esta factura sumando todos los pagos.
        
        Returns:
            Decimal: Total pagado
        """
        try:
            from .proveedores import PagoProveedor
            pagos = PagoProveedor.objects.filter(
                factura_proveedor=self
            )
            return sum(pago.monto for pago in pagos)
        except:
            # Si no existe el modelo PagoProveedor aún, retornar 0
            return Decimal('0.00')
    
    def calcular_saldo_pendiente(self):
        """
        Calcula el saldo pendiente de pago.
        
        Returns:
            Decimal: Saldo pendiente (total_con_iva - pagos)
        """
        total_pagado = self.calcular_total_pagado()
        return self.total_con_iva - total_pagado
    
    def actualizar_estado_pago_automatico(self):
        """
        Actualiza el estado de pago automáticamente según los pagos realizados.
        """
        total_pagado = self.calcular_total_pagado()
        
        # Usar comparación con tolerancia para decimales
        from decimal import Decimal
        if total_pagado <= Decimal('0.00'):
            nuevo_estado = 'pendiente'
        elif total_pagado >= self.total_con_iva:
            nuevo_estado = 'pagado'
        else:
            nuevo_estado = 'parcial'
        
        # Solo actualizar si el estado cambió
        if self.estado_pago != nuevo_estado:
            self.estado_pago = nuevo_estado
            self.save(update_fields=['estado_pago'])
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    class Meta:
        managed = False
        db_table = 'factura_proveedor'
        verbose_name = 'Factura de Proveedor'
        verbose_name_plural = 'Facturas de Proveedores'
        ordering = ['-fecha_factura']
        unique_together = [['numero_factura', 'proveedor']]


# ================================================================
# =          MODELO: DETALLE FACTURA PROVEEDOR                   =
# ================================================================
# 
# Este modelo representa cada producto individual dentro de una factura de proveedor.
# Por ejemplo, si una factura incluye 50 kg de harina y 20 kg de azúcar, habrá 2 registros
# de DetalleFacturaProveedor: uno para la harina y otro para el azúcar.

class DetalleFacturaProveedor(models.Model):
    """
    Modelo que representa un producto específico dentro de una factura de proveedor.
    
    Este modelo maneja:
    - Cantidad y precio unitario del producto
    - Descuento aplicado
    - Información del lote recibido
    - Relación con la factura y el producto
    """
    
    # ============================================================
    # RELACIONES
    # ============================================================
    factura_proveedor = models.ForeignKey(
        FacturaProveedor,
        on_delete=models.CASCADE,  # Si se elimina la factura, se eliminan sus detalles
        related_name='detalles',
        help_text='Factura a la que pertenece este detalle'
    )
    
    productos = models.ForeignKey(
        Productos,
        on_delete=models.RESTRICT,  # No se puede eliminar producto con detalles de factura
        related_name='detalles_factura_proveedor',
        help_text='Producto incluido en este detalle'
    )
    
    # ============================================================
    # CANTIDAD Y PRECIO
    # ============================================================
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Cantidad de productos recibidos'
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Precio unitario de compra'
    )
    
    descuento_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Porcentaje de descuento aplicado'
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Subtotal del detalle (cantidad * precio_unitario * (1 - descuento_pct/100))'
    )
    
    # ============================================================
    # INFORMACIÓN DEL LOTE
    # ============================================================
    fecha_vencimiento_producto = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de vencimiento del lote recibido (si se especifica, prevalece sobre la fecha del producto)'
    )
    
    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Número de lote del producto recibido'
    )
    
    observaciones = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text='Observaciones sobre este detalle'
    )
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    def __str__(self):
        return f"{self.cantidad}x {self.productos.nombre} - ${self.subtotal}"
    
    def calcular_subtotal(self):
        """
        Calcula el subtotal de este detalle.
        
        Returns:
            Decimal: Subtotal calculado
        """
        subtotal = self.cantidad * self.precio_unitario
        
        # Si hay descuento, lo aplicamos
        if self.descuento_pct and self.descuento_pct > 0:
            descuento = subtotal * (self.descuento_pct / 100)
            subtotal = subtotal - descuento
        
        return subtotal
    
    def actualizar_subtotal(self):
        """
        Actualiza el campo subtotal con el valor calculado.
        """
        self.subtotal = self.calcular_subtotal()
        self.save()
    
    def actualizar_stock_producto(self):
        """
        Actualiza el stock del producto cuando se recibe este detalle.
        Debe llamarse cuando se confirma la recepción de la factura.
        
        IMPORTANTE: Solo actualiza stock si la factura está en estado 'recibida'.
        También crea un movimiento de inventario para trazabilidad.
        """
        # Verificar que la factura esté recibida
        if self.factura_proveedor.estado_recepcion != 'recibida':
            raise ValueError(
                "No se puede actualizar stock. La factura debe estar en estado 'recibida'"
            )
        
        producto = self.productos
        
        # Actualizar cantidad y stock_actual
        producto.cantidad += self.cantidad
        if producto.stock_actual is not None:
            producto.stock_actual += self.cantidad
        else:
            producto.stock_actual = self.cantidad
        
        producto.save()
        
        # Crear movimiento de inventario para trazabilidad
        try:
            from .movimientos import MovimientosInventario
            MovimientosInventario.objects.create(
                tipo_movimiento='entrada',
                cantidad=self.cantidad,
                productos=producto,
                origen='compra',
                referencia_id=self.factura_proveedor.id,
                tipo_referencia='factura_proveedor'
            )
        except Exception as e:
            # Si falla la creación del movimiento, registrar pero no fallar
            print(f"Error al crear movimiento de inventario: {e}")
    
    def revertir_stock_producto(self):
        """
        Revierte el stock del producto cuando se cancela la recepción de la factura.
        Crea un movimiento de salida para mantener trazabilidad.
        """
        producto = self.productos
        
        # Revertir cantidad y stock_actual
        producto.cantidad = max(0, producto.cantidad - self.cantidad)
        if producto.stock_actual is not None:
            producto.stock_actual = max(0, producto.stock_actual - self.cantidad)
        
        producto.save()
        
        # Crear movimiento de inventario de salida para trazabilidad
        try:
            from .movimientos import MovimientosInventario
            MovimientosInventario.objects.create(
                tipo_movimiento='salida',
                cantidad=self.cantidad,
                productos=producto,
                origen='devolucion',
                referencia_id=self.factura_proveedor.id,
                tipo_referencia='factura_proveedor'
            )
        except Exception as e:
            # Si falla la creación del movimiento, registrar pero no fallar
            print(f"Error al crear movimiento de inventario: {e}")
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    class Meta:
        managed = False
        db_table = 'detalle_factura_proveedor'
        verbose_name = 'Detalle de Factura de Proveedor'
        verbose_name_plural = 'Detalles de Facturas de Proveedores'


# ================================================================
# =                MODELO: PAGO PROVEEDOR                         =
# ================================================================
# 
# Este modelo representa un pago realizado a una factura de proveedor.
# Permite registrar pagos parciales, múltiples pagos a una misma factura.

class PagoProveedor(models.Model):
    """
    Modelo que representa un pago realizado a una factura de proveedor.
    
    Este modelo permite:
    - Registrar pagos parciales
    - Múltiples pagos a una misma factura
    - Trazabilidad de pagos
    """
    
    # ============================================================
    # RELACIÓN CON FACTURA
    # ============================================================
    factura_proveedor = models.ForeignKey(
        FacturaProveedor,
        on_delete=models.RESTRICT,  # No se puede eliminar factura con pagos
        related_name='pagos',
        help_text='Factura a la que se aplica este pago'
    )
    
    # ============================================================
    # INFORMACIÓN DEL PAGO
    # ============================================================
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monto del pago'
    )
    
    fecha_pago = models.DateField(
        help_text='Fecha en que se realizó el pago'
    )
    
    metodo_pago = models.CharField(
        max_length=20,
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia'),
            ('cheque', 'Cheque'),
            ('tarjeta', 'Tarjeta'),
        ],
        default='efectivo',
        help_text='Método de pago utilizado'
    )
    
    numero_comprobante = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Número de comprobante o referencia del pago',
        db_column='numero_comprobante'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones sobre el pago'
    )
    
    # ============================================================
    # TIMESTAMPS
    # ============================================================
    creado = models.DateTimeField(
        blank=True,
        null=True,
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    def clean(self):
        """
        Validaciones personalizadas del modelo.
        """
        super().clean()
        
        # Validar que el monto no exceda el saldo pendiente
        if self.factura_proveedor_id:
            factura = FacturaProveedor.objects.get(id=self.factura_proveedor_id)
            saldo_pendiente = factura.calcular_saldo_pendiente()
            
            # Si es un pago nuevo (sin ID), verificar saldo
            if not self.id and self.monto > saldo_pendiente:
                raise ValidationError({
                    'monto': f'El monto del pago (${self.monto}) excede el saldo pendiente (${saldo_pendiente}).'
                })
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para ejecutar validaciones y actualizar estado de factura.
        """
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Actualizar estado de pago de la factura automáticamente
        if self.factura_proveedor:
            self.factura_proveedor.actualizar_estado_pago_automatico()
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    def __str__(self):
        return f"Pago ${self.monto} - Factura {self.factura_proveedor.numero_factura}"
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    class Meta:
        managed = False
        db_table = 'pago_proveedor'
        verbose_name = 'Pago de Proveedor'
        verbose_name_plural = 'Pagos de Proveedores'
        ordering = ['-fecha_pago']

