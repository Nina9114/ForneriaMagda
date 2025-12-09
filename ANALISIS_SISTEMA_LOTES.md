# Análisis: Sistema de Gestión de Lotes

## Problema Actual

El sistema actual tiene un producto "Galletas" con:
- Una fecha de elaboración
- Una fecha de caducidad
- Una cantidad total

**Problema**: Cuando llega un nuevo lote con diferentes fechas, el sistema:
1. Sobrescribe las fechas del producto anterior
2. No puede rastrear qué lote se está vendiendo
3. No puede aplicar FIFO (First In First Out)
4. Las alertas de vencimiento no son precisas por lote

## Ejemplo del Problema

**Situación actual:**
- Lote 1: 50 galletas, elaboración: 01/01/2025, caducidad: 15/01/2025
- Lote 2: 30 galletas, elaboración: 10/01/2025, caducidad: 25/01/2025

**Problema**: El sistema solo guarda UNA fecha de elaboración y UNA de caducidad, perdiendo información del Lote 1.

## Solución Propuesta: Tabla de Lotes

### Estructura de Base de Datos

```sql
CREATE TABLE `lotes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `productos_id` INT NOT NULL,
  `numero_lote` VARCHAR(50) NULL,  -- Opcional: número de lote del proveedor
  `cantidad` INT NOT NULL DEFAULT 0,
  `cantidad_inicial` INT NOT NULL,  -- Cantidad original del lote
  `fecha_elaboracion` DATE NULL,
  `fecha_caducidad` DATE NOT NULL,
  `fecha_recepcion` DATETIME NOT NULL,  -- Cuándo se recibió en el almacén
  `detalle_factura_proveedor_id` INT NULL,  -- Relación con la factura que lo trajo
  `estado` ENUM('activo', 'agotado', 'vencido', 'en_merma') DEFAULT 'activo',
  `creado` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `modificado` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_lotes_productos_idx` (`productos_id`),
  KEY `fk_lotes_detalle_factura_idx` (`detalle_factura_proveedor_id`),
  KEY `idx_fecha_caducidad` (`fecha_caducidad`),
  KEY `idx_estado` (`estado`),
  CONSTRAINT `fk_lotes_productos` FOREIGN KEY (`productos_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `fk_lotes_detalle_factura` FOREIGN KEY (`detalle_factura_proveedor_id`) REFERENCES `detalle_factura_proveedor` (`id`)
) ENGINE=InnoDB;
```

### Cambios en el Modelo Productos

El modelo `Productos` ya NO tendrá `elaboracion` y `caducidad` directas. En su lugar:
- `cantidad` = Suma de `lotes.cantidad` donde `estado='activo'`
- Las fechas se obtienen del lote más antiguo (FIFO)

### Flujo de Trabajo

#### 1. Recepción de Factura de Proveedor
Cuando se recibe una factura:
- Por cada `DetalleFacturaProveedor`, crear un `Lote`
- El lote tiene las fechas del detalle (si están disponibles)
- Estado inicial: 'activo'

#### 2. Ventas (FIFO)
Al vender productos:
- Buscar el lote más antiguo (menor `fecha_caducidad`) con stock disponible
- Reducir `cantidad` del lote
- Si `cantidad = 0`, cambiar `estado = 'agotado'`

#### 3. Alertas de Vencimiento
- Generar alertas por lote, no por producto
- Alerta roja: lote vence en < 3 días
- Alerta amarilla: lote vence en < 7 días

#### 4. Merma
- Mover lotes específicos a merma
- Mantener historial de qué lote se fue a merma

## Ventajas de esta Solución

1. ✅ **Trazabilidad completa**: Saber exactamente qué lote se vendió
2. ✅ **FIFO automático**: Siempre se vende el lote más antiguo
3. ✅ **Alertas precisas**: Por lote, no por producto
4. ✅ **Gestión de merma por lote**: Saber qué lote específico se fue a merma
5. ✅ **Historial completo**: Rastrear todos los lotes que han pasado por el inventario

## Desventajas / Consideraciones

1. ⚠️ **Complejidad**: Requiere cambios significativos en el código
2. ⚠️ **Migración de datos**: Los productos existentes necesitan lotes iniciales
3. ⚠️ **Rendimiento**: Más consultas a la BD (pero manejable con índices)

## Implementación Sugerida (Fases)

### Fase 1: Crear Tabla y Modelo de Lotes
- Crear tabla `lotes` en BD
- Crear modelo Django `Lote`
- Migrar datos existentes (crear lote inicial para cada producto)

### Fase 2: Modificar Recepción de Facturas
- Al recibir factura, crear lotes automáticamente
- Asociar lote con `DetalleFacturaProveedor`

### Fase 3: Modificar Sistema de Ventas
- Implementar FIFO en ventas
- Actualizar cantidad de lotes al vender

### Fase 4: Modificar Alertas
- Generar alertas por lote
- Mostrar alertas agrupadas por producto

### Fase 5: Modificar Merma
- Mover lotes específicos a merma
- Mantener historial por lote

## Alternativa Simplificada (Si no se puede implementar lotes completos)

Si la implementación completa es muy compleja, se puede hacer una solución temporal:

1. **Agregar campos de lote a DetalleFacturaProveedor**:
   - `fecha_elaboracion_lote`
   - `fecha_caducidad_lote`
   - `numero_lote`

2. **Al recibir factura**: Guardar fechas en el detalle

3. **Al vender**: Usar el detalle más antiguo (FIFO básico)

4. **Limitación**: No se puede tener múltiples lotes del mismo producto simultáneamente con esta solución.

## Recomendación

**Implementar la solución completa de lotes** porque:
- Es la forma correcta de manejar inventario con fechas de vencimiento
- Permite cumplir con normativas de trazabilidad
- Facilita auditorías
- Mejora la gestión de stock

¿Procedemos con la implementación completa?

