# Análisis y Propuesta: Sistema de Unidades de Medida

## 🔍 Problema Identificado

### Situación Actual
1. **Campo `cantidad`**: Es `IntegerField` (solo números enteros)
   - ❌ No puede manejar 1.5 kilos, 250 gramos, 0.5 litros
   - ❌ Solo permite unidades enteras

2. **Campo `formato`**: Se construye como texto (ej: "1 kg")
   - ❌ No se usa para cálculos de venta
   - ❌ No distingue entre unidad de stock y unidad de venta
   - ❌ Confusión: ¿el precio es por unidad o por formato?

3. **POS (Punto de Venta)**:
   - ❌ Solo permite vender por "cantidad" (unidades enteras)
   - ❌ No permite vender por peso/volumen (kilos, gramos, litros)
   - ❌ Ejemplo: Pan por kilo - llegaron 20 kg, cliente quiere 1.5 kg → IMPOSIBLE

### Casos de Uso Reales

#### Caso 1: Productos por Unidad
- **Pan individual**: Se vende por unidad (1 pan, 2 panes, 3 panes)
- **Stock**: 50 panes
- **Precio**: $500 por pan
- ✅ Funciona con sistema actual

#### Caso 2: Productos por Peso
- **Pan por kilo**: Se vende por peso (0.5 kg, 1.2 kg, 2.5 kg)
- **Stock**: 20 kilos
- **Precio**: $3,000 por kilo
- ❌ NO funciona con sistema actual

#### Caso 3: Productos por Volumen
- **Aceite**: Se vende por litro (0.5 L, 1.2 L)
- **Stock**: 50 litros
- **Precio**: $2,500 por litro
- ❌ NO funciona con sistema actual

#### Caso 4: Productos Mixtos
- **Harina en bolsas**: Stock por bolsas (unidades), pero se puede vender por kilo
- **Stock**: 30 bolsas de 1 kg cada una = 30 kg total
- **Precio**: $2,000 por bolsa O $2,000 por kilo
- ❌ NO funciona con sistema actual

---

## 💡 Propuesta de Solución

### Opción A: Sistema Híbrido (Recomendada) ⭐

**Concepto**: Separar claramente **Unidad de Stock** vs **Unidad de Venta**

#### Cambios en el Modelo `Productos`:

```python
# NUEVOS CAMPOS
unidad_stock = models.CharField(
    max_length=20,
    choices=[
        ('unidad', 'Unidad'),
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
    ],
    default='unidad',
    help_text='Unidad en que se almacena el stock'
)

cantidad = models.DecimalField(  # CAMBIO: IntegerField → DecimalField
    max_digits=10,
    decimal_places=3,  # Permite decimales (ej: 20.5 kg, 1.250 L)
    default=0,
    validators=[MinValueValidator(0)]
)

unidad_venta = models.CharField(
    max_length=20,
    choices=[
        ('unidad', 'Unidad'),
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
    ],
    default='unidad',
    help_text='Unidad en que se vende el producto'
)

precio_por_unidad_venta = models.DecimalField(  # NUEVO
    max_digits=10,
    decimal_places=2,
    validators=[MinValueValidator(0)],
    help_text='Precio por unidad de venta (ej: precio por kilo, precio por litro)'
)

# MANTENER (para compatibilidad)
formato = models.CharField(max_length=100, blank=True, null=True)  # Deprecated
```

#### Ejemplos de Uso:

**Ejemplo 1: Pan por Unidad**
```
nombre: "Pan Integral"
unidad_stock: "unidad"
cantidad: 50.000
unidad_venta: "unidad"
precio_por_unidad_venta: 500.00
→ Stock: 50 panes, Precio: $500 por pan
```

**Ejemplo 2: Pan por Kilo**
```
nombre: "Pan por Kilo"
unidad_stock: "kg"
cantidad: 20.500
unidad_venta: "kg"
precio_por_unidad_venta: 3000.00
→ Stock: 20.5 kilos, Precio: $3,000 por kilo
```

**Ejemplo 3: Pan por Kilo (pero stock en gramos)**
```
nombre: "Pan por Kilo"
unidad_stock: "g"
cantidad: 20500.000  # 20.5 kg en gramos
unidad_venta: "kg"
precio_por_unidad_venta: 3000.00
→ Stock: 20,500 gramos (20.5 kg), Precio: $3,000 por kilo
```

#### Cambios en POS:

1. **Mostrar unidad de venta** junto al precio:
   ```
   Pan por Kilo
   $3,000 / kg
   Stock: 20.5 kg
   ```

2. **Input flexible según unidad_venta**:
   - Si `unidad_venta == 'unidad'`: Input entero (1, 2, 3...)
   - Si `unidad_venta == 'kg'`: Input decimal (0.5, 1.2, 2.5...)
   - Si `unidad_venta == 'g'`: Input decimal (250.5, 1000...)
   - Si `unidad_venta == 'l'`: Input decimal (0.5, 1.2...)
   - Si `unidad_venta == 'ml'`: Input decimal (250, 500...)

3. **Cálculo de precio**:
   ```javascript
   subtotal = cantidad_venta * precio_por_unidad_venta
   ```

4. **Validación de stock**:
   - Convertir `cantidad` (stock) a unidad de venta si es necesario
   - Validar que `cantidad_venta <= stock_disponible`

---

### Opción B: Sistema de Conversión Automática

**Concepto**: Sistema más complejo con conversiones automáticas entre unidades.

**Ventajas**:
- ✅ Máxima flexibilidad
- ✅ Permite múltiples unidades de venta para el mismo producto

**Desventajas**:
- ❌ Más complejo de implementar
- ❌ Requiere tabla de conversiones
- ❌ Puede generar confusión

**No recomendada** para este caso de uso.

---

## 🎯 Recomendación Final

### Implementar **Opción A: Sistema Híbrido**

**Razones**:
1. ✅ Soluciona todos los casos de uso
2. ✅ Fácil de entender para usuarios
3. ✅ Implementación relativamente simple
4. ✅ Mantiene compatibilidad con productos por unidad
5. ✅ Escalable para futuras necesidades

### Plan de Implementación

#### Fase 1: Modificar Modelo y Base de Datos
1. Agregar campos nuevos a tabla `productos`
2. Migrar datos existentes:
   - `unidad_stock = 'unidad'` (por defecto)
   - `unidad_venta = 'unidad'` (por defecto)
   - `precio_por_unidad_venta = precio` (copiar precio actual)
   - `cantidad` convertir a DecimalField (mantener valores)

#### Fase 2: Actualizar Formularios
1. Formulario "Agregar Producto":
   - Selector de `unidad_stock`
   - Input `cantidad` (decimal)
   - Selector de `unidad_venta`
   - Input `precio_por_unidad_venta`
   - Eliminar campos confusos de `formato`

2. Formulario "Editar Producto":
   - Mismos campos que agregar

#### Fase 3: Actualizar POS
1. Mostrar unidad de venta en tarjetas de productos
2. Input flexible según `unidad_venta`
3. Validación de stock con conversión si es necesario
4. Cálculo correcto de subtotales

#### Fase 4: Actualizar Reportes y Vistas
1. Mostrar unidad correcta en inventario
2. Actualizar reportes para usar nuevas unidades
3. Actualizar dashboard y métricas

---

## 📊 Comparación de Opciones

| Característica | Sistema Actual | Opción A (Híbrido) | Opción B (Conversión) |
|---------------|----------------|-------------------|----------------------|
| Productos por unidad | ✅ Funciona | ✅ Funciona | ✅ Funciona |
| Productos por peso | ❌ No funciona | ✅ Funciona | ✅ Funciona |
| Productos por volumen | ❌ No funciona | ✅ Funciona | ✅ Funciona |
| Flexibilidad | ❌ Baja | ✅ Media | ✅ Alta |
| Complejidad | ✅ Baja | ✅ Media | ❌ Alta |
| Tiempo implementación | - | 2-3 días | 5-7 días |
| Facilidad de uso | ⚠️ Confusa | ✅ Clara | ⚠️ Puede confundir |

---

## ✅ Conclusión

**Recomendación**: Implementar **Opción A (Sistema Híbrido)**

Esta solución:
- ✅ Resuelve todos los problemas identificados
- ✅ Es clara y fácil de usar
- ✅ Mantiene compatibilidad con productos existentes
- ✅ Permite crecimiento futuro
- ✅ Implementación en tiempo razonable

¿Procedemos con la implementación de la Opción A?

