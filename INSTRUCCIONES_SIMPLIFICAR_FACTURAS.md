# Instrucciones: Simplificar Sistema de Facturas

## 📋 Resumen de Cambios

Se ha simplificado el modelo de facturas eliminando el campo `estado_recepcion` y usando `fecha_recepcion` para determinar si una factura fue recibida.

### Cambios Realizados:

1. **Eliminado campo `estado_recepcion`** de la tabla `factura_proveedor`
2. **Agregado estado 'atrasado'** al enum `estado_pago`
3. **Campos `subtotal_sin_iva` y `total_iva` ahora son nullable** (se calculan automáticamente)
4. **Lógica simplificada**: Si `fecha_recepcion` es NULL → factura pendiente; si tiene valor → factura recibida

---

## 🔧 Pasos para Aplicar los Cambios

### Paso 1: Ejecutar Script SQL

Ejecuta el script SQL en phpMyAdmin:

**Archivo**: `sql_simplificar_factura_compra_phpmyadmin.sql`

Este script:
- Agrega el estado 'atrasado' al enum `estado_pago`
- Hace `subtotal_sin_iva` y `total_iva` nullable
- Elimina el campo `estado_recepcion`

### Paso 2: Verificar Cambios en el Código

Los siguientes archivos han sido actualizados:

#### Modelo Django:
- ✅ `ventas/models/proveedores.py`
  - Eliminado `ESTADO_RECEPCION_CHOICES`
  - Eliminado campo `estado_recepcion`
  - Agregado 'atrasado' a `ESTADO_PAGO_CHOICES`
  - `subtotal_sin_iva` y `total_iva` ahora son nullable

#### Vistas:
- ✅ `ventas/views/views_facturas_proveedores.py`
  - Filtros actualizados para usar `fecha_recepcion` en lugar de `estado_recepcion`
  - Eliminadas referencias a `estado_recepcion` en creación/edición

- ✅ `ventas/views/views_detalles_factura.py`
  - Actualizado `recibir_factura_ajax` para usar `fecha_recepcion`

#### Templates:
- ✅ `templates/factura_proveedor_form.html`
  - Reemplazado select de `estado_recepcion` por campo de fecha `fecha_recepcion`

- ✅ `templates/facturas_proveedores_list.html`
  - Filtro actualizado para usar `fecha_recepcion`

- ✅ `templates/factura_proveedor_detalle.html`
  - Todas las referencias a `estado_recepcion` reemplazadas por lógica basada en `fecha_recepcion`

---

## 📊 Nueva Estructura de la Tabla

```sql
CREATE TABLE `factura_proveedor` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `numero_factura` VARCHAR(50) NOT NULL,
  `fecha_factura` DATE NOT NULL,
  `fecha_vencimiento` DATE NULL,
  `fecha_recepcion` DATE NULL,  -- Si es NULL = pendiente, si tiene valor = recibida
  `subtotal_sin_iva` DECIMAL(10,2) NULL,  -- Se calcula automáticamente
  `descuento` DECIMAL(10,2) DEFAULT 0,
  `total_iva` DECIMAL(10,2) NULL,  -- Se calcula automáticamente
  `total_con_iva` DECIMAL(10,2) NOT NULL,
  `estado_pago` ENUM('pendiente', 'pagado', 'parcial', 'atrasado', 'cancelado') DEFAULT 'pendiente',
  `observaciones` TEXT NULL,
  `proveedor_id` INT NOT NULL,
  `creado` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `modificado` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `eliminado` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`proveedor_id`) REFERENCES `proveedor` (`id`)
);
```

---

## 🔄 Lógica de Recepción

**Antes:**
- Campo `estado_recepcion` con valores: 'pendiente', 'recibida', 'parcial', 'cancelada'
- Campo `fecha_recepcion` separado

**Ahora:**
- Solo campo `fecha_recepcion`
  - Si `fecha_recepcion` es `NULL` → Factura **pendiente** de recibir
  - Si `fecha_recepcion` tiene valor → Factura **recibida** (fecha indica cuándo)

---

## ✅ Verificación Post-Migración

Después de ejecutar el script SQL, verifica:

1. **Estructura de la tabla:**
   ```sql
   DESCRIBE factura_proveedor;
   ```
   - Debe mostrar `estado_pago` con opción 'atrasado'
   - No debe existir columna `estado_recepcion`
   - `subtotal_sin_iva` y `total_iva` deben ser NULL

2. **Datos existentes:**
   - Las facturas con `estado_recepcion = 'recibida'` deben tener `fecha_recepcion` establecida
   - Las facturas con `estado_recepcion = 'pendiente'` deben tener `fecha_recepcion = NULL`

3. **Funcionalidad:**
   - Crear nueva factura → debe funcionar sin campo `estado_recepcion`
   - Recibir factura → debe establecer `fecha_recepcion`
   - Filtrar facturas → debe funcionar con el nuevo filtro

---

## ⚠️ Notas Importantes

1. **Migración de datos existentes:**
   Si tienes facturas existentes, asegúrate de que:
   - Facturas con `estado_recepcion = 'recibida'` tengan `fecha_recepcion` establecida
   - Facturas con `estado_recepcion = 'pendiente'` tengan `fecha_recepcion = NULL`

2. **Cálculo automático de totales:**
   Los campos `subtotal_sin_iva` y `total_iva` ahora son nullable porque se calculan automáticamente desde los detalles de la factura usando el método `actualizar_totales()`.

3. **Estado 'atrasado':**
   El nuevo estado 'atrasado' se puede usar para facturas vencidas sin pagar. Puedes implementar lógica automática para marcar facturas como 'atrasado' cuando `fecha_vencimiento < hoy` y `estado_pago = 'pendiente'`.

---

## 🚀 Próximos Pasos

1. Ejecutar el script SQL en phpMyAdmin
2. Reiniciar el servidor Django (`python manage.py runserver`)
3. Probar crear una nueva factura
4. Probar recibir una factura
5. Verificar que los filtros funcionen correctamente

---

## 📝 Ejemplo de Uso

### Crear Factura:
```python
factura = FacturaProveedor.objects.create(
    proveedor=proveedor,
    numero_factura="FAC-2025-001",
    fecha_factura=date.today(),
    fecha_vencimiento=date.today() + timedelta(days=30),
    fecha_recepcion=None,  # Pendiente de recibir
    estado_pago='pendiente',
    total_con_iva=Decimal('1000.00')
)
```

### Recibir Factura:
```python
factura.fecha_recepcion = date.today()  # Marca como recibida
factura.save()
```

### Verificar si está recibida:
```python
if factura.fecha_recepcion:
    print("Factura recibida")
else:
    print("Factura pendiente")
```

---

¿Necesitas ayuda con algún paso? Consulta la documentación o revisa los archivos actualizados.

