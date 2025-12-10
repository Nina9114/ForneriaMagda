-- ============================================================
-- SCRIPT: CREAR TABLA HISTORIAL_MERMA
-- Sistema: Prototipo Fornería
-- Descripción: Tabla para mantener historial completo de merma
--              con estado activo/inactivo (no se eliminan registros)
-- ============================================================

CREATE TABLE IF NOT EXISTS `historial_merma` (
  `id` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `cantidad_merma` decimal(10,3) NOT NULL COMMENT 'Cantidad que se fue a merma',
  `motivo_merma` text NOT NULL COMMENT 'Motivo detallado por el cual el producto fue movido a merma',
  `fecha_merma` datetime NOT NULL COMMENT 'Fecha y hora en que el producto fue movido a merma',
  `activo` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Si True, el registro está activo. Si False, está inactivo (no se elimina)',
  `creado` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora de creación del registro',
  `modificado` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha y hora de última modificación',
  PRIMARY KEY (`id`),
  KEY `fk_historial_merma_producto_idx` (`producto_id`),
  KEY `idx_fecha_merma` (`fecha_merma`),
  KEY `idx_activo` (`activo`),
  KEY `idx_producto_activo` (`producto_id`, `activo`),
  CONSTRAINT `fk_historial_merma_producto`
    FOREIGN KEY (`producto_id`)
    REFERENCES `productos` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Historial completo de productos en merma (no se eliminan registros, solo se desactivan)';

