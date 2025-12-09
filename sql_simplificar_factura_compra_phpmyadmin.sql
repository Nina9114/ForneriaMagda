-- ================================================================
-- Script para simplificar la tabla factura_proveedor (phpMyAdmin)
-- ================================================================
-- 
-- Cambios:
-- 1. Eliminar campo estado_recepcion (ya no necesario)
-- 2. Agregar estado 'atrasado' al enum estado_pago
-- 3. Hacer subtotal_sin_iva, total_iva nullable (se calculan automáticamente)
-- ================================================================

-- Desactivar verificación de claves foráneas temporalmente
SET FOREIGN_KEY_CHECKS = 0;

-- Paso 1: Agregar estado 'atrasado' al enum estado_pago
ALTER TABLE `factura_proveedor` 
CHANGE `estado_pago` `estado_pago` ENUM('pendiente', 'pagado', 'parcial', 'atrasado', 'cancelado') 
NOT NULL DEFAULT 'pendiente' 
COMMENT 'Estado del pago';

-- Paso 2: Hacer subtotal_sin_iva y total_iva nullable
ALTER TABLE `factura_proveedor`
CHANGE `subtotal_sin_iva` `subtotal_sin_iva` DECIMAL(10,2) NULL DEFAULT NULL 
COMMENT 'Subtotal sin IVA (se calcula automáticamente)';

ALTER TABLE `factura_proveedor`
CHANGE `total_iva` `total_iva` DECIMAL(10,2) NULL DEFAULT NULL 
COMMENT 'Total de IVA (se calcula automáticamente)';

-- Paso 3: Eliminar campo estado_recepcion
ALTER TABLE `factura_proveedor`
DROP COLUMN `estado_recepcion`;

-- Reactivar verificación de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- Verificar la estructura final
DESCRIBE `factura_proveedor`;

-- Mensaje de confirmación
SELECT 'Tabla factura_proveedor simplificada exitosamente' AS mensaje;

