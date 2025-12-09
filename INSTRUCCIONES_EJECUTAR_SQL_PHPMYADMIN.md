# Instrucciones para Ejecutar Scripts SQL en phpMyAdmin

## 📋 Pasos para Ejecutar los Scripts

### Paso 1: Crear la Tabla de Lotes

1. **Abre phpMyAdmin** en tu navegador
2. **Selecciona la base de datos** `forneria` (o el nombre que uses)
3. **Haz clic en la pestaña "SQL"** (arriba del área de trabajo)
4. **Abre el archivo** `sql_crear_tabla_lotes_phpmyadmin.sql`
5. **Copia TODO el contenido** del archivo
6. **Pega el contenido** en el área de texto de phpMyAdmin
7. **Haz clic en "Continuar"** o "Ejecutar" (botón azul abajo)
8. **Verifica** que aparezca el mensaje de éxito y la descripción de la tabla

### Paso 2: Migrar Productos Existentes a Lotes (Opcional)

**⚠️ IMPORTANTE**: Solo ejecutar si ya tienes productos en la base de datos y quieres crear lotes iniciales para ellos.

1. **Abre phpMyAdmin** (si no está abierto)
2. **Selecciona la base de datos** `forneria`
3. **Haz clic en la pestaña "SQL"**
4. **Abre el archivo** `sql_migrar_productos_a_lotes_phpmyadmin.sql`
5. **Copia TODO el contenido** del archivo
6. **Pega el contenido** en el área de texto de phpMyAdmin
7. **Haz clic en "Continuar"** o "Ejecutar"
8. **Revisa el resultado**: Deberías ver un resumen con:
   - Total de lotes creados
   - Total de unidades
   - Lotes activos

## ✅ Verificación

Después de ejecutar los scripts, verifica que todo esté correcto:

### Verificar que la tabla existe:
```sql
SHOW TABLES LIKE 'lotes';
```

### Verificar estructura de la tabla:
```sql
DESCRIBE lotes;
```

### Ver algunos lotes creados:
```sql
SELECT * FROM lotes LIMIT 5;
```

## 🔍 Solución de Problemas

### Error: "Table 'lotes' already exists"
- **Solución**: La tabla ya existe. Puedes omitir el Paso 1 o eliminar la tabla primero (si está vacía):
```sql
DROP TABLE IF EXISTS lotes;
```

### Error: "Cannot add foreign key constraint"
- **Causa**: La tabla `productos` o `detalle_factura_proveedor` no existe
- **Solución**: Verifica que todas las tablas existan antes de crear `lotes`

### Error: "Unknown column 'estado_merma'"
- **Causa**: La tabla `productos` no tiene el campo `estado_merma`
- **Solución**: Ejecuta primero `sql_agregar_campos_merma.sql` si no lo has hecho

## 📝 Notas

- Los scripts están diseñados para ser **idempotentes** (puedes ejecutarlos múltiples veces sin problemas)
- El script de migración solo crea lotes para productos con `cantidad > 0`
- Los productos con `cantidad = 0` no tendrán lotes iniciales (se crearán cuando se reabastezcan)

## 🎯 Próximos Pasos

Después de ejecutar los scripts:
1. Reinicia el servidor Django (si está corriendo)
2. Prueba el módulo de Producción: `http://127.0.0.1:8000/produccion/`
3. Intenta registrar un lote de producción propia

