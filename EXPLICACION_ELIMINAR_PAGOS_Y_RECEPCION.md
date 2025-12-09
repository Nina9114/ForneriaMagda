# ¿Qué pasa si elimino pagos o quito la recepción?

## 📋 Situación actual del sistema

### 1. ✅ **ELIMINAR PAGOS** - Funciona correctamente

**¿Qué pasa cuando eliminas un pago?**

✅ **Lo que SÍ hace:**
- Elimina el registro del pago de la base de datos
- **Actualiza automáticamente el estado de la factura**:
  - Si era "Pagado" y eliminas el pago → vuelve a "Pendiente" o "Pago Parcial"
  - Si era "Pago Parcial" y eliminas el último pago → vuelve a "Pendiente"
  - Recalcula el saldo pendiente correctamente

❌ **Lo que NO hace (y está bien):**
- **NO revierte el stock** - Los pagos no afectan el stock, solo el estado de pago
- El stock se actualiza cuando recibes la factura, no cuando pagas

**Ejemplo:**
```
Factura: $100,000
Pago 1: $50,000 → Estado: "Pago Parcial", Saldo: $50,000
Pago 2: $50,000 → Estado: "Pagado", Saldo: $0

Si eliminas Pago 2:
→ Estado vuelve a: "Pago Parcial", Saldo: $50,000
→ El stock NO cambia (sigue igual)
```

---

### 2. ⚠️ **QUITAR RECEPCIÓN** - Parcialmente implementado

**¿Qué pasa cuando quitas la recepción de una factura?**

✅ **Lo que SÍ hace:**
- Quita la fecha de recepción (`fecha_recepcion = None`)
- Permite agregar más productos a la factura
- Permite editar los productos de la factura

❌ **Lo que NO hace (PROBLEMA):**
- **NO revierte el stock** - Si ya se actualizó el stock al recibir la factura, el stock queda incorrecto
- No crea movimientos de salida para revertir el stock

**Ejemplo:**
```
1. Creas factura con 100 unidades de pan
2. Recibes la factura → Stock aumenta en 100 unidades
3. Quitas la recepción → Stock sigue con +100 unidades (INCORRECTO)
```

---

## 🔧 Solución recomendada

### Opción A: Mejorar "Quitar Recepción" (Recomendado)

Modificar `quitar_recepcion_factura_ajax` para que:
1. Revierte el stock de todos los productos
2. Crea movimientos de salida para trazabilidad
3. Quita la fecha de recepción

**Ventajas:**
- Mantiene el stock correcto
- Permite corregir errores
- Trazabilidad completa

**Desventajas:**
- Si ya vendiste productos, el stock puede quedar negativo
- Requiere validación adicional

### Opción B: Crear "Cancelar Recepción" separado

Crear una nueva función `cancelar_recepcion_factura_ajax` que:
1. Revierte el stock
2. Crea movimientos de salida
3. Quita la fecha de recepción
4. Marca la factura como "cancelada"

**Ventajas:**
- Separación clara entre "quitar recepción" (solo fecha) y "cancelar" (revertir todo)
- Más control sobre qué operaciones hacer

**Desventajas:**
- Dos funciones similares pueden confundir
- Más código que mantener

---

## 💡 Recomendación

**Implementar Opción A**: Mejorar "Quitar Recepción" para que revierta el stock automáticamente.

**Razón:**
- Si quitas la recepción, es porque probablemente hubo un error
- El stock debe estar sincronizado con las facturas recibidas
- Es más seguro revertir el stock que dejarlo incorrecto

**Advertencia al usuario:**
Mostrar un mensaje de confirmación:
```
⚠️ ADVERTENCIA: Al quitar la recepción, se revertirá el stock de todos los productos.
Esto puede afectar el inventario si ya se vendieron productos.
¿Está seguro que desea continuar?
```

---

## 📊 Resumen

| Acción | Estado Actual | Stock | Estado Factura | Recomendación |
|--------|--------------|-------|---------------|--------------|
| **Eliminar Pago** | ✅ Funciona | No afecta | Se actualiza | ✅ Correcto |
| **Quitar Recepción** | ⚠️ Parcial | No revierte | Se quita fecha | 🔧 Mejorar |

---

## 🎯 Próximos pasos

1. **Implementar reversión de stock en "Quitar Recepción"**
2. **Agregar validación para evitar quitar recepción si hay ventas**
3. **Agregar mensaje de advertencia al usuario**
4. **Crear movimientos de salida para trazabilidad**

---

¿Quieres que implemente la mejora para "Quitar Recepción"?

