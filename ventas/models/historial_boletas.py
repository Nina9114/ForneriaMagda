# ================================================================
# =                                                              =
# =           MODELO: HISTORIAL DE BOLETAS                      =
# =                                                              =
# ================================================================
#
# Este modelo almacena un snapshot (copia) de cada boleta emitida
# para auditoría y revisión histórica. Permite:
# - Revisar boletas emitidas
# - Detectar modificaciones o errores
# - Reconstruir boletas originales
# - Auditoría de caja
#
# ESTRATEGIA DE ALMACENAMIENTO:
# - Guardar datos estructurados en JSON (eficiente, no ocupa mucho espacio)
# - No guardar PDFs como blobs (ocupan mucho espacio)
# - Generar PDFs bajo demanda cuando se necesiten
# - Incluir metadatos para búsqueda rápida

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import json


class HistorialBoletas(models.Model):
    """
    Modelo que almacena un snapshot de cada boleta emitida.
    
    Almacena los datos estructurados de la boleta en formato JSON
    para permitir reconstrucción y auditoría sin ocupar mucho espacio.
    """
    
    # ============================================================
    # RELACIÓN CON LA VENTA ORIGINAL
    # ============================================================
    venta = models.ForeignKey(
        'ventas.Ventas',
        on_delete=models.PROTECT,  # No eliminar si hay historial
        related_name='historial_boletas',
        help_text='Venta original asociada a esta boleta'
    )
    
    # ============================================================
    # METADATOS PARA BÚSQUEDA RÁPIDA
    # ============================================================
    folio = models.CharField(
        max_length=20,
        db_index=True,  # Índice para búsquedas rápidas
        help_text='Folio de la boleta (ej: BOL-20251209123456)'
    )
    
    fecha_emision = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # Índice para búsquedas por fecha
        help_text='Fecha y hora en que se emitió la boleta'
    )
    
    fecha_venta = models.DateTimeField(
        help_text='Fecha y hora de la venta original'
    )
    
    # ============================================================
    # DATOS RESUMIDOS PARA BÚSQUEDA Y FILTRADO
    # ============================================================
    cliente_nombre = models.CharField(
        max_length=150,
        help_text='Nombre del cliente (para búsqueda rápida)'
    )
    
    total_con_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Total de la venta con IVA'
    )
    
    num_productos = models.IntegerField(
        default=0,
        help_text='Número de productos en la boleta'
    )
    
    canal_venta = models.CharField(
        max_length=20,
        choices=[
            ('presencial', 'Presencial'),
            ('delivery', 'Delivery'),
        ],
        help_text='Canal de venta'
    )
    
    # ============================================================
    # DATOS COMPLETOS EN JSON
    # ============================================================
    datos_boleta = models.JSONField(
        help_text='Datos completos de la boleta en formato JSON (cabecera + detalles)'
    )
    
    # ============================================================
    # INFORMACIÓN DE AUDITORÍA
    # ============================================================
    usuario_emisor = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text='Usuario que emitió la boleta'
    )
    
    modificado = models.BooleanField(
        default=False,
        help_text='Indica si la boleta fue modificada después de emitida'
    )
    
    fecha_modificacion = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha de última modificación (si aplica)'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones sobre esta boleta (errores, correcciones, etc.)'
    )
    
    # ============================================================
    # MÉTODOS
    # ============================================================
    def __str__(self):
        return f"Boleta {self.folio} - {self.fecha_emision.strftime('%d/%m/%Y %H:%M')}"
    
    def get_datos_boleta_dict(self):
        """
        Retorna los datos de la boleta como diccionario Python.
        """
        if isinstance(self.datos_boleta, str):
            return json.loads(self.datos_boleta)
        return self.datos_boleta or {}
    
    def set_datos_boleta_dict(self, datos):
        """
        Guarda los datos de la boleta como JSON.
        """
        if isinstance(datos, dict):
            self.datos_boleta = datos
        else:
            self.datos_boleta = json.loads(datos) if isinstance(datos, str) else {}
    
    class Meta:
        db_table = 'historial_boletas'
        verbose_name = 'Historial de Boleta'
        verbose_name_plural = 'Historial de Boletas'
        ordering = ['-fecha_emision']
        indexes = [
            models.Index(fields=['folio']),
            models.Index(fields=['fecha_emision']),
            models.Index(fields=['cliente_nombre']),
        ]

