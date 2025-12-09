-- ================================================================
-- Script para agregar campos de motivo y fecha de merma
-- ================================================================
-- 
-- Este script agrega dos campos a la tabla productos:
-- 1. motivo_merma: Texto libre para describir el motivo de la merma
-- 2. fecha_merma: Fecha y hora en que el producto fue movido a merma
--
-- Ejecutar este script en la base de datos MySQL antes de usar
-- la nueva funcionalidad de motivo de merma.
-- ================================================================

USE forneria;

-- Agregar campo motivo_merma (TEXT, permite NULL)
ALTER TABLE productos 
ADD COLUMN motivo_merma TEXT NULL 
COMMENT 'Motivo detallado por el cual el producto fue movido a merma (ej: roto, robado, vencido, etc.)';

-- Agregar campo fecha_merma (DATETIME, permite NULL)
ALTER TABLE productos 
ADD COLUMN fecha_merma DATETIME NULL 
COMMENT 'Fecha y hora en que el producto fue movido a merma';

-- Verificar que los campos se agregaron correctamente
DESCRIBE productos;

