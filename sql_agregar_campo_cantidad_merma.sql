-- ================================================================
-- Script SQL para agregar el campo cantidad_merma a la tabla productos
-- ================================================================
-- 
-- Este campo almacena la cantidad de unidades que se fueron a merma
-- antes de poner la cantidad en 0. Esto permite mantener un registro
-- histórico de cuántas unidades se perdieron.
--
-- Ejecutar este script en la base de datos MySQL:
-- mysql -u usuario -p nombre_base_datos < sql_agregar_campo_cantidad_merma.sql
--
-- ================================================================

USE forneria;

-- Agregar el campo cantidad_merma a la tabla productos
ALTER TABLE productos 
ADD COLUMN cantidad_merma INT NULL DEFAULT 0 
AFTER fecha_merma;

-- Agregar comentario al campo
ALTER TABLE productos 
MODIFY COLUMN cantidad_merma INT NULL DEFAULT 0 
COMMENT 'Cantidad de unidades que se fueron a merma (se guarda antes de poner cantidad en 0)';

-- Verificar que el campo se agregó correctamente
DESCRIBE productos;

