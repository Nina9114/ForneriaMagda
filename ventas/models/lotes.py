# ================================================================
# =                                                              =
# =           MODELO PARA GESTIÓN DE LOTES                      =
# =                                                              =
# ================================================================
#
# Este archivo define el modelo de Lote que permite rastrear
# diferentes lotes del mismo producto con diferentes fechas.
#
# PROPÓSITO:
# - Manejar múltiples lotes del mismo producto
# - Rastrear fechas de elaboración y caducidad por lote
# - Implementar FIFO (First In First Out) en ventas
# - Generar alertas de vencimiento por lote
#
# ORIGEN DE LOTES:
# - 'compra': Viene de factura de proveedor
# - 'produccion_propia': Producido internamente
# - 'ajuste_manual': Ajuste manual de stock

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date
from decimal import Decimal
from .productos import Productos
from .proveedores import DetalleFacturaProveedor


# ================================================================
# =                    MODELO: LOTE                              =
# ================================================================

class Lote(models.Model):
    """
    Modelo para gestionar lotes de productos.
    
    Un lote representa un grupo de productos del mismo tipo que:
    - Fueron producidos o comprados en la misma fecha
    - Tienen la misma fecha de elaboración
    - Tienen la misma fecha de caducidad
    
    Ejemplo:
    - Lote 1: 50 panes, elaboración 01/01/2025, caducidad 15/01/2025
    - Lote 2: 30 panes, elaboración 10/01/2025, caducidad 25/01/2025
    """
    
    # ============================================================
    # OPCIONES PARA EL ORIGEN DEL LOTE
    # ============================================================
    ORIGEN_CHOICES = [
        ('compra', 'Compra a Proveedor'),
        ('produccion_propia', 'Producción Propia'),
        ('ajuste_manual', 'Ajuste Manual'),
    ]
    
    # ============================================================
    # OPCIONES PARA EL ESTADO DEL LOTE
    # ============================================================
    ESTADO_CHOICES = [
        ('activo', 'Activo'),           # Lote con stock disponible
        ('inactivo', 'Inactivo'),       # Lote deshabilitado temporalmente (no disponible para venta)
        ('agotado', 'Agotado'),         # Lote sin stock (cantidad = 0)
        ('vencido', 'Vencido'),         # Lote que superó fecha de caducidad
        ('en_merma', 'En Merma'),       # Lote movido a merma
    ]
    
    # ============================================================
    # RELACIONES
    # ============================================================
    productos = models.ForeignKey(
        Productos,
        on_delete=models.CASCADE,
        related_name='lotes',
        help_text='Producto al que pertenece este lote'
    )
    
    detalle_factura_proveedor = models.ForeignKey(
        DetalleFacturaProveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes',
        help_text='Detalle de factura que originó este lote (si viene de compra)'
    )
    
    # ============================================================
    # INFORMACIÓN DEL LOTE
    # ============================================================
    numero_lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Número de lote del proveedor o código interno (opcional)'
    )
    
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Cantidad actual del lote (permite decimales para kg, litros, etc.)'
    )
    
    cantidad_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text='Cantidad original cuando se creó el lote (permite decimales para kg, litros, etc.)'
    )
    
    # ============================================================
    # FECHAS
    # ============================================================
    fecha_elaboracion = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de elaboración del lote'
    )
    
    fecha_caducidad = models.DateField(
        help_text='Fecha de caducidad del lote'
    )
    
    fecha_recepcion = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora en que se recibió/creó el lote en el sistema'
    )
    
    # ============================================================
    # ORIGEN Y ESTADO
    # ============================================================
    origen = models.CharField(
        max_length=20,
        choices=ORIGEN_CHOICES,
        default='produccion_propia',
        help_text='Origen del lote: compra, producción propia o ajuste manual'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo',
        help_text='Estado actual del lote'
    )
    
    # ============================================================
    # AUDITORÍA
    # ============================================================
    creado = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora de creación del registro'
    )
    
    modificado = models.DateTimeField(
        auto_now=True,
        help_text='Fecha y hora de última modificación'
    )
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    
    def __str__(self):
        """Representación en texto del lote."""
        origen_display = self.get_origen_display()
        return f"Lote #{self.id} - {self.productos.nombre} ({self.cantidad}/{self.cantidad_inicial}) - {origen_display}"
    
    def esta_vencido(self):
        """
        Verifica si el lote está vencido.
        
        Returns:
            bool: True si la fecha de caducidad es anterior a hoy, False en caso contrario
        """
        if self.fecha_caducidad is None:
            return False
        return self.fecha_caducidad < date.today()
    
    def dias_hasta_vencer(self):
        """
        Calcula cuántos días faltan para que el lote venza.
        
        Returns:
            int: Número de días (negativo si ya venció)
            None si no tiene fecha de caducidad
        """
        if self.fecha_caducidad is None:
            return None
        delta = self.fecha_caducidad - date.today()
        return delta.days
    
    def reducir_cantidad(self, cantidad_a_reducir):
        """
        Reduce la cantidad del lote (usado en ventas).
        
        Args:
            cantidad_a_reducir (Decimal): Cantidad a reducir (permite decimales)
            
        Returns:
            bool: True si se pudo reducir, False si no hay suficiente stock
        """
        cantidad_a_reducir = Decimal(str(cantidad_a_reducir))
        if cantidad_a_reducir > self.cantidad:
            return False
        
        self.cantidad -= cantidad_a_reducir
        
        # Si se agotó, cambiar estado
        if self.cantidad <= Decimal('0'):
            self.estado = 'agotado'
        
        self.save()
        return True
    
    def marcar_como_vencido(self):
        """Marca el lote como vencido si la fecha de caducidad pasó."""
        if self.esta_vencido() and self.estado == 'activo':
            self.estado = 'vencido'
            self.save()
    
    def mover_a_merma(self, motivo_merma=''):
        """
        Mueve el lote a merma.
        
        Args:
            motivo_merma (str): Motivo por el cual se mueve a merma
        """
        self.cantidad = 0
        self.estado = 'en_merma'
        self.save()
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    
    class Meta:
        managed = False  # Django NO creará esta tabla (ya existe en MySQL)
        db_table = 'lotes'
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['fecha_caducidad', 'fecha_recepcion']  # Ordenar por fecha de caducidad (FIFO)
        indexes = [
            models.Index(fields=['productos', 'estado']),
            models.Index(fields=['fecha_caducidad']),
            models.Index(fields=['origen']),
        ]

