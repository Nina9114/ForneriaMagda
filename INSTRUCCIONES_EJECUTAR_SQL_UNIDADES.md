# Instrucciones: Ejecutar SQL para Unidades de Medida

## ⚠️ IMPORTANTE

**Ejecuta el script SQL ANTES de continuar con el código Django.**

## Pasos para Ejecutar

### Opción 1: phpMyAdmin (Recomendado)

1. Abre phpMyAdmin en tu navegador
2. Selecciona la base de datos `forneria`
3. Ve a la pestaña **"SQL"**
4. Abre el archivo `sql_agregar_unidades_medida_phpmyadmin.sql`
5. Copia TODO el contenido del archivo
6. Pégalo en el área de texto de phpMyAdmin
7. Haz clic en **"Continuar"** o presiona `Ctrl+Enter`
8. Verifica que aparezca el mensaje de éxito

### Opción 2: Línea de Comandos MySQL

```bash
mysql -u tu_usuario -p forneria < sql_agregar_unidades_medida.sql
```

## ¿Qué hace el script?

1. ✅ Agrega campo `unidad_stock` (ENUM: unidad, kg, g, l, ml)
2. ✅ Agrega campo `unidad_venta` (ENUM: unidad, kg, g, l, ml)
3. ✅ Agrega campo `precio_por_unidad_venta` (DECIMAL)
4. ✅ Copia el precio actual a `precio_por_unidad_venta`
5. ✅ Modifica `cantidad` de INT a DECIMAL(10,3) para permitir decimales

## Verificación

Después de ejecutar, verifica con:

```sql
DESCRIBE productos;
```

Deberías ver los nuevos campos:
- `unidad_stock`
- `unidad_venta`
- `precio_por_unidad_venta`
- `cantidad` (ahora DECIMAL)

## Datos Existentes

Los productos existentes se configuran automáticamente:
- `unidad_stock = 'unidad'` (por defecto)
- `unidad_venta = 'unidad'` (por defecto)
- `precio_por_unidad_venta = precio` (copiado del precio actual)
- `cantidad` se mantiene igual (convertido a decimal)

## Siguiente Paso

Una vez ejecutado el SQL, continúa con la actualización de formularios y POS.

