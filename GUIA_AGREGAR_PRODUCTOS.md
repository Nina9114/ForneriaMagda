# Guía: Cómo Agregar Productos al Sistema

Esta guía explica las diferentes formas de agregar productos al inventario después de todos los cambios implementados.

## 📋 Índice

1. [Productos Comprados a Proveedores](#1-productos-comprados-a-proveedores)
2. [Productos de Producción Propia](#2-productos-de-producción-propia)
3. [Productos Nuevos (Manual)](#3-productos-nuevos-manual)
4. [Ajustes de Stock Manuales](#4-ajustes-de-stock-manuales)

---

## 1. Productos Comprados a Proveedores

### Cuándo usar:
- Cuando compras productos a un proveedor externo
- Productos que vienen con factura del proveedor

### Pasos:

1. **Ir a "Facturas Proveedores"** en el menú lateral
2. **Crear una nueva factura** o editar una existente
3. **Agregar productos a la factura**:
   - Seleccionar el producto (debe existir previamente)
   - Ingresar cantidad (permite decimales si `unidad_stock` no es "unidad")
   - Ingresar precio unitario (precio de compra, sin IVA)
   - Opcional: porcentaje de descuento
4. **Recibir la factura**: Al hacer clic en "Recibir Factura y Actualizar Stock"
   - Se actualiza el stock del producto
   - Se crea un movimiento de inventario de tipo "entrada"
   - Se registra el origen como "compra"

### Campos importantes:
- **Cantidad**: Puede ser decimal (ej: 1.5 kg, 2.5 litros)
- **Precio unitario**: Precio de compra (sin IVA)
- **Unidad de stock**: Se toma del producto (kg, g, l, ml, unidad)

### Nota:
Actualmente, las facturas de proveedores actualizan directamente el campo `cantidad` del producto. En el futuro, se podría integrar con el sistema de lotes para crear lotes automáticamente.

---

## 2. Productos de Producción Propia

### Cuándo usar:
- Cuando produces productos en tu panadería (pan, galletas, pasteles, etc.)
- Productos que tienen fecha de elaboración y caducidad específicas

### Pasos:

1. **Ir a "Producción"** en el menú lateral
2. **Hacer clic en "Registrar Producción"**
3. **Completar el formulario**:
   - **Producto**: Seleccionar el producto (debe existir previamente)
   - **Cantidad Producida**: Cantidad en la unidad de stock del producto (ej: 1.5 kg, 30 unidades)
   - **Fecha de Elaboración**: Fecha en que se elaboró
   - **Fecha de Caducidad**: Fecha en que vence (obligatoria)
   - **Número de Lote** (opcional): Si tienes un sistema de numeración de lotes
4. **Guardar**: Al guardar:
   - Se crea un lote nuevo
   - Se actualiza el stock del producto (suma la cantidad del lote)
   - Se crea un movimiento de inventario de tipo "entrada"
   - Se registra el origen como "produccion_propia"
   - Si el producto estaba en merma, se reactiva automáticamente

### Campos importantes:
- **Cantidad Producida**: Puede ser decimal (ej: 1.5 kg, 2.5 litros)
- **Unidad de stock**: Se muestra automáticamente según el producto seleccionado
- **Fecha de Caducidad**: Debe ser posterior a la fecha de elaboración

### Ventajas del sistema de lotes:
- Permite tener múltiples lotes del mismo producto con diferentes fechas
- El sistema usa FIFO (First In, First Out) para ventas
- Puedes ver el detalle de cada lote en el módulo de Producción

---

## 3. Productos Nuevos (Manual)

### Cuándo usar:
- Cuando quieres crear un producto nuevo en el sistema
- Productos que no provienen de compra ni producción propia

### Pasos:

1. **Ir a "Inventario"** en el menú lateral
2. **Hacer clic en "Agregar Producto"**
3. **Completar el formulario**:

   **Información Básica:**
   - **Nombre**: Nombre del producto (obligatorio)
   - **Marca**: Marca del producto (opcional)
   - **Descripción**: Descripción breve (opcional)
   - **Categoría**: Seleccionar categoría (obligatorio)
   - **Tipo**: Tipo de producto (obligatorio)

   **Unidades de Medida:**
   - **Unidad de Stock**: Unidad en que se almacena (unidad, kg, g, l, ml)
   - **Unidad de Venta**: Unidad en que se vende (puede ser diferente)
   - **Precio por Unidad de Venta**: Precio con IVA incluido (obligatorio)
   - **Peso/Tamaño o Presentación**: Tamaño individual (ej: "100g", "500ml", "Bolsa")

   **Stock:**
   - **Cantidad**: Cantidad inicial (puede ser decimal si no es "unidad")
   - **Stock Mínimo**: Cantidad mínima para alertas (puede ser decimal)
   - **Stock Máximo**: Cantidad máxima recomendada (puede ser decimal)

   **Fechas (opcional):**
   - **Fecha de Elaboración**: Si aplica
   - **Fecha de Caducidad**: Si aplica

4. **Guardar**: El producto se crea y queda disponible en el inventario

### Campos importantes:
- **Precio por Unidad de Venta**: Este precio **YA INCLUYE IVA** (19%)
- **Cantidad**: Puede ser decimal (ej: 1.5 kg, 2.5 litros)
- **Unidad de Stock vs Unidad de Venta**:
  - Ejemplo: Almacenas en kg (`unidad_stock = 'kg'`) pero vendes en gramos (`unidad_venta = 'g'`)
  - El sistema maneja las conversiones automáticamente

### Nota:
Si creas un producto nuevo manualmente y luego quieres agregar más stock, puedes:
- Usar el módulo de Producción (si es producción propia)
- Editar el producto y cambiar la cantidad (se crea un movimiento de inventario)
- Usar ajustes de stock manuales

---

## 4. Ajustes de Stock Manuales

### Cuándo usar:
- Para corregir errores en el inventario
- Para ajustes menores de stock
- Cuando necesitas agregar/quitar stock sin una factura o producción

### Pasos:

1. **Ir a "Inventario"** en el menú lateral
2. **Seleccionar el producto** que quieres ajustar
3. **Hacer clic en "Ajustar Stock"** (si está disponible)
4. **Seleccionar tipo de ajuste**:
   - **Entrada**: Agregar stock
   - **Salida**: Quitar stock
5. **Ingresar cantidad** (puede ser decimal)
6. **Confirmar**: Se crea un movimiento de inventario de tipo "ajuste"

### Nota:
Los ajustes manuales deben usarse con precaución y solo por usuarios autorizados (Administrador, Contador).

---

## 📊 Resumen de Métodos

| Método | Cuándo Usar | Crea Lote | Crea Movimiento | Actualiza Stock |
|--------|-------------|-----------|-----------------|------------------|
| **Factura Proveedor** | Compra a proveedor | ❌ No | ✅ Sí | ✅ Sí |
| **Producción Propia** | Productos elaborados | ✅ Sí | ✅ Sí | ✅ Sí |
| **Producto Nuevo** | Crear producto nuevo | ❌ No | ❌ No | ✅ Sí (cantidad inicial) |
| **Editar Producto** | Cambiar cantidad | ❌ No | ✅ Sí | ✅ Sí |
| **Ajuste Manual** | Correcciones | ❌ No | ✅ Sí | ✅ Sí |

---

## ⚠️ Consideraciones Importantes

### 1. Precio con IVA Incluido
- El precio que ingresas en el producto **YA INCLUYE IVA** (19%)
- El sistema desglosa el IVA automáticamente en las boletas
- No necesitas calcular el IVA manualmente

### 2. Unidades de Medida
- **Unidad de Stock**: Unidad en que almacenas (ej: kg, litros)
- **Unidad de Venta**: Unidad en que vendes (ej: gramos, ml)
- El sistema maneja las conversiones automáticamente

### 3. Cantidades Decimales
- Puedes usar decimales para productos vendidos por peso/volumen
- Ejemplos: 1.5 kg, 2.5 litros, 0.5 kg
- El sistema redondea a 3 decimales

### 4. Sistema de Lotes
- Los lotes se crean automáticamente en Producción Propia
- Cada lote tiene su propia fecha de elaboración y caducidad
- El stock total se calcula sumando todos los lotes activos

### 5. Reactivación Automática
- Si un producto está en merma y creas un nuevo lote, se reactiva automáticamente
- El historial de merma se mantiene (no se elimina)

---

## 🔄 Flujo Recomendado

### Para productos comprados:
1. Crear factura de proveedor
2. Agregar productos a la factura
3. Recibir la factura (actualiza stock)

### Para productos propios:
1. Ir a Producción
2. Registrar nuevo lote
3. El stock se actualiza automáticamente

### Para productos nuevos:
1. Crear producto en Inventario
2. Si es producción propia, registrar lote en Producción
3. Si es compra, agregar a factura de proveedor

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Comprar Harina
1. Ir a "Facturas Proveedores" → "Nueva Factura"
2. Seleccionar proveedor de harina
3. Agregar producto "Harina" → Cantidad: 50 kg, Precio: $1,500/kg
4. Recibir factura → Stock actualizado a 50 kg

### Ejemplo 2: Producir Pan
1. Ir a "Producción" → "Registrar Producción"
2. Seleccionar "Pan"
3. Cantidad: 30 unidades
4. Fecha elaboración: Hoy
5. Fecha caducidad: +3 días
6. Guardar → Se crea lote y se actualiza stock

### Ejemplo 3: Crear Producto Nuevo
1. Ir a "Inventario" → "Agregar Producto"
2. Nombre: "Galleta de Chocolate"
3. Unidad Stock: "unidad"
4. Unidad Venta: "unidad"
5. Precio: $2,000 (con IVA incluido)
6. Cantidad inicial: 0 (se agregará con producción o compra)
7. Guardar → Producto creado

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo agregar stock editando el producto directamente?**
R: Sí, pero se crea un movimiento de inventario. Es mejor usar Producción o Facturas.

**P: ¿Qué pasa si creo un producto con cantidad 0?**
R: El producto se crea, pero no estará disponible para venta hasta que agregues stock.

**P: ¿Puedo tener múltiples lotes del mismo producto?**
R: Sí, especialmente útil para productos de producción propia con diferentes fechas.

**P: ¿El precio incluye IVA?**
R: Sí, el precio que ingresas YA INCLUYE IVA. El sistema lo desglosa automáticamente.

**P: ¿Puedo cambiar la cantidad de un producto después de crearlo?**
R: Sí, editando el producto o usando ajustes de stock, pero se registra un movimiento.

---

## 📞 Soporte

Si tienes dudas sobre cómo agregar productos, consulta esta guía o revisa la documentación del sistema.

