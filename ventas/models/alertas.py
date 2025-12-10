# ================================================================
# =                                                              =
# =                 MODELO PARA ALERTAS DE PRODUCTOS            =
# =                                                              =
# ================================================================
#
# Este archivo define el modelo de Alertas que se conecta con la
# tabla 'alertas' de MySQL.
#
# Las alertas son notificaciones automáticas que se generan cuando
# un producto está próximo a vencer, clasificadas por colores:
# - VERDE: 30+ días hasta vencer (informativo)
# - AMARILLA: 14-29 días hasta vencer (precaución)
# - ROJA: 0-13 días hasta vencer (urgente)

from django.db import models
from django.utils import timezone
from datetime import timedelta
from .productos import Productos
from .proveedores import FacturaProveedor


# ================================================================
# =                    MODELO: ALERTAS                           =
# ================================================================

class Alertas(models.Model):
    """
    Modelo para gestionar alertas de vencimiento de productos.
    
    Cada alerta está asociada a un producto específico y tiene un
    tipo (color) que indica la urgencia según los días hasta vencer.
    """
    
    # --- Opciones para el tipo de alerta ---
    # Definimos las tres categorías de alertas según urgencia
    TIPO_CHOICES = [
        ('verde', 'Verde (30+ días)'),      # Informativo
        ('amarilla', 'Amarilla (14-29 días)'),  # Precaución
        ('roja', 'Roja (0-13 días)'),       # Urgente
    ]
    
    # --- Opciones para el estado de la alerta ---
    # Permite hacer seguimiento de qué alertas se han atendido
    ESTADO_CHOICES = [
        ('activa', 'Activa'),           # Alerta recién creada o pendiente
        ('resuelta', 'Resuelta'),       # Se tomó acción sobre el producto
        ('ignorada', 'Ignorada'),       # Se decidió no actuar
    ]
    
    # --- Campo: Tipo de alerta ---
    # El color/categoría de la alerta según días hasta vencer
    tipo_alerta = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='verde',
        verbose_name='Tipo de alerta'
    )
    
    # --- Campo: Mensaje descriptivo ---
    # Texto que describe la alerta (ej: "Pan integral vence en 5 días")
    mensaje = models.CharField(
        max_length=255,
        verbose_name='Mensaje'
    )
    
    # --- Campo: Fecha de generación ---
    # Cuándo se creó la alerta (automático)
    fecha_generada = models.DateTimeField(
        auto_now_add=True,  # Se llena automáticamente al crear
        verbose_name='Fecha generada'
    )
    
    # --- Campo: Estado ---
    # Si la alerta está activa, resuelta o ignorada
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa',
        verbose_name='Estado'
    )
    
    # --- Relación: Producto asociado (opcional) ---
    # Cada alerta puede estar asociada a un producto específico
    productos = models.ForeignKey(
        Productos,
        on_delete=models.CASCADE,  # Si se borra el producto, se borran sus alertas
        related_name='alertas',    # Para hacer producto.alertas.all()
        verbose_name='Producto',
        null=True,
        blank=True,
        help_text='Producto asociado a esta alerta (opcional si es alerta de factura)'
    )
    
    # --- Relación: Factura asociada (opcional) ---
    # Cada alerta puede estar asociada a una factura de proveedor
    factura_proveedor = models.ForeignKey(
        FacturaProveedor,
        on_delete=models.CASCADE,  # Si se borra la factura, se borran sus alertas
        related_name='alertas',    # Para hacer factura.alertas.all()
        verbose_name='Factura Proveedor',
        null=True,
        blank=True,
        help_text='Factura asociada a esta alerta (opcional si es alerta de producto)'
    )
    
    # ============================================================
    # =                   MÉTODOS AUXILIARES                     =
    # ============================================================
    
    def __str__(self):
        """
        Representación en texto de la alerta.
        Se usa en el admin de Django y al imprimir.
        """
        return f"[{self.get_tipo_alerta_display()}] {self.mensaje}"
    
    def get_dias_hasta_vencer(self):
        """
        Calcula cuántos días faltan para que venza el producto o la factura.
        
        Returns:
            int: Número de días hasta la fecha de caducidad o vencimiento
            None: Si no hay fecha de vencimiento disponible
        """
        hoy = timezone.now().date()
        
        # Si es alerta de producto
        if self.productos and self.productos.caducidad:
            dias = (self.productos.caducidad - hoy).days
            return dias
        
        # Si es alerta de factura
        if self.factura_proveedor and self.factura_proveedor.fecha_vencimiento:
            dias = (self.factura_proveedor.fecha_vencimiento - hoy).days
            return dias
        
        # Si no hay fecha disponible
        return None
    
    def get_dias_hasta_vencer_display(self):
        """
        Retorna el texto formateado para mostrar los días hasta vencer.
        
        Returns:
            str: Texto formateado (ej: "5 días", "Vencida hace 2 días", "—")
        """
        dias = self.get_dias_hasta_vencer()
        
        if dias is None:
            return "—"
        
        if dias < 0:
            return f"Vencida hace {abs(dias)} días"
        else:
            return f"{dias} días"
    
    def get_color_badge(self):
        """
        Retorna la clase CSS de Bootstrap según el tipo de alerta.
        Útil para mostrar badges de colores en el HTML.
        
        Returns:
            str: Clase CSS de Bootstrap (danger, warning, success)
        """
        colores = {
            'roja': 'danger',      # Bootstrap rojo
            'amarilla': 'warning', # Bootstrap amarillo
            'verde': 'success',    # Bootstrap verde
        }
        return colores.get(self.tipo_alerta, 'secondary')
    
    def get_icono(self):
        """
        Retorna un icono Bootstrap según el tipo de alerta.
        
        Returns:
            str: Clase de icono Bootstrap Icons
        """
        iconos = {
            'roja': 'bi-exclamation-triangle-fill',    # Triángulo con !
            'amarilla': 'bi-exclamation-circle-fill',  # Círculo con !
            'verde': 'bi-info-circle-fill',            # Círculo con i
        }
        return iconos.get(self.tipo_alerta, 'bi-bell-fill')
    
    def marcar_como_resuelta(self):
        """
        Marca la alerta como resuelta.
        Útil cuando se toma acción sobre el producto.
        """
        self.estado = 'resuelta'
        self.save(update_fields=['estado'])
    
    def marcar_como_ignorada(self):
        """
        Marca la alerta como ignorada.
        Útil cuando se decide no actuar sobre la alerta.
        """
        self.estado = 'ignorada'
        self.save(update_fields=['estado'])
    
    # ============================================================
    # =                MÉTODO ESTÁTICO: GENERAR ALERTAS          =
    # ============================================================
    
    @staticmethod
    def generar_alertas_automaticas():
        """
        Genera alertas automáticamente para:
        - Productos según sus fechas de caducidad Y niveles de stock
        - Facturas de proveedores según fecha de vencimiento de pago
        
        Este método debe ejecutarse diariamente (puede ser con un cron job
        o un comando de Django que se ejecute al iniciar el servidor).
        
        Lógica de VENCIMIENTO (productos):
        - Roja: 0 a 13 días hasta vencer
        - Amarilla: 14 a 29 días hasta vencer
        - Verde: 30 o más días hasta vencer
        
        Lógica de STOCK BAJO:
        - Roja: cantidad <= stock_minimo (o <= 5 si no hay stock_minimo definido)
        - Se resuelve automáticamente cuando el stock vuelve a ser normal
        
        Lógica de FACTURAS VENCIDAS:
        - Roja: Factura vencida sin pagar
        - Amarilla: Factura vence en 7 días o menos
        - Verde: Factura vence en 8-30 días
        
        Returns:
            dict: Diccionario con estadísticas de alertas generadas
        """
        hoy = timezone.now().date()
        
        # Contadores para las estadísticas
        alertas_creadas = {
            'roja': 0,
            'amarilla': 0,
            'verde': 0,
            'stock_bajo': 0,
            'facturas_vencidas': 0,
            'total': 0
        }
        
        # Obtener todos los productos activos (no eliminados)
        productos = Productos.objects.filter(
            eliminado__isnull=True,
            estado_merma='activo'  # Solo productos activos (no en merma)
        )
        
        for producto in productos:
            # ============================================================
            # PARTE 1: ALERTAS DE VENCIMIENTO
            # ============================================================
            # Solo generar alertas de vencimiento si el producto tiene stock
            if producto.cantidad > 0:
                # Calcular días hasta vencer
                dias_hasta_vencer = (producto.caducidad - hoy).days
                
                # Determinar el tipo de alerta según los días
                if dias_hasta_vencer < 0:
                    # Producto ya vencido (tratamos como roja urgente)
                    tipo = 'roja'
                    mensaje = f"{producto.nombre} YA VENCIÓ hace {abs(dias_hasta_vencer)} días"
                elif dias_hasta_vencer <= 13:
                    # Alerta ROJA: 0-13 días
                    tipo = 'roja'
                    mensaje = f"{producto.nombre} vence en {dias_hasta_vencer} días - URGENTE"
                elif dias_hasta_vencer <= 29:
                    # Alerta AMARILLA: 14-29 días
                    tipo = 'amarilla'
                    mensaje = f"{producto.nombre} vence en {dias_hasta_vencer} días - PRECAUCIÓN"
                else:
                    # Alerta VERDE: 30+ días (opcional, puedes omitir estas)
                    tipo = 'verde'
                    mensaje = f"{producto.nombre} vence en {dias_hasta_vencer} días - OK"
                
                # Verificar si ya existe una alerta activa de VENCIMIENTO para este producto
                alerta_vencimiento = Alertas.objects.filter(
                    productos=producto,
                    estado='activa',
                    mensaje__contains='vence'  # Distinguir alertas de vencimiento
                ).first()
                
                if alerta_vencimiento:
                    # Si existe, actualizar el tipo y mensaje si cambió
                    if alerta_vencimiento.tipo_alerta != tipo or alerta_vencimiento.mensaje != mensaje:
                        alerta_vencimiento.tipo_alerta = tipo
                        alerta_vencimiento.mensaje = mensaje
                        alerta_vencimiento.fecha_generada = timezone.now()
                        alerta_vencimiento.save()
                        alertas_creadas[tipo] += 1
                        alertas_creadas['total'] += 1
                else:
                    # Si no existe, crear nueva alerta de vencimiento
                    Alertas.objects.create(
                        tipo_alerta=tipo,
                        mensaje=mensaje,
                        productos=producto,
                        estado='activa'
                    )
                    alertas_creadas[tipo] += 1
                    alertas_creadas['total'] += 1
            
            # ============================================================
            # PARTE 2: ALERTAS DE STOCK BAJO
            # ============================================================
            # Determinar el stock mínimo (usar el definido o 5 por defecto)
            stock_minimo = producto.stock_minimo if producto.stock_minimo is not None else 5
            
            # Verificar si el stock está bajo
            if producto.cantidad <= stock_minimo:
                # Stock bajo - generar alerta ROJA
                tipo_stock = 'roja'
                mensaje_stock = f"{producto.nombre} - STOCK BAJO: {producto.cantidad} unidades (mínimo: {stock_minimo})"
                
                # Verificar si ya existe una alerta activa de STOCK para este producto
                alerta_stock = Alertas.objects.filter(
                    productos=producto,
                    estado='activa',
                    mensaje__contains='STOCK BAJO'  # Distinguir alertas de stock
                ).first()
                
                if alerta_stock:
                    # Si existe, actualizar el mensaje si cambió
                    if alerta_stock.mensaje != mensaje_stock:
                        alerta_stock.mensaje = mensaje_stock
                        alerta_stock.fecha_generada = timezone.now()
                        alerta_stock.save()
                        alertas_creadas['stock_bajo'] += 1
                        alertas_creadas['total'] += 1
                else:
                    # Si no existe, crear nueva alerta de stock
                    Alertas.objects.create(
                        tipo_alerta=tipo_stock,
                        mensaje=mensaje_stock,
                        productos=producto,
                        estado='activa'
                    )
                    alertas_creadas['stock_bajo'] += 1
                    alertas_creadas['total'] += 1
            else:
                # Stock normal - resolver alertas de stock activas
                alertas_stock_activas = Alertas.objects.filter(
                    productos=producto,
                    estado='activa',
                    mensaje__contains='STOCK BAJO'
                )
                for alerta in alertas_stock_activas:
                    alerta.marcar_como_resuelta()
        
        # ============================================================
        # PARTE 3: ALERTAS DE FACTURAS VENCIDAS
        # ============================================================
        # Obtener facturas pendientes de pago
        facturas_pendientes = FacturaProveedor.objects.filter(
            eliminado__isnull=True,
            estado_pago__in=['pendiente', 'parcial']  # Solo facturas no pagadas completamente
        )
        
        for factura in facturas_pendientes:
            if not factura.fecha_vencimiento:
                continue  # Si no tiene fecha de vencimiento, saltar
            
            # Calcular días hasta vencer o días vencida
            dias_para_vencer = (factura.fecha_vencimiento - hoy).days
            
            # Determinar tipo de alerta
            if dias_para_vencer < 0:
                # Factura ya vencida - ROJA urgente
                tipo = 'roja'
                mensaje = f"Factura {factura.numero_factura} de {factura.proveedor.nombre} VENCIDA hace {abs(dias_para_vencer)} días - ${factura.total_con_iva}"
            elif dias_para_vencer <= 7:
                # Factura vence en 7 días o menos - ROJA
                tipo = 'roja'
                mensaje = f"Factura {factura.numero_factura} de {factura.proveedor.nombre} vence en {dias_para_vencer} días - ${factura.total_con_iva}"
            elif dias_para_vencer <= 30:
                # Factura vence en 8-30 días - AMARILLA
                tipo = 'amarilla'
                mensaje = f"Factura {factura.numero_factura} de {factura.proveedor.nombre} vence en {dias_para_vencer} días - ${factura.total_con_iva}"
            else:
                # Factura vence en más de 30 días - VERDE (opcional, puedes omitir)
                tipo = 'verde'
                mensaje = f"Factura {factura.numero_factura} de {factura.proveedor.nombre} vence en {dias_para_vencer} días - ${factura.total_con_iva}"
            
            # Verificar si ya existe una alerta activa para esta factura
            alerta_factura = Alertas.objects.filter(
                factura_proveedor=factura,
                estado='activa'
            ).first()
            
            if alerta_factura:
                # Si existe, actualizar el tipo y mensaje si cambió
                if alerta_factura.tipo_alerta != tipo or alerta_factura.mensaje != mensaje:
                    alerta_factura.tipo_alerta = tipo
                    alerta_factura.mensaje = mensaje
                    alerta_factura.fecha_generada = timezone.now()
                    alerta_factura.save()
                    alertas_creadas[tipo] += 1
                    alertas_creadas['facturas_vencidas'] += 1
                    alertas_creadas['total'] += 1
            else:
                # Si no existe, crear nueva alerta de factura
                Alertas.objects.create(
                    tipo_alerta=tipo,
                    mensaje=mensaje,
                    factura_proveedor=factura,
                    productos=None,  # No es alerta de producto
                    estado='activa'
                )
                alertas_creadas[tipo] += 1
                alertas_creadas['facturas_vencidas'] += 1
                alertas_creadas['total'] += 1
            
            # Si la factura se pagó completamente, resolver alertas activas
            if factura.estado_pago == 'pagado':
                alertas_factura_activas = Alertas.objects.filter(
                    factura_proveedor=factura,
                    estado='activa'
                )
                for alerta in alertas_factura_activas:
                    alerta.marcar_como_resuelta()
        
        return alertas_creadas
    
    # ============================================================
    # =              CONFIGURACIÓN DEL MODELO                    =
    # ============================================================
    
    class Meta:
        managed = False              # Django NO creará esta tabla (ya existe)
        db_table = 'alertas'        # Nombre de la tabla en MySQL
        verbose_name = 'Alerta'     # Singular en el admin
        verbose_name_plural = 'Alertas'  # Plural en el admin
        ordering = ['-fecha_generada']  # Ordenar por fecha (más recientes primero)
        
        # Índices para mejorar el rendimiento
        indexes = [
            models.Index(fields=['tipo_alerta']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_generada']),
        ]

