# Análisis de Diseño: Productos en Merma y Duplicados

## 🔍 Problema Identificado

Cuando un producto se mueve a merma, sigue existiendo en la base de datos pero con `estado_merma != 'activo'`. Sin embargo, al intentar crear un nuevo producto con el mismo nombre, el sistema valida que no exista ningún producto con ese nombre, **incluso si está en merma**.

**Ejemplo:**
- Producto "Pan" se mueve a merma (vencido)
- Usuario intenta crear nuevo producto "Pan" (fresco)
- Sistema dice: "Ya existe un producto con este nombre"
- ❌ **Problema**: No puede crear el nuevo producto

## 🎯 Análisis como Experto en Bases de Datos

### Opciones de Diseño:

#### **Opción 1: Permitir duplicados si el anterior está en merma** ✅ RECOMENDADA
**Implementación:**
- Modificar validación de unicidad para excluir productos en merma
- Solo validar unicidad contra productos activos (`estado_merma='activo'`)

**Ventajas:**
- ✅ Permite crear nuevos productos cuando el anterior está en merma
- ✅ Mantiene el historial (producto en merma sigue existiendo)
- ✅ Lógica de negocio clara: "producto en merma = no disponible = puede reemplazarse"

**Desventajas:**
- ⚠️ Puede haber múltiples productos con el mismo nombre (uno activo, otros en merma)
- ⚠️ Requiere filtrar por estado en todas las consultas

#### **Opción 2: No "desaparecer" productos en merma del inventario**
**Implementación:**
- Mostrar productos en merma en el inventario con badge distintivo
- Permitir filtro para ocultar/mostrar merma
- Mantener visibilidad del historial

**Ventajas:**
- ✅ Transparencia total: se ve todo el historial
- ✅ Fácil identificar qué productos están en merma
- ✅ No se "pierden" productos

**Desventajas:**
- ⚠️ Inventario puede verse "sucio" con muchos productos en merma
- ⚠️ Requiere mejor UI para distinguir productos activos vs merma

#### **Opción 3: Crear tabla separada de merma** ❌ NO RECOMENDADA
**Razón:** Ya analizamos esto antes y decidimos que NO es necesario. Un campo de estado es suficiente.

## 💡 Solución Recomendada: **Opción 1 + Opción 2 (Híbrida)**

### Implementación:

1. **Modificar validación de unicidad** (Inmediato):
   - Excluir productos en merma de la verificación
   - Solo validar contra productos activos

2. **Mejorar visualización en inventario** (Opcional, futuro):
   - Mostrar productos en merma con badge distintivo
   - Agregar filtro "Mostrar/Ocultar merma"
   - Mantener historial visible pero claramente marcado

### Lógica de Negocio:

**Regla de Unicidad:**
- Un producto con nombre+marca es único **solo entre productos activos**
- Si un producto está en merma, puede crearse otro con el mismo nombre+marca
- Esto permite "reemplazar" productos en merma con productos frescos

**Ejemplo Práctico:**
1. "Pan Integral" (lote 1) → se vence → va a merma
2. Usuario crea "Pan Integral" (lote 2) → ✅ Permitido (el anterior está en merma)
3. Ambos existen en BD:
   - "Pan Integral" (lote 1) - estado_merma='vencido'
   - "Pan Integral" (lote 2) - estado_merma='activo'

## 📊 Comparación de Opciones

| Aspecto | Opción 1 (Solo Validación) | Opción 1+2 (Híbrida) |
|---------|---------------------------|---------------------|
| **Permite crear duplicados** | ✅ Sí | ✅ Sí |
| **Mantiene historial** | ✅ Sí | ✅ Sí |
| **Visibilidad en inventario** | ❌ No (oculto) | ✅ Sí (con badge) |
| **Complejidad** | Baja | Media |
| **UX** | Buena | Excelente |

## ✅ Decisión Final

**Implementar Opción 1 (validación) ahora**, y considerar Opción 2 (visualización) como mejora futura.

**Razón:** Resuelve el problema inmediato sin complicar demasiado el diseño. La visualización puede mejorarse después si es necesario.

