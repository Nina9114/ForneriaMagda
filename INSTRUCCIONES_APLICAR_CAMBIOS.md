# 📋 Instrucciones para Aplicar los Cambios

## ⚠️ IMPORTANTE: Ejecutar Scripts SQL Primero

Antes de probar los cambios, debes ejecutar estos scripts SQL en tu base de datos:

### 1. Crear tabla de Historial de Merma

**Archivo:** `sql_crear_historial_merma.sql`

**Cómo ejecutar:**
- Abre phpMyAdmin o tu cliente MySQL
- Selecciona la base de datos `forneria` (o la que uses)
- Ve a la pestaña "SQL"
- Copia y pega el contenido de `sql_crear_historial_merma.sql`
- Haz clic en "Ejecutar"

**O desde PowerShell con MySQL:**
```powershell
mysql -u forneria_user -p forneria < sql_crear_historial_merma.sql
```

### 2. Actualizar tabla de Alertas

**Archivo:** `sql_actualizar_alertas_facturas.sql`

**Cómo ejecutar:**
- En phpMyAdmin, ve a la pestaña "SQL"
- Copia y pega el contenido de `sql_actualizar_alertas_facturas.sql`
- Haz clic en "Ejecutar"

**O desde PowerShell:**
```powershell
mysql -u forneria_user -p forneria < sql_actualizar_alertas_facturas.sql
```

## 🔄 Reiniciar el Servidor Django

Después de ejecutar los scripts SQL, reinicia el servidor Django:

### Si el servidor está corriendo:
1. Presiona `Ctrl + C` en la terminal donde está corriendo
2. Luego ejecuta:
```powershell
python manage.py runserver
```

### Si no está corriendo:
```powershell
python manage.py runserver
```

## ✅ Verificar que Todo Funcione

1. **Merma:** Intenta mover un producto a merma y verifica que se cree un registro en `historial_merma`
2. **Facturas:** Crea una factura marcándola como "pagada" y verifica que se cree el pago automáticamente
3. **Lotes:** Recibe una factura y verifica que se creen lotes para los productos
4. **Alertas:** Verifica que aparezcan alertas de facturas vencidas
5. **Inventario:** Prueba los filtros (activos, inactivos, en merma, todos)

## 🐛 Si Hay Errores

Si encuentras errores al ejecutar los scripts SQL:

1. **Error: "Column already exists"** - La columna ya existe, puedes ignorar ese error
2. **Error: "Table already exists"** - La tabla ya existe, puedes ignorar ese error
3. **Error de Foreign Key** - Verifica que las tablas `productos` y `factura_proveedor` existan

## 📝 Notas

- Los modelos Django tienen `managed = False`, por lo que NO necesitas hacer `makemigrations` ni `migrate`
- Los cambios en las vistas y lógica de negocio se aplican automáticamente al reiniciar el servidor
- Si modificas los modelos (agregas campos nuevos), necesitarás ejecutar los scripts SQL correspondientes

