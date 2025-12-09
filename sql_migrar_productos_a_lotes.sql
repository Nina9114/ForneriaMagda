-- ================================================================
-- Script SQL para migrar productos existentes a lotes
-- ================================================================
-- 
-- Este script crea lotes iniciales para todos los productos
-- existentes que tienen cantidad > 0.
--
-- IMPORTANTE: Ejecutar DESPUÉS de crear la tabla lotes
-- Ejecutar: mysql -u usuario -p forneria < sql_migrar_productos_a_lotes.sql
--
-- ================================================================

USE forneria;

-- Crear lotes iniciales para productos existentes
INSERT INTO lotes (
    productos_id,
    cantidad,
    cantidad_inicial,
    fecha_elaboracion,
    fecha_caducidad,
    fecha_recepcion,
    origen,
    estado,
    creado
)
SELECT 
    id AS productos_id,
    cantidad,
    cantidad AS cantidad_inicial,
    elaboracion AS fecha_elaboracion,
    caducidad AS fecha_caducidad,
    NOW() AS fecha_recepcion,
    'ajuste_manual' AS origen,
    CASE 
        WHEN cantidad > 0 THEN 'activo'
        WHEN estado_merma = 'en_merma' THEN 'en_merma'
        ELSE 'agotado'
    END AS estado,
    NOW() AS creado
FROM productos
WHERE eliminado IS NULL
  AND cantidad > 0;

-- Mostrar resumen
SELECT 
    COUNT(*) AS total_lotes_creados,
    SUM(cantidad) AS total_unidades,
    COUNT(CASE WHEN estado = 'activo' THEN 1 END) AS lotes_activos
FROM lotes
WHERE origen = 'ajuste_manual';

-- Verificar que se crearon correctamente
SELECT 
    p.nombre,
    p.cantidad AS cantidad_producto,
    l.cantidad AS cantidad_lote,
    l.estado,
    l.fecha_caducidad
FROM productos p
LEFT JOIN lotes l ON p.id = l.productos_id
WHERE p.eliminado IS NULL
  AND p.cantidad > 0
ORDER BY p.nombre
LIMIT 10;

SELECT 'Migración completada. Revisa los resultados arriba.' AS mensaje;

