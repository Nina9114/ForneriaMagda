(function(){
  function fmt(dateStr){
    // Convierte YYYY-MM-DD a DD/MM/YYYY
    const parts = dateStr.split('-');
    if (parts.length !== 3) return dateStr;
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }

  function renderList(items, listId, extraWrapId, extraListId, toggleBtnId, emptyMessage){
    const list = document.getElementById(listId);
    const extraWrap = document.getElementById(extraWrapId);
    const extraList = document.getElementById(extraListId);
    const toggleBtn = document.getElementById(toggleBtnId);

    if (!list || !extraWrap || !extraList || !toggleBtn) return;

    if (!items || items.length === 0){
      list.innerHTML = `<li>${emptyMessage}</li>`;
      toggleBtn.style.display = 'none';
      return;
    }

    const first = items.slice(0, 5);
    const rest = items.slice(5);

    // Función para crear el HTML de un item con botón
    function createItemHtml(item) {
      const productoId = item.id || '';
      const productoUrl = productoId ? `/inventario/detalle/${productoId}/` : '#';
      return `
        <li style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span>${item.nombre} — ${fmt(item.caducidad)}</span>
          ${productoId ? `
            <a href="${productoUrl}" 
               class="btn-ver-producto" 
               style="
                 padding: 4px 12px;
                 background-color: #D4AF37;
                 color: #1a1a1a;
                 text-decoration: none;
                 border-radius: 4px;
                 font-size: 0.85rem;
                 font-weight: 600;
                 transition: background-color 0.2s;
                 white-space: nowrap;
                 margin-left: 10px;
               "
               onmouseover="this.style.backgroundColor='#c9a030'"
               onmouseout="this.style.backgroundColor='#D4AF37'"
               title="Ver detalles del producto">
              Ver
            </a>
          ` : ''}
        </li>
      `;
    }

    list.innerHTML = first.map(createItemHtml).join('');

    if (rest.length > 0){
      extraList.innerHTML = rest.map(createItemHtml).join('');
      toggleBtn.style.display = 'inline-block';
      let open = false;
      toggleBtn.textContent = 'Ver más';
      toggleBtn.onclick = function(){
        open = !open;
        extraWrap.style.display = open ? 'block' : 'none';
        toggleBtn.textContent = open ? 'Ver menos' : 'Ver más';
      };
    } else {
      extraWrap.style.display = 'none';
      toggleBtn.style.display = 'none';
    }
  }

  async function loadVencimientos(url, listId, extraWrapId, extraListId, toggleBtnId, dias){
    try {
      const res = await fetch(url, {credentials: 'same-origin'});
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      renderList(
        data.items || [], 
        listId, 
        extraWrapId, 
        extraListId, 
        toggleBtnId, 
        `No hay productos por vencer en ${dias} días.`
      );
    } catch (err){
      const list = document.getElementById(listId);
      if (list) list.innerHTML = `<li>Error cargando vencimientos: ${err.message}</li>`;
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    // Cargar vencimientos de 7 días
    loadVencimientos(
      '/api/proximos-vencimientos/',
      'vencimientos-list',
      'vencimientos-extra',
      'vencimientos-extra-list',
      'vencimientos-toggle',
      7
    );

    // Cargar vencimientos de 14 días
    loadVencimientos(
      '/api/proximos-vencimientos-14/',
      'vencimientos-14-list',
      'vencimientos-14-extra',
      'vencimientos-14-extra-list',
      'vencimientos-14-toggle',
      14
    );

    // Cargar vencimientos de 30 días
    loadVencimientos(
      '/api/proximos-vencimientos-30/',
      'vencimientos-30-list',
      'vencimientos-30-extra',
      'vencimientos-30-extra-list',
      'vencimientos-30-toggle',
      30
    );
  });
})();