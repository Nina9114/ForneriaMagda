-- ================================================================
-- =                                                              =
-- =     SCRIPT SQL: CREAR TABLA HISTORIAL_BOLETAS               =
-- =                                                              =
-- ================================================================
-- 
-- Este script crea la tabla para almacenar el historial de boletas
-- emitidas. Almacena los datos en formato JSON para eficiencia.
--
-- IMPORTANTE: Ejecutar este script en la base de datos MySQL
-- antes de usar el módulo de historial de boletas.

CREATE TABLE IF NOT EXISTS `historial_boletas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `folio` varchar(20) NOT NULL,
  `fecha_emision` datetime(6) NOT NULL,
  `fecha_venta` datetime(6) NOT NULL,
  `cliente_nombre` varchar(150) NOT NULL,
  `total_con_iva` decimal(10,2) NOT NULL,
  `num_productos` int NOT NULL DEFAULT '0',
  `canal_venta` varchar(20) NOT NULL,
  `datos_boleta` json NOT NULL,
  `usuario_emisor` varchar(150) DEFAULT NULL,
  `modificado` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_modificacion` datetime(6) DEFAULT NULL,
  `observaciones` longtext,
  PRIMARY KEY (`id`),
  KEY `historial_boletas_venta_id_idx` (`venta_id`),
  KEY `historial_boletas_folio_idx` (`folio`),
  KEY `historial_boletas_fecha_emision_idx` (`fecha_emision`),
  KEY `historial_boletas_cliente_nombre_idx` (`cliente_nombre`),
  CONSTRAINT `historial_boletas_venta_id_fk` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

