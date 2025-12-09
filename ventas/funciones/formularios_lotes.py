# ================================================================
# =                                                              =
# =           FORMULARIOS PARA GESTIÓN DE LOTES                 =
# =                                                              =
# ================================================================

from django import forms
from ventas.models import Productos, Lote
from ventas.funciones.validators import validador_fecha_no_futuro
from django.utils import timezone
from datetime import date


class LoteProduccionForm(forms.ModelForm):
    """
    Formulario para registrar un lote de producción propia.
    
    Se usa en el módulo de Producción para registrar productos
    producidos internamente (pan, pasteles, etc.)
    """
    
    # Campo adicional para seleccionar el producto
    # Solo productos activos (excluye inactivos y en_merma)
    producto = forms.ModelChoiceField(
        queryset=Productos.objects.filter(eliminado__isnull=True, estado_merma='activo'),
        required=True,
        label='Producto',
        help_text='Seleccione el producto producido'
    )
    
    class Meta:
        model = Lote
        fields = [
            'producto',
            'numero_lote',
            'cantidad_inicial',
            'fecha_elaboracion',
            'fecha_caducidad',
        ]
        widgets = {
            'numero_lote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PROD-2025-001 (opcional)'
            }),
            'cantidad_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.001',
                'step': '0.001',
                'placeholder': 'Ej: 20.5 (permite decimales para kg, litros)'
            }),
            'fecha_elaboracion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': timezone.now().date().isoformat()
            }),
            'fecha_caducidad': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'numero_lote': 'Número de Lote (Opcional)',
            'cantidad_inicial': 'Cantidad Producida',
            'fecha_elaboracion': 'Fecha de Elaboración',
            'fecha_caducidad': 'Fecha de Caducidad',
        }
        help_texts = {
            'cantidad_inicial': 'Cantidad producida en este lote (se mostrará la unidad del producto seleccionado)',
            'fecha_elaboracion': 'Fecha en que se elaboró el producto',
            'fecha_caducidad': 'Fecha en que vence el producto',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Prellenar fecha de elaboración con hoy si es nuevo lote
        if not self.instance.pk:
            self.fields['fecha_elaboracion'].initial = timezone.now().date()
        
        # Ajustar formatos de fecha
        self.fields['fecha_elaboracion'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_caducidad'].input_formats = ['%Y-%m-%d']
    
    def clean_cantidad_inicial(self):
        """Valida que la cantidad sea mayor a 0 (permite decimales)."""
        cantidad = self.cleaned_data.get('cantidad_inicial')
        if cantidad is None:
            raise forms.ValidationError('La cantidad es obligatoria')
        try:
            cantidad_decimal = Decimal(str(cantidad))
            if cantidad_decimal <= Decimal('0'):
                raise forms.ValidationError('La cantidad debe ser mayor a 0')
            return cantidad_decimal
        except (ValueError, TypeError):
            raise forms.ValidationError('La cantidad debe ser un número válido')
    
    def clean_fecha_elaboracion(self):
        """Valida que la fecha de elaboración no sea futura."""
        fecha = self.cleaned_data.get('fecha_elaboracion')
        if fecha:
            return validador_fecha_no_futuro(fecha, field_label="Fecha de elaboración")
        return fecha
    
    def clean_fecha_caducidad(self):
        """Valida que la fecha de caducidad sea posterior a la de elaboración."""
        fecha_caducidad = self.cleaned_data.get('fecha_caducidad')
        fecha_elaboracion = self.cleaned_data.get('fecha_elaboracion')
        
        if fecha_caducidad and fecha_elaboracion:
            if fecha_caducidad <= fecha_elaboracion:
                raise forms.ValidationError(
                    'La fecha de caducidad debe ser posterior a la fecha de elaboración'
                )
        
        return fecha_caducidad
    
    def save(self, commit=True):
        """Guarda el lote y actualiza el stock del producto."""
        instance = super().save(commit=False)
        
        # Asignar el producto
        producto = self.cleaned_data.get('producto')
        instance.productos = producto
        
        # Configurar origen y estado
        instance.origen = 'produccion_propia'
        instance.estado = 'activo'
        instance.cantidad = Decimal(str(instance.cantidad_inicial))  # Cantidad inicial = cantidad actual (Decimal)
        
        # Fecha de recepción es ahora
        instance.fecha_recepcion = timezone.now()
        
        if commit:
            instance.save()
            
            # Actualizar cantidad del producto (sumar el nuevo lote) - manejar Decimal
            cantidad_producto = Decimal(str(producto.cantidad)) if producto.cantidad else Decimal('0')
            cantidad_lote = Decimal(str(instance.cantidad))
            producto.cantidad = cantidad_producto + cantidad_lote
            
            stock_actual = Decimal(str(producto.stock_actual)) if producto.stock_actual is not None else Decimal('0')
            producto.stock_actual = stock_actual + cantidad_lote
            
            # Si el producto estaba en merma y ahora tiene lotes activos, reactivarlo
            if producto.estado_merma == 'en_merma':
                from ventas.models import Lote
                tiene_lotes_activos = Lote.objects.filter(
                    productos=producto,
                    estado='activo',
                    cantidad__gt=0
                ).exists()
                
                if tiene_lotes_activos:
                    # Reactivar el producto automáticamente
                    producto.estado_merma = 'activo'
                    # Actualizar fecha de caducidad con la del lote más antiguo (FIFO)
                    lote_mas_antiguo = Lote.objects.filter(
                        productos=producto,
                        estado='activo',
                        cantidad__gt=0
                    ).order_by('fecha_caducidad', 'fecha_recepcion').first()
                    
                    if lote_mas_antiguo:
                        producto.caducidad = lote_mas_antiguo.fecha_caducidad
                        if lote_mas_antiguo.fecha_elaboracion:
                            producto.elaboracion = lote_mas_antiguo.fecha_elaboracion
            
            producto.save()
            
            # Crear movimiento de inventario
            try:
                from ventas.models import MovimientosInventario
                MovimientosInventario.objects.create(
                    tipo_movimiento='entrada',
                    cantidad=instance.cantidad,
                    productos=producto,
                    origen='produccion_propia',
                    referencia_id=instance.id,
                    tipo_referencia='lote'
                )
            except Exception as e:
                # Si falla la creación del movimiento, registrar pero no fallar
                import logging
                logger = logging.getLogger('ventas')
                logger.warning(f'Error al crear movimiento de inventario para lote {instance.id}: {e}')
        
        return instance

