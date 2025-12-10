# ================================================================
# =                                                              =
# =        MODELO: HISTORIAL DE MERMA                           =
# =                                                              =
# ================================================================
#
# Este modelo guarda el historial completo de productos en merma,
# permitiendo mantener todos los registros para reportes y métricas
# sin eliminar datos. Cada registro puede estar activo o inactivo.

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from .productos import Productos


# ================================================================
# =                MODELO: HISTORIAL MERMA                       =
# ================================================================

class HistorialMerma(models.Model):
    """
    Modelo que guarda el historial completo de productos en merma.
    
    Permite:
    - Mantener todos los registros de merma (no se eliminan)
    - Activar/desactivar registros en vez de eliminarlos
    - Generar reportes y métricas históricas
    - Rastrear cuándo un producto pasó a merma y por qué
    """
    
    # ============================================================
    # RELACIÓN CON PRODUCTO
    # ============================================================
    producto = models.ForeignKey(
        Productos,
        on_delete=models.CASCADE,
        related_name='historial_merma',
        help_text='Producto que pasó a merma'
    )
    
    # ============================================================
    # INFORMACIÓN DE LA MERMA
    # ============================================================
    cantidad_merma = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text='Cantidad que se fue a merma'
    )
    
    motivo_merma = models.TextField(
        help_text='Motivo detallado por el cual el producto fue movido a merma'
    )
    
    fecha_merma = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora en que el producto fue movido a merma'
    )
    
    # ============================================================
    # ESTADO DEL REGISTRO
    # ============================================================
    activo = models.BooleanField(
        default=True,
        help_text='Si True, el registro está activo. Si False, está inactivo (no se elimina)'
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
        estado = "Activo" if self.activo else "Inactivo"
        return f"Merma #{self.id} - {self.producto.nombre} ({self.cantidad_merma}) - {estado}"
    
    def desactivar(self):
        """Desactiva el registro de merma (no lo elimina)."""
        self.activo = False
        self.save(update_fields=['activo', 'modificado'])
    
    def activar(self):
        """Activa el registro de merma."""
        self.activo = True
        self.save(update_fields=['activo', 'modificado'])
    
    # ============================================================
    # CONFIGURACIÓN DEL MODELO
    # ============================================================
    
    class Meta:
        managed = False  # Django NO creará esta tabla (se creará con migración SQL)
        db_table = 'historial_merma'
        verbose_name = 'Registro de Merma'
        verbose_name_plural = 'Historial de Merma'
        ordering = ['-fecha_merma']
        indexes = [
            models.Index(fields=['producto', 'activo']),
            models.Index(fields=['fecha_merma']),
            models.Index(fields=['activo']),
        ]

