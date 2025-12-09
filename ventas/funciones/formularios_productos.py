from django import forms
from django.db.models import Q
from decimal import Decimal
from ventas.models.productos import Productos, Categorias, Nutricional
from ventas.funciones.validators import (
    validador_texto_estricto,
    validador_texto_opcional_estricto,
    validador_precio_decimal_estricto,
    validador_entero_no_negativo,
    validador_fecha_no_futuro,
    validador_fecha_no_pasado,
    validador_texto_solo_letras_opcional,
    validador_decimal_opcional_no_negativo,
)

class ProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar productos con sistema de unidades de medida.
    
    Nuevo sistema:
    - unidad_stock: Unidad en que se almacena (unidad, kg, g, l, ml)
    - unidad_venta: Unidad en que se vende (puede ser diferente)
    - precio_por_unidad_venta: Precio por unidad de venta
    - cantidad: Permite decimales (para kg, litros, etc.)
    """

    class Meta:
        model = Productos
        fields = [
            'nombre', 'descripcion', 'marca', 
            'unidad_stock', 'unidad_venta', 'precio_por_unidad_venta',
            'cantidad', 'stock_minimo', 'stock_maximo',
            'caducidad', 'elaboracion', 'tipo',
            'categorias', 'presentacion'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Pan Integral',
                'autocomplete': 'off',
                'inputmode': 'text',
            }),
            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Ej: Descripción breve',
                'autocomplete': 'off',
                'inputmode': 'text',
            }),
            'marca': forms.TextInput(attrs={
                'placeholder': 'Ej: Fornería',
                'autocomplete': 'off',
                'inputmode': 'text',
            }),
            'tipo': forms.TextInput(attrs={
                'placeholder': 'Ej: Panadería',
                'autocomplete': 'off',
                'inputmode': 'text',
            }),
            'formato': forms.HiddenInput(),  # se completa en save()
            'categorias': forms.Select(attrs={'title': 'Selecciona una categoría'}),
            'caducidad': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'elaboracion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'unidad_stock': forms.Select(attrs={
                'class': 'form-control',
                'title': 'Unidad en que se almacena el stock'
            }),
            'unidad_venta': forms.Select(attrs={
                'class': 'form-control',
                'title': 'Unidad en que se vende el producto'
            }),
            'precio_por_unidad_venta': forms.NumberInput(attrs={
                'min': '0', 'step': '0.01', 'inputmode': 'decimal',
                'placeholder': 'Ej: 3000.00',
                'pattern': r'\d{1,8}(\.\d{1,2})?',
                'title': 'Precio por unidad de venta (ej: precio por kilo, precio por litro)'
            }),
            'cantidad': forms.NumberInput(attrs={
                'min': '0', 'step': '0.001', 'inputmode': 'decimal',
                'placeholder': 'Ej: 20.5 (permite decimales para kg, litros)',
                'pattern': r'\d+(\.\d{1,3})?'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'min': '0', 'step': '0.001', 'inputmode': 'decimal',
                'placeholder': 'Ej: 5.0 (permite decimales)',
                'pattern': r'\d+(\.\d{1,3})?'
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'min': '0', 'step': '0.001', 'inputmode': 'decimal',
                'placeholder': 'Ej: 100.0 (permite decimales)',
                'pattern': r'\d+(\.\d{1,3})?'
            }),
            'presentacion': forms.TextInput(attrs={
                'placeholder': 'Ej: 100g, 500ml, Bolsa, Caja (peso/tamaño o presentación)',
                'autocomplete': 'off',
                'inputmode': 'text',
                'title': 'Peso/tamaño individual del producto (ej: 100g por galleta) o presentación (Bolsa, Caja)'
            }),
        }

    def clean_nombre(self):
        return validador_texto_estricto(self.cleaned_data.get('nombre'),
                                        field_label="Nombre del producto", max_len=100)

    def clean_descripcion(self):
        return validador_texto_opcional_estricto(self.cleaned_data.get('descripcion'),
                                                 field_label="Descripción", max_len=300)

    def clean_marca(self):
        # Permite letras, números y espacios; sin signos especiales
        return validador_texto_opcional_estricto(self.cleaned_data.get('marca'),
                                                 field_label="Marca", max_len=100)

    def clean_elaboracion(self):
        # Elaboración opcional: permitir vacío
        valor = self.cleaned_data.get('elaboracion')
        if valor in (None, ''):
            return None
        from ventas.funciones.validators import validador_fecha_no_futuro
        return validador_fecha_no_futuro(valor, field_label="Fecha de elaboración")

    def clean_caducidad(self):
        # Caducidad ahora puede ser NULL (para productos en merma)
        caducidad = self.cleaned_data.get('caducidad')
        if caducidad is None:
            return None  # Permitir NULL para productos en merma
        return validador_fecha_no_pasado(caducidad, field_label="Fecha de caducidad")

    def clean(self):
        cleaned = super().clean()
        elaboracion = cleaned.get('elaboracion')
        caducidad = cleaned.get('caducidad')
        if elaboracion and caducidad and elaboracion > caducidad:
            self.add_error('caducidad', 'La caducidad debe ser posterior a la fecha de elaboración.')

        # Unicidad por combinación nombre+marca (case-insensitive).
        # IMPORTANTE: Validación estricta - no permite duplicados, incluso si está en merma
        # Si un producto está en merma, debe reabastecerse editando el existente, no creando uno nuevo
        nombre = cleaned.get('nombre')
        marca = cleaned.get('marca') or None  # el validador opcional puede dejar None/""

        if nombre:
            if not marca:
                # Marca vacía/None: considerar equivalentes NULL y "" en BD
                qs = Productos.objects.filter(
                    nombre__iexact=nombre,
                    eliminado__isnull=True  # Solo productos no eliminados
                ).filter(Q(marca__isnull=True) | Q(marca__exact=''))
            else:
                qs = Productos.objects.filter(
                    nombre__iexact=nombre,
                    marca__iexact=marca,
                    eliminado__isnull=True  # Solo productos no eliminados
                )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error('nombre', 'Ya existe un producto con este nombre y marca. Si está en merma, edítalo para reabastecerlo.')

        return cleaned


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dejamos "categorias" OPCIONAL como comentaste
        self.fields['categorias'].required = False

        # Mostramos SOLO estas dos opciones en el select
        opciones = ['Perecible', 'No perecible']

        # Buscamos si existen esas categorías en la BD
        qs = Categorias.objects.filter(nombre__in=opciones)

        # Si faltan, las creamos para que el select siempre muestre ambas
        if qs.count() < 2:
            for nombre in opciones:
                # Crea la categoría si no existe (con una descripción simple)
                Categorias.objects.get_or_create(
                    nombre=nombre,
                    defaults={'descripcion': f'Categoria {nombre.lower()}'}
                )
            qs = Categorias.objects.filter(nombre__in=opciones)

        # Asignamos el queryset filtrado y ordenado
        self.fields['categorias'].queryset = qs.order_by('nombre')

        # Quitamos el "---" y usamos un texto claro como placeholder
        self.fields['categorias'].empty_label = "Selecciona categoría..."

        # Prellenar fechas y ajustar formatos de entrada
        self.fields['caducidad'].initial = getattr(self.instance, 'caducidad', None)
        self.fields['elaboracion'].initial = getattr(self.instance, 'elaboracion', None)
        self.fields['caducidad'].input_formats = ['%Y-%m-%d']
        self.fields['elaboracion'].input_formats = ['%Y-%m-%d']
        
        # Prefill de unidades al editar
        if self.instance.pk:
            self.fields['unidad_stock'].initial = getattr(self.instance, 'unidad_stock', 'unidad')
            self.fields['unidad_venta'].initial = getattr(self.instance, 'unidad_venta', 'unidad')
            self.fields['precio_por_unidad_venta'].initial = getattr(self.instance, 'precio_por_unidad_venta', None) or getattr(self.instance, 'precio', None)

    def clean_tipo(self):
        # Validamos “tipo” permitiendo SOLO letras y espacios.
        # Este campo se mantiene OPCIONAL (puede venir vacío).
        return validador_texto_solo_letras_opcional(
            self.cleaned_data.get('tipo'),
            field_label="Tipo",
            max_len=100
        )


    def clean_cantidad(self):
        """Valida cantidad permitiendo decimales."""
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None:
            return Decimal('0')
        try:
            cantidad_decimal = Decimal(str(cantidad))
            if cantidad_decimal < Decimal('0'):
                raise forms.ValidationError("La cantidad no puede ser negativa.")
            return cantidad_decimal
        except (ValueError, TypeError):
            raise forms.ValidationError("La cantidad debe ser un número válido.")
    
    def clean_stock_minimo(self):
        """Valida stock_minimo permitiendo decimales."""
        stock_min = self.cleaned_data.get('stock_minimo')
        if stock_min is None:
            return None
        try:
            stock_decimal = Decimal(str(stock_min))
            if stock_decimal < Decimal('0'):
                raise forms.ValidationError("El stock mínimo no puede ser negativo.")
            return stock_decimal
        except (ValueError, TypeError):
            raise forms.ValidationError("El stock mínimo debe ser un número válido.")
    
    def clean_stock_maximo(self):
        """Valida stock_maximo permitiendo decimales."""
        stock_max = self.cleaned_data.get('stock_maximo')
        if stock_max is None:
            return None
        try:
            stock_decimal = Decimal(str(stock_max))
            if stock_decimal < Decimal('0'):
                raise forms.ValidationError("El stock máximo no puede ser negativo.")
            return stock_decimal
        except (ValueError, TypeError):
            raise forms.ValidationError("El stock máximo debe ser un número válido.")
    
    def clean_precio_por_unidad_venta(self):
        """Valida precio_por_unidad_venta."""
        from ventas.funciones.validators import validador_precio_decimal_estricto
        return validador_precio_decimal_estricto(
            self.cleaned_data.get('precio_por_unidad_venta'), 
            field_label="Precio por unidad de venta"
        )

    def clean_elaboracion(self):
        # Elaboración opcional: permitir vacío
        valor = self.cleaned_data.get('elaboracion')
        if valor in (None, ''):
            return None
        from ventas.funciones.validators import validador_fecha_no_futuro
        return validador_fecha_no_futuro(valor, field_label="Fecha de elaboración")


    def save(self, commit=True):
        instance = super().save(commit=False)

        # Mantener compatibilidad: copiar precio_por_unidad_venta a precio (para compatibilidad con código existente)
        if instance.precio_por_unidad_venta:
            instance.precio = instance.precio_por_unidad_venta

        # Mantener compatibilidad: copiar presentacion a formato (para compatibilidad con código que aún usa formato)
        # Siempre actualizar formato con presentacion si presentacion tiene valor
        if instance.presentacion:
            instance.formato = instance.presentacion

        # Asegurar que 'nutricional_id' nunca sea NULL
        if instance.nutricional_id is None:
            instance.nutricional = Nutricional.objects.create()

        # Fallback de categoría si no se seleccionó
        if instance.categorias_id is None:
            cat, _ = Categorias.objects.get_or_create(
                nombre='No perecible',
                defaults={'descripcion': 'Categoria no perecible'}
            )
            instance.categorias = cat

        if commit:
            instance.save()
        return instance

class NutricionalForm(forms.ModelForm):
    def clean_calorias(self):
        from ventas.funciones.validators import validador_decimal_opcional_no_negativo
        return validador_decimal_opcional_no_negativo(self.cleaned_data.get('calorias'), "Calorías")

    def clean_proteinas(self):
        from ventas.funciones.validators import validador_decimal_opcional_no_negativo
        return validador_decimal_opcional_no_negativo(self.cleaned_data.get('proteinas'), "Proteínas")

    def clean_grasas(self):
        from ventas.funciones.validators import validador_decimal_opcional_no_negativo
        return validador_decimal_opcional_no_negativo(self.cleaned_data.get('grasas'), "Grasas")

    def clean_carbohidratos(self):
        from ventas.funciones.validators import validador_decimal_opcional_no_negativo
        return validador_decimal_opcional_no_negativo(self.cleaned_data.get('carbohidratos'), "Carbohidratos")

    def clean_azucares(self):
        from ventas.funciones.validators import validador_decimal_opcional_no_negativo
        return validador_decimal_opcional_no_negativo(self.cleaned_data.get('azucares'), "Azúcares")

    def clean_sodio(self):
        from ventas.funciones.validators import validador_decimal_opcional_no_negativo
        return validador_decimal_opcional_no_negativo(self.cleaned_data.get('sodio'), "Sodio")
    class Meta:
        model = Nutricional
        fields = ['calorias', 'proteinas', 'grasas', 'carbohidratos', 'azucares', 'sodio']
        widgets = {
            'calorias': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Ej: 250'}),
            'proteinas': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'grasas': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'carbohidratos': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'azucares': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'sodio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }