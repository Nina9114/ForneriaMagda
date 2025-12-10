-- ================================================================
-- =                                                              =
-- =     SCRIPT SQL: AGREGAR CAMPO MEDIO_PAGO A VENTAS            =
-- =                                                              =
-- ================================================================
-- 
-- Este script agrega el campo medio_pago a la tabla ventas
-- para permitir registrar diferentes métodos de pago.
--
-- IMPORTANTE: Ejecutar este script en la base de datos MySQL
-- antes de usar el nuevo sistema de métodos de pago.

ALTER TABLE `ventas` 
ADD COLUMN `medio_pago` VARCHAR(20) NOT NULL DEFAULT 'efectivo' 
AFTER `folio`;

-- Agregar comentario al campo
ALTER TABLE `ventas` 
MODIFY COLUMN `medio_pago` VARCHAR(20) NOT NULL DEFAULT 'efectivo' 
COMMENT 'Método de pago: efectivo, tarjeta_debito, tarjeta_credito, transferencia, cheque, otro';

