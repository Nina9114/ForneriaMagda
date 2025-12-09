# Análisis: Lotes para Productos de Producción Propia

## Problema Identificado

El sistema de lotes propuesto inicialmente solo consideraba productos comprados a proveedores (vía facturas). Pero la Fornería también **produce productos propios** como:
- Pan horneado diario
- Pasteles
- Galletas artesanales
- Otros productos de panadería

Estos productos **NO vienen de facturas de proveedores**, pero **SÍ necesitan lotes** porque:
- Se producen en diferentes días (lote del lunes vs lote del martes)
- Tienen diferentes fechas de elaboración
- Tienen diferentes fechas de caducidad
- Necesitan FIFO (vender primero el pan más antiguo)

## Solución: Sistema de Lotes Unificado

### Casos de Uso para Crear Lotes

#### 1. **Productos Comprados (Facturas de Proveedores)**
- **Origen**: `DetalleFacturaProveedor`
- **Proceso**: Al recibir factura → Crear lote automáticamente
- **Fechas**: Del detalle de la factura

#### 2. **Productos de Producción Propia**
- **Origen**: Producción interna / Ajuste de stock manual
- **Proceso**: Al agregar stock manualmente → Crear lote
- **Fechas**: Ingresadas manualmente por el usuario

### Estructura de la Tabla `lotes`

```sql
CREATE TABLE `lotes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `productos_id` INT NOT NULL,
  
  -- Información del lote
  `numero_lote` VARCHAR(50) NULL,  -- Opcional: número de lote del proveedor o código interno
  `cantidad` INT NOT NULL DEFAULT 0,
  `cantidad_inicial` INT NOT NULL,  -- Cantidad original del lote
  
  -- Fechas
  `fecha_elaboracion` DATE NULL,
  `fecha_caducidad` DATE NOT NULL,
  `fecha_recepcion` DATETIME NOT NULL,  -- Cuándo se recibió/creó en el sistema
  
  -- Origen del lote
  `origen` ENUM('compra', 'produccion_propia', 'ajuste_manual') NOT NULL,
  `detalle_factura_proveedor_id` INT NULL,  -- Si viene de factura
  `usuario_creacion_id` INT NULL,  -- Usuario que creó el lote (para producción propia)
  
  -- Estado
  `estado` ENUM('activo', 'agotado', 'vencido', 'en_merma') DEFAULT 'activo',
  
  -- Auditoría
  `creado` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `modificado` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  KEY `fk_lotes_productos_idx` (`productos_id`),
  KEY `fk_lotes_detalle_factura_idx` (`detalle_factura_proveedor_id`),
  KEY `fk_lotes_usuario_idx` (`usuario_creacion_id`),
  KEY `idx_fecha_caducidad` (`fecha_caducidad`),
  KEY `idx_estado` (`estado`),
  KEY `idx_origen` (`origen`),
  
  CONSTRAINT `fk_lotes_productos` FOREIGN KEY (`productos_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `fk_lotes_detalle_factura` FOREIGN KEY (`detalle_factura_proveedor_id`) REFERENCES `detalle_factura_proveedor` (`id`),
  CONSTRAINT `fk_lotes_usuario` FOREIGN KEY (`usuario_creacion_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;
```

## Flujos de Trabajo

### Flujo 1: Productos Comprados (Facturas)

```
1. Usuario recibe factura de proveedor
2. Sistema crea lotes automáticamente:
   - Por cada DetalleFacturaProveedor
   - origen = 'compra'
   - detalle_factura_proveedor_id = ID del detalle
   - fecha_elaboracion = del detalle (si existe)
   - fecha_caducidad = del detalle (si existe)
   - cantidad = cantidad del detalle
```

### Flujo 2: Productos de Producción Propia

#### Opción A: Al Agregar Producto Nuevo
```
1. Usuario crea producto nuevo (ej: "Pan Integral")
2. Al guardar, si tiene cantidad > 0:
   - Sistema pregunta: "¿Es producción propia o comprado?"
   - Si es producción propia:
     - Crear lote con:
       - origen = 'produccion_propia'
       - fecha_elaboracion = fecha ingresada
       - fecha_caducidad = fecha ingresada
       - cantidad = cantidad inicial
```

#### Opción B: Al Agregar Stock a Producto Existente
```
1. Usuario edita producto existente
2. Aumenta cantidad (ej: de 10 a 50)
3. Sistema detecta aumento y pregunta:
   "¿Agregar como nuevo lote de producción propia?"
   - Si SÍ:
     - Formulario para ingresar:
       - Fecha elaboración
       - Fecha caducidad
       - Cantidad del nuevo lote
     - Crear lote con origen = 'produccion_propia'
   - Si NO:
     - Agregar al lote existente más reciente (comportamiento actual)
```

#### Opción C: Módulo de Producción (Recomendado)
```
1. Nuevo módulo "Producción" en el menú
2. Formulario para registrar producción diaria:
   - Seleccionar producto
   - Cantidad producida
   - Fecha elaboración (default: hoy)
   - Fecha caducidad (calculada o manual)
   - Observaciones
3. Al guardar:
   - Crear lote automáticamente
   - origen = 'produccion_propia'
   - Actualizar cantidad del producto
```

## Interfaz de Usuario Propuesta

### Vista: Agregar Stock de Producción Propia

```
┌─────────────────────────────────────────┐
│  Registrar Producción Propia            │
├─────────────────────────────────────────┤
│                                         │
│  Producto: [Pan Integral        ▼]     │
│  Cantidad: [50]                         │
│                                         │
│  Fecha Elaboración: [15/01/2025]       │
│  Fecha Caducidad:   [18/01/2025]       │
│                                         │
│  Número de Lote (opcional):            │
│  [PROD-2025-001]                        │
│                                         │
│  Observaciones:                         │
│  [Pan horneado en horno #2...]         │
│                                         │
│  [Cancelar]  [Guardar]                 │
└─────────────────────────────────────────┘
```

### Vista: Listado de Lotes por Producto

En el detalle del producto, mostrar todos los lotes:

```
┌─────────────────────────────────────────┐
│  Lotes de Pan Integral                   │
├─────────────────────────────────────────┤
│  Lote #1 (Compra)                       │
│  Cantidad: 30/50 | Vence: 20/01/2025   │
│  Elaboración: 10/01/2025               │
│  [Más antiguo - se vende primero]       │
│                                         │
│  Lote #2 (Producción Propia)            │
│  Cantidad: 50/50 | Vence: 18/01/2025   │
│  Elaboración: 15/01/2025                │
│                                         │
│  Lote #3 (Producción Propia)            │
│  Cantidad: 25/25 | Vence: 22/01/2025   │
│  Elaboración: 17/01/2025                │
└─────────────────────────────────────────┘
```

## Ventas con FIFO

Al vender productos, el sistema:
1. Busca el lote más antiguo (menor `fecha_caducidad`) con stock
2. Resta cantidad de ese lote
3. Si el lote se agota, marca como 'agotado'
4. Si necesita más unidades, pasa al siguiente lote más antiguo

**Ejemplo:**
- Cliente compra 60 panes
- Lote #1 tiene 30 → se venden 30 del Lote #1
- Lote #2 tiene 50 → se venden 30 del Lote #2
- Lote #1 queda agotado
- Lote #2 queda con 20 unidades

## Consideraciones Importantes

### 1. Productos Sin Fecha de Caducidad
Algunos productos de producción propia pueden no tener fecha de caducidad clara:
- **Solución**: Permitir `fecha_caducidad` NULL
- **FIFO**: Lotes sin fecha van al final
- **Alertas**: No generar alertas para lotes sin fecha

### 2. Productos que se Producen Diariamente
- **Ejemplo**: Pan fresco que se produce todos los días
- **Solución**: Crear un lote nuevo cada día automáticamente
- **Opcional**: Agrupar por día en la interfaz

### 3. Migración de Datos Existentes
Para productos existentes sin lotes:
- Crear un lote inicial con:
  - `origen = 'ajuste_manual'`
  - `cantidad = cantidad actual del producto`
  - `fecha_elaboracion = NULL` (desconocida)
  - `fecha_caducidad = caducidad actual` (si existe)

## Recomendación de Implementación

### Fase 1: Estructura Base
1. Crear tabla `lotes`
2. Crear modelo Django `Lote`
3. Migrar productos existentes (crear lote inicial)

### Fase 2: Facturas de Proveedores
1. Al recibir factura, crear lotes automáticamente
2. Asociar con `DetalleFacturaProveedor`

### Fase 3: Producción Propia
1. Crear vista/formulario para registrar producción
2. Al agregar stock manualmente, opción de crear lote
3. Mostrar lotes en detalle del producto

### Fase 4: Ventas FIFO
1. Modificar sistema de ventas para usar lotes
2. Implementar lógica FIFO

### Fase 5: Alertas por Lote
1. Generar alertas por lote
2. Mostrar en dashboard y detalle de producto

## Pregunta para el Usuario

¿Cómo prefieres registrar la producción propia?

**Opción A**: Módulo separado "Producción" (más organizado)
**Opción B**: Al editar producto, opción de "Agregar como nuevo lote" (más simple)
**Opción C**: Ambos (módulo para producción diaria, edición para ajustes)

¿Cuál prefieres?

