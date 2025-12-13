Manual de Usuario - Sistema de Gestión La Fornería

Índice
1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Dashboard](#dashboard)
4. [Gestión de Usuarios](#gestión-de-usuarios)
5. [Gestión de Productos](#gestión-de-productos)
6. [Punto de Venta (POS)](#punto-de-venta-pos)
7. [Gestión de Inventario](#gestión-de-inventario)
8. [Control de Producción](#control-de-producción)
9. [Gestión de Proveedores](#gestión-de-proveedores)
10. [Reportes](#reportes)
11. [Sistema de Alertas](#sistema-de-alertas)
12. [Gestión de Merma](#gestión-de-merma)

---

Introducción

Este manual le guiará paso a paso en el uso del Sistema de Gestión La Fornería, una plataforma web diseñada para administrar de manera integral las operaciones de su panadería.

Características Principales
- Sistema de ventas (POS) con múltiples métodos de pago
- Gestión de inventario en tiempo real
- Control de producción
- Gestión de proveedores y facturas
- Gestión de usuarios y roles
- Reportes y análisis
- Sistema de alertas automatizado

---

Acceso al Sistema

Paso 1: Abrir el Navegador
1. Abra su navegador web (Chrome, Firefox o Edge)
2. Ingrese la URL del sistema: `[COMPLETAR URL]`

Paso 2: Iniciar Sesión
1. En la pantalla de login, ingrese su usuario y contraseña
2. Haga clic en el botón "Iniciar Sesión"
3. Si las credenciales son correctas, será redirigido al Dashboard

Recuperar Contraseña

Si olvidó su contraseña:

1. En la pantalla de login, haga clic en "¿Olvidó su contraseña?"
2. Ingrese su correo electrónico asociado a su cuenta
3. Haga clic en "Enviar"
4. Revise su bandeja de entrada. Recibirá un correo con un enlace para restablecer su contraseña
5. Haga clic en el enlace del correo
6. Ingrese su nueva contraseña y confirme la contraseña
7. Haga clic en "Restablecer Contraseña"
8. Podrá iniciar sesión con su nueva contraseña

Nota: El enlace de recuperación tiene una validez limitada. Si expira, deberá solicitar uno nuevo.

[CAPTURA DE PANTALLA: Pantalla de Login]

---

Dashboard

El Dashboard es la pantalla principal del sistema y muestra información clave en tiempo real.

Métricas Principales
- Ventas del Día: Total de ventas realizadas en el día actual
- Alertas Pendientes: Cantidad de alertas que requieren atención
- Stock Bajo: Número de productos con stock bajo
- Top Producto: Producto más vendido del día

Secciones del Dashboard
1. Métricas en Tarjetas: Resumen visual de indicadores clave
2. Tabla de Ventas del Día: Detalle de todas las ventas del día
3. Tabla de Productos con Stock Bajo: Lista de productos que requieren reposición
4. Tabla de Productos en Merma: Productos que han sido enviados a merma

[CAPTURA DE PANTALLA: Dashboard completo]

---

Gestión de Usuarios

> Importante: Esta sección solo está disponible para usuarios con permisos de Superusuario (Administrador). Si no ve esta opción en el menú, contacte al administrador del sistema.

El módulo de gestión de usuarios permite administrar las cuentas de todos los usuarios del sistema, asignar roles y gestionar permisos.

Ver Lista de Usuarios

1. En el menú lateral, haga clic en "Usuarios"
2. Se mostrará una tabla con todos los usuarios del sistema, incluyendo:
   - ID: Identificador único del usuario
   - Usuario: Nombre de usuario para iniciar sesión
   - Correo: Correo electrónico del usuario
   - Nombre y Apellidos: Nombre completo del usuario
   - Rol: Rol asignado al usuario en el sistema
   - Staff: Indica si el usuario tiene permisos de staff
   - Super: Indica si el usuario es superusuario
   -Activo:Indica si la cuenta está activa
   -Último login:Fecha y hora del último acceso

[CAPTURA DE PANTALLA: Lista de usuarios]

Crear un Nuevo Usuario

1. En la lista de usuarios, haga clic en el botón "➕ Crear Usuario"
2. Complete el formulario con la siguiente información:
   - Usuario: Nombre de usuario único (obligatorio)
   - Correo electrónico: Correo válido y único (obligatorio)
   - Nombre: Nombre del usuario (opcional)
   - Apellidos: Apellidos del usuario (opcional)
   - Contraseña: Contraseña segura (obligatorio)
   - Confirmar contraseña: Repita la contraseña (obligatorio)
   - RUN: Número de RUN del usuario (opcional, formato: 12345678-9)
   - Rol: Seleccione un rol del sistema (opcional)

3. Haga clic en "Guardar"
4. El usuario será creado y podrá iniciar sesión inmediatamente

Nota: Por defecto, los nuevos usuarios se crean como usuarios activos con permisos de staff, pero sin permisos de superusuario.

[CAPTURA DE PANTALLA: Formulario de crear usuario]

Editar un Usuario

1. En la lista de usuarios, haga clic en el botón "Editar" del usuario deseado
2. Modifique los campos necesarios:
   - Puede cambiar el nombre, apellidos, correo electrónico
   - Puede cambiar el RUN
   - Puede asignar o cambiar el rol del usuario
   - Puede cambiar la contraseña (opcional, deje en blanco si no desea cambiarla)
   - Puede activar o desactivar la cuenta

3. Haga clic en "Guardar Cambios"

Nota: Si deja el campo de contraseña en blanco, la contraseña actual se mantendrá sin cambios.

[CAPTURA DE PANTALLA: Formulario de editar usuario]

Eliminar un Usuario

1. En la lista de usuarios, haga clic en el botón "Eliminar" del usuario deseado
2. Se mostrará una confirmación para asegurar que desea eliminar el usuario
3. Revise la información del usuario a eliminar
4. Haga clic en "Confirmar Eliminación"

Importante: 
-No puede eliminar su propio usuariomientras esté conectado
- La eliminación es permanente y no se puede deshacer
- Asegúrese de que el usuario no tenga datos críticos asociados antes de eliminarlo

[CAPTURA DE PANTALLA: Confirmación de eliminar usuario]

Roles de Usuario

El sistema utiliza roles para asignar permisos y controlar el acceso a diferentes secciones:

-Administrador/Superusuario:Acceso completo al sistema, incluyendo gestión de usuarios
-Staff:Usuarios con permisos de personal, pueden acceder a funciones administrativas básicas
-Roles personalizados:El sistema puede tener roles adicionales definidos por el administrador

Nota: Los roles disponibles pueden variar según la configuración del sistema. Contacte al administrador para más información sobre los roles específicos.

---

Gestión de Productos

La página de Inventario permite gestionar todos los productos del sistema. En la parte superior encontrará botones para:

- Agregar Producto: Crear un nuevo producto
- Mostrar/Ocultar Inactivos: Alternar la visualización de productos inactivos
- Ajustes de Stock: Acceder a la página de ajustes manuales de stock

Agregar un Nuevo Producto

1. En el menú lateral, haga clic en "Inventario"
2. Haga clic en el botón "Agregar Producto"
3. Complete el formulario con la siguiente información:
   - Nombre del Producto: Nombre descriptivo
   - SKU: Código único del producto
   - Categoría: Seleccione la categoría correspondiente
   - Precio Neto: Precio sin IVA
   - Unidad de Medida: Unidad, Kilo, Litro, etc.
   - Stock Inicial: Cantidad inicial en inventario
   - Stock Mínimo: Cantidad mínima antes de generar alerta
   - Fecha de Vencimiento: Si aplica
   - Descripción: Información adicional del producto

4. Haga clic en "Guardar"

[CAPTURA DE PANTALLA: Formulario de agregar producto]

Editar un Producto

1. En la lista de productos, haga clic en el botón "Editar" del producto deseado
2. Modifique los campos necesarios
3. Haga clic en "Guardar Cambios"

[CAPTURA DE PANTALLA: Formulario de editar producto]

Activar o Desactivar un Producto

Los productos pueden estar en estado "Activo" o "Inactivo". Un producto inactivo no está disponible para venta.

Para activar o desactivar un producto:

1. En la lista de productos, localice el producto deseado
2. En la columna "Acciones", encontrará:
   - Si el producto está Activo: verá un botón "Desactivar" (icono de pausa)
   - Si el producto está Inactivo: verá un botón "Activar" (icono de play)
3. Haga clic en el botón correspondiente
4. Confirme la acción en el mensaje que aparece
5. El producto cambiará de estado automáticamente

Nota: 
- Un producto inactivo no aparecerá en el punto de venta (POS)
- Los productos inactivos se pueden ver activando el filtro "Mostrar Inactivos"
- Desactivar un producto no elimina su información, solo lo oculta de las ventas

[CAPTURA DE PANTALLA: Botones de activar/desactivar producto]

Ver Detalle de un Producto

1. En la lista de productos, haga clic en elnombre del productoo en el botón "Ver Detalle"
2. Se mostrará información completa:
   - Datos generales del producto
   - Stock actual
   - Historial de lotes
   - Historial de movimientos
   - Historial de merma

[CAPTURA DE PANTALLA: Detalle de producto]

Filtrar y Buscar Productos

En la lista de productos, puede usar las siguientes opciones:

Búsqueda por Texto:
- Utilice el campo de búsqueda para buscar productos por:
  - Nombre del producto
  - Marca
  - Tipo
  - Formato
  - Categoría (puede buscar por nombre de categoría)

Mostrar/Ocultar Productos Inactivos:
- Haga clic en el botón "Mostrar Inactivos" para ver también los productos que están inactivos
- Por defecto, solo se muestran los productos activos y los productos en merma

Nota: Los productos con stock bajo se muestran automáticamente en el Dashboard en la sección "Productos con Stock Bajo", pero no hay un filtro específico en la página de inventario para filtrar solo por stock bajo.

[CAPTURA DE PANTALLA: Búsqueda y filtros de productos]

Acciones Masivas en Inventario

En la página de inventario, puede realizar acciones sobre múltiples productos seleccionados usando los checkboxes de cada fila.

Para usar las acciones masivas:

1. Seleccione uno o más productos marcando los checkboxes en la primera columna de la tabla
2. También puede usar el checkbox del encabezado para seleccionar/deseleccionar todos los productos visibles
3. Una vez seleccionados, se habilitarán los botones de acción masiva en la parte superior de la tabla

Acciones disponibles:

Crear Alertas:
- Seleccione los productos para los que desea crear alertas de vencimiento
- Haga clic en el botón "Crear Alertas" (icono de campana)
- Se generarán alertas automáticas para los productos seleccionados

Mover a Merma:
- Seleccione los productos que desea enviar a merma
- Haga clic en el botón "Mover a Merma" (icono de triángulo de advertencia)
- Se abrirá un modal para seleccionar los lotes específicos y cantidades a enviar a merma
- Ingrese el motivo de la merma y confirme

Eliminar:
- Seleccione los productos que desea eliminar
- Haga clic en el botón "Eliminar" (icono de papelera)
- Confirme la eliminación
- Nota: La eliminación es lógica (el producto se marca como eliminado pero no se borra de la base de datos)

[CAPTURA DE PANTALLA: Acciones masivas en inventario]

Ajustes de Stock desde Inventario

1. En la página de Inventario, haga clic en el botón "Ajustes de Stock" (icono de controles deslizantes) en la parte superior
2. Será redirigido a la página de Ajustes de Stock donde puede:
   - Agregar stock (entrada)
   - Reducir stock (salida)
   - Ver el historial de ajustes

Para más detalles sobre cómo realizar ajustes de stock, consulte la sección "Gestión de Inventario" → "Ajustar Stock".

---

Punto de Venta (POS)

Realizar una Venta

Paso 1: Seleccionar Cliente (Opcional)
1. En el menú lateral, haga clic en "Punto de Venta"
2. En la sección "Cliente", encontrará un selector desplegable con la lista de clientes registrados
3. Puede realizar una de las siguientes acciones:
   
   Opción A: Venta sin Cliente (Cliente Genérico)
   - Deje el selector en "-- Seleccionar cliente --"
   - La venta se registrará sin asociar un cliente específico
   - Esta opción es útil para ventas rápidas o cuando no se necesita registrar el cliente
   
   Opción B: Seleccionar Cliente Existente
   - Seleccione un cliente de la lista desplegable
   - El cliente quedará asociado a la venta
   
   Opción C: Crear Cliente Nuevo
   - Haga clic en el botón "Nuevo Cliente" (icono de persona con signo +)
   - Se abrirá un modal para registrar el cliente rápidamente
   - Complete el formulario:
     * Nombre: Nombre del cliente (obligatorio)
     * RUT: RUT del cliente (opcional, formato: 12345678-9)
     * Teléfono: Número de teléfono (opcional)
     * Email: Correo electrónico (opcional)
     * Dirección: Dirección del cliente (opcional)
   - Haga clic en "Guardar Cliente"
   - El nuevo cliente se agregará automáticamente al selector y quedará seleccionado
   - El modal se cerrará automáticamente

Nota: Si no selecciona un cliente, la venta se registrará como "Cliente Genérico" y no se asociará a ningún cliente específico.

[CAPTURA DE PANTALLA: Selector de cliente y modal de nuevo cliente]

Paso 2: Agregar Productos al Carrito
1. Busque el producto en la lista o use el buscador
2. Haga clic en el botón "Agregar" del producto
3. Ingrese la cantidad deseada
4. El producto se agregará al carrito automáticamente

[CAPTURA DE PANTALLA: POS con productos en carrito]

Paso 3: Aplicar Descuentos (Opcional)
1. En el carrito, puede aplicar descuentos individuales por producto:
   - Haga clic en el botón "Descuento" del producto en el carrito
   - Ingrese el porcentaje de descuento deseado
   - El descuento se aplicará solo a ese producto específico

[CAPTURA DE PANTALLA: Aplicar descuentos]

Paso 4: Seleccionar Método de Pago
1. En la sección de pago, seleccione el método:
   - Efectivo
   - Tarjeta Débito
   - Tarjeta Crédito
   - Transferencia
   - Cheque

2. Si es efectivo, ingrese el monto pagado por el cliente
3. El sistema calculará automáticamente el vuelto

[CAPTURA DE PANTALLA: Selección de método de pago]

Paso 5: Confirmar Venta
1. Revise el resumen de la venta:
   - Subtotal Neto
   - IVA (19%)
   - Total a Pagar
   - Método de Pago
   - Vuelto (si aplica)

2. Haga clic en "Confirmar Venta"
3. Se generará automáticamente el comprobante

[CAPTURA DE PANTALLA: Confirmación de venta]

Ver Historial de Ventas

1. En el menú lateral, haga clic en "Ventas"
2. Se mostrará una lista de todas las ventas realizadas
3. Puede filtrar por fecha, cliente o método de pago
4. Haga clic en una venta para ver el detalle completo

[CAPTURA DE PANTALLA: Lista de ventas]

Generar Comprobante

1. En el detalle de una venta, haga clic en "Descargar PDF" o "Descargar TXT"
2. El comprobante se descargará automáticamente

[CAPTURA DE PANTALLA: Comprobante PDF]

---

Gestión de Inventario

Ver Movimientos de Inventario

1. En el menú lateral, haga clic en "Inventario" → "Movimientos"
2. Se mostrará el historial completo de movimientos (Kardex)
3. Puede filtrar por:
   - Producto específico
   - Tipo de movimiento (Entrada, Salida, Ajuste)
   - Rango de fechas

[CAPTURA DE PANTALLA: Movimientos de inventario]

Ajustar Stock

1. En la lista de productos, haga clic en "Ajustar Stock"
2. Seleccione el tipo de ajuste:
   -Entrada:Para aumentar stock
   -Salida:Para disminuir stock
   -Ajuste:Para corregir diferencias

3. Ingrese la cantidad y una observación
4. Haga clic en "Guardar"

[CAPTURA DE PANTALLA: Ajuste de stock]

---

Control de Producción

El módulo de Control de Producción permite registrar los productos elaborados internamente (pan, pasteles, etc.) y gestionar sus lotes de producción.

Registrar un Lote de Producción

1. En el menú lateral, haga clic en "Producción"
2. Haga clic en el botón "Registrar Producción" o "Nueva Producción"
3. Complete el formulario con la siguiente información:
   - Producto: Seleccione el producto que se produjo (solo productos activos)
   - Cantidad Producida: Ingrese la cantidad producida
     - Importante: El sistema mostrará automáticamente la unidad de medida del producto seleccionado (kg, g, l, ml, unidad)
     - Por ejemplo, si el producto está en kilogramos y usted ingresa "10", se guardará como "10 kilogramos"
     - Puede ingresar decimales (ej: 10.5 kg, 2.3 litros)
   - Número de Lote: (Opcional) Código identificador del lote (ej: PROD-2025-001)
   - Fecha de Elaboración: Fecha en que se elaboró el producto (por defecto: fecha actual)
   - Fecha de Caducidad: Fecha en que vence el producto (obligatorio)

4. Haga clic en "Registrar Producción"

Nota Importante sobre Unidades de Medida:
- Al seleccionar un producto, el sistema mostrará automáticamente su unidad de medida junto al campo de cantidad
- Si el producto está configurado en kilogramos (kg), al ingresar "10" se guardará como "10 kg"
- Si el producto está en gramos (g), al ingresar "500" se guardará como "500 g"
- Si el producto está en litros (l), al ingresar "5" se guardará como "5 litros"
- El sistema permite decimales para unidades de peso y volumen (ej: 10.5 kg, 2.3 litros)

[CAPTURA DE PANTALLA: Formulario de registro de producción]

Ver Lista de Lotes de Producción

1. En el menú lateral, haga clic en "Producción"
2. Se mostrará una lista de todos los lotes de producción propia registrados
3. Puede filtrar por:
   - Producto: Seleccione un producto específico
   - Estado: Activo, Agotado, Vencido
   - Rango de fechas: Fecha desde y hasta
   - Búsqueda: Buscar por nombre de producto o número de lote

4. La lista muestra:
   - Producto
   - Cantidad actual del lote
   - Cantidad inicial del lote
   - Fecha de elaboración
   - Fecha de caducidad
   - Días hasta vencer
   - Estado del lote

[CAPTURA DE PANTALLA: Lista de producción]

Ver Detalle de un Lote

1. En la lista de producción, haga clic en el lote deseado
2. Se mostrará información detallada:
   - Información completa del lote
   - Producto asociado
   - Cantidad inicial y cantidad actual
   - Porcentaje consumido
   - Fechas (elaboración, caducidad, recepción)
   - Movimientos de inventario relacionados

[CAPTURA DE PANTALLA: Detalle de lote]

Información Importante

-Actualización Automática de Stock:Al registrar un lote de producción, el stock del producto se actualiza automáticamente
-Sistema FIFO:El sistema utiliza FIFO (First In First Out) para las ventas, vendiendo primero los lotes más antiguos
-Movimientos de Inventario:Cada lote registrado genera automáticamente un movimiento de inventario de tipo "entrada"

---

Gestión de Proveedores

Agregar un Proveedor

1. En el menú lateral, haga clic en "Proveedores"
2. Haga clic en "Nuevo Proveedor"
3. Complete el formulario con la siguiente información:

Campos Obligatorios:
   - Nombre: Razón social o nombre del proveedor (obligatorio)

Campos Opcionales:
   - RUT: RUT del proveedor (formato: 12345678-9)
   - Persona de Contacto: Nombre de la persona con quien contactar (ej: Juan Pérez)
   - Teléfono: Número telefónico de contacto (ej: +56 9 1234 5678)
   - Email: Correo electrónico del proveedor
   - Dirección: Dirección física del proveedor
   - Ciudad: Ciudad donde se encuentra el proveedor
   - Región: Región donde se encuentra el proveedor
   - Estado: Estado del proveedor (Activo o Inactivo). Por defecto se establece como "Activo"
   - Notas: Notas adicionales sobre el proveedor (información adicional que desee registrar)

4. Haga clic en "Guardar"

Nota: Solo el campo "Nombre" es obligatorio. Todos los demás campos son opcionales y pueden completarse según la información disponible del proveedor.

[CAPTURA DE PANTALLA: Formulario de proveedor]

Registrar Factura de Compra

1. En el menú lateral, haga clic en "Facturas Proveedores"
2. En la página de facturas, haga clic en el botón "Nueva Factura"
3. Complete el formulario con la siguiente información:

Campos Obligatorios:
   - Proveedor: Seleccione el proveedor que emitió la factura (obligatorio)
   - Número de Factura: Número de la factura del proveedor (obligatorio)
   - Fecha de Factura: Fecha en que el proveedor emitió la factura (obligatorio)

Campos Opcionales:
   - Fecha de Vencimiento: Fecha límite para pagar la factura (recomendado para control de pagos)
   - Estado de Pago: Estado del pago (Pendiente, Pago Parcial, Pagado, Atrasado, Cancelado/Anulado). Por defecto: Pendiente
   - Fecha de Recepción: Fecha en que se recibió la factura. Dejar vacío si aún no se ha recibido
   - Subtotal sin IVA (Neto): Monto sin IVA (el sistema calculará automáticamente el IVA y total)
   - Descuento (en pesos): Monto fijo en pesos a descontar (ej: 1000)
   - Observaciones: Notas adicionales sobre la factura

Nota: El sistema calcula automáticamente el IVA (19%) y el Total con IVA basándose en el Subtotal sin IVA y el Descuento ingresados.

4. Haga clic en "Guardar"
5. Será redirigido automáticamente al detalle de la factura creada

[CAPTURA DE PANTALLA: Formulario de nueva factura]

Agregar Productos a la Factura

Importante: Antes de agregar productos a una factura, los productos deben estar creados en el sistema. Si necesita crear un producto nuevo, debe hacerlo primero desde el módulo de Inventario (botón "Agregar Producto") antes de poder agregarlo a la factura.

Una vez creada la factura, puede agregar los productos que contiene:

1. En el detalle de la factura, encontrará la sección "Agregar Producto" (solo visible si la factura no ha sido recibida)
2. Complete el formulario para cada producto:
   - Producto: Seleccione el producto de la lista (obligatorio)
   - Cantidad: Ingrese la cantidad comprada (obligatorio)
   - Precio Unitario: Ingrese el precio unitario del producto (obligatorio)
   - Descuento %: Porcentaje de descuento aplicado al producto (opcional, por defecto 0%)
   - Fecha Vencimiento: Fecha de vencimiento del producto (opcional, si no se especifica se usará la fecha del producto o fecha factura + 30 días)
   - Número de Lote: Código del lote del proveedor (opcional, si no se especifica se generará automáticamente)
3. Haga clic en "Agregar"
4. El producto se agregará a la lista de productos de la factura
5. Repita el proceso para cada producto de la factura

Nota: Solo puede agregar productos a facturas que aún no han sido recibidas. Una vez recibida la factura, no se pueden agregar más productos.

[CAPTURA DE PANTALLA: Agregar producto a factura]

Recibir Factura

Cuando reciba físicamente la factura y los productos:

1. En el detalle de la factura, haga clic en el botón "Recibir Factura"
2. Ingrese la fecha de recepción (por defecto se usará la fecha actual)
3. Haga clic en "Confirmar Recepción"
4. El sistema actualizará automáticamente:
   - El stock de todos los productos agregados a la factura
   - Se crearán los lotes correspondientes para cada producto
   - La factura quedará marcada como "Recibida"

Nota: Una vez recibida la factura, no se pueden agregar más productos. Si necesita agregar productos adicionales, debe quitar la recepción primero.

[CAPTURA DE PANTALLA: Recepción de factura]

---

Reportes

El sistema de reportes permite generar análisis detallados de ventas, productos e inventario. Todos los reportes pueden exportarse a Excel, PDF o CSV para análisis adicionales o archivo.

Acceder al Sistema de Reportes

1. En el menú lateral, haga clic en "Reportes"
2. Se mostrará el portal de reportes con las siguientes opciones disponibles:
   - Reporte de Ventas
   - Top Productos
   - Reporte de Inventario

[CAPTURA DE PANTALLA: Portal de reportes]

Reporte de Ventas

Este reporte permite analizar las ventas realizadas con filtros avanzados y ver totales agregados.

1. En el portal de reportes, haga clic en "Ver Reporte" en la tarjeta de "Reporte de Ventas"
2. Complete los filtros de búsqueda:
   - Fecha Desde: Fecha inicial del rango (opcional)
   - Fecha Hasta: Fecha final del rango (opcional)
   - Cliente: Seleccione un cliente específico o "Todos los clientes" (opcional)
   - Canal: Seleccione el canal de venta (Presencial, Delivery) o "Todos" (opcional)

3. Haga clic en "Generar Reporte"
4. El reporte mostrará:
   - Lista de ventas que cumplen con los filtros seleccionados
   - Información de cada venta: fecha, cliente, canal, totales
   - Totales agregados: Total Neto, Total IVA, Total con IVA, Cantidad de Ventas, Promedio por Venta

5. Para exportar el reporte, haga clic en uno de los botones de exportación:
   - "Exportar Excel": Descarga el reporte en formato Excel (XLSX)
   - "Exportar PDF": Descarga el reporte en formato PDF para impresión
   - "Exportar CSV": Descarga el reporte en formato CSV para importación a otros sistemas

Nota: Si no selecciona fechas, el reporte mostrará todas las ventas. Se recomienda siempre especificar un rango de fechas para obtener resultados más precisos.

[CAPTURA DE PANTALLA: Reporte de ventas]

Reporte Top Productos

Este reporte muestra un ranking de los productos más vendidos, ya sea por cantidad de unidades vendidas o por monto neto facturado.

1. En el portal de reportes, haga clic en "Ver Reporte" en la tarjeta de "Top Productos"
2. Seleccione el tipo de ranking:
   - Por Cantidad: Muestra los productos más vendidos por número de unidades
   - Por Monto Neto: Muestra los productos con mayor facturación (monto neto)

3. Complete los filtros de búsqueda:
   - Fecha Desde: Fecha inicial del rango (opcional)
   - Fecha Hasta: Fecha final del rango (opcional)

4. Haga clic en "Generar Reporte"
5. El reporte mostrará:
   - Ranking de productos ordenados según el tipo seleccionado
   - Para cada producto: nombre, cantidad vendida, monto neto total, precio unitario promedio

6. Para exportar el reporte, haga clic en uno de los botones de exportación:
   - "Exportar Excel": Descarga el ranking en formato Excel (XLSX)
   - "Exportar PDF": Descarga el ranking en formato PDF
   - "Exportar CSV": Descarga el ranking en formato CSV

Nota: Si no selecciona fechas, el reporte usará el último mes por defecto.

[CAPTURA DE PANTALLA: Reporte top productos]

Reporte de Inventario

Este reporte permite valorizar el inventario y ver el stock actual de los productos, agrupados por categoría.

1. En el portal de reportes, haga clic en "Ver Reporte" en la tarjeta de "Reporte de Inventario"
2. Complete los filtros de búsqueda:
   - Categoría: Seleccione una categoría específica o "Todas las categorías" (opcional)

3. Haga clic en "Generar Reporte"
4. El reporte mostrará:
   - Lista de productos con su información: nombre, categoría, stock actual, precio unitario
   - Valorización de cada producto (precio × stock)
   - Resumen por categoría con totales de valorización
   - Valor total del inventario

5. Para exportar el reporte, haga clic en uno de los botones de exportación:
   - "Exportar Excel": Descarga el reporte en formato Excel (XLSX)
   - "Exportar PDF": Descarga el reporte en formato PDF para impresión
   - "Exportar CSV": Descarga el reporte en formato CSV

Nota: El reporte solo incluye productos activos. Los productos inactivos o en merma no aparecen en el reporte.

[CAPTURA DE PANTALLA: Reporte de inventario]

Exportación de Reportes

Todos los reportes pueden exportarse en tres formatos:

- Excel (XLSX): Ideal para análisis en hojas de cálculo como Microsoft Excel o Google Sheets. Permite realizar cálculos adicionales y crear gráficos.
- PDF: Ideal para impresión y archivo. Mantiene el formato visual del reporte y es fácil de compartir.
- CSV: Ideal para importación a otros sistemas o bases de datos. Formato de texto plano separado por comas.

Los archivos exportados se descargarán automáticamente en su navegador. Asegúrese de tener permisos de descarga habilitados.

---

Sistema de Alertas

El sistema de alertas permite monitorear productos que están próximos a vencer, tienen stock bajo, o facturas de proveedores que requieren atención. Las alertas se clasifican por colores según su urgencia.

Acceder al Sistema de Alertas

1. En el menú lateral, haga clic en "Alertas"
2. Se mostrará la página de alertas con:
   - Tarjetas de estadísticas: Alertas Rojas, Amarillas, Verdes y Alertas Activas
   - Lista completa de alertas con filtros
   - Opciones para crear alertas manualmente o generar alertas automáticas

[CAPTURA DE PANTALLA: Portal de alertas]

Tipos de Alertas

Las alertas se clasifican por colores según su urgencia:

- Alertas Rojas (Urgente): 0-13 días hasta vencer. Requieren atención inmediata
- Alertas Amarillas (Precaución): 14-29 días hasta vencer. Requieren atención pronto
- Alertas Verdes (OK): 30 o más días hasta vencer. Informativo, no urgente

Estados de Alertas

Cada alerta puede tener uno de los siguientes estados:

- Activa: Alerta pendiente de atención
- Resuelta: Se tomó acción sobre el producto o factura
- Ignorada: Se decidió no actuar sobre la alerta

Ver y Filtrar Alertas

1. En la página de alertas, encontrará la sección "Filtros de Búsqueda"
2. Puede filtrar por:
   - Tipo de Alerta: Roja, Amarilla, Verde, o Todas
   - Estado: Activa, Resuelta, Ignorada, o Todas
   - Fecha Desde: Fecha inicial del rango (opcional)
   - Fecha Hasta: Fecha final del rango (opcional)
   - Buscar Producto: Buscar por nombre de producto o factura (opcional)

3. Haga clic en "Filtrar" para aplicar los filtros
4. Haga clic en "Limpiar" para quitar todos los filtros

La tabla muestra:
- Tipo de alerta (icono con color)
- Mensaje descriptivo
- Producto o Factura asociada
- Días hasta vencer
- Fecha de generación
- Estado actual
- Acciones disponibles

[CAPTURA DE PANTALLA: Lista de alertas con filtros]

Generar Alertas Automáticas

El sistema puede generar alertas automáticamente para:
- Productos próximos a vencer (según días hasta caducidad)
- Productos con stock bajo
- Facturas de proveedores próximas a vencer

Importante: Las alertas NO se generan automáticamente sin intervención. Debe presionar el botón "Generar Alertas Automáticas" para que el sistema analice los productos y facturas y cree o actualice las alertas.

Para generar alertas:

1. En la página de alertas, haga clic en el botón "Generar Alertas Automáticas"
2. El sistema analizará todos los productos y facturas
3. Se crearán o actualizarán las alertas según corresponda
4. Verá un mensaje con las estadísticas de alertas generadas
5. La página se recargará automáticamente para mostrar las nuevas alertas

Nota: Se recomienda ejecutar esta función diariamente para mantener las alertas actualizadas.

Crear Alerta Manualmente

1. En la página de alertas, haga clic en "Nueva Alerta"
2. Complete el formulario:
   - Producto: Seleccione el producto para el cual crear la alerta (obligatorio)
   - Tipo de Alerta: Seleccione Roja, Amarilla o Verde (obligatorio)
   - Mensaje: Ingrese un mensaje descriptivo (obligatorio)
3. Haga clic en "Crear Alerta"

También puede crear una alerta desde el inventario:
1. En la lista de productos, seleccione el producto
2. Haga clic en "Crear Alertas" en las acciones masivas
3. O desde el detalle del producto, use el botón "Crear Alerta"

[CAPTURA DE PANTALLA: Formulario de crear alerta]

Gestionar Estados de Alertas

Puede cambiar el estado de una alerta de varias formas:

Opción 1: Desde el menú de acciones individual
1. En la lista de alertas, haga clic en el botón de acciones (icono de check) de la alerta
2. Seleccione el nuevo estado:
   - Marcar como Activa
   - Marcar como Resuelta
   - Marcar como Ignorada

Opción 2: Acciones masivas
1. Seleccione una o más alertas marcando los checkboxes
2. Se mostrará una barra de acciones masivas
3. Haga clic en el botón correspondiente:
   - "Marcar como Resuelta": Marca las alertas seleccionadas como resueltas
   - "Marcar como Ignorada": Marca las alertas seleccionadas como ignoradas
   - "Marcar como Activa": Reactiva las alertas seleccionadas
   - "Eliminar": Elimina las alertas seleccionadas

Editar o Eliminar Alertas

1. En la lista de alertas, use los botones de acciones:
   - "Editar" (icono de lápiz): Modifica la alerta
   - "Eliminar" (icono de papelera): Elimina la alerta permanentemente

[CAPTURA DE PANTALLA: Acciones en alertas]

---

Gestión de Merma

La gestión de merma permite registrar productos que no se pueden vender debido a vencimiento, deterioro, daño u otras razones. El sistema calcula automáticamente la pérdida económica asociada.

Ver Productos en Merma

1. En el menú lateral, haga clic en "Merma"
2. Se mostrará la página de gestión de merma con:
   - Resumen de merma: Total de productos, unidades y pérdida económica total
   - Barra de búsqueda: Para buscar productos por nombre
   - Tabla de productos en merma con toda la información

La tabla muestra:
- Producto: Nombre y descripción del producto
- Estado: Estado de merma (En Merma, Vencido, Deteriorado, Dañado, etc.)
- Motivo: Motivo detallado de la merma
- Fecha Merma: Fecha y hora en que se registró la merma
- Cantidad: Cantidad de unidades en merma
- Precio Unitario: Precio unitario del producto
- Pérdida Total: Pérdida económica calculada (cantidad × precio)
- Fecha Caducidad: Fecha de caducidad del producto (si aplica)
- Acciones: Botones para gestionar el registro

[CAPTURA DE PANTALLA: Lista de merma]

Enviar Productos a Merma

Para enviar productos a merma, debe hacerlo desde el Inventario. Puede mover un producto individual o varios productos a la vez:

Desde el Inventario

1. En la página de Inventario, seleccione uno o más productos marcando los checkboxes en la primera columna de la tabla
2. Haga clic en el botón "Mover a Merma" (icono de triángulo de advertencia) en la barra de acciones masivas
3. El sistema mostrará diferentes opciones según la cantidad de productos seleccionados:

   Si seleccionó UN solo producto:
   - Se abrirá un modal para configurar la merma con selección de lotes
   - Seleccione los lotes específicos que desea enviar a merma (si el producto tiene lotes)
   - Para cada lote, puede:
     * Seleccionar la cantidad total del lote (por defecto)
     * Ingresar una cantidad parcial específica
   - Ingrese el motivo detallado de la merma (obligatorio)
   - Haga clic en "Confirmar Merma"

   Si seleccionó VARIOS productos:
   - Se mostrará un diálogo para ingresar el motivo detallado de la merma (obligatorio)
   - Confirme la acción
   - Todos los productos seleccionados se moverán a merma con su stock completo

4. El sistema:
   - Reducirá el stock del producto según los lotes seleccionados (si fue un solo producto con lotes)
   - O reducirá todo el stock a 0 (si fueron varios productos o un producto sin lotes)
   - Creará un registro en el historial de merma
   - Calculará la pérdida económica
   - Actualizará el estado del producto

[CAPTURA DE PANTALLA: Modal de mover a merma desde inventario]

Nota: Solo puede mover a merma productos que tienen stock disponible. Si un producto ya está en merma, no aparecerá en las acciones masivas del inventario.

Eliminar Registro de Merma

Si necesita eliminar un registro de merma (por ejemplo, si fue un error):

1. En la página de Merma (menú lateral → "Merma"), localice el producto en la lista
2. En la columna "Acciones" de la tabla, haga clic en el botón "Eliminar Registro" del producto
3. Confirme la eliminación en el diálogo que aparece
4. El registro de merma se eliminará del historial

Nota Importante: 
- Solo puede eliminar registros de merma desde la lista de merma, no desde el detalle del producto
- Eliminar el registro de merma NO restaura automáticamente el stock del producto. El producto permanecerá con el stock actual
- Si necesita restaurar stock, debe hacerlo manualmente mediante un ajuste de stock o registrando un nuevo lote

Búsqueda y Filtrado

En la página de merma puede:
- Buscar productos por nombre usando la barra de búsqueda
- Ordenar la tabla haciendo clic en los encabezados de columna (Cantidad, Precio, Pérdida, Fecha)

[CAPTURA DE PANTALLA: Búsqueda en merma]

---

Preguntas Frecuentes

Gestión de Stock e Inventario

¿Cómo actualizo el stock de un producto?
Puede actualizar el stock de tres formas:
1. Ajuste manual: Use la opción "Ajustes de Stock" desde el botón en la lista de productos o desde el menú lateral
2. Recepción de factura: Al recibir una factura de proveedor, el stock se actualiza automáticamente
3. Registro de producción: Al registrar un lote de producción propia, el stock se actualiza automáticamente

¿Qué pasa si intento vender más de lo que hay en stock?
El sistema validará el stock disponible y mostrará un mensaje de error si no hay suficiente cantidad. No podrá completar la venta hasta que haya stock suficiente.

¿Cómo funciona el sistema de lotes?
El sistema utiliza lotes para rastrear productos con fechas de elaboración y caducidad. Las ventas utilizan el método FIFO (First In First Out), vendiendo primero los lotes más antiguos.

¿Puedo ajustar el stock de un producto que tiene lotes?
Sí, el sistema de ajustes de stock considera los lotes. Si es una entrada, se creará un nuevo lote. Si es una salida, se reducirá de los lotes existentes usando FIFO.

Ventas y Punto de Venta

¿Puedo realizar una venta sin seleccionar un cliente?
Sí, puede dejar el selector de cliente en "-- Seleccionar cliente --" y la venta se registrará como "Cliente Genérico". Esta opción es útil para ventas rápidas.

¿Puedo crear un cliente nuevo mientras estoy haciendo una venta?
Sí, en el punto de venta puede hacer clic en el botón "Nuevo Cliente" para crear un cliente rápidamente. Solo necesita ingresar el nombre (obligatorio), y opcionalmente RUT, teléfono, email y dirección. El nuevo cliente quedará automáticamente seleccionado para la venta.

¿Puedo cancelar una venta?
No, las ventas no se pueden cancelar una vez procesadas. Si necesita corregir una venta, debe crear un ajuste de stock para corregir las cantidades.

¿Cómo aplico descuentos en una venta?
Puede aplicar descuentos individuales por producto. En el carrito, haga clic en el botón "Descuento" del producto y ingrese el porcentaje de descuento deseado. El descuento se aplicará solo a ese producto específico.

Gestión de Usuarios

¿Quién puede gestionar usuarios?
Solo los usuarios con permisos de Superusuario (Administrador) pueden acceder al módulo de gestión de usuarios. Si necesita crear o modificar usuarios y no tiene acceso, contacte al administrador del sistema.

¿Qué pasa si olvido mi contraseña?
Puede recuperar su contraseña usando la opción "¿Olvidó su contraseña?" en la pantalla de login. El sistema le enviará un correo electrónico con un enlace para restablecer su contraseña. El enlace tiene una validez limitada.

¿Puedo cambiar mi propia contraseña?
Sí, un administrador puede editar su propio usuario y cambiar su contraseña. También puede usar la función de recuperación de contraseña si la olvida.

Control de Producción

¿Cómo registro la producción de pan u otros productos?
1. Vaya a "Producción" en el menú lateral
2. Haga clic en "Registrar Producción" o "Nueva Producción"
3. Seleccione el producto producido (solo productos activos)
4. Ingrese la cantidad (el sistema mostrará la unidad de medida automáticamente)
5. Complete las fechas de elaboración y caducidad
6. Haga clic en "Registrar Producción"
7. El stock se actualizará automáticamente

¿En qué unidad debo ingresar la cantidad al registrar producción?
El sistema muestra automáticamente la unidad de medida del producto seleccionado. Por ejemplo:
- Si el producto está en kilogramos, al ingresar "10" se guardará como "10 kg"
- Si el producto está en gramos, al ingresar "500" se guardará como "500 g"
- Si el producto está en litros, al ingresar "5" se guardará como "5 litros"
- Si el producto está en unidades, al ingresar "20" se guardará como "20 unidades"

Solo necesita ingresar el número; el sistema interpretará la unidad según la configuración del producto.

Facturas de Proveedores

¿Debo crear los productos antes de agregarlos a una factura?
Sí, los productos deben estar creados en el sistema antes de poder agregarlos a una factura. Si necesita crear un producto nuevo, debe hacerlo primero desde el módulo de Inventario (botón "Agregar Producto").

¿Puedo agregar productos a una factura después de recibirla?
No, una vez que una factura ha sido recibida, no se pueden agregar más productos. Si necesita agregar productos adicionales, debe quitar la recepción primero.

¿Qué pasa cuando recibo una factura?
Al recibir una factura, el sistema actualiza automáticamente el stock de todos los productos agregados a la factura y crea los lotes correspondientes para cada producto.

Sistema de Alertas

¿Las alertas se generan automáticamente?
No, las alertas no se generan automáticamente. Debe presionar el botón "Generar Alertas Automáticas" en la página de alertas para que el sistema analice los productos y facturas y cree o actualice las alertas. Se recomienda ejecutar esta función diariamente.

¿Qué significan los colores de las alertas?
- Roja (Urgente): 0-13 días hasta vencer. Requieren atención inmediata
- Amarilla (Precaución): 14-29 días hasta vencer. Requieren atención pronto
- Verde (OK): 30 o más días hasta vencer. Informativo, no urgente

¿Puedo crear alertas manualmente?
Sí, puede crear alertas manualmente desde la página de alertas haciendo clic en "Nueva Alerta", o desde el inventario usando las acciones masivas "Crear Alertas".

Gestión de Merma

¿Cómo muevo un producto a merma?
1. En la página de Inventario, seleccione uno o más productos marcando los checkboxes
2. Haga clic en el botón "Mover a Merma" en la barra de acciones masivas
3. Si seleccionó un solo producto, podrá seleccionar lotes específicos. Si seleccionó varios, se moverá todo el stock
4. Ingrese el motivo detallado de la merma (obligatorio)
5. Confirme la acción

¿Puedo eliminar un registro de merma?
Sí, desde la página de Merma puede hacer clic en "Eliminar Registro" del producto. Esto elimina el registro del historial, pero no restaura automáticamente el stock del producto.

Reportes

¿Cómo genero un reporte de ventas del mes?
1. Vaya a "Reportes" en el menú lateral
2. Haga clic en "Ver Reporte" en la tarjeta de "Reporte de Ventas"
3. Seleccione el primer día del mes como fecha desde
4. Seleccione el último día del mes como fecha hasta
5. Opcionalmente, seleccione filtros adicionales (cliente, canal)
6. Haga clic en "Generar Reporte"

¿Puedo exportar los reportes?
Sí, todos los reportes pueden exportarse en tres formatos:
- Excel (XLSX): Para análisis en hojas de cálculo
- PDF: Para impresión y archivo
- CSV: Para importación a otros sistemas

¿Qué diferencia hay entre el reporte Top Productos por Cantidad y por Monto Neto?
- Por Cantidad: Muestra los productos más vendidos por número de unidades
- Por Monto Neto: Muestra los productos con mayor facturación (monto total vendido)

---

Soporte

Si tiene dudas o problemas con el sistema, contacte al administrador:
- Email: [COMPLETAR]
- Teléfono: [COMPLETAR]

---

Última actualización: [COMPLETAR FECHA]

