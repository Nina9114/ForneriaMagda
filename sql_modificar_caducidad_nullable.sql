-- ================================================================
-- Script para permitir NULL en campo caducidad
-- ================================================================
-- 
-- Este script modifica la tabla productos para permitir que el campo
-- caducidad sea NULL. Esto es necesario para productos en merma,
-- donde el lote específico ya no existe pero el SKU permanece.
--
-- Ejecutar este script en la base de datos MySQL antes de usar
-- la nueva funcionalidad de merma mejorada.
-- ================================================================

USE forneria;

-- Modificar campo caducidad para permitir NULL
ALTER TABLE productos 
MODIFY COLUMN caducidad DATE NULL 
COMMENT 'Fecha de caducidad. NULL cuando el producto está en merma (ese lote ya no existe)';

-- Verificar que el cambio se aplicó correctamente
DESCRIBE productos;

