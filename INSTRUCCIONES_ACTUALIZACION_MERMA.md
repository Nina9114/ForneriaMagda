# Instrucciones: Actualización del Sistema de Merma

## 🔧 Cambios en la Base de Datos

### Script SQL Requerido

**IMPORTANTE:** Debes ejecutar este script SQL antes de usar la nueva funcionalidad:

```sql
-- Archivo: sql_modificar_caducidad_nullable.sql
ALTER TABLE productos 
MODIFY COLUMN caducidad DATE NULL;
```

**Razón:** El campo `caducidad` ahora puede ser NULL para productos en merma (ese lote ya no existe, pero el SKU permanece).

## 📋 Cambios Implementados

### 1. **Lógica de Merma Mejorada**

Cuando un producto se mueve a merma:
- ✅ `cantidad = 0` (stock agotado)
- ✅ `caducidad = NULL` (ese lote ya no existe)
- ✅ `elaboracion = NULL` (ese lote ya no existe)
- ✅ `estado_merma = 'en_merma'` (marcado como en merma)
- ✅ `motivo_merma = motivo` (registrado)
- ✅ `fecha_merma = ahora` (registrado)
- ✅ **Producto permanece visible en inventario**

### 2. **Visualización en Inventario**

Productos en merma se muestran con:
- Badge rojo "En Merma"
- Cantidad: **0** (en rojo)
- Caducidad: **—** (sin fecha)
- Botón verde "Reabastecer" (en lugar de "Editar")

### 3. **Reabastecimiento**

Para reabastecer un producto en merma:
1. Hacer clic en "Reabastecer" (botón verde)
2. Se abre formulario de edición
3. **Requerido:** Ingresar nueva cantidad y nueva fecha de caducidad
4. Opcional: Fecha de elaboración
5. Al guardar:
   - `estado_merma = 'activo'`
   - `motivo_merma = NULL`
   - `fecha_merma = NULL`
   - Producto vuelve a estar disponible

### 4. **Validación de Unicidad Estricta**

- Un producto = un SKU (nombre+marca)
- No permite duplicados, incluso si está en merma
- Si está en merma, debe reabastecerse editando, no creando uno nuevo

## ✅ Checklist de Implementación

- [ ] Ejecutar `sql_modificar_caducidad_nullable.sql` en la base de datos
- [ ] Verificar que productos en merma aparecen con cantidad 0 y caducidad "—"
- [ ] Probar reabastecer un producto en merma
- [ ] Verificar que no se pueden crear productos duplicados

## 🎯 Resultado Esperado

**Antes de mover a merma:**
- Pan | Fornería | 1 kg | $2000 | **10 unidades** | **15/12/2025**

**Después de mover a merma:**
- Pan | Fornería | 1 kg | $2000 | **0** (rojo) | **—** | [Badge: En Merma] | [Botón: Reabastecer]

**Después de reabastecer:**
- Pan | Fornería | 1 kg | $2000 | **20 unidades** | **20/12/2025** | [Botón: Editar]

