-- ================================================================
-- =  SCRIPT SQL PARA PHPMYADMIN: UNIDADES DE MEDIDA            =
-- ================================================================
-- 
-- INSTRUCCIONES:
-- 1. Abrir phpMyAdmin
-- 2. Seleccionar la base de datos "forneria"
-- 3. Ir a la pestaña "SQL"
-- 4. Copiar y pegar este script completo
-- 5. Hacer clic en "Continuar"
--
-- ================================================================

-- Paso 1: Agregar campo unidad_stock
ALTER TABLE `productos` 
ADD COLUMN `unidad_stock` ENUM('unidad', 'kg', 'g', 'l', 'ml') 
NOT NULL DEFAULT 'unidad' 
COMMENT 'Unidad en que se almacena el stock (unidad, kg, g, l, ml)';

-- Paso 2: Agregar campo unidad_venta
ALTER TABLE `productos` 
ADD COLUMN `unidad_venta` ENUM('unidad', 'kg', 'g', 'l', 'ml') 
NOT NULL DEFAULT 'unidad' 
COMMENT 'Unidad en que se vende el producto (unidad, kg, g, l, ml)';

-- Paso 3: Agregar campo precio_por_unidad_venta
ALTER TABLE `productos` 
ADD COLUMN `precio_por_unidad_venta` DECIMAL(10,2) 
NULL 
COMMENT 'Precio por unidad de venta (ej: precio por kilo, precio por litro). NULL se copiará desde precio';

-- Paso 4: Copiar precio actual a precio_por_unidad_venta
UPDATE `productos` 
SET `precio_por_unidad_venta` = `precio` 
WHERE `precio_por_unidad_venta` IS NULL;

-- Paso 5: Hacer precio_por_unidad_venta NOT NULL después de copiar
ALTER TABLE `productos` 
MODIFY COLUMN `precio_por_unidad_venta` DECIMAL(10,2) 
NOT NULL 
COMMENT 'Precio por unidad de venta';

-- Paso 6: Modificar cantidad de INT a DECIMAL(10,3) para permitir decimales
-- IMPORTANTE: Esto preserva los valores existentes
ALTER TABLE `productos` 
MODIFY COLUMN `cantidad` DECIMAL(10,3) 
NOT NULL DEFAULT 0.000 
COMMENT 'Cantidad de stock (permite decimales para kg, litros, etc.)';

-- Verificar cambios
DESCRIBE `productos`;

