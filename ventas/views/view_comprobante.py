# ================================================================
# =                                                              =
# =        VISTA: GENERACIÓN DE COMPROBANTE PDF                 =
# =                                                              =
# ================================================================
#
# Este archivo implementa la generación de comprobante PDF según RF-V3 del Jira:
# "Registrar pago y vuelto; emitir comprobante"
#
# REQUISITOS JIRA:
# - RF-V3: Emitir comprobante
#
# FUNCIONALIDADES:
# - Generar comprobante en formato PDF
# - Incluir datos fiscales requeridos
# - Diseño profesional
# - Opción de impresión directa

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ventas.models import Ventas, DetalleVenta
from decimal import Decimal

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ================================================================
# =        VISTA: COMPROBANTE PDF                               =
# ================================================================

@login_required
def comprobante_pdf_view(request, venta_id):
    """
    Genera un comprobante de venta en formato PDF.
    
    Cumple con RF-V3 del Jira:
    - Emitir comprobante de venta
    
    Args:
        request: HttpRequest
        venta_id: ID de la venta
        
    Returns:
        HttpResponse: Archivo PDF descargable
    """
    
    # Obtener la venta
    venta = get_object_or_404(Ventas, pk=venta_id)
    
    # Si reportlab no está disponible, generar texto plano
    if not REPORTLAB_AVAILABLE:
        return comprobante_texto_plano_view(request, venta_id)
    
    # ============================================================
    # PASO 1: Crear respuesta HTTP para PDF
    # ============================================================
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprobante_{venta.folio or venta.id}.pdf"'
    
    # ============================================================
    # PASO 2: Crear documento PDF
    # ============================================================
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Contenedor para elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # ============================================================
    # PASO 3: Encabezado del comprobante
    # ============================================================
    elements.append(Paragraph("LA FORNERÍA", title_style))
    elements.append(Paragraph("Comprobante de Venta", styles['Heading2']))
    elements.append(Spacer(1, 0.3*cm))
    
    # ============================================================
    # PASO 4: Información de la venta
    # ============================================================
    # Formato más simple, línea por línea
    folio_text = f"Folio: {venta.folio or f'VENTA-{venta.id}'}"
    fecha_text = f"Fecha: {venta.fecha.strftime('%d/%m/%Y')}"
    hora_text = f"Hora: {venta.fecha.strftime('%H:%M:%S')}"
    tipo_text = f"Tipo: {venta.canal_venta.upper()}"
    
    elements.append(Paragraph(folio_text, styles['Normal']))
    elements.append(Paragraph(fecha_text, styles['Normal']))
    elements.append(Paragraph(hora_text, styles['Normal']))
    elements.append(Paragraph(tipo_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*cm))
    
    # Cliente
    cliente_text = f"Cliente: {venta.clientes.nombre if venta.clientes else 'Cliente Genérico'}"
    elements.append(Paragraph(cliente_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*cm))
    
    # Título de productos
    elements.append(Paragraph("Productos:", styles['Normal']))
    elements.append(Spacer(1, 0.2*cm))
    
    # ============================================================
    # PASO 5: Detalles de productos (formato simple)
    # ============================================================
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    
    # Mostrar cada producto en formato simple
    for detalle in detalles:
        subtotal = detalle.calcular_subtotal()
        # Nombre del producto
        elements.append(Paragraph(f"<b>{detalle.productos.nombre}</b>", styles['Normal']))
        # Cantidad
        elements.append(Paragraph(f"Cantidad: {detalle.cantidad}", styles['Normal']))
        # Precio unitario (con IVA)
        precio_unitario_text = f"Precio unitario (con IVA): {detalle.precio_unitario:,.0f}"
        elements.append(Paragraph(precio_unitario_text, styles['Normal']))
        # Subtotal (con IVA)
        subtotal_text = f"Subtotal (con IVA): {subtotal:,.0f}"
        elements.append(Paragraph(subtotal_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*cm))
    
    elements.append(Spacer(1, 0.3*cm))
    
    # ============================================================
    # PASO 6: Totales (formato simple)
    # ============================================================
    # SubTotal (sin IVA)
    subtotal_sin_iva_text = f"SubTotal (sin IVA): {venta.total_sin_iva:,.0f}"
    elements.append(Paragraph(subtotal_sin_iva_text, styles['Normal']))
    
    # IVA 19%
    iva_text = f"IVA 19%: {venta.total_iva:,.0f}"
    elements.append(Paragraph(iva_text, styles['Normal']))
    
    # Total (con IVA)
    total_text = f"<b>Total (con IVA): {venta.total_con_iva:,.0f}</b>"
    elements.append(Paragraph(total_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*cm))
    
    # Información de pago
    if venta.monto_pagado:
        # Medio de pago (por defecto Efectivo, ya que no tenemos ese campo)
        medio_pago_text = "Medio de pago: Efectivo"
        elements.append(Paragraph(medio_pago_text, styles['Normal']))
        
        # Pago recibido
        pago_text = f"Pago recibido: {venta.monto_pagado:,.0f}"
        elements.append(Paragraph(pago_text, styles['Normal']))
        
        # Vuelto
        vuelto_text = f"Vuelto: {venta.vuelto:,.0f}"
        elements.append(Paragraph(vuelto_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
    
    # ============================================================
    # PASO 7: Pie de página
    # ============================================================
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(
        "Gracias por su compra. Síganos en @LaForneria",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER)
    ))
    
    # ============================================================
    # PASO 8: Construir PDF
    # ============================================================
    doc.build(elements)
    
    return response


# ================================================================
# =        VISTA: COMPROBANTE HTML (Fallback)                   =
# ================================================================

# ================================================================
# =        VISTA: COMPROBANTE TEXTO PLANO (Fallback)            =
# ================================================================

@login_required
def comprobante_texto_plano_view(request, venta_id):
    """
    Genera un comprobante de venta en formato texto plano (fallback si no hay reportlab).
    
    Args:
        request: HttpRequest
        venta_id: ID de la venta
        
    Returns:
        HttpResponse: Archivo de texto plano con el comprobante
    """
    
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    
    # Construir el texto del comprobante
    texto = []
    texto.append("=" * 50)
    texto.append("")
    texto.append("         LA FORNERÍA")
    texto.append("     Comprobante de Venta")
    texto.append("")
    texto.append("=" * 50)
    texto.append("")
    texto.append(f"Folio: {venta.folio or f'VENTA-{venta.id}'}")
    texto.append(f"Fecha: {venta.fecha.strftime('%d/%m/%Y')}")
    texto.append(f"Hora: {venta.fecha.strftime('%H:%M:%S')}")
    texto.append(f"Tipo: {venta.canal_venta.upper()}")
    texto.append("")
    texto.append("-" * 50)
    texto.append("")
    texto.append(f"Cliente: {venta.clientes.nombre if venta.clientes else 'Cliente Genérico'}")
    texto.append("")
    texto.append("-" * 50)
    texto.append("")
    texto.append("Productos:")
    texto.append("")
    
    # Detalles de productos
    for detalle in detalles:
        subtotal = detalle.calcular_subtotal()
        texto.append(f"  {detalle.productos.nombre}")
        texto.append(f"  Cantidad: {detalle.cantidad} x ${detalle.precio_unitario:,.0f}")
        texto.append(f"  Subtotal: ${subtotal:,.0f}")
        texto.append("")
    
    texto.append("-" * 50)
    texto.append("")
    texto.append(f"  SubTotal (sin IVA):        ${venta.total_sin_iva:,.0f}")
    texto.append(f"  IVA (19%):                 ${venta.total_iva:,.0f}")
    texto.append("")
    texto.append("-" * 50)
    texto.append("")
    texto.append(f"  TOTAL (con IVA):           ${venta.total_con_iva:,.0f}")
    texto.append("")
    texto.append("-" * 50)
    texto.append("")
    
    # Información de pago
    if venta.monto_pagado:
        texto.append(f"  Pago recibido:            ${venta.monto_pagado:,.0f}")
        texto.append(f"  Vuelto:                   ${venta.vuelto:,.0f}")
        texto.append("")
    
    texto.append("=" * 50)
    texto.append("")
    texto.append("          ¡Gracias por su compra!")
    texto.append("      Visite nuestras redes sociales")
    texto.append("             @LaForneria")
    texto.append("")
    texto.append("=" * 50)
    
    # Crear respuesta HTTP con texto plano
    response = HttpResponse('\n'.join(texto), content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="comprobante_{venta.folio or venta.id}.txt"'
    
    return response


# ================================================================
# =        VISTA: COMPROBANTE HTML (Fallback)                   =
# ================================================================

@login_required
def comprobante_html_view(request, venta_id):
    """
    Genera un comprobante de venta en formato HTML (fallback si no hay reportlab).
    
    Args:
        request: HttpRequest
        venta_id: ID de la venta
        
    Returns:
        HttpResponse: Página HTML con el comprobante
    """
    
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    
    context = {
        'venta': venta,
        'detalles': detalles,
    }
    
    return render(request, 'comprobante.html', context)

