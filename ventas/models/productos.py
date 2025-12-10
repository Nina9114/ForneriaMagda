from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Categorias(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'categorias'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

class Nutricional(models.Model):
    calorias = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proteinas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    grasas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohidratos = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    azucares = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nutricional'
        verbose_name = 'Informacion Nutricional'
        verbose_name_plural = 'Informaciones Nutricionales'

class Productos(models.Model):
    """
    Modelo que representa un producto en el inventario de la Fornería.
    
    Este modelo maneja toda la información de productos, incluyendo:
    - Información básica (nombre, descripción, marca)
    - Precios y stock
    - Fechas de elaboración y caducidad
    - Estado de merma (para productos vencidos o deteriorados)
    """
    
    # ============================================================
    # OPCIONES DE ESTADO DE MERMA
    # ============================================================
    ESTADO_MERMA_CHOICES = [
        ('activo', 'Activo'),           # Producto en buen estado, disponible para venta
        ('inactivo', 'Inactivo'),       # Producto deshabilitado temporalmente (no disponible para venta)
        ('en_merma', 'En Merma'),       # Producto en merma (cantidad = 0, necesita reabastecimiento)
        ('vencido', 'Vencido'),         # Producto que superó su fecha de caducidad (deprecated, usar en_merma)
        ('deteriorado', 'Deteriorado'), # Producto en mal estado físico (deprecated, usar en_merma)
        ('dañado', 'Dañado'),           # Producto con daño en empaque o estructura (deprecated, usar en_merma)
        ('roto', 'Roto'),               # Producto roto o fracturado (deprecated, usar en_merma)
        ('robado', 'Robado'),           # Producto robado o extraviado (deprecated, usar en_merma)
        ('otro', 'Otro'),               # Otro motivo (deprecated, usar en_merma)
    ]
    
    # ============================================================
    # CAMPOS BÁSICOS DEL PRODUCTO
    # ============================================================
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # ============================================================
    # FECHAS
    # ============================================================
    caducidad = models.DateField(blank=True, null=True, help_text='Fecha de caducidad. NULL cuando el producto está en merma (ese lote ya no existe)')
    elaboracion = models.DateField(blank=True, null=True)
    creado = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modificado = models.DateTimeField(blank=True, null=True, auto_now=True)
    eliminado = models.DateTimeField(blank=True, null=True)
    
    # ============================================================
    # CLASIFICACIÓN Y FORMATO
    # ============================================================
    tipo = models.CharField(max_length=100, blank=True, null=True)
    formato = models.CharField(max_length=100, blank=True, null=True, help_text='[DEPRECATED] Usar unidad_stock y unidad_venta en su lugar')
    presentacion = models.CharField(max_length=100, blank=True, null=True, help_text='Peso/tamaño individual del producto (ej: 100g, 500ml) o presentación (Bolsa, Caja, Botella)')
    
    # ============================================================
    # UNIDADES DE MEDIDA (NUEVO - Sistema Híbrido)
    # ============================================================
    UNIDAD_CHOICES = [
        ('unidad', 'Unidad'),
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
    ]
    
    unidad_stock = models.CharField(
        max_length=20,
        choices=UNIDAD_CHOICES,
        default='unidad',
        help_text='Unidad en que se almacena el stock (unidad, kg, g, l, ml)'
    )
    
    unidad_venta = models.CharField(
        max_length=20,
        choices=UNIDAD_CHOICES,
        default='unidad',
        help_text='Unidad en que se vende el producto (unidad, kg, g, l, ml)'
    )
    
    precio_por_unidad_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Precio por unidad de venta (ej: precio por kilo, precio por litro, precio por unidad)'
    )
    
    # ============================================================
    # STOCK Y CANTIDAD
    # ============================================================
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Cantidad de stock (permite decimales para kg, litros, etc.)'
    )
    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Stock actual (permite decimales)'
    )
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Stock mínimo (permite decimales)'
    )
    stock_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Stock máximo (permite decimales)'
    )
    
    # ============================================================
    # ESTADO DE MERMA (NUEVO)
    # ============================================================
    estado_merma = models.CharField(
        max_length=20,
        choices=ESTADO_MERMA_CHOICES,
        default='activo',
        help_text='Estado del producto: activo, vencido, deteriorado o dañado'
    )
    
    # ============================================================
    # INFORMACIÓN ADICIONAL DE MERMA
    # ============================================================
    motivo_merma = models.TextField(
        blank=True,
        null=True,
        help_text='Motivo detallado por el cual el producto fue movido a merma (ej: roto, robado, vencido, etc.)'
    )
    
    fecha_merma = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha y hora en que el producto fue movido a merma'
    )
    
    cantidad_merma = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Cantidad de unidades que se fueron a merma (se guarda antes de poner cantidad en 0)'
    )
    
    # ============================================================
    # RELACIONES
    # ============================================================
    categorias = models.ForeignKey(Categorias, on_delete=models.SET_NULL, null=True, blank=True)
    nutricional = models.ForeignKey(Nutricional, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    def __str__(self):
        return self.nombre
    
    def esta_vencido(self):
        """
        Verifica si el producto está vencido comparando con la fecha actual.
        
        Returns:
            bool: True si el producto está vencido, False en caso contrario
            None si no tiene fecha de caducidad (producto en merma)
        """
        if self.caducidad is None:
            return None  # Producto en merma, no tiene caducidad
        from datetime import date
        return self.caducidad < date.today()
    
    def dias_hasta_vencer(self):
        """
        Calcula cuántos días faltan para que el producto venza.
        
        Returns:
            int: Número de días (negativo si ya venció)
            None si no tiene fecha de caducidad (producto en merma)
        """
        if self.caducidad is None:
            return None  # Producto en merma, no tiene caducidad
        from datetime import date
        delta = self.caducidad - date.today()
        return delta.days
    
    def es_merma(self):
        """
        Verifica si el producto está en estado de merma.
        
        Returns:
            bool: True si el producto está en merma (cantidad = 0 y estado = 'en_merma'), False si está activo
        """
        return self.estado_merma == 'en_merma' or (self.cantidad == Decimal('0') and self.motivo_merma)
    
    def mover_a_merma(self, motivo_merma=''):
        """
        Mueve el producto a estado de merma.
        Guarda la cantidad actual en cantidad_merma antes de ponerla en 0.
        Limpia el "contenido" del producto (cantidad, caducidad, elaboración) pero el SKU permanece.
        
        Args:
            motivo_merma (str): Motivo detallado (ej: 'roto', 'robado', 'vencido hace 2 días')
        """
        from django.utils import timezone
        
        # Guardar la cantidad que se va a merma antes de ponerla en 0
        self.cantidad_merma = self.cantidad if self.cantidad > Decimal('0') else Decimal('0')
        self.cantidad = Decimal('0')  # Reducir cantidad a 0
        self.caducidad = None  # Limpiar caducidad (ese lote ya no existe)
        self.elaboracion = None  # Limpiar elaboración (ese lote ya no existe)
        self.estado_merma = 'en_merma'  # Estado especial para productos en merma
        self.motivo_merma = motivo_merma
        self.fecha_merma = timezone.now()
        self.save()
    
    def reabastecer(self, nueva_cantidad, nueva_caducidad, nueva_elaboracion=None):
        """
        Reabastece un producto que estaba en merma.
        
        Args:
            nueva_cantidad (Decimal o int): Nueva cantidad de stock
            nueva_caducidad (date): Nueva fecha de caducidad
            nueva_elaboracion (date, optional): Nueva fecha de elaboración
        """
        """
        Reabastece un producto que estaba en merma.
        Actualiza cantidad y fechas, y lo reactiva, pero MANTIENE el historial de merma.
        
        Args:
            nueva_cantidad (int): Nueva cantidad de stock
            nueva_caducidad (date): Nueva fecha de caducidad (requerida)
            nueva_elaboracion (date, optional): Nueva fecha de elaboración
        """
        if nueva_caducidad is None:
            raise ValueError("La fecha de caducidad es requerida para reabastecer un producto")
        
        self.cantidad = nueva_cantidad
        self.caducidad = nueva_caducidad  # Nueva caducidad (requerida)
        self.estado_merma = 'activo'  # Reactivar producto
        # NO limpiar motivo_merma ni fecha_merma - mantener historial
        
        if nueva_elaboracion:
            self.elaboracion = nueva_elaboracion
        
        self.save()
    
    def eliminar_registro_merma(self):
        """
        Elimina el registro de merma manualmente.
        Limpia motivo_merma, fecha_merma y cantidad_merma, pero mantiene el estado actual.
        """
        self.motivo_merma = None
        self.fecha_merma = None
        self.cantidad_merma = None
        self.save()
    
    def tiene_historial_merma(self):
        """
        Verifica si el producto tiene historial de merma (aunque esté activo).
        
        Returns:
            bool: True si tiene motivo_merma, fecha_merma o cantidad_merma, False en caso contrario
        """
        return bool(self.motivo_merma or self.fecha_merma or (self.cantidad_merma and self.cantidad_merma > Decimal('0')))
    
    def calcular_cantidad_desde_lotes(self):
        """
        Calcula la cantidad total del producto desde sus lotes activos.
        
        Si el producto tiene lotes, retorna la suma de lotes activos.
        Si no tiene lotes, retorna la cantidad directa del producto.
        
        Returns:
            Decimal: Cantidad total calculada desde lotes o cantidad directa (permite decimales)
        """
        try:
            from .lotes import Lote
            from decimal import Decimal
            from django.db.models import Sum
            cantidad_lotes = Lote.objects.filter(
                productos=self,
                estado='activo'  # Solo lotes activos (excluye inactivos, agotados, vencidos, en_merma)
            ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0')
            
            # Convertir a Decimal si es necesario
            if not isinstance(cantidad_lotes, Decimal):
                cantidad_lotes = Decimal(str(cantidad_lotes))
            
            # Si tiene lotes, usar cantidad de lotes
            # Si no tiene lotes, usar cantidad directa (compatibilidad)
            if Lote.objects.filter(productos=self).exists():
                return cantidad_lotes
            else:
                return Decimal(str(self.cantidad)) if self.cantidad else Decimal('0')
        except Exception:
            # Si hay error (tabla no existe, etc.), retornar cantidad directa
            return Decimal(str(self.cantidad)) if self.cantidad else Decimal('0')
    
    def obtener_lote_mas_antiguo(self):
        """
        Obtiene el lote más antiguo (menor fecha de caducidad) con stock disponible.
        Se usa para FIFO en ventas.
        Solo considera lotes activos (excluye inactivos, agotados, vencidos, en_merma).
        
        Returns:
            Lote o None: El lote más antiguo con stock, o None si no hay lotes
        """
        try:
            from .lotes import Lote
            return Lote.objects.filter(
                productos=self,
                estado='activo',  # Solo lotes activos (excluye inactivos)
                cantidad__gt=Decimal('0')
            ).order_by('fecha_caducidad', 'fecha_recepcion').first()
        except Exception:
            return None
    
    def obtener_fecha_caducidad_mas_proxima(self):
        """
        Obtiene la fecha de caducidad del lote más antiguo (para alertas).
        
        Returns:
            date o None: Fecha de caducidad más próxima, o None si no hay lotes
        """
        lote = self.obtener_lote_mas_antiguo()
        return lote.fecha_caducidad if lote else self.caducidad
    
    def calcular_perdida(self):
        """
        Calcula la pérdida económica del producto (cantidad_merma × precio).
        Usa cantidad_merma si está disponible, sino usa cantidad.
        
        Returns:
            Decimal: Pérdida total del producto
        """
        cantidad_perdida = self.cantidad_merma if (self.cantidad_merma and self.cantidad_merma > Decimal('0')) else self.cantidad
        return Decimal(str(cantidad_perdida)) * self.precio_por_unidad_venta
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    class Meta:
        managed = False
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'