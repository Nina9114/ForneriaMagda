-- ================================================================
-- Script SQL para crear la tabla de lotes
-- ================================================================
-- 
-- Esta tabla permite gestionar múltiples lotes del mismo producto
-- con diferentes fechas de elaboración y caducidad.
--
-- Ejecutar este script en la base de datos MySQL:
-- mysql -u usuario -p nombre_base_datos < sql_crear_tabla_lotes.sql
--
-- ================================================================

USE forneria;

-- Crear tabla de lotes
CREATE TABLE IF NOT EXISTS `lotes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  
  -- Relaciones
  `productos_id` INT NOT NULL,
  `detalle_factura_proveedor_id` INT NULL,
  
  -- Información del lote
  `numero_lote` VARCHAR(50) NULL COMMENT 'Número de lote del proveedor o código interno (opcional)',
  `cantidad` INT NOT NULL DEFAULT 0 COMMENT 'Cantidad actual del lote',
  `cantidad_inicial` INT NOT NULL COMMENT 'Cantidad original cuando se creó el lote',
  
  -- Fechas
  `fecha_elaboracion` DATE NULL COMMENT 'Fecha de elaboración del lote',
  `fecha_caducidad` DATE NOT NULL COMMENT 'Fecha de caducidad del lote',
  `fecha_recepcion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora en que se recibió/creó el lote',
  
  -- Origen y estado
  `origen` ENUM('compra', 'produccion_propia', 'ajuste_manual') NOT NULL DEFAULT 'produccion_propia' COMMENT 'Origen del lote',
  `estado` ENUM('activo', 'agotado', 'vencido', 'en_merma') NOT NULL DEFAULT 'activo' COMMENT 'Estado actual del lote',
  
  -- Auditoría
  `creado` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `modificado` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  KEY `fk_lotes_productos_idx` (`productos_id`),
  KEY `fk_lotes_detalle_factura_idx` (`detalle_factura_proveedor_id`),
  KEY `idx_fecha_caducidad` (`fecha_caducidad`),
  KEY `idx_estado` (`estado`),
  KEY `idx_origen` (`origen`),
  KEY `idx_productos_estado` (`productos_id`, `estado`),
  
  CONSTRAINT `fk_lotes_productos` 
    FOREIGN KEY (`productos_id`) 
    REFERENCES `productos` (`id`) 
    ON DELETE CASCADE,
    
  CONSTRAINT `fk_lotes_detalle_factura` 
    FOREIGN KEY (`detalle_factura_proveedor_id`) 
    REFERENCES `detalle_factura_proveedor` (`id`) 
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Verificar que la tabla se creó correctamente
DESCRIBE lotes;

-- Mostrar mensaje de confirmación
SELECT 'Tabla lotes creada exitosamente' AS mensaje;

