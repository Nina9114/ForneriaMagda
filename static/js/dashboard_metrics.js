// ================================================================
// =                                                              =
// =           JAVASCRIPT PARA MÉTRICAS DEL DASHBOARD            =
// =                                                              =
// ================================================================
//
// Este archivo maneja la carga y actualización de las métricas
// principales del dashboard en tiempo real.

/**
 * Formatea un número como moneda chilena (CLP)
 * @param {number} valor - El valor a formatear
 * @returns {string} - Valor formateado como "$1.234.567"
 */
function formatearMoneda(valor) {
    if (valor === null || valor === undefined || isNaN(valor)) {
        return '$0';
    }
    return '$' + Math.round(valor).toLocaleString('es-CL');
}

/**
 * Carga las ventas del día desde la API
 */
function cargarVentasDelDia() {
    console.log('Cargando ventas del día...');
    fetch('/api/ventas-del-dia/')
        .then(response => {
            console.log('Respuesta ventas del día:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos ventas del día:', data);
            // Actualizar el valor de ventas - usar múltiples selectores para mayor robustez
            const ventasCol = document.querySelector('.dashboard-row .dashboard-col:first-child');
            const ventasValue = ventasCol?.querySelector('.metric-card-value');
            const ventasSubtitle = ventasCol?.querySelector('.metric-card-subtitle');
            
            console.log('Elementos encontrados - ventasValue:', ventasValue, 'ventasSubtitle:', ventasSubtitle);
            
            if (ventasValue && ventasSubtitle) {
                if (data.error) {
                    console.error('Error en API ventas del día:', data.error);
                    ventasValue.textContent = 'Error';
                    ventasSubtitle.textContent = '0 transacciones';
                } else {
                    const totalFormateado = formatearMoneda(data.total_ventas || 0);
                    const transacciones = data.num_transacciones || 0;
                    console.log('Actualizando ventas del día:', totalFormateado, transacciones);
                    ventasValue.textContent = totalFormateado;
                    ventasSubtitle.textContent = `${transacciones} transacciones`;
                }
            } else {
                console.warn('No se encontraron elementos para ventas del día. Buscando alternativas...');
                // Intentar con selector alternativo
                const altValue = document.querySelector('.metric-card-title:contains("Ventas del Día")')?.nextElementSibling;
                console.warn('Selector alternativo:', altValue);
            }
        })
        .catch(error => {
            console.error('Error al cargar ventas del día:', error);
            const ventasValue = document.querySelector('.dashboard-row .dashboard-col:nth-child(1) .metric-card-value');
            const ventasSubtitle = document.querySelector('.dashboard-row .dashboard-col:nth-child(1) .metric-card-subtitle');
            if (ventasValue && ventasSubtitle) {
                ventasValue.textContent = 'Error';
                ventasSubtitle.textContent = '0 transacciones';
            }
        });
}

/**
 * Carga los productos con stock bajo desde la API
 */
function cargarStockBajo() {
    console.log('Cargando stock bajo...');
    fetch('/api/stock-bajo/')
        .then(response => {
            console.log('Respuesta stock bajo:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos stock bajo:', data);
            // Actualizar el valor de stock bajo - usar múltiples selectores
            const stockCol = document.querySelector('.dashboard-row .dashboard-col:nth-child(2)');
            const stockCard = stockCol?.querySelector('.dashboard-metric-card');
            const stockValue = stockCol?.querySelector('.metric-card-value');
            const stockSubtitle = stockCol?.querySelector('.metric-card-subtitle');
            
            console.log('Elementos encontrados - stockValue:', stockValue, 'stockSubtitle:', stockSubtitle);
            
            if (stockValue && stockSubtitle) {
                if (data.error) {
                    console.error('Error en API stock bajo:', data.error);
                    stockValue.textContent = 'Error';
                    stockSubtitle.textContent = 'Error';
                } else {
                    const numProductos = data.num_productos || 0;
                    console.log('Actualizando stock bajo:', numProductos);
                    stockValue.textContent = numProductos;
                    stockSubtitle.textContent = 'Productos';
                
                    // Cambiar color si hay productos con stock bajo
                    if (data.num_productos > 0) {
                        stockValue.style.color = '#ff6b6b';
                        
                        // Agregar enlace al inventario si no existe
                        if (stockCard && !stockCard.querySelector('.btn-ver-inventario')) {
                            const linkInventario = document.createElement('a');
                            linkInventario.href = '/inventario/';
                            linkInventario.className = 'btn-ver-inventario';
                            linkInventario.textContent = 'Ver Inventario';
                            linkInventario.style.cssText = `
                                display: inline-block;
                                margin-top: 10px;
                                padding: 6px 16px;
                                background-color: #D4AF37;
                                color: #1a1a1a;
                                text-decoration: none;
                                border-radius: 4px;
                                font-size: 0.9rem;
                                font-weight: 600;
                                transition: background-color 0.2s;
                            `;
                            linkInventario.onmouseover = function() { this.style.backgroundColor = '#c9a030'; };
                            linkInventario.onmouseout = function() { this.style.backgroundColor = '#D4AF37'; };
                            stockCard.appendChild(linkInventario);
                        }
                    } else {
                        // Remover enlace si no hay productos con stock bajo
                        const linkInventario = stockCard?.querySelector('.btn-ver-inventario');
                        if (linkInventario) {
                            linkInventario.remove();
                        }
                    }
                }
            } else {
                console.warn('No se encontraron elementos para stock bajo');
            }
        })
        .catch(error => {
            console.error('Error al cargar stock bajo:', error);
            const stockValue = document.querySelector('.dashboard-row .dashboard-col:nth-child(2) .metric-card-value');
            const stockSubtitle = document.querySelector('.dashboard-row .dashboard-col:nth-child(2) .metric-card-subtitle');
            if (stockValue && stockSubtitle) {
                stockValue.textContent = 'Error';
                stockSubtitle.textContent = 'Error';
            }
        });
}

/**
 * Carga las alertas pendientes desde la API
 */
function cargarAlertasPendientes() {
    console.log('Cargando alertas pendientes...');
    fetch('/api/alertas-pendientes/')
        .then(response => {
            console.log('Respuesta alertas:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos alertas:', data);
            // Actualizar el valor de alertas - usar múltiples selectores
            const alertasCol = document.querySelector('.dashboard-row .dashboard-col:nth-child(3)');
            const alertasCard = alertasCol?.querySelector('.dashboard-metric-card');
            const alertasValue = alertasCol?.querySelector('.metric-card-value');
            const alertasSubtitle = alertasCol?.querySelector('.metric-card-subtitle');
            
            console.log('Elementos encontrados - alertasValue:', alertasValue, 'alertasSubtitle:', alertasSubtitle);
            
            if (alertasValue && alertasSubtitle) {
                const numAlertas = data.num_alertas || 0;
                console.log('Actualizando alertas:', numAlertas);
                alertasValue.textContent = numAlertas;
                
                // Mostrar desglose por tipo
                const rojas = data.por_tipo?.roja || 0;
                const amarillas = data.por_tipo?.amarilla || 0;
                const verdes = data.por_tipo?.verde || 0;
                
                alertasSubtitle.innerHTML = `
                    <span style="color: #ff6b6b;">${rojas} rojas</span> | 
                    <span style="color: #ffd93d;">${amarillas} amarillas</span> | 
                    <span style="color: #6bcf7f;">${verdes} verdes</span>
                `;
                
                // Cambiar color si hay alertas rojas
                if (rojas > 0) {
                    alertasValue.style.color = '#ff6b6b';
                } else {
                    alertasValue.style.color = '';
                }
                
                // Agregar enlace a alertas si hay alertas y no existe el botón
                if (numAlertas > 0 && alertasCard && !alertasCard.querySelector('.btn-ver-alertas')) {
                    const linkAlertas = document.createElement('a');
                    linkAlertas.href = '/alertas/';
                    linkAlertas.className = 'btn-ver-alertas';
                    linkAlertas.textContent = 'Ver Alertas';
                    linkAlertas.style.cssText = `
                        display: inline-block;
                        margin-top: 10px;
                        padding: 6px 16px;
                        background-color: #D4AF37;
                        color: #1a1a1a;
                        text-decoration: none;
                        border-radius: 4px;
                        font-size: 0.9rem;
                        font-weight: 600;
                        transition: background-color 0.2s;
                    `;
                    linkAlertas.onmouseover = function() { this.style.backgroundColor = '#c9a030'; };
                    linkAlertas.onmouseout = function() { this.style.backgroundColor = '#D4AF37'; };
                    alertasCard.appendChild(linkAlertas);
                } else if (numAlertas === 0) {
                    // Remover enlace si no hay alertas
                    const linkAlertas = alertasCard?.querySelector('.btn-ver-alertas');
                    if (linkAlertas) {
                        linkAlertas.remove();
                    }
                }
            } else {
                console.warn('No se encontraron elementos para alertas');
            }
        })
        .catch(error => {
            console.error('Error al cargar alertas pendientes:', error);
            const alertasValue = document.querySelector('.dashboard-row .dashboard-col:nth-child(3) .metric-card-value');
            const alertasSubtitle = document.querySelector('.dashboard-row .dashboard-col:nth-child(3) .metric-card-subtitle');
            if (alertasValue && alertasSubtitle) {
                alertasValue.textContent = 'Error';
                alertasSubtitle.textContent = 'Error';
            }
        });
}

/**
 * Carga el producto más vendido del día desde la API
 */
function cargarTopProducto() {
    console.log('Cargando top producto...');
    fetch('/api/top-producto/')
        .then(response => {
            console.log('Respuesta top producto:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos top producto:', data);
            // Actualizar el valor del top producto - usar múltiples selectores
            const topCol = document.querySelector('.dashboard-row .dashboard-col:nth-child(4)');
            const topCard = topCol?.querySelector('.dashboard-metric-card');
            const topValue = topCol?.querySelector('.metric-card-value');
            const topSubtitle = topCol?.querySelector('.metric-card-subtitle');
            
            console.log('Elementos encontrados - topValue:', topValue, 'topSubtitle:', topSubtitle);
            
            if (topValue && topSubtitle) {
                if (data.error) {
                    console.error('Error en API top producto:', data.error);
                    topValue.textContent = 'Error';
                    topSubtitle.textContent = '0 unidades';
                    topValue.style.color = '#888';
                } else {
                    const nombre = data.nombre || 'Sin ventas';
                    const unidades = data.unidades || 0;
                    console.log('Actualizando top producto:', nombre, unidades);
                    topValue.textContent = nombre;
                    topSubtitle.textContent = `${unidades} unidades`;
                    
                    // Cambiar estilo si es "Sin ventas"
                    if (data.nombre === 'Sin ventas' || !data.nombre) {
                        topValue.style.color = '#888';
                        topValue.style.fontSize = '1.2rem';
                    } else {
                        topValue.style.color = '#D4AF37';
                        topValue.style.fontSize = '1.5rem';
                        
                        // Agregar enlace al reporte de top productos si no existe
                        if (topCard && !topCard.querySelector('.btn-ver-top-productos')) {
                            const linkTopProductos = document.createElement('a');
                            linkTopProductos.href = '/reportes/top-productos/';
                            linkTopProductos.className = 'btn-ver-top-productos';
                            linkTopProductos.textContent = 'Ver Reporte';
                            linkTopProductos.style.cssText = `
                                display: inline-block;
                                margin-top: 10px;
                                padding: 6px 16px;
                                background-color: #D4AF37;
                                color: #1a1a1a;
                                text-decoration: none;
                                border-radius: 4px;
                                font-size: 0.9rem;
                                font-weight: 600;
                                transition: background-color 0.2s;
                            `;
                            linkTopProductos.onmouseover = function() { this.style.backgroundColor = '#c9a030'; };
                            linkTopProductos.onmouseout = function() { this.style.backgroundColor = '#D4AF37'; };
                            topCard.appendChild(linkTopProductos);
                        }
                    }
                }
            } else {
                console.warn('No se encontraron elementos para top producto');
            }
        })
        .catch(error => {
            console.error('Error al cargar top producto:', error);
            const topValue = document.querySelector('.dashboard-row .dashboard-col:nth-child(4) .metric-card-value');
            const topSubtitle = document.querySelector('.dashboard-row .dashboard-col:nth-child(4) .metric-card-subtitle');
            if (topValue && topSubtitle) {
                topValue.textContent = 'Error';
                topSubtitle.textContent = '0 unidades';
                topValue.style.color = '#888';
            }
        });
}

/**
 * Carga la tabla detallada de productos con stock bajo
 */
function cargarTablaStockBajo() {
    console.log('[TABLA] Cargando tabla stock bajo...');
    const container = document.getElementById('tabla-stock-bajo');
    if (!container) {
        console.error('[TABLA] No se encontró el contenedor tabla-stock-bajo');
        return;
    }
    
    // Remover el mensaje de "Cargando..." si existe
    const loadingMsg = document.getElementById('tabla-stock-bajo-loading');
    if (loadingMsg) {
        loadingMsg.remove();
    }
    
    console.log('[TABLA] Contenedor encontrado, haciendo petición a /api/stock-bajo/');
    fetch('/api/stock-bajo/')
        .then(response => {
            console.log('Respuesta stock bajo:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos stock bajo recibidos:', data);
            
            if (data.error) {
                container.innerHTML = '<p class="text-danger">Error al cargar datos</p>';
                console.log('[TABLA] Error en datos, mostrando mensaje de error');
                return;
            }
            
            if (!data.productos || data.productos.length === 0) {
                console.log('[TABLA] No hay productos con stock bajo, mostrando mensaje');
                container.innerHTML = '<p class="text-muted"><i class="bi bi-check-circle"></i> No hay productos con stock bajo</p>';
                console.log('[TABLA] Mensaje actualizado en contenedor');
                return;
            }
            
            let html = '<table class="table table-sm table-hover" style="font-size: 0.85rem;">';
            html += '<thead><tr><th>Producto</th><th>Stock</th><th>Mínimo</th></tr></thead><tbody>';
            
            data.productos.forEach(producto => {
                const porcentaje = (producto.cantidad / producto.stock_minimo) * 100;
                const colorClass = porcentaje <= 50 ? 'text-danger' : 'text-warning';
                html += `
                    <tr>
                        <td>
                            <a href="/inventario/detalle/${producto.id}/" style="text-decoration: none; color: inherit;">
                                ${producto.nombre}
                            </a>
                        </td>
                        <td class="${colorClass}"><strong>${producto.cantidad}</strong></td>
                        <td>${producto.stock_minimo}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
            console.log('Tabla stock bajo actualizada correctamente');
        })
        .catch(error => {
            console.error('Error al cargar tabla stock bajo:', error);
            const container = document.getElementById('tabla-stock-bajo');
            if (container) {
                container.innerHTML = '<p class="text-danger">Error al cargar datos</p>';
            }
        });
}

/**
 * Carga la tabla detallada de productos en merma
 */
function cargarTablaMerma() {
    console.log('[TABLA] Cargando tabla merma...');
    const container = document.getElementById('tabla-merma');
    if (!container) {
        console.error('[TABLA] No se encontró el contenedor tabla-merma');
        return;
    }
    
    // Remover el mensaje de "Cargando..." si existe
    const loadingMsg = document.getElementById('tabla-merma-loading');
    if (loadingMsg) {
        loadingMsg.remove();
    }
    
    console.log('[TABLA] Contenedor encontrado, haciendo petición a /api/merma/lista/');
    fetch('/api/merma/lista/')
        .then(response => {
            console.log('Respuesta merma:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos merma recibidos:', data);
            
            if (data.error) {
                container.innerHTML = '<p class="text-danger">Error al cargar datos</p>';
                return;
            }
            
            if (!data.productos || data.productos.length === 0) {
                container.innerHTML = '<p class="text-muted"><i class="bi bi-check-circle"></i> No hay productos en merma</p>';
                console.log('No hay productos en merma');
                return;
            }
            
            let html = '<table class="table table-sm table-hover" style="font-size: 0.85rem;">';
            html += '<thead><tr><th>Producto</th><th>Cantidad</th><th>Pérdida</th></tr></thead><tbody>';
            
            data.productos.slice(0, 10).forEach(producto => {
                html += `
                    <tr>
                        <td>
                            <a href="/inventario/detalle/${producto.id}/" style="text-decoration: none; color: inherit;">
                                ${producto.nombre}
                            </a>
                        </td>
                        <td class="text-danger">${producto.cantidad_merma} ${producto.unidad}</td>
                        <td class="text-danger"><strong>${formatearMoneda(producto.perdida)}</strong></td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            if (data.productos.length > 10) {
                html += `<p class="text-muted small">Mostrando 10 de ${data.productos.length} productos. <a href="/merma/">Ver todos</a></p>`;
            } else {
                html += `<p class="text-muted small"><a href="/merma/">Ver todos</a></p>`;
            }
            container.innerHTML = html;
            console.log('Tabla merma actualizada correctamente');
        })
        .catch(error => {
            console.error('Error al cargar tabla merma:', error);
            const container = document.getElementById('tabla-merma');
            if (container) {
                container.innerHTML = '<p class="text-danger">Error al cargar datos</p>';
            }
        });
}

/**
 * Carga la tabla detallada de ventas del día
 */
function cargarTablaVentasDia() {
    console.log('[TABLA] Cargando tabla ventas del día...');
    const container = document.getElementById('tabla-ventas-dia');
    if (!container) {
        console.error('[TABLA] No se encontró el contenedor tabla-ventas-dia');
        return;
    }
    
    // Remover el mensaje de "Cargando..." si existe
    const loadingMsg = document.getElementById('tabla-ventas-dia-loading');
    if (loadingMsg) {
        loadingMsg.remove();
    }
    
    console.log('[TABLA] Contenedor encontrado, haciendo petición a /api/ventas-del-dia/lista/');
    fetch('/api/ventas-del-dia/lista/')
        .then(response => {
            console.log('Respuesta ventas del día:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos ventas del día recibidos:', data);
            
            if (data.error) {
                console.log('[TABLA] Error en datos ventas del día');
                container.innerHTML = '<p class="text-danger">Error al cargar datos</p>';
                return;
            }
            
            if (!data.ventas || data.ventas.length === 0) {
                console.log('[TABLA] No hay ventas del día');
                container.innerHTML = '<p class="text-muted"><i class="bi bi-info-circle"></i> No hay ventas registradas hoy</p>';
                return;
            }
            
            console.log(`[TABLA] Procesando ${data.ventas.length} ventas del día`);
            let html = '<table class="table table-sm table-hover" style="font-size: 0.85rem;">';
            html += '<thead><tr><th>Folio</th><th>Hora</th><th>Total</th><th>Cliente</th></tr></thead><tbody>';
            
            data.ventas.slice(0, 10).forEach(venta => {
                html += `
                    <tr>
                        <td>
                            <a href="/ventas/comprobante/${venta.id}/" style="text-decoration: none; color: inherit;">
                                ${venta.folio}
                            </a>
                        </td>
                        <td>${venta.hora}</td>
                        <td class="text-success"><strong>${formatearMoneda(venta.total)}</strong></td>
                        <td>${venta.cliente}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            if (data.ventas.length > 10) {
                html += `<p class="text-muted small">Mostrando 10 de ${data.ventas.length} ventas</p>`;
            }
            console.log('[TABLA] Actualizando HTML de ventas del día...');
            container.innerHTML = html;
            console.log('[TABLA] Tabla ventas del día actualizada correctamente, HTML length:', html.length);
        })
        .catch(error => {
            console.error('Error al cargar tabla ventas del día:', error);
            const container = document.getElementById('tabla-ventas-dia');
            if (container) {
                container.innerHTML = '<p class="text-danger">Error al cargar datos</p>';
            }
        });
}

/**
 * Inicializa todas las métricas del dashboard
 */
function inicializarMetricas() {
    console.log('=== Inicializando métricas del dashboard ===');
    
    // Verificar que los elementos existan
    const dashboardRow = document.querySelector('.dashboard-row');
    if (!dashboardRow) {
        console.error('ERROR: No se encontró .dashboard-row en el DOM');
        return;
    }
    
    const cols = dashboardRow.querySelectorAll('.dashboard-col');
    console.log('Columnas encontradas:', cols.length);
    
    // Verificar que los contenedores de tablas existan
    const tablaStockBajo = document.getElementById('tabla-stock-bajo');
    const tablaMerma = document.getElementById('tabla-merma');
    const tablaVentasDia = document.getElementById('tabla-ventas-dia');
    
    console.log('Contenedores encontrados:', {
        stockBajo: !!tablaStockBajo,
        merma: !!tablaMerma,
        ventasDia: !!tablaVentasDia
    });
    
    cargarVentasDelDia();
    cargarStockBajo();
    cargarAlertasPendientes();
    cargarTopProducto();
    
    // Cargar tablas detalladas (con un pequeño delay para asegurar que el DOM esté listo)
    setTimeout(() => {
        console.log('Cargando tablas detalladas...');
        cargarTablaStockBajo();
        cargarTablaMerma();
        cargarTablaVentasDia();
    }, 200);
    
    console.log('=== Métricas inicializadas ===');
}

/**
 * Actualiza las métricas cada cierto tiempo
 * @param {number} intervalo - Intervalo en milisegundos (default: 30 segundos)
 */
function actualizarMetricasPeriodicamente(intervalo = 30000) {
    setInterval(() => {
        inicializarMetricas();
    }, intervalo);
}

// Inicializar cuando el DOM esté listo
(function() {
    function init() {
        console.log('[INIT] Inicializando métricas del dashboard...');
        console.log('[INIT] Estado del DOM:', document.readyState);
        
        // Verificar que los elementos existan antes de inicializar
        const tablaStockBajo = document.getElementById('tabla-stock-bajo');
        const tablaMerma = document.getElementById('tabla-merma');
        const tablaVentasDia = document.getElementById('tabla-ventas-dia');
        
        console.log('[INIT] Contenedores:', {
            stockBajo: !!tablaStockBajo,
            merma: !!tablaMerma,
            ventasDia: !!tablaVentasDia
        });
        
        if (!tablaStockBajo || !tablaMerma || !tablaVentasDia) {
            console.warn('[INIT] Algunos contenedores no están disponibles aún, reintentando en 500ms...');
            setTimeout(init, 500);
            return;
        }
        
        console.log('[INIT] Todos los contenedores encontrados, inicializando métricas...');
        inicializarMetricas();
        actualizarMetricasPeriodicamente(30000);
    }
    
    // Esperar a que el DOM esté completamente cargado
    if (document.readyState === 'loading') {
        console.log('[INIT] DOM está cargando, esperando DOMContentLoaded...');
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[INIT] DOMContentLoaded disparado, iniciando en 300ms...');
            setTimeout(init, 300);
        });
    } else {
        // DOM ya está listo, pero esperar un poco más para asegurar que todo esté renderizado
        console.log('[INIT] DOM ya está listo, iniciando en 300ms...');
        setTimeout(init, 300);
    }
})();
