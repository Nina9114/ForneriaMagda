# ================================================================
# =                                                              =
# =              VISTA PARA SISTEMA DE REPORTES                 =
# =                                                              =
# ================================================================
#
# Este archivo contiene la vista principal del sistema de reportes.
#
# PROPÓSITO:
# - Portal de acceso a todos los reportes disponibles
# - Navegación centralizada a reportes específicos
#
# FUNCIONALIDADES:
# - Mostrar enlaces a reportes específicos
# - Portal de navegación

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# ================================================================
# =                    VISTA: REPORTES                           =
# ================================================================

@login_required
def reportes_view(request):
    """
    Vista principal del sistema de reportes (portal de navegación).
    
    Muestra un portal con enlaces a todos los reportes disponibles.
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        HttpResponse: Página HTML con el portal de reportes
    """
    
    # ============================================================
    # PASO 1: Preparar contexto
    # ============================================================
    context = {}
    
    # ============================================================
    # PASO 2: Renderizar template
    # ============================================================
    return render(request, 'reportes.html', context)
