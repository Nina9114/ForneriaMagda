# Propuesta de Diseño Mejorada: Gestión de Merma

## 🎯 Propuesta del Usuario

**Concepto clave:** Un producto es un **SKU/Plantilla** que permanece en el sistema, no un lote específico.

### Lógica Propuesta:

1. **Producto = SKU permanente**
   - "Pan" es siempre "Pan", independiente del lote
   - El producto NO desaparece cuando va a merma
   - El producto permanece visible en inventario

2. **Merma = Reducción de stock, no cambio de estado**
   - Cuando va a merma: `cantidad = 0`
   - Se registra `motivo_merma` y `fecha_merma` (para historial)
   - `estado_merma` puede quedar como 'activo' o tener un estado especial
   - El producto sigue apareciendo en inventario (con cantidad 0)

3. **Reabastecimiento = Editar producto existente**
   - Cuando llega nuevo stock, editar el producto existente
   - Actualizar `cantidad`, `caducidad`, `elaboracion`
   - Limpiar `motivo_merma` y `fecha_merma`
   - No crear productos duplicados

## 📊 Comparación: Diseño Actual vs Propuesta

| Aspecto | Diseño Actual ❌ | Propuesta Usuario ✅ |
|---------|-----------------|---------------------|
| **Producto en merma** | Desaparece del inventario | Permanece visible (cantidad 0) |
| **Estado** | `estado_merma != 'activo'` | `estado_merma = 'activo'` (o especial) |
| **Cantidad** | Se mantiene | Se reduce a 0 |
| **Crear duplicados** | Permitido si está en merma | NO permitido (unicidad estricta) |
| **Reabastecer** | Crear nuevo producto | Editar producto existente |
| **Visibilidad** | Oculto en inventario | Visible con badge "En Merma" |
| **Historial** | Se mantiene | Se mantiene (motivo_merma) |

## 💡 Ventajas de la Propuesta

### ✅ Ventajas:

1. **Unicidad clara**
   - Un producto = un SKU
   - No hay confusión con duplicados
   - Validación simple y estricta

2. **Gestión simplificada**
   - No necesitas crear productos nuevos
   - Solo editas y rellenas el existente
   - Menos trabajo administrativo

3. **Historial completo**
   - El producto siempre existe
   - Puedes ver historial de mermas
   - Trazabilidad completa

4. **UX mejorada**
   - Productos siempre visibles
   - Fácil identificar qué necesita reabastecimiento
   - No se "pierden" productos

### ⚠️ Consideraciones:

1. **Visualización en inventario**
   - Necesita badge distintivo para productos en merma
   - Filtro para ocultar/mostrar productos con cantidad 0
   - UI clara para distinguir activos vs merma

2. **Lógica de estado**
   - ¿`estado_merma` sigue siendo necesario?
   - O usar solo `cantidad = 0` + `motivo_merma` para identificar merma?

3. **Filtros en consultas**
   - POS: filtrar `cantidad > 0` (ya lo hace)
   - Inventario: mostrar todos o filtrar cantidad
   - Reportes: considerar productos en merma

## 🔧 Implementación Propuesta

### Cambio 1: Lógica de Merma
```python
# Cuando se mueve a merma:
producto.cantidad = 0  # Reducir a 0
producto.motivo_merma = motivo  # Registrar motivo
producto.fecha_merma = timezone.now()  # Registrar fecha
producto.estado_merma = 'activo'  # Mantener activo (o crear estado 'en_merma')
producto.save()
```

### Cambio 2: Inventario
- Mostrar productos con cantidad 0
- Badge distintivo: "En Merma" o "Sin Stock"
- Filtro: "Mostrar/Ocultar productos en merma"

### Cambio 3: Validación
- Mantener unicidad estricta (sin excepciones)
- No permitir duplicados, incluso si cantidad = 0

### Cambio 4: Reabastecimiento
- Editar producto existente
- Actualizar cantidad, fechas
- Limpiar motivo_merma y fecha_merma

## 🎯 Decisión de Diseño

### Opción A: Mantener `estado_merma` pero con lógica diferente
- `estado_merma = 'en_merma'` cuando cantidad = 0 y motivo_merma existe
- `estado_merma = 'activo'` cuando cantidad > 0
- Permite filtrar fácilmente

### Opción B: Eliminar `estado_merma`, usar solo cantidad + motivo
- Si `cantidad = 0` y `motivo_merma` existe → está en merma
- Más simple, menos campos
- Requiere lógica en consultas

## ✅ Recomendación Final

**Implementar Opción A** con estos cambios:

1. **Nuevo estado:** `'en_merma'` (además de los existentes)
2. **Lógica de merma:**
   - `cantidad = 0`
   - `motivo_merma = motivo`
   - `fecha_merma = ahora`
   - `estado_merma = 'en_merma'`
3. **Inventario:**
   - Mostrar productos con `estado_merma = 'en_merma'`
   - Badge distintivo
   - Filtro opcional
4. **Validación:**
   - Unicidad estricta (sin excepciones)
   - No permitir duplicados
5. **Reabastecimiento:**
   - Editar producto
   - Actualizar cantidad
   - `estado_merma = 'activo'`
   - Limpiar motivo_merma y fecha_merma

