-- ============================================================
-- Script SIMPLE para agregar campos faltantes a detalle_factura_proveedor
-- ============================================================
-- 
-- Si el script anterior no funciona, usa este que es más directo
-- Solo ejecuta los ALTER TABLE directamente
-- ============================================================

-- Agregar fecha_vencimiento_producto
ALTER TABLE `detalle_factura_proveedor` 
ADD COLUMN `fecha_vencimiento_producto` DATE NULL 
COMMENT 'Fecha de vencimiento del lote recibido' 
AFTER `subtotal`;

-- Agregar lote
ALTER TABLE `detalle_factura_proveedor` 
ADD COLUMN `lote` VARCHAR(50) NULL 
COMMENT 'Número de lote del producto recibido' 
AFTER `fecha_vencimiento_producto`;

-- Agregar observaciones
ALTER TABLE `detalle_factura_proveedor` 
ADD COLUMN `observaciones` VARCHAR(300) NULL 
COMMENT 'Observaciones sobre este detalle' 
AFTER `lote`;

