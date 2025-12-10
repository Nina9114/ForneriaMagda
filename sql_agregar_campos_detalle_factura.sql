-- ============================================================
-- Script para agregar campos faltantes a detalle_factura_proveedor
-- ============================================================
-- 
-- Este script agrega los campos:
-- - fecha_vencimiento_producto: Fecha de vencimiento del lote recibido
-- - lote: Número de lote del producto recibido
-- - observaciones: Observaciones sobre este detalle
--
-- Estos campos ya existen en el modelo Django pero faltan en la BD
-- ============================================================

-- Verificar si las columnas ya existen antes de agregarlas
-- (MySQL no tiene IF NOT EXISTS para ALTER TABLE ADD COLUMN, así que usamos un procedimiento)

-- Agregar fecha_vencimiento_producto si no existe
SET @dbname = DATABASE();
SET @tablename = 'detalle_factura_proveedor';
SET @columnname = 'fecha_vencimiento_producto';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1', -- Columna ya existe, no hacer nada
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DATE NULL COMMENT ''Fecha de vencimiento del lote recibido''')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar lote si no existe
SET @columnname = 'lote';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1', -- Columna ya existe, no hacer nada
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(50) NULL COMMENT ''Número de lote del producto recibido''')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar observaciones si no existe
SET @columnname = 'observaciones';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1', -- Columna ya existe, no hacer nada
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(300) NULL COMMENT ''Observaciones sobre este detalle''')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Verificar que las columnas se agregaron correctamente
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE, 
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'detalle_factura_proveedor'
    AND COLUMN_NAME IN ('fecha_vencimiento_producto', 'lote', 'observaciones')
ORDER BY COLUMN_NAME;

