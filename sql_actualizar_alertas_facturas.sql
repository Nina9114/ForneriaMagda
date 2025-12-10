-- ============================================================
-- SCRIPT: ACTUALIZAR TABLA ALERTAS PARA FACTURAS
-- Sistema: Prototipo Fornería
-- Descripción: Agregar campo factura_proveedor_id a la tabla alertas
--              para permitir alertas de facturas vencidas
-- ============================================================

-- Agregar columna factura_proveedor_id (opcional, puede ser NULL)
ALTER TABLE `alertas`
ADD COLUMN `factura_proveedor_id` int NULL COMMENT 'Factura asociada a esta alerta (opcional si es alerta de producto)',
ADD KEY `fk_alertas_factura_proveedor_idx` (`factura_proveedor_id`),
ADD CONSTRAINT `fk_alertas_factura_proveedor`
    FOREIGN KEY (`factura_proveedor_id`)
    REFERENCES `factura_proveedor` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- Hacer que productos_id sea opcional (puede ser NULL si es alerta de factura)
ALTER TABLE `alertas`
MODIFY COLUMN `productos_id` int NULL COMMENT 'Producto asociado a esta alerta (opcional si es alerta de factura)';

-- Agregar índice compuesto para búsquedas eficientes
ALTER TABLE `alertas`
ADD INDEX `idx_estado_tipo` (`estado`, `tipo_alerta`);

