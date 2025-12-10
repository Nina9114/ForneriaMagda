import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Forneria.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'historial_merma'
    """)
    existe = cursor.fetchone()[0] > 0
    
    if existe:
        print("✅ La tabla 'historial_merma' EXISTE")
        cursor.execute("SELECT COUNT(*) FROM historial_merma")
        print(f"   Total registros: {cursor.fetchone()[0]}")
    else:
        print("❌ La tabla 'historial_merma' NO EXISTE")
        print("   Ejecuta: sql_crear_historial_merma.sql en phpMyAdmin")

