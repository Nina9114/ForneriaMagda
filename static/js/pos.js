// ================================================================
// =                                                              =
// =            JAVASCRIPT: PUNTO DE VENTA (POS)                  =
// =                                                              =
// ================================================================
//
// Este archivo maneja TODA la lógica del lado del cliente (navegador)
// para el sistema de Punto de Venta.
//
// FUNCIONALIDADES PRINCIPALES:
// 1. Gestión del carrito de compras (agregar, quitar, modificar cantidades)
// 2. Cálculo automático de totales (subtotal, IVA, descuentos, vuelto)
// 3. Validación de productos (stock, disponibilidad)
// 4. Procesamiento de ventas (envío a Django vía AJAX)
// 5. Gestión de clientes (crear clientes rápidos)
// 6. Búsqueda y filtrado de productos
// 7. Descuentos individuales por producto
// 8. Generación de comprobantes de venta
//
// ================================================================


// ================================================================
// =                    VARIABLES GLOBALES                        =
// ================================================================

// Array que almacena todos los productos agregados al carrito
// Estructura de cada item:
// {
//     producto_id: número,
//     nombre: texto,
//     precio: número (precio unitario),
//     stock: número (disponible),
//     cantidad: número (cuántos se están comprando),
//     descuento: número (% de descuento, 0-100)
// }
let carrito = [];

// Tipo de venta seleccionado: 'presencial' o 'delivery'
let tipoVenta = 'presencial';

// Token CSRF de Django (para seguridad en peticiones AJAX)
// Lo obtenemos del template HTML
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;


// ================================================================
// =              INICIALIZACIÓN AL CARGAR LA PÁGINA              =
// ================================================================
//
// Este código se ejecuta cuando el DOM está completamente cargado

document.addEventListener('DOMContentLoaded', function() {
    
    // --- Reloj en tiempo real ---
    // Actualiza la hora cada segundo
    actualizarHora();
    setInterval(actualizarHora, 1000);
    
    // --- Botones de Presencial/Delivery ---
    // Asignar eventos a los botones de tipo de venta
    document.getElementById('btn-presencial').addEventListener('click', function() {
        seleccionarTipoVenta('presencial');
    });
    
    document.getElementById('btn-delivery').addEventListener('click', function() {
        seleccionarTipoVenta('delivery');
    });
    
    // --- Buscar productos ---
    // Evento del campo de búsqueda
    const inputBuscar = document.getElementById('input-buscar-producto');
    if (inputBuscar) {
        inputBuscar.addEventListener('input', function() {
            filtrarProductos(this.value);
        });
    }
    
    // --- Botón de cancelar venta ---
    // Evento para el botón de cancelar venta completa
    document.getElementById('btn-cancelar-venta').addEventListener('click', cancelarVenta);
    
    // --- Botón de procesar venta ---
    // Evento para finalizar la venta
    document.getElementById('btn-procesar-venta').addEventListener('click', abrirModalConfirmacion);
    
    // --- Botón de cliente rápido ---
    // Evento para abrir el modal de agregar cliente
    document.getElementById('btn-agregar-cliente-rapido').addEventListener('click', function() {
        document.getElementById('form-cliente-rapido').reset();
    });
    
    // --- Evento: Agregar todos los productos al carrito ---
    // Delegación de eventos: esperamos clicks en cualquier botón "agregar al carrito"
    document.querySelectorAll('.btn-agregar-producto, .btn-agregar-carrito').forEach(boton => {
        boton.addEventListener('click', agregarProductoAlCarrito);
    });
    
    // --- Aplicar descuento en el modal ---
    document.getElementById('btn-aplicar-descuento').addEventListener('click', aplicarDescuentoIndividual);
    
    // --- Confirmar venta en el modal ---
    document.getElementById('btn-confirmar-venta-final').addEventListener('click', procesarVenta);
    
    // --- IVA siempre incluido (precio ya incluye IVA) ---
    // El toggle de IVA fue eliminado porque el precio ya incluye IVA
});


// ================================================================
// =                 FUNCIÓN: ACTUALIZAR HORA                     =
// ================================================================
//
// Muestra la hora actual en formato HH:MM:SS en el header

function actualizarHora() {
    const ahora = new Date();
    const horas = String(ahora.getHours()).padStart(2, '0');
    const minutos = String(ahora.getMinutes()).padStart(2, '0');
    const segundos = String(ahora.getSeconds()).padStart(2, '0');
    
    const horaActual = `${horas}:${minutos}:${segundos}`;
    
    const elementoHora = document.getElementById('hora-actual');
    if (elementoHora) {
        elementoHora.textContent = horaActual;
    }
}


// ================================================================
// =           FUNCIÓN: SELECCIONAR TIPO DE VENTA                 =
// ================================================================
//
// Cambia entre 'presencial' y 'delivery'
//
// @param {string} tipo - 'presencial' o 'delivery'

function seleccionarTipoVenta(tipo) {
    // Actualizar variable global
    tipoVenta = tipo;
    
    // Obtener los botones
    const btnPresencial = document.getElementById('btn-presencial');
    const btnDelivery = document.getElementById('btn-delivery');
    
    // Remover la clase activa de ambos botones
    btnPresencial.classList.remove('active');
    btnDelivery.classList.remove('active');
    
    // Agregar clase activa al botón seleccionado
    if (tipo === 'presencial') {
        btnPresencial.classList.add('active');
    } else {
        btnDelivery.classList.add('active');
    }
    
    console.log('Tipo de venta seleccionado:', tipo);
}


// ================================================================
// =         FUNCIÓN: AGREGAR AL CARRITO (WRAPPER)                =
// ================================================================
//
// Función wrapper que se llama desde el onclick del HTML
// Recibe el ID del producto directamente
//
// @param {number} productoId - ID del producto a agregar

function agregarAlCarrito(productoId) {
    // Buscar la tarjeta del producto
    const card = document.querySelector(`.producto-card[data-producto-id="${productoId}"]`);
    
    if (!card) {
        mostrarAlerta('error', 'Producto no encontrado');
        return;
    }
    
    // Extraer información del producto
    const unidadVenta = card.dataset.productoUnidadVenta || 'unidad';
    const stockDisponible = parseFloat(card.dataset.productoStock) || 0;
    const precioPorUnidad = parseFloat(card.dataset.productoPrecioOriginal) || parseFloat(card.dataset.productoPrecio) || 0;
    
    // Obtener nombres de unidades para mostrar
    const nombresUnidades = {
        'unidad': 'unidad(es)',
        'kg': 'kilo(s)',
        'g': 'gramo(s)',
        'l': 'litro(s)',
        'ml': 'mililitro(s)'
    };
    const nombreUnidad = nombresUnidades[unidadVenta] || unidadVenta;
    
    // Validar stock
    if (stockDisponible <= 0) {
        mostrarAlerta('error', 'Este producto no tiene stock disponible');
        return;
    }
    
    // Determinar cantidad inicial según unidad de venta
    let cantidadInicial = 1;
    let cantidadIngresada = null;
    
    // Si no es unidad, pedir cantidad al usuario
    if (unidadVenta !== 'unidad') {
        const mensaje = `Ingrese la cantidad en ${nombreUnidad}:\n\n` +
                       `Stock disponible: ${stockDisponible.toFixed(3)} ${nombreUnidad}\n` +
                       `Precio: $${precioPorUnidad.toFixed(0)} por ${nombreUnidad}\n\n` +
                       `Ejemplo: 1.5, 0.75, 2.25`;
        
        const input = prompt(mensaje);
        
        if (input === null) {
            // Usuario canceló
            return;
        }
        
        cantidadIngresada = parseFloat(input);
        
        // Validar entrada
        if (isNaN(cantidadIngresada) || cantidadIngresada <= 0) {
            mostrarAlerta('error', 'Debe ingresar una cantidad válida mayor a 0');
            return;
        }
        
        // Validar que no exceda stock
        if (cantidadIngresada > stockDisponible) {
            mostrarAlerta('error', `Solo hay ${stockDisponible.toFixed(3)} ${nombreUnidad} disponibles`);
            return;
        }
        
        cantidadInicial = cantidadIngresada;
    }
    
    // Crear objeto producto
    const producto = {
        producto_id: parseInt(productoId),
        nombre: card.dataset.productoNombre,
        precio: precioPorUnidad,
        stock: stockDisponible,
        unidad_venta: unidadVenta,
        cantidad: cantidadInicial,
        descuento: 0
    };
    
    // Verificar si ya está en el carrito
    const indiceExistente = carrito.findIndex(item => item.producto_id === producto.producto_id);
    
    if (indiceExistente >= 0) {
        // Ya está en el carrito
        const cantidadActual = carrito[indiceExistente].cantidad;
        const nuevaCantidadTotal = cantidadActual + cantidadInicial;
        
        if (nuevaCantidadTotal > producto.stock) {
            mostrarAlerta('warning', `Solo hay ${producto.stock.toFixed(3)} ${nombreUnidad} disponibles de ${producto.nombre}`);
            return;
        }
        
        carrito[indiceExistente].cantidad = nuevaCantidadTotal;
        mostrarAlerta('success', `Cantidad de ${producto.nombre} aumentada a ${nuevaCantidadTotal.toFixed(3)} ${nombreUnidad}`);
    } else {
        // Agregar nuevo producto
        carrito.push(producto);
        mostrarAlerta('success', `${producto.nombre} agregado al carrito (${cantidadInicial.toFixed(3)} ${nombreUnidad})`);
    }
    
    // Actualizar visualización
    renderizarCarrito();
    actualizarTotales();
}


// ================================================================
// =         FUNCIÓN: AGREGAR PRODUCTO AL CARRITO                 =
// ================================================================
//
// Esta es una de las funciones más importantes.
// Se ejecuta cuando el usuario hace click en "Agregar" en un producto.
//
// PROCESO:
// 1. Obtener información del producto clickeado
// 2. Validar que haya stock disponible
// 3. Si ya está en el carrito, aumentar la cantidad
// 4. Si no está, agregarlo al carrito
// 5. Actualizar la visualización del carrito
// 6. Recalcular totales

function agregarProductoAlCarrito(evento) {
    // "evento.currentTarget" es el botón que se clickeó
    const boton = evento.currentTarget;
    
    // Obtenemos el ID del producto desde el atributo "data-producto-id"
    const productoId = boton.dataset.productoId;
    
    // Buscamos la tarjeta completa del producto (el div padre)
    const card = document.querySelector(`.producto-card[data-producto-id="${productoId}"]`);
    
    // Extraer información del producto
    const unidadVenta = card.dataset.productoUnidadVenta || 'unidad';
    const stockDisponible = parseFloat(card.dataset.productoStock) || 0;
    const precioPorUnidad = parseFloat(card.dataset.productoPrecioOriginal) || parseFloat(card.dataset.productoPrecio) || 0;
    
    // --- Validación 1: Verificar que haya stock ---
    if (stockDisponible <= 0) {
        mostrarAlerta('error', 'Este producto no tiene stock disponible');
        return;  // Salir de la función, no agregar al carrito
    }
    
    // Nombres de unidades para mostrar
    const nombresUnidades = {
        'unidad': 'unidad(es)',
        'kg': 'kilo(s)',
        'g': 'gramo(s)',
        'l': 'litro(s)',
        'ml': 'mililitro(s)'
    };
    const nombreUnidad = nombresUnidades[unidadVenta] || unidadVenta;
    
    // Determinar cantidad inicial según unidad de venta
    let cantidadInicial = 1;
    
    // Si no es unidad, pedir cantidad al usuario
    if (unidadVenta !== 'unidad') {
        const mensaje = `Ingrese la cantidad en ${nombreUnidad}:\n\n` +
                       `Stock disponible: ${stockDisponible.toFixed(3)} ${nombreUnidad}\n` +
                       `Precio: $${precioPorUnidad.toFixed(0)} por ${nombreUnidad}\n\n` +
                       `Ejemplo: 1.5, 0.75, 2.25`;
        
        const input = prompt(mensaje);
        
        if (input === null) {
            // Usuario canceló
            return;
        }
        
        const cantidadIngresada = parseFloat(input);
        
        // Validar entrada
        if (isNaN(cantidadIngresada) || cantidadIngresada <= 0) {
            mostrarAlerta('error', 'Debe ingresar una cantidad válida mayor a 0');
            return;
        }
        
        // Validar que no exceda stock
        if (cantidadIngresada > stockDisponible) {
            mostrarAlerta('error', `Solo hay ${stockDisponible.toFixed(3)} ${nombreUnidad} disponibles`);
            return;
        }
        
        cantidadInicial = parseFloat(cantidadIngresada.toFixed(3));
    }
    
    // Extraemos toda la información del producto desde los data-attributes
    const producto = {
        producto_id: parseInt(productoId),
        nombre: card.dataset.productoNombre,
        precio: precioPorUnidad,
        stock: stockDisponible,
        unidad_venta: unidadVenta,
        cantidad: cantidadInicial,
        descuento: 0  // Sin descuento por defecto
    };
    
    // --- Verificar si el producto ya está en el carrito ---
    const indiceExistente = carrito.findIndex(item => item.producto_id === producto.producto_id);
    
    if (indiceExistente >= 0) {
        // El producto YA está en el carrito
        
        // Verificamos si podemos aumentar la cantidad
        const cantidadActual = carrito[indiceExistente].cantidad;
        
        if (cantidadActual >= producto.stock) {
            // No hay más stock disponible
            mostrarAlerta('warning', `Solo hay ${producto.stock} unidades disponibles de ${producto.nombre}`);
            return;
        }
        
        // Aumentamos la cantidad en 1
        carrito[indiceExistente].cantidad += 1;
        mostrarAlerta('success', `Cantidad de ${producto.nombre} aumentada a ${carrito[indiceExistente].cantidad}`);
        
    } else {
        // El producto NO está en el carrito, lo agregamos
        carrito.push(producto);
        mostrarAlerta('success', `${producto.nombre} agregado al carrito`);
    }
    
    // Actualizar la visualización del carrito en la pantalla
    renderizarCarrito();
    
    // Recalcular los totales
    actualizarTotales();
}


// ================================================================
// =         FUNCIÓN: RENDERIZAR (MOSTRAR) EL CARRITO             =
// ================================================================
//
// Esta función actualiza la visualización del carrito en el HTML.
// Toma el array "carrito" y lo convierte en elementos HTML visibles.

function renderizarCarrito() {
    // Obtener el contenedor donde se mostrarán los items
    const contenedor = document.getElementById('carrito-items');
    
    // Obtener el mensaje de "carrito vacío"
    const mensajeVacio = document.getElementById('carrito-vacio');
    
    // Obtener el contador de items en el header del carrito
    const contadorItems = document.getElementById('items-count');
    
    // --- Caso 1: Si el carrito está vacío ---
    if (carrito.length === 0) {
        // Mostrar mensaje de "carrito vacío"
        mensajeVacio.classList.remove('d-none');
        
        // Limpiar el contenedor
        contenedor.innerHTML = '';
        
        // Actualizar contador a 0
        contadorItems.textContent = '0';
        
        // Deshabilitar el botón de procesar venta
        document.getElementById('btn-procesar-venta').disabled = true;
        
        return;  // Salir de la función
    }
    
    // --- Caso 2: Hay productos en el carrito ---
    
    // Ocultar el mensaje de "carrito vacío"
    mensajeVacio.classList.add('d-none');
    
    // Limpiar el contenedor antes de agregar los nuevos items
    contenedor.innerHTML = '';
    
    // Contador de items totales (sumando las cantidades)
    let totalItems = 0;
    
    // Nombres de unidades para mostrar
    const nombresUnidades = {
        'unidad': 'unidad(es)',
        'kg': 'kilo(s)',
        'g': 'gramo(s)',
        'l': 'litro(s)',
        'ml': 'mililitro(s)'
    };
    
    // --- Recorrer cada producto del carrito ---
    carrito.forEach((item, indice) => {
        // Sumar la cantidad de este item al total
        totalItems += item.cantidad;
        
        // Obtener unidad de venta (por defecto 'unidad')
        const unidadVenta = item.unidad_venta || 'unidad';
        const nombreUnidad = nombresUnidades[unidadVenta] || unidadVenta;
        const esDecimal = unidadVenta !== 'unidad';
        
        // Calcular el precio con descuento
        const precioConDescuento = item.precio * (1 - item.descuento / 100);
        
        // Calcular el subtotal de este item (precio × cantidad)
        const subtotalItem = precioConDescuento * item.cantidad;
        
        // Formatear cantidad según unidad
        const cantidadFormateada = esDecimal ? parseFloat(item.cantidad).toFixed(3) : parseInt(item.cantidad);
        const stockFormateado = esDecimal ? parseFloat(item.stock).toFixed(3) : parseInt(item.stock);
        
        // Determinar step y min para el input
        const stepValue = esDecimal ? '0.001' : '1';
        const minValue = esDecimal ? '0.001' : '1';
        
        // Crear el HTML para este item del carrito
        const itemHTML = `
            <div class="carrito-item-card mb-2" data-item-index="${indice}">
                <div class="carrito-item-body">
                    <!-- Nombre del producto y botón quitar -->
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <strong class="text-truncate text-white" style="max-width: 180px;">
                            ${item.nombre}
                        </strong>
                        <!-- Botón para quitar del carrito -->
                        <button class="btn btn-sm btn-danger btn-quitar-item" 
                                data-index="${indice}"
                                title="Quitar del carrito">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                    
                    <!-- Precio unitario con descuento si aplica -->
                    <div class="mb-2">
                        ${item.descuento > 0 ? `
                            <small class="text-muted text-decoration-line-through">
                                $${formatearPrecio(item.precio)} / ${nombreUnidad}
                            </small>
                            <span class="badge bg-success ms-1">${item.descuento}% OFF</span>
                            <div class="text-warning fw-bold">
                                $${formatearPrecio(precioConDescuento)} / ${nombreUnidad}
                            </div>
                        ` : `
                            <small class="text-muted">
                                $${formatearPrecio(item.precio)} / ${nombreUnidad}
                            </small>
                        `}
                    </div>
                    
                    <!-- Controles de cantidad y subtotal -->
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="btn-group btn-group-sm" role="group">
                            <!-- Botón para disminuir cantidad -->
                            <button class="btn btn-outline-warning btn-disminuir" 
                                    data-index="${indice}"
                                    data-step="${stepValue}"
                                    type="button"
                                    title="Disminuir cantidad">
                                <i class="bi bi-dash"></i>
                            </button>
                            
                            <!-- Input de cantidad -->
                            <input type="number" 
                                   class="form-control form-control-sm text-center input-cantidad" 
                                   data-index="${indice}"
                                   data-unidad="${unidadVenta}"
                                   value="${cantidadFormateada}" 
                                   min="${minValue}" 
                                   max="${item.stock}"
                                   step="${stepValue}"
                                   style="width: ${esDecimal ? '80px' : '60px'};">
                            
                            <!-- Botón para aumentar cantidad -->
                            <button class="btn btn-outline-warning btn-aumentar" 
                                    data-index="${indice}"
                                    data-step="${stepValue}"
                                    type="button"
                                    title="Aumentar cantidad">
                                <i class="bi bi-plus"></i>
                            </button>
                        </div>
                        
                        <!-- Subtotal del item -->
                        <div class="text-end">
                            <div class="fw-bold text-warning" style="font-size: 1.1rem;">
                                $${formatearPrecio(subtotalItem)}
                            </div>
                            <small class="text-muted">${cantidadFormateada} ${nombreUnidad}</small>
                        </div>
                    </div>
                    
                    <!-- Indicadores adicionales -->
                    <div class="mt-2 d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="bi bi-box"></i> Stock: ${stockFormateado} ${nombreUnidad}
                        </small>
                        <!-- Botón para aplicar descuento individual -->
                        <button class="btn btn-sm btn-outline-warning btn-descuento-item"
                                data-index="${indice}"
                                title="Aplicar descuento">
                            <i class="bi bi-percent"></i> Descuento
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Agregar este item al contenedor
        contenedor.insertAdjacentHTML('beforeend', itemHTML);
    });
    
    // Actualizar el contador de items
    contadorItems.textContent = totalItems;
    
    // Habilitar el botón de procesar venta
    document.getElementById('btn-procesar-venta').disabled = false;
    
    // --- Asignar eventos a los nuevos botones creados ---
    asignarEventosCarrito();
}


// ================================================================
// =       FUNCIÓN: ASIGNAR EVENTOS A BOTONES DEL CARRITO         =
// ================================================================
//
// Después de renderizar el carrito, necesitamos asignar eventos
// a todos los botones nuevos (quitar, aumentar, disminuir, descuento)

function asignarEventosCarrito() {
    
    // --- Botones para quitar items ---
    document.querySelectorAll('.btn-quitar-item').forEach(boton => {
        boton.addEventListener('click', function() {
            const indice = parseInt(this.dataset.index);
            quitarDelCarrito(indice);
        });
    });
    
    // --- Botones para disminuir cantidad ---
    document.querySelectorAll('.btn-disminuir').forEach(boton => {
        boton.addEventListener('click', function() {
            const indice = parseInt(this.dataset.index);
            cambiarCantidad(indice, -1);  // -1 significa disminuir
        });
    });
    
    // --- Botones para aumentar cantidad ---
    document.querySelectorAll('.btn-aumentar').forEach(boton => {
        boton.addEventListener('click', function() {
            const indice = parseInt(this.dataset.index);
            cambiarCantidad(indice, 1);  // +1 significa aumentar
        });
    });
    
    // --- Inputs de cantidad (cuando el usuario escribe directamente) ---
    document.querySelectorAll('.input-cantidad').forEach(input => {
        input.addEventListener('change', function() {
            const indice = parseInt(this.dataset.index);
            const unidad = this.dataset.unidad || 'unidad';
            // Usar parseFloat para permitir decimales
            const nuevaCantidad = unidad !== 'unidad' ? parseFloat(this.value) : parseInt(this.value);
            establecerCantidad(indice, nuevaCantidad);
        });
    });
    
    // --- Botones para aplicar descuento individual ---
    document.querySelectorAll('.btn-descuento-item').forEach(boton => {
        boton.addEventListener('click', function() {
            const indice = parseInt(this.dataset.index);
            abrirModalDescuento(indice);
        });
    });
}


// ================================================================
// =         FUNCIÓN: CAMBIAR CANTIDAD DE UN ITEM                 =
// ================================================================
//
// Aumenta o disminuye la cantidad de un producto en el carrito
//
// @param {number} indice - Posición del producto en el array carrito
// @param {number} cambio - Cantidad a sumar (+1) o restar (-1)

function cambiarCantidad(indice, cambio) {
    // Obtener el item del carrito
    const item = carrito[indice];
    
    // Determinar el step según unidad de venta
    const unidadVenta = item.unidad_venta || 'unidad';
    const step = unidadVenta !== 'unidad' ? 0.1 : 1;  // Para decimales, usar 0.1; para unidades, usar 1
    
    // Calcular la nueva cantidad
    const nuevaCantidad = parseFloat((item.cantidad + (cambio * step)).toFixed(3));
    
    // Validar que la cantidad esté en el rango válido
    const minValue = unidadVenta !== 'unidad' ? 0.001 : 1;
    if (nuevaCantidad < minValue) {
        // Si intentan poner menos del mínimo, preguntar si desea quitar
        if (confirm(`¿Desea quitar "${item.nombre}" del carrito?`)) {
            quitarDelCarrito(indice);
        }
        return;
    }
    
    if (nuevaCantidad > item.stock) {
        // No hay suficiente stock
        const nombresUnidades = {
            'unidad': 'unidad(es)',
            'kg': 'kilo(s)',
            'g': 'gramo(s)',
            'l': 'litro(s)',
            'ml': 'mililitro(s)'
        };
        const nombreUnidad = nombresUnidades[unidadVenta] || unidadVenta;
        const stockFormateado = unidadVenta !== 'unidad' ? parseFloat(item.stock).toFixed(3) : parseInt(item.stock);
        mostrarAlerta('warning', `Solo hay ${stockFormateado} ${nombreUnidad} disponibles de ${item.nombre}`);
        return;
    }
    
    // Actualizar la cantidad (redondear a 3 decimales si es decimal)
    item.cantidad = unidadVenta !== 'unidad' ? parseFloat(nuevaCantidad.toFixed(3)) : parseInt(nuevaCantidad);
    
    // Re-renderizar el carrito
    renderizarCarrito();
    
    // Recalcular totales
    actualizarTotales();
}


// ================================================================
// =      FUNCIÓN: ESTABLECER CANTIDAD EXACTA DE UN ITEM          =
// ================================================================
//
// Cuando el usuario escribe directamente en el input de cantidad
//
// @param {number} indice - Posición del producto en el array carrito
// @param {number} cantidad - Nueva cantidad deseada

function establecerCantidad(indice, cantidad) {
    // Obtener el item del carrito
    const item = carrito[indice];
    
    // Validar que la cantidad sea un número válido
    if (isNaN(cantidad) || cantidad < 1) {
        // Restaurar la cantidad anterior
        renderizarCarrito();
        mostrarAlerta('error', 'La cantidad debe ser al menos 1');
        return;
    }
    
    if (cantidad > item.stock) {
        // Restaurar la cantidad anterior
        renderizarCarrito();
        mostrarAlerta('warning', `Solo hay ${item.stock} unidades disponibles de ${item.nombre}`);
        return;
    }
    
    // Actualizar la cantidad
    item.cantidad = cantidad;
    
    // Re-renderizar el carrito
    renderizarCarrito();
    
    // Recalcular totales
    actualizarTotales();
}


// ================================================================
// =           FUNCIÓN: QUITAR PRODUCTO DEL CARRITO               =
// ================================================================
//
// Elimina un producto del carrito
//
// @param {number} indice - Posición del producto en el array carrito

function quitarDelCarrito(indice) {
    // Obtener nombre del producto para el mensaje
    const nombreProducto = carrito[indice].nombre;
    
    // Eliminar el producto del array
    carrito.splice(indice, 1);
    
    // Re-renderizar el carrito
    renderizarCarrito();
    
    // Recalcular totales
    actualizarTotales();
    
    // Mostrar mensaje
    mostrarAlerta('info', `${nombreProducto} quitado del carrito`);
}


// ================================================================
// =       FUNCIÓN: ABRIR MODAL DE DESCUENTO INDIVIDUAL           =
// ================================================================
//
// Abre el modal para aplicar un descuento a un producto específico
//
// @param {number} indice - Posición del producto en el array carrito

function abrirModalDescuento(indice) {
    const item = carrito[indice];
    
    // Guardar el índice actual para usarlo después
    document.getElementById('modal-descuento-item').dataset.itemIndex = indice;
    
    // Mostrar nombre del producto en el modal
    document.getElementById('nombre-producto-descuento').textContent = item.nombre;
    
    // Establecer el descuento actual en el input
    document.getElementById('input-descuento-individual').value = item.descuento;
    
    // Abrir el modal
    const modal = new bootstrap.Modal(document.getElementById('modal-descuento-item'));
    modal.show();
}


// ================================================================
// =       FUNCIÓN: APLICAR DESCUENTO A PRODUCTO INDIVIDUAL       =
// ================================================================
//
// Aplica el descuento ingresado por el usuario a un producto específico

function aplicarDescuentoIndividual() {
    // Obtener el índice del producto
    const indice = parseInt(document.getElementById('modal-descuento-item').dataset.itemIndex);
    
    // Obtener el descuento ingresado
    const descuento = parseFloat(document.getElementById('input-descuento-individual').value);
    
    // Validar descuento
    if (isNaN(descuento) || descuento < 0 || descuento > 100) {
        mostrarAlerta('error', 'El descuento debe estar entre 0 y 100');
        return;
    }
    
    // Aplicar el descuento al producto
    carrito[indice].descuento = descuento;
    
    // Cerrar el modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('modal-descuento-item'));
    modal.hide();
    
    // Re-renderizar carrito y actualizar totales
    renderizarCarrito();
    actualizarTotales();
    
    mostrarAlerta('success', `Descuento del ${descuento}% aplicado`);
}


// ================================================================
// =              FUNCIÓN: ACTUALIZAR TOTALES                     =
// ================================================================
//
// Calcula y muestra los totales del carrito:
// - Subtotal (suma de todos los items CON descuentos individuales)
// - IVA (19%)
// - Total final
// - Vuelto (si el cliente pagó más)

function actualizarTotales() {
    // --- IMPORTANTE: El precio del producto YA INCLUYE IVA (precio final al consumidor) ---
    // Por lo tanto, debemos calcular:
    // 1. Total con IVA incluido (precio mostrado × cantidad)
    // 2. Subtotal sin IVA (total / 1.19)
    // 3. IVA (subtotal sin IVA × 0.19)
    // 4. Total final = precio original (con IVA incluido)
    
    // --- Calcular Total con IVA Incluido ---
    // Suma del precio × cantidad de cada producto (con sus descuentos individuales)
    let totalConIvaIncluido = 0;
    
    carrito.forEach(item => {
        // Aplicar descuento individual al precio
        const precioConDescuento = item.precio * (1 - item.descuento / 100);
        totalConIvaIncluido += precioConDescuento * item.cantidad;
    });
    
    // --- El precio ya incluye IVA, entonces:
    // Subtotal sin IVA = Total con IVA / 1.19
    const subtotalSinIva = totalConIvaIncluido / 1.19;
    // IVA = Subtotal sin IVA × 0.19
    const iva = subtotalSinIva * 0.19;
    // Total final = precio original (con IVA incluido)
    const total = totalConIvaIncluido;
    
    // --- Actualizar en el HTML ---
    document.getElementById('subtotal').textContent = formatearPrecio(subtotalSinIva);
    document.getElementById('iva').textContent = formatearPrecio(iva);
    document.getElementById('total').textContent = formatearPrecio(total);
    
    // --- Calcular Vuelto ---
    // El vuelto solo se calcula si el usuario ingresó el monto pagado
    const montoPagadoInput = document.getElementById('monto-pagado-input');
    if (montoPagadoInput) {
        const montoPagado = parseFloat(montoPagadoInput.value) || 0;
        // Total con IVA incluido (precio original)
        const totalFinal = totalConIvaIncluido;
        const vuelto = montoPagado - totalFinal;
        
        const vueltoElemento = document.getElementById('vuelto');
        if (vueltoElemento) {
            vueltoElemento.textContent = vuelto >= 0 ? formatearPrecio(vuelto) : '0';
            
            // Cambiar color si es negativo (pago insuficiente)
            if (vuelto < 0) {
                vueltoElemento.classList.add('text-danger');
            } else {
                vueltoElemento.classList.remove('text-danger');
            }
        }
    }
}


// ================================================================
// =              FUNCIÓN: FORMATEAR PRECIO                       =
// ================================================================
//
// Convierte un número a formato de precio sin decimales
// Ejemplo: 1500 → "1500"
//
// @param {number} valor - El número a formatear
// @returns {string} - El precio formateado

function formatearPrecio(valor) {
    return Math.round(valor).toLocaleString('es-CL');
}


// ================================================================
// =              FUNCIÓN: CANCELAR VENTA COMPLETA                =
// ================================================================
//
// Vacía el carrito completamente y restaura todo al estado inicial

function cancelarVenta() {
    // Verificar si hay productos en el carrito
    if (carrito.length === 0) {
        mostrarAlerta('info', 'El carrito ya está vacío');
        return;
    }
    
    // Confirmar con el usuario
    if (!confirm('¿Está seguro de cancelar la venta? Se perderán todos los productos del carrito.')) {
        return;
    }
    
    // Vaciar el carrito
    carrito = [];
    
    // Resetear tipo de venta a presencial
    seleccionarTipoVenta('presencial');
    
    // Limpiar campo de cliente
    document.getElementById('select-cliente').value = '';
    
    // Re-renderizar el carrito (mostrará mensaje de vacío)
    renderizarCarrito();
    
    // Actualizar totales a 0
    actualizarTotales();
    
    // Mensaje de confirmación
    mostrarAlerta('info', 'Venta cancelada. El carrito ha sido vaciado.');
}


// ================================================================
// =         FUNCIÓN: ABRIR MODAL DE CONFIRMACIÓN                 =
// ================================================================
//
// Abre el modal de confirmación final antes de procesar la venta

function abrirModalConfirmacion() {
    // Validar que el carrito no esté vacío
    if (carrito.length === 0) {
        mostrarAlerta('error', 'El carrito está vacío');
        return;
    }
    
    // Validar que se haya seleccionado un cliente
    const clienteId = document.getElementById('select-cliente').value;
    if (!clienteId) {
        mostrarAlerta('error', 'Debe seleccionar un cliente');
        return;
    }
    
    // Calcular totales actuales (precio ya incluye IVA)
    let totalConIvaIncluido = 0;
    carrito.forEach(item => {
        const precioConDescuento = item.precio * (1 - item.descuento / 100);
        totalConIvaIncluido += precioConDescuento * item.cantidad;
    });
    
    // El precio ya incluye IVA, entonces:
    // Subtotal sin IVA = Total con IVA / 1.19
    const subtotalSinIva = totalConIvaIncluido / 1.19;
    // IVA = Subtotal sin IVA × 0.19
    const iva = subtotalSinIva * 0.19;
    // Total final = precio original (con IVA incluido)
    const total = totalConIvaIncluido;
    
    // Mostrar totales en el modal
    document.getElementById('modal-subtotal').textContent = formatearPrecio(subtotalSinIva);
    document.getElementById('modal-iva').textContent = formatearPrecio(iva);
    document.getElementById('modal-total').textContent = formatearPrecio(total);
    
    // Limpiar el input de monto pagado
    document.getElementById('monto-pagado-input').value = '';
    document.getElementById('modal-vuelto').textContent = '0';
    
    // Agregar evento para calcular vuelto en tiempo real (solo para efectivo)
    const montoPagadoInput = document.getElementById('monto-pagado-input');
    montoPagadoInput.removeEventListener('input', calcularVueltoModal); // Evitar duplicados
    montoPagadoInput.addEventListener('input', function() {
        calcularVueltoModal(total);
    });
    
    // Manejar cambio de medio de pago
    const medioPagoSelect = document.getElementById('medio-pago-select');
    const montoPagadoContainer = document.getElementById('monto-pagado-container');
    const vueltoContainer = document.getElementById('vuelto-container');
    
    function actualizarCamposPago() {
        const medioPago = medioPagoSelect.value;
        if (medioPago === 'efectivo') {
            montoPagadoContainer.style.display = 'block';
            vueltoContainer.style.display = 'block';
            montoPagadoInput.required = true;
            // Establecer monto pagado al total por defecto
            montoPagadoInput.value = Math.round(total);
            calcularVueltoModal(total);
        } else {
            montoPagadoContainer.style.display = 'none';
            vueltoContainer.style.display = 'none';
            montoPagadoInput.required = false;
            montoPagadoInput.value = Math.round(total);
            document.getElementById('modal-vuelto').textContent = '0';
        }
    }
    
    medioPagoSelect.addEventListener('change', actualizarCamposPago);
    actualizarCamposPago(); // Inicializar
    
    // Abrir el modal
    const modal = new bootstrap.Modal(document.getElementById('modal-confirmar-venta'));
    modal.show();
}


// ================================================================
// =         FUNCIÓN: CALCULAR VUELTO EN EL MODAL                 =
// ================================================================
//
// Calcula el vuelto en tiempo real mientras el usuario escribe
//
// @param {number} total - El total de la venta

function calcularVueltoModal(total) {
    const montoPagado = parseFloat(document.getElementById('monto-pagado-input').value) || 0;
    const vuelto = montoPagado - total;
    
    const vueltoElemento = document.getElementById('modal-vuelto');
    vueltoElemento.textContent = vuelto >= 0 ? formatearPrecio(vuelto) : '0';
    
    // Cambiar color si es negativo
    if (vuelto < 0) {
        vueltoElemento.classList.add('text-danger');
        vueltoElemento.classList.remove('text-success');
    } else {
        vueltoElemento.classList.add('text-success');
        vueltoElemento.classList.remove('text-danger');
    }
}


// ================================================================
// =              FUNCIÓN: PROCESAR VENTA FINAL                   =
// ================================================================
//
// Envía la venta al servidor (Django) vía AJAX

function procesarVenta() {
    // --- Validaciones finales ---
    
    const clienteId = document.getElementById('select-cliente').value;
    if (!clienteId) {
        mostrarAlerta('error', 'Debe seleccionar un cliente');
        return;
    }
    
    if (carrito.length === 0) {
        mostrarAlerta('error', 'El carrito está vacío');
        return;
    }
    
    // Obtener medio de pago
    const medioPago = document.getElementById('medio-pago-select').value;
    
    // Calcular total (precio ya incluye IVA)
    let totalConIvaIncluido = 0;
    carrito.forEach(item => {
        const precioConDescuento = item.precio * (1 - item.descuento / 100);
        totalConIvaIncluido += precioConDescuento * item.cantidad;
    });
    
    // Total = precio original (con IVA incluido)
    const total = totalConIvaIncluido;
    
    // Validar monto pagado según el medio de pago
    let montoPagado;
    if (medioPago === 'efectivo') {
        montoPagado = parseFloat(document.getElementById('monto-pagado-input').value);
        if (isNaN(montoPagado) || montoPagado <= 0) {
            mostrarAlerta('error', 'Debe ingresar el monto pagado por el cliente');
            return;
        }
        // Validar que el pago sea suficiente
        if (montoPagado < total) {
            mostrarAlerta('error', 'El monto pagado es insuficiente');
            return;
        }
    } else {
        // Para otros métodos de pago, el monto pagado es igual al total
        montoPagado = total;
    }
    
    // Deshabilitar el botón para evitar doble click
    const btnConfirmar = document.getElementById('btn-confirmar-venta-final');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
    
    // --- Preparar datos para enviar ---
    // Preparar el carrito en el formato que espera Django
    const carritoParaEnviar = carrito.map(item => ({
        producto_id: item.producto_id,
        cantidad: item.cantidad,
        precio_unitario: item.precio,
        descuento: item.descuento
    }));
    
    const datosVenta = {
        cliente_id: clienteId,
        canal_venta: tipoVenta,  // 'presencial' o 'delivery'
        carrito: carritoParaEnviar,
        medio_pago: medioPago,
        monto_pagado: montoPagado,
        descuento: 0  // Descuento global (no lo usamos, solo descuentos individuales)
    };
    
    // --- Enviar petición AJAX a Django ---
    fetch('/api/procesar-venta/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(datosVenta)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modal-confirmar-venta'));
            modal.hide();
            
            // Obtener información de la venta procesada
            const ventaInfo = data.venta || {};
            const ventaId = ventaInfo.id || data.id;
            const folio = ventaInfo.folio || 'N/A';
            
            // Generar comprobante
            generarComprobante(ventaId, folio, datosVenta);
            
            // Limpiar carrito
            carrito = [];
            renderizarCarrito();
            actualizarTotales();
            
            // Mostrar mensaje de éxito
            mostrarAlerta('success', `✓ Venta procesada exitosamente. Folio: ${folio}`);
            
            // Resetear formulario
            document.getElementById('select-cliente').value = '';
            seleccionarTipoVenta('presencial');
        } else {
            // Mostrar error
            mostrarAlerta('error', data.mensaje || 'Error al procesar la venta');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('error', 'Error de conexión con el servidor');
    })
    .finally(() => {
        // Re-habilitar el botón
        btnConfirmar.disabled = false;
        btnConfirmar.textContent = 'Confirmar Venta';
    });
}


// ================================================================
// =              FUNCIÓN: GENERAR COMPROBANTE                    =
// ================================================================
//
// Genera un comprobante de venta en formato de texto y lo descarga
//
// @param {number} ventaId - ID de la venta registrada
// @param {string} folio - Folio de la venta
// @param {object} datosVenta - Objeto con toda la información de la venta

function generarComprobante(ventaId, folio, datosVenta) {
    // Obtener fecha y hora actual
    const ahora = new Date();
    const fecha = ahora.toLocaleDateString('es-CL');
    const hora = ahora.toLocaleTimeString('es-CL');
    
    // Obtener nombre del cliente
    const selectCliente = document.getElementById('select-cliente');
    const nombreCliente = selectCliente.options[selectCliente.selectedIndex].text;
    
    // Calcular totales (precio ya incluye IVA)
    let totalConIvaIncluido = 0;
    carrito.forEach(item => {
        const precioConDescuento = item.precio * (1 - item.descuento / 100);
        totalConIvaIncluido += precioConDescuento * item.cantidad;
    });
    
    // El precio ya incluye IVA, entonces:
    // Subtotal sin IVA = Total con IVA / 1.19
    const subtotalSinIva = totalConIvaIncluido / 1.19;
    // IVA = Subtotal sin IVA × 0.19
    const iva = subtotalSinIva * 0.19;
    // Total final = precio original (con IVA incluido)
    const total = totalConIvaIncluido;
    
    // Construir el texto del comprobante
    let comprobante = `
═══════════════════════════════════════════════
         LA FORNERÍA - COMPROBANTE DE VENTA
═══════════════════════════════════════════════

FOLIO: ${folio}
FECHA: ${fecha}
HORA: ${hora}
TIPO: ${tipoVenta.toUpperCase()}

───────────────────────────────────────────────
CLIENTE: ${nombreCliente}
───────────────────────────────────────────────

PRODUCTOS:
`;

    // Agregar cada producto del carrito
    carrito.forEach(item => {
        const precioConDescuento = item.precio * (1 - item.descuento / 100);
        const subtotalItem = precioConDescuento * item.cantidad;
        
        comprobante += `
  ${item.nombre}
  Cantidad: ${item.cantidad} x $${formatearPrecio(item.precio)}`;
        
        if (item.descuento > 0) {
            comprobante += ` (-${item.descuento}%)`;
        }
        
        comprobante += `
  Subtotal: $${formatearPrecio(subtotalItem)}
`;
    });
    
    // Obtener medio de pago
    const medioPago = datosVenta.medio_pago || 'efectivo';
    const medioPagoDisplayMap = {
        'efectivo': 'Efectivo',
        'tarjeta_debito': 'Tarjeta Débito',
        'tarjeta_credito': 'Tarjeta Crédito',
        'transferencia': 'Transferencia',
        'cheque': 'Cheque',
        'otro': 'Otro'
    };
    const medioPagoDisplay = medioPagoDisplayMap[medioPago] || 'Efectivo';
    
    // Calcular vuelto (solo para efectivo)
    const vuelto = medioPago === 'efectivo' ? (datosVenta.monto_pagado - total) : 0;
    
    // Agregar totales
    comprobante += `
───────────────────────────────────────────────
  SubTotal (sin IVA):        $${formatearPrecio(Math.round(subtotalSinIva))}
  IVA (19%):                 $${formatearPrecio(Math.round(iva))}
───────────────────────────────────────────────
  TOTAL (con IVA):           $${formatearPrecio(Math.round(total))}
───────────────────────────────────────────────
  Medio de pago:             ${medioPagoDisplay}
  Pago recibido:             $${formatearPrecio(datosVenta.monto_pagado)}
`;
    
    // Agregar vuelto solo si es efectivo
    if (medioPago === 'efectivo') {
        comprobante += `  Vuelto:                    $${formatearPrecio(vuelto)}
`;
    }
    
    comprobante += `
═══════════════════════════════════════════════

          ¡Gracias por su compra!
      Visite nuestras redes sociales
             @LaForneria

═══════════════════════════════════════════════
`;
    
    // Crear un archivo de texto y descargarlo
    const blob = new Blob([comprobante], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const fechaArchivo = fecha.replace(/\//g, '-');
    a.download = `Forneria_${folio}_${fechaArchivo}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log('📄 Comprobante generado y descargado:', folio);
}


// ================================================================
// =              FUNCIÓN: FILTRAR PRODUCTOS                      =
// ================================================================
//
// Filtra los productos mostrados según el texto de búsqueda
//
// @param {string} textoBusqueda - Texto ingresado por el usuario

function filtrarProductos(textoBusqueda) {
    // Convertir a minúsculas para búsqueda case-insensitive
    const busqueda = textoBusqueda.toLowerCase();
    
    // Obtener todas las tarjetas de productos
    const productos = document.querySelectorAll('.producto-card');
    
    productos.forEach(card => {
        // Obtener el nombre del producto
        const nombreProducto = card.dataset.productoNombre.toLowerCase();
        
        // Mostrar u ocultar según coincidencia
        if (nombreProducto.includes(busqueda)) {
            card.parentElement.style.display = '';  // Mostrar
        } else {
            card.parentElement.style.display = 'none';  // Ocultar
        }
    });
}


// ================================================================
// =              FUNCIÓN: MOSTRAR ALERTA (TOAST)                 =
// ================================================================
//
// Muestra un mensaje toast en la esquina de la pantalla
// Solo muestra un toast a la vez para evitar saturar la pantalla
//
// @param {string} tipo - 'success', 'error', 'warning', 'info'
// @param {string} mensaje - Texto a mostrar

function mostrarAlerta(tipo, mensaje) {
    // Mapeo de tipos a clases de Bootstrap
    const clases = {
        'success': 'bg-success text-white',
        'error': 'bg-danger text-white',
        'warning': 'bg-warning text-dark',
        'info': 'bg-info text-white'
    };
    
    // Mapeo de tipos a iconos
    const iconos = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-x-circle-fill',
        'warning': 'bi-exclamation-triangle-fill',
        'info': 'bi-info-circle-fill'
    };
    
    // Buscar o crear el contenedor de toasts
    let contenedorToasts = document.getElementById('toast-container');
    if (!contenedorToasts) {
        contenedorToasts = document.createElement('div');
        contenedorToasts.id = 'toast-container';
        contenedorToasts.className = 'toast-container position-fixed top-0 end-0 p-3';
        contenedorToasts.style.zIndex = '9999';
        document.body.appendChild(contenedorToasts);
    }
    
    // IMPORTANTE: Limpiar todos los toasts anteriores para evitar saturación
    contenedorToasts.innerHTML = '';
    
    // Crear el elemento toast
    const toastHTML = `
        <div class="toast align-items-center ${clases[tipo]} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${iconos[tipo]} me-2"></i>
                    ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Agregar el toast al contenedor
    contenedorToasts.insertAdjacentHTML('beforeend', toastHTML);
    
    // Obtener el toast recién creado y mostrarlo
    const toastElement = contenedorToasts.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000  // 3 segundos
    });
    toast.show();
    
    // Eliminar el toast del DOM después de que se oculte
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
        // Si no quedan más toasts, limpiar el contenedor
        if (contenedorToasts.children.length === 0) {
            contenedorToasts.innerHTML = '';
        }
    });
}


// ================================================================
// =              FUNCIÓN: AGREGAR CLIENTE RÁPIDO                 =
// ================================================================
//
// Envía el formulario de cliente rápido vía AJAX

function agregarClienteRapido() {
    const form = document.getElementById('form-cliente-rapido');
    const formData = new FormData(form);
    
    // Enviar petición AJAX
    fetch('/api/agregar-cliente/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modal-cliente-rapido'));
            modal.hide();
            
            // Agregar el nuevo cliente al select
            const selectCliente = document.getElementById('select-cliente');
            const option = document.createElement('option');
            option.value = data.cliente_id;
            option.textContent = data.cliente_nombre;
            option.selected = true;
            selectCliente.appendChild(option);
            
            // Mostrar mensaje de éxito
            mostrarAlerta('success', 'Cliente agregado correctamente');
            
            // Limpiar el formulario
            form.reset();
        } else {
            // Mostrar errores
            mostrarAlerta('error', data.mensaje || 'Error al agregar el cliente');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('error', 'Error de conexión con el servidor');
    });
}


// ================================================================
// =                    FIN DEL ARCHIVO                           =
// ================================================================
