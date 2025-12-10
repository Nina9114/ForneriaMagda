"""
Script de prueba para verificar que se crean registros en historial_merma
Ejecutar con: python manage.py shell < test_crear_merma.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Forneria.settings')
django.setup()

from ventas.models import Productos, HistorialMerma
from decimal import Decimal
from django.utils import timezone

# Buscar un producto activo para probar
producto = Productos.objects.filter(eliminado__isnull=True, estado_merma='activo').first()

if producto:
    print(f"Probando con producto: {producto.nombre} (ID: {producto.id})")
    print(f"Cantidad actual: {producto.cantidad}")
    
    cantidad_original = producto.cantidad if producto.cantidad else Decimal('0')
    cantidad_merma_historial = cantidad_original if cantidad_original > 0 else Decimal('0.001')
    
    try:
        registro = HistorialMerma.objects.create(
            producto=producto,
            cantidad_merma=cantidad_merma_historial,
            motivo_merma="Prueba de creación de registro",
            fecha_merma=timezone.now(),
            activo=True
        )
        print(f"✅ Registro creado exitosamente: ID {registro.id}")
        print(f"   Cantidad merma: {registro.cantidad_merma}")
        print(f"   Activo: {registro.activo}")
        
        # Verificar que existe en la BD
        existe = HistorialMerma.objects.filter(id=registro.id).exists()
        print(f"   Verificado en BD: {'✅ SÍ' if existe else '❌ NO'}")
        
        # Limpiar: eliminar el registro de prueba
        registro.delete()
        print("\n🧹 Registro de prueba eliminado")
        
    except Exception as e:
        print(f"❌ Error al crear registro: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No se encontró ningún producto activo para probar")

