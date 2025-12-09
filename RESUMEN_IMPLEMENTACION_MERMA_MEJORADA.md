# Resumen de Implementación: Sistema de Merma Mejorado

## ✅ Cambios Implementados

### 1. **Nuevo Estado: 'en_merma'**
- Agregado estado `'en_merma'` al modelo `Productos`
- Estado especial para productos que están en merma pero permanecen visibles

### 2. **Nueva Lógica de Merma**
**Antes:**
- Cambiaba `estado_merma` a 'vencido', 'deteriorado', etc.
- Producto desaparecía del inventario
- Permitía crear duplicados

**Ahora:**
- Reduce `cantidad` a 0
- Establece `estado_merma = 'en_merma'`
- Registra `motivo_merma` y `fecha_merma`
- **Producto permanece visible en inventario**

### 3. **Inventario Mejorado**
- Muestra productos en merma con badge rojo "En Merma"
- Botón "Reabastecer" (verde) para productos en merma
- Botón "Editar" (gris) para productos activos
- Filtro "Mostrar/Ocultar Merma" para controlar visibilidad
- Cantidad en rojo cuando está en merma

### 4. **Validación de Unicidad Estricta**
- **Revertida** la validación que permitía duplicados
- Un producto = un SKU (nombre+marca)
- Si está en merma, debe reabastecerse editando, no creando uno nuevo
- Mensaje de error: "Ya existe un producto con este nombre y marca. Si está en merma, edítalo para reabastecerlo."

### 5. **Filtros Actualizados**
- **POS**: Solo muestra productos con `estado_merma='activo'` y `cantidad > 0`
- **Inventario**: Muestra todos (con filtro opcional para ocultar merma)
- **Alertas**: Solo genera alertas para productos activos
- **Dashboard**: Solo cuenta productos activos

### 6. **Método de Reabastecimiento**
- Nuevo método `reabastecer()` en modelo `Productos`
- Permite reactivar productos en merma
- Actualiza cantidad, fechas, y limpia motivo_merma

## 📋 Flujo de Trabajo

### Mover a Merma:
1. Usuario selecciona productos en inventario
2. Hace clic en "Mover a Merma"
3. Sistema solicita motivo detallado
4. Sistema:
   - Reduce `cantidad` a 0
   - Establece `estado_merma = 'en_merma'`
   - Registra `motivo_merma` y `fecha_merma`
   - Resuelve alertas automáticamente
5. Producto permanece visible con badge "En Merma"

### Reabastecer:
1. Usuario ve producto en merma (cantidad 0, badge rojo)
2. Hace clic en "Reabastecer" (botón verde)
3. Se abre formulario de edición
4. Usuario actualiza:
   - Cantidad
   - Fecha de caducidad
   - Fecha de elaboración (opcional)
5. Al guardar:
   - `estado_merma = 'activo'`
   - `motivo_merma = None`
   - `fecha_merma = None`
   - Producto vuelve a estar disponible

## 🎯 Ventajas del Nuevo Diseño

1. ✅ **Unicidad clara**: Un producto = un SKU, sin duplicados
2. ✅ **Gestión simplificada**: No crear productos nuevos, solo editar
3. ✅ **Historial completo**: Producto siempre existe, se puede ver historial
4. ✅ **UX mejorada**: Productos siempre visibles, fácil identificar qué reabastecer
5. ✅ **Lógica de negocio clara**: Merma = stock agotado, no eliminación

## 🔧 Archivos Modificados

1. `ventas/models/productos.py`:
   - Agregado estado 'en_merma'
   - Actualizado método `mover_a_merma()`
   - Nuevo método `reabastecer()`
   - Actualizado `es_merma()`

2. `ventas/views/view_acciones_masivas.py`:
   - Nueva lógica: reducir cantidad a 0, estado 'en_merma'

3. `ventas/views/view_merma.py`:
   - Nueva lógica: reducir cantidad a 0, estado 'en_merma'
   - Simplificado (ya no pide tipo, solo motivo)

4. `ventas/views/views_productos.py`:
   - Inventario muestra productos en merma
   - Filtro para mostrar/ocultar merma

5. `ventas/funciones/formularios_productos.py`:
   - Validación estricta de unicidad (revertida)

6. `templates/inventario.html`:
   - Badge "En Merma" para productos en merma
   - Botón "Reabastecer" vs "Editar"
   - Filtro mostrar/ocultar merma
   - JavaScript simplificado

7. `templates/merma_list.html`:
   - Badge para estado 'en_merma'

## ⚠️ Nota Importante

Los productos existentes que ya están en merma con estados antiguos ('vencido', 'deteriorado', etc.) seguirán funcionando. El sistema es compatible hacia atrás.

Para migrar productos antiguos a la nueva lógica, se puede ejecutar un script SQL o comando de Django que:
- Cambie `estado_merma` de 'vencido', 'deteriorado', etc. a 'en_merma'
- O simplemente dejarlos como están (el sistema los manejará correctamente)

