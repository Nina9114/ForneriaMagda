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

Ver Detalle de un Producto

1. En la lista de productos, haga clic en elnombre del productoo en el botón "Ver Detalle"
2. Se mostrará información completa:
   - Datos generales del producto
   - Stock actual
   - Historial de lotes
   - Historial de movimientos
   - Historial de merma

[CAPTURA DE PANTALLA: Detalle de producto]

Filtrar Productos

En la lista de productos, puede usar los siguientes filtros:
-Bajo Stock:Muestra solo productos con stock bajo
-Próximos a Vencer:Muestra productos que vencen pronto
-Activos/Inactivos:Filtra por estado del producto
-Por Categoría:Filtra por categoría específica

[CAPTURA DE PANTALLA: Filtros de productos]

---

Punto de Venta (POS)

Realizar una Venta

#Paso 1: Agregar Productos al Carrito
1. En el menú lateral, haga clic en "Punto de Venta"
2. Busque el producto en la lista o use el buscador
3. Haga clic en el botón "Agregar" del producto
4. Ingrese la cantidad deseada
5. El producto se agregará al carrito automáticamente

[CAPTURA DE PANTALLA: POS con productos en carrito]

#Paso 2: Aplicar Descuentos (Opcional)
1. En el carrito, puede aplicar descuentos:
   -Descuento por línea:Haga clic en el producto y agregue un porcentaje
   -Descuento global:Ingrese un monto fijo en el campo "Descuento Global"

[CAPTURA DE PANTALLA: Aplicar descuentos]

#Paso 3: Seleccionar Método de Pago
1. En la sección de pago, seleccione el método:
   -Efectivo**
   -Tarjeta Débito**
   -Tarjeta Crédito**
   -Transferencia**
   -Cheque**

2. Si es efectivo, ingrese el monto pagado por el cliente
3. El sistema calculará automáticamente el vuelto

[CAPTURA DE PANTALLA: Selección de método de pago]

#Paso 4: Confirmar Venta
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
-Reactivación de Productos:Si un producto estaba en merma y se registra un nuevo lote, el producto se reactiva automáticamente

---

Gestión de Proveedores

Agregar un Proveedor

1. En el menú lateral, haga clic en "Proveedores"
2. Haga clic en "Nuevo Proveedor"
3. Complete el formulario:
   - Nombre: Nombre del proveedor
   - RUT: RUT del proveedor
   - Contacto: Nombre de contacto
   - Teléfono: Número de teléfono
   - Email: Correo electrónico
   - Dirección: Dirección del proveedor

4. Haga clic en "Guardar"

[CAPTURA DE PANTALLA: Formulario de proveedor]

Registrar Factura de Compra

1. En la lista de proveedores, haga clic en "Ver Facturas" del proveedor
2. Haga clic en "Nueva Factura"
3. Complete los datos de la factura:
   - Número de Factura
   - Fecha de Factura
   - Fecha de Vencimiento
   - Subtotal sin IVA
   - Descuento (si aplica)
   - Total IVA
   - Total con IVA
   - Estado de Pago

4. Agregue los productos de la factura:
   - Seleccione el producto
   - Ingrese cantidad
   - Ingrese precio unitario
   - Se calculará automáticamente el subtotal

5. Haga clic en "Guardar"

[CAPTURA DE PANTALLA: Formulario de factura]

Recibir Factura

1. En la lista de facturas, haga clic en "Recibir" de la factura pendiente
2. Ingrese la fecha de recepción
3. El sistema actualizará automáticamente el stock de los productos

[CAPTURA DE PANTALLA: Recepción de factura]

---

Reportes

Reporte de Ventas

1. En el menú lateral, haga clic en "Reportes" → "Ventas"
2. Seleccione el rango de fechas
3. Opcionalmente, seleccione filtros adicionales:
   - Canal de venta
   - Cliente
   - Método de pago

4. Haga clic en "Generar Reporte"
5. Para exportar, haga clic en:
   - "Exportar CSV"
   - "Exportar Excel"
   - "Exportar PDF"

[CAPTURA DE PANTALLA: Reporte de ventas]

Reporte Top Productos

1. En el menú lateral, haga clic en "Reportes" → "Top Productos"
2. Seleccione el tipo de ranking:
   -Por Cantidad:Productos más vendidos por cantidad
   -Por Monto Neto:Productos con mayor facturación

3. Seleccione el rango de fechas
4. Haga clic en "Generar Reporte"
5. Puede exportar el reporte en los formatos disponibles

[CAPTURA DE PANTALLA: Reporte top productos]

Reporte de Inventario

1. En el menú lateral, haga clic en "Reportes" → "Inventario"
2. Seleccione filtros:
   - Categoría
   - Estado (Activo/Inactivo)
   - Stock bajo

3. Haga clic en "Generar Reporte"
4. El reporte mostrará:
   - Lista de productos
   - Stock actual
   - Valorización por categoría

[CAPTURA DE PANTALLA: Reporte de inventario]

---

Sistema de Alertas

Ver Alertas

1. En el Dashboard, verá la sección "Alertas Pendientes"
2. Haga clic en "Ver Todas las Alertas" para ver el detalle completo
3. Las alertas se clasifican en:
   -Stock Bajo:Productos con stock por debajo del mínimo
   -Vencimiento Próximo:Productos que vencen en los próximos 7 días
   -Facturas por Vencer:Facturas de proveedores próximas a vencer

[CAPTURA DE PANTALLA: Lista de alertas]

Resolver Alertas

1. En la lista de alertas, haga clic en "Resolver" de la alerta correspondiente
2. Realice la acción necesaria (reponer stock, atender factura, etc.)
3. La alerta se marcará como resuelta automáticamente

[CAPTURA DE PANTALLA: Resolver alerta]

---

Gestión de Merma

Enviar Producto a Merma

1. En la lista de productos, haga clic en "Enviar a Merma"
2. Se abrirá un modal con los lotes disponibles del producto
3. Seleccione los lotes y cantidades que desea enviar a merma:
   - Puede seleccionar lotes específicos
   - Puede ingresar cantidades parciales de un lote
   - El valor por defecto es la cantidad total del lote

4. Ingrese una observación (opcional)
5. Haga clic en "Confirmar Merma"

[CAPTURA DE PANTALLA: Modal de selección de lotes para merma]

Ver Productos en Merma

1. En el menú lateral, haga clic en "Merma"
2. Se mostrará la lista de productos que están en merma
3. Puede ver:
   - Producto
   - Cantidad en merma
   - Fecha de merma
   - Lotes afectados

[CAPTURA DE PANTALLA: Lista de merma]

Eliminar Registro de Merma

1. En la lista de merma, haga clic en "Eliminar" del registro
2. Confirme la eliminación
3. Nota: El producto permanecerá en inventario con stock cero, listo para reabastecimiento

[CAPTURA DE PANTALLA: Eliminar merma]

---

Preguntas Frecuentes

¿Cómo actualizo el stock de un producto?
Puede actualizar el stock de tres formas:
1.Ajuste manual:Use la opción "Ajustar Stock" en la lista de productos
2.Recepción de factura:Al recibir una factura de proveedor, el stock se actualiza automáticamente
3.Registro de producción:Al registrar un lote de producción propia, el stock se actualiza automáticamente

¿Qué pasa si intento vender más de lo que hay en stock?
El sistema validará el stock disponible y mostrará un mensaje de error si no hay suficiente cantidad.

¿Cómo genero un reporte de ventas del mes?
1. Vaya a "Reportes" → "Ventas"
2. Seleccione el primer día del mes como fecha desde
3. Seleccione el último día del mes como fecha hasta
4. Haga clic en "Generar Reporte"

¿Puedo cancelar una venta?
No, las ventas no se pueden cancelar. Si necesita corregir una venta, debe crear un ajuste de stock.

¿Quién puede gestionar usuarios?
Solo los usuarios con permisos deSuperusuario (Administrador)pueden acceder al módulo de gestión de usuarios. Si necesita crear o modificar usuarios y no tiene acceso, contacte al administrador del sistema.

¿Qué pasa si olvido mi contraseña?
Puede recuperar su contraseña usando la opción "¿Olvidó su contraseña?" en la pantalla de login. El sistema le enviará un correo electrónico con un enlace para restablecer su contraseña.

¿Puedo cambiar mi propia contraseña?
Sí, un administrador puede editar su propio usuario y cambiar su contraseña. También puede usar la función de recuperación de contraseña si la olvida.

¿Cómo registro la producción de pan u otros productos?
1. Vaya a "Producción" en el menú lateral
2. Haga clic en "Registrar Producción"
3. Seleccione el producto producido
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

---

Soporte

Si tiene dudas o problemas con el sistema, contacte al administrador:
- Email: [COMPLETAR]
- Teléfono: [COMPLETAR]

---

Última actualización: [COMPLETAR FECHA]

