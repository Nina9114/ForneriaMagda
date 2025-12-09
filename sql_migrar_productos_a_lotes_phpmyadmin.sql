-- ================================================================
-- Script SQL para migrar productos existentes a lotes
-- ================================================================
-- 
-- INSTRUCCIONES PARA PHPMyAdmin:
-- 1. Abre phpMyAdmin
-- 2. Selecciona la base de datos "forneria"
-- 3. Ve a la pestaña "SQL"
-- 4. Copia y pega este script completo
-- 5. Haz clic en "Continuar" o "Ejecutar"
--
-- IMPORTANTE: Ejecutar DESPUÉS de crear la tabla lotes
--
-- ================================================================

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

-- Mostrar resumen de lotes creados
SELECT 
    COUNT(*) AS total_lotes_creados,
    SUM(cantidad) AS total_unidades,
    COUNT(CASE WHEN estado = 'activo' THEN 1 END) AS lotes_activos,
    COUNT(CASE WHEN estado = 'en_merma' THEN 1 END) AS lotes_en_merma
FROM lotes
WHERE origen = 'ajuste_manual';

