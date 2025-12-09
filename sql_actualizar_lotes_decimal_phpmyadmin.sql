-- ================================================================
-- =  SCRIPT SQL: ACTUALIZAR LOTES A DECIMAL (phpMyAdmin)         =
-- ================================================================
-- 
-- Este script actualiza los campos cantidad y cantidad_inicial
-- de la tabla lotes de INT a DECIMAL(10,3) para soportar
-- unidades de medida con decimales (kg, litros, etc.)
--
-- IMPORTANTE: Ejecutar este script DESPUÉS de actualizar el código Django
-- ================================================================

-- Paso 1: Modificar cantidad de INT a DECIMAL(10,3)
ALTER TABLE `lotes` 
MODIFY COLUMN `cantidad` DECIMAL(10,3) 
NOT NULL DEFAULT 0.000 
COMMENT 'Cantidad actual del lote (permite decimales para kg, litros, etc.)';

-- Paso 2: Modificar cantidad_inicial de INT a DECIMAL(10,3)
ALTER TABLE `lotes` 
MODIFY COLUMN `cantidad_inicial` DECIMAL(10,3) 
NOT NULL 
COMMENT 'Cantidad original cuando se creó el lote (permite decimales para kg, litros, etc.)';

-- Paso 3: Verificar cambios
DESCRIBE `lotes`;

-- Paso 4: Mostrar resumen
SELECT 
    'Campos actualizados exitosamente' AS mensaje,
    COUNT(*) AS total_lotes,
    SUM(cantidad) AS total_cantidad_actual,
    SUM(cantidad_inicial) AS total_cantidad_inicial
FROM `lotes`;

SELECT 'Script ejecutado exitosamente. Los lotes ahora soportan cantidades decimales.' AS resultado;

