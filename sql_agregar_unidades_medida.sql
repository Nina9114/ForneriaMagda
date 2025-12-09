-- ================================================================
-- =  SCRIPT SQL: AGREGAR CAMPOS DE UNIDADES DE MEDIDA           =
-- ================================================================
-- 
-- Este script agrega los campos necesarios para el sistema
-- híbrido de unidades de medida (Opción A).
--
-- CAMPOS NUEVOS:
-- 1. unidad_stock: Unidad en que se almacena el stock
-- 2. unidad_venta: Unidad en que se vende el producto
-- 3. precio_por_unidad_venta: Precio por unidad de venta
-- 4. cantidad: Se modifica de INT a DECIMAL(10,3)
--
-- IMPORTANTE: Ejecutar este script ANTES de actualizar el código Django
-- ================================================================

USE forneria;

-- Paso 1: Agregar campo unidad_stock
ALTER TABLE productos 
ADD COLUMN unidad_stock ENUM('unidad', 'kg', 'g', 'l', 'ml') 
NOT NULL DEFAULT 'unidad' 
COMMENT 'Unidad en que se almacena el stock (unidad, kg, g, l, ml)';

-- Paso 2: Agregar campo unidad_venta
ALTER TABLE productos 
ADD COLUMN unidad_venta ENUM('unidad', 'kg', 'g', 'l', 'ml') 
NOT NULL DEFAULT 'unidad' 
COMMENT 'Unidad en que se vende el producto (unidad, kg, g, l, ml)';

-- Paso 3: Agregar campo precio_por_unidad_venta
ALTER TABLE productos 
ADD COLUMN precio_por_unidad_venta DECIMAL(10,2) 
NULL 
COMMENT 'Precio por unidad de venta (ej: precio por kilo, precio por litro). NULL se copiará desde precio';

-- Paso 4: Copiar precio actual a precio_por_unidad_venta
UPDATE productos 
SET precio_por_unidad_venta = precio 
WHERE precio_por_unidad_venta IS NULL;

-- Paso 5: Hacer precio_por_unidad_venta NOT NULL después de copiar
ALTER TABLE productos 
MODIFY COLUMN precio_por_unidad_venta DECIMAL(10,2) 
NOT NULL 
COMMENT 'Precio por unidad de venta';

-- Paso 6: Modificar cantidad de INT a DECIMAL(10,3) para permitir decimales
-- IMPORTANTE: Esto preserva los valores existentes
ALTER TABLE productos 
MODIFY COLUMN cantidad DECIMAL(10,3) 
NOT NULL DEFAULT 0.000 
COMMENT 'Cantidad de stock (permite decimales para kg, litros, etc.)';

-- Paso 7: Verificar cambios
DESCRIBE productos;

-- Paso 8: Mostrar resumen
SELECT 
    'Campos agregados exitosamente' AS mensaje,
    COUNT(*) AS total_productos,
    SUM(CASE WHEN unidad_stock = 'unidad' THEN 1 ELSE 0 END) AS productos_por_unidad,
    SUM(CASE WHEN unidad_venta = 'unidad' THEN 1 ELSE 0 END) AS venta_por_unidad
FROM productos;

SELECT 'Script ejecutado exitosamente. Los productos existentes mantienen unidad_stock=unidad y unidad_venta=unidad por defecto.' AS resultado;

