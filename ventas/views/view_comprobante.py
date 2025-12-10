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
from django.utils import timezone
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
    # Convertir fecha a zona horaria local
    fecha_local = timezone.localtime(venta.fecha)
    
    # Formato más simple, línea por línea
    folio_text = f"Folio: {venta.folio or f'VENTA-{venta.id}'}"
    fecha_text = f"Fecha: {fecha_local.strftime('%d/%m/%Y')}"
    hora_text = f"Hora: {fecha_local.strftime('%H:%M:%S')}"
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
    # PASO 5: Detalles de productos (formato tabla)
    # ============================================================
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    
    # Crear tabla de productos
    productos_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
    
    for detalle in detalles:
        subtotal = detalle.calcular_subtotal()
        productos_data.append([
            detalle.productos.nombre,
            str(detalle.cantidad),
            f"${detalle.precio_unitario:,.0f}",
            f"${subtotal:,.0f}"
        ])
    
    productos_table = Table(productos_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
    productos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elements.append(productos_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ============================================================
    # PASO 6: Totales (formato tabla)
    # ============================================================
    totales_data = [
        ['SubTotal (sin IVA):', f"${venta.total_sin_iva:,.0f}"],
        ['IVA (19%):', f"${venta.total_iva:,.0f}"],
        ['TOTAL (con IVA):', f"${venta.total_con_iva:,.0f}"]
    ]
    
    totales_table = Table(totales_data, colWidths=[10*cm, 6*cm])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('TOPPADDING', (0, -1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(totales_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # Información de pago
    if venta.monto_pagado:
        # Medio de pago
        medio_pago_display = venta.get_medio_pago_display() if hasattr(venta, 'get_medio_pago_display') else (
            'Efectivo' if hasattr(venta, 'medio_pago') and venta.medio_pago == 'efectivo' else
            'Tarjeta Débito' if hasattr(venta, 'medio_pago') and venta.medio_pago == 'tarjeta_debito' else
            'Tarjeta Crédito' if hasattr(venta, 'medio_pago') and venta.medio_pago == 'tarjeta_credito' else
            'Transferencia' if hasattr(venta, 'medio_pago') and venta.medio_pago == 'transferencia' else
            'Cheque' if hasattr(venta, 'medio_pago') and venta.medio_pago == 'cheque' else
            'Otro' if hasattr(venta, 'medio_pago') and venta.medio_pago == 'otro' else 'Efectivo'
        )
        medio_pago_text = f"Medio de pago: {medio_pago_display}"
        elements.append(Paragraph(medio_pago_text, styles['Normal']))
        
        # Pago recibido
        pago_text = f"Pago recibido: {venta.monto_pagado:,.0f}"
        elements.append(Paragraph(pago_text, styles['Normal']))
        
        # Vuelto (solo para efectivo)
        if hasattr(venta, 'medio_pago') and venta.medio_pago == 'efectivo' and venta.vuelto:
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
    
    # Refrescar el objeto desde la base de datos para asegurar que tenemos todos los campos
    venta.refresh_from_db()
    
    # Convertir fecha a zona horaria local
    fecha_local = timezone.localtime(venta.fecha)
    
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
    texto.append(f"Fecha: {fecha_local.strftime('%d/%m/%Y')}")
    texto.append(f"Hora: {fecha_local.strftime('%H:%M:%S')}")
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
        # Medio de pago - leer directamente de la base de datos
        # Como el modelo tiene managed=False, necesitamos leer el campo directamente
        medio_pago = 'efectivo'  # Valor por defecto
        try:
            # Primero intentar leer del objeto (puede funcionar si Django reconoce el campo)
            if hasattr(venta, 'medio_pago'):
                medio_pago = venta.medio_pago or 'efectivo'
            else:
                # Si no está en el objeto, leer directamente de la BD
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT medio_pago FROM ventas WHERE id = %s", [venta.id])
                    row = cursor.fetchone()
                    if row and row[0]:
                        medio_pago = row[0]
        except Exception as e:
            # Si falla, usar valor por defecto
            import logging
            logger = logging.getLogger('ventas')
            logger.warning(f'Error al leer medio_pago para venta {venta.id}: {e}')
            medio_pago = 'efectivo'
        
        medio_pago_display_map = {
            'efectivo': 'Efectivo',
            'tarjeta_debito': 'Tarjeta Débito',
            'tarjeta_credito': 'Tarjeta Crédito',
            'transferencia': 'Transferencia',
            'cheque': 'Cheque',
            'otro': 'Otro'
        }
        medio_pago_display = medio_pago_display_map.get(medio_pago, 'Efectivo')
        
        # Agregar medio de pago ANTES de pago recibido
        texto.append(f"  Medio de pago:            {medio_pago_display}")
        texto.append(f"  Pago recibido:            ${venta.monto_pagado:,.0f}")
        if medio_pago == 'efectivo' and venta.vuelto:
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

