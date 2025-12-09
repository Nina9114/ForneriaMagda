# Guía: Flujo Completo para Registrar una Factura de Proveedor

## 📋 Pasos Después de Registrar un Proveedor

Cuando te llega una factura física con productos, sigue estos pasos:

---

## 🔄 Flujo Completo

### **Paso 1: Crear la Factura**

1. **Ir a "Facturas Proveedores"** en el menú lateral
2. **Hacer clic en "Nueva Factura"**
3. **Completar la información básica:**
   - **Proveedor**: Seleccionar el proveedor que emitió la factura
   - **Número de Factura**: Número que aparece en la factura física (ej: "FAC-2025-001")
   - **Fecha de Factura**: Fecha de emisión de la factura
   - **Fecha de Vencimiento**: Fecha límite para pagar (opcional)
   - **Fecha de Recepción**: Dejar vacío por ahora (se llenará cuando recibas la factura)
   - **Estado de Pago**: "Pendiente" (por defecto)
   - **Subtotal sin IVA (Neto)**: Ingresar el monto sin IVA de la factura
   - **IVA (19%)**: Se calcula automáticamente
   - **Descuento (en pesos)**: Si hay descuento, ingresar el monto fijo
   - **Total con IVA**: Se calcula automáticamente
   - **Observaciones**: Notas adicionales (opcional)

4. **Hacer clic en "Guardar"**

   ⚠️ **IMPORTANTE**: En este paso solo estás creando la factura. Los productos se agregan después.

---

### **Paso 2: Agregar Productos a la Factura**

Después de guardar la factura, serás redirigido a la página de **detalle de la factura**.

1. **En la sección "Agregar Producto"**, completar:
   - **Producto**: Seleccionar el producto de la lista (debe existir previamente en el inventario)
   - **Cantidad**: Cantidad recibida (puede ser decimal si no es "unidad")
   - **Precio Unitario**: Precio de compra (sin IVA)
   - **Descuento %**: Porcentaje de descuento para este producto (opcional)
   - **Número de Lote**: Si el proveedor proporciona un número de lote (opcional)

2. **Hacer clic en "Agregar Producto"**

3. **Repetir** para cada producto de la factura

   📝 **Nota**: Los productos se agregan uno por uno. Si tienes muchos productos, puedes agregarlos todos antes de recibir la factura.

---

### **Paso 3: Recibir la Factura y Actualizar Stock**

Una vez que hayas agregado todos los productos:

1. **Verificar** que todos los productos estén correctos en la tabla "Productos en la Factura"
2. **Hacer clic en el botón "✓ Recibir Factura y Actualizar Stock"** (botón verde)

   ⚠️ **IMPORTANTE**: Este paso:
   - Marca la factura como recibida (establece `fecha_recepcion`)
   - Actualiza el stock de todos los productos agregados
   - Crea movimientos de inventario de tipo "entrada"
   - **NO se puede deshacer fácilmente** (requiere cancelar la recepción)

3. **Confirmar** la acción cuando se solicite

---

### **Paso 4: Registrar Pagos (Opcional)**

Si pagaste la factura o parte de ella:

1. **En la sección "Pagos Realizados"**, hacer clic en "Registrar Pago"
2. **Completar:**
   - **Monto**: Cantidad pagada
   - **Fecha de Pago**: Fecha en que se realizó el pago
   - **Método de Pago**: Transferencia, efectivo, cheque, etc.
   - **Comprobante**: Número de comprobante (opcional)
   - **Observaciones**: Notas adicionales (opcional)

3. **Guardar**

   💡 **Tip**: Puedes registrar múltiples pagos para la misma factura (pagos parciales).

---

## 📊 Resumen del Flujo

```
1. Registrar Proveedor
   ↓
2. Crear Factura (información básica)
   ↓
3. Agregar Productos (uno por uno)
   ↓
4. Recibir Factura → Actualiza Stock ✅
   ↓
5. Registrar Pagos (cuando corresponda)
```

---

## ⚠️ Puntos Importantes

### **Antes de Recibir la Factura:**
- ✅ Puedes agregar, editar o eliminar productos
- ✅ Puedes modificar los totales
- ✅ El stock NO se actualiza todavía

### **Después de Recibir la Factura:**
- ❌ NO puedes agregar más productos
- ❌ NO puedes eliminar productos
- ✅ Puedes registrar pagos
- ✅ El stock YA está actualizado

### **Si Cometiste un Error:**
- Si aún NO has recibido la factura: Puedes editar o eliminar productos
- Si YA recibiste la factura: Debes cancelar la recepción (esto revierte el stock)

---

## 🔍 Ejemplo Práctico

### Escenario: Llegó una factura de harina

**Paso 1: Crear Factura**
- Proveedor: "Molinos del Sur"
- Número: "FAC-2025-001"
- Fecha: 15/01/2025
- Subtotal sin IVA: $50,000
- IVA: $9,500 (calculado automáticamente)
- Total: $59,500

**Paso 2: Agregar Productos**
- Producto: "Harina"
  - Cantidad: 50 kg
  - Precio Unitario: $1,000/kg
  - Descuento: 0%
- Producto: "Azúcar"
  - Cantidad: 30 kg
  - Precio Unitario: $800/kg
  - Descuento: 5%

**Paso 3: Recibir Factura**
- Hacer clic en "Recibir Factura y Actualizar Stock"
- ✅ Stock de "Harina" aumenta en 50 kg
- ✅ Stock de "Azúcar" aumenta en 30 kg
- ✅ Se crean movimientos de inventario

**Paso 4: Registrar Pago (si pagaste)**
- Monto: $59,500
- Fecha: 20/01/2025
- Método: Transferencia bancaria

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo agregar productos después de recibir la factura?**
R: No, una vez recibida la factura, no puedes agregar más productos. Debes cancelar la recepción primero.

**P: ¿Qué pasa si el producto no existe en el inventario?**
R: Primero debes crear el producto en "Inventario" → "Agregar Producto", y luego agregarlo a la factura.

**P: ¿Puedo recibir la factura sin agregar productos?**
R: Sí, pero no tiene mucho sentido porque no se actualizará ningún stock. Es mejor agregar los productos primero.

**P: ¿El precio de compra afecta el precio de venta?**
R: No automáticamente. El precio de compra se guarda en el detalle de la factura, pero el precio de venta del producto se mantiene independiente.

**P: ¿Puedo editar una factura después de recibirla?**
R: Puedes editar la información básica (fechas, totales, etc.), pero no puedes agregar o eliminar productos.

---

## 🎯 Checklist Rápido

Cuando te llega una factura:

- [ ] ¿El proveedor está registrado? → Si no, registrarlo primero
- [ ] ¿Los productos existen en el inventario? → Si no, crearlos primero
- [ ] Crear la factura con la información básica
- [ ] Agregar todos los productos de la factura
- [ ] Verificar que los totales coincidan con la factura física
- [ ] Recibir la factura (actualiza stock)
- [ ] Registrar pagos cuando corresponda

---

## 📞 ¿Necesitas Ayuda?

Si tienes dudas sobre algún paso, consulta:
- La guía de "Cómo Agregar Productos" (`GUIA_AGREGAR_PRODUCTOS.md`)
- La documentación del sistema
- O revisa los ejemplos en esta guía

