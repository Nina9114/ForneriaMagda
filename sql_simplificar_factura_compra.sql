-- ================================================================
-- Script para simplificar la tabla factura_proveedor
-- ================================================================
-- 
-- Cambios:
-- 1. Eliminar campo estado_recepcion (ya no necesario)
-- 2. Agregar estado 'atrasado' al enum estado_pago
-- 3. Hacer subtotal_sin_iva, total_iva nullable (se calculan automáticamente)
-- 4. Renombrar tabla a factura_compra (opcional, si quieres)
--
-- NOTA: Si quieres renombrar la tabla, descomenta las líneas al final
-- ================================================================

USE forneria;

-- Paso 1: Agregar estado 'atrasado' al enum estado_pago
-- Primero necesitamos modificar la columna para agregar la nueva opción
ALTER TABLE `factura_proveedor` 
MODIFY COLUMN `estado_pago` ENUM('pendiente', 'pagado', 'parcial', 'atrasado', 'cancelado') 
NOT NULL DEFAULT 'pendiente' 
COMMENT 'Estado del pago';

-- Paso 2: Hacer subtotal_sin_iva y total_iva nullable (se calculan automáticamente)
ALTER TABLE `factura_proveedor`
MODIFY COLUMN `subtotal_sin_iva` DECIMAL(10,2) NULL DEFAULT NULL COMMENT 'Subtotal sin IVA (se calcula automáticamente)';

ALTER TABLE `factura_proveedor`
MODIFY COLUMN `total_iva` DECIMAL(10,2) NULL DEFAULT NULL COMMENT 'Total de IVA (se calcula automáticamente)';

-- Paso 3: Eliminar campo estado_recepcion (ya no necesario)
-- Primero verificar si hay datos que dependan de este campo
-- Si fecha_recepcion es NULL, significa que no se ha recibido
-- Si fecha_recepcion tiene valor, significa que se recibió
ALTER TABLE `factura_proveedor`
DROP COLUMN `estado_recepcion`;

-- Paso 4: Eliminar índices relacionados con estado_recepcion (si existen)
-- MySQL los elimina automáticamente, pero por si acaso:
-- DROP INDEX idx_estado_recepcion ON factura_proveedor;

-- Paso 5: Verificar la estructura final
DESCRIBE `factura_proveedor`;

-- Paso 6: Mostrar mensaje de confirmación
SELECT 'Tabla factura_proveedor simplificada exitosamente' AS mensaje;

-- ================================================================
-- OPCIONAL: Renombrar tabla a factura_compra
-- ================================================================
-- Si quieres renombrar la tabla, descomenta las siguientes líneas:
--
-- RENAME TABLE `factura_proveedor` TO `factura_compra`;
-- 
-- También necesitarías renombrar la tabla de detalles:
-- RENAME TABLE `detalle_factura_proveedor` TO `detalle_factura_compra`;
--
-- Y actualizar las foreign keys:
-- ALTER TABLE `detalle_factura_compra` 
-- DROP FOREIGN KEY `fk_detalle_factura_proveedor_factura_proveedor1`;
-- 
-- ALTER TABLE `detalle_factura_compra`
-- ADD CONSTRAINT `fk_detalle_factura_compra_factura_compra1`
-- FOREIGN KEY (`factura_proveedor_id`) REFERENCES `factura_compra` (`id`)
-- ON DELETE CASCADE ON UPDATE CASCADE;
--
-- ALTER TABLE `pago_proveedor`
-- DROP FOREIGN KEY `fk_pago_proveedor_factura_proveedor1`;
--
-- ALTER TABLE `pago_proveedor`
-- ADD CONSTRAINT `fk_pago_proveedor_factura_compra1`
-- FOREIGN KEY (`factura_proveedor_id`) REFERENCES `factura_compra` (`id`)
-- ON DELETE CASCADE ON UPDATE CASCADE;

