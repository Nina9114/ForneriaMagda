"""
Script para verificar si la tabla historial_merma existe en la base de datos.
Ejecutar con: python manage.py shell < verificar_tabla_historial_merma.py
O copiar y pegar en: python manage.py shell
"""

from django.db import connection

def verificar_tabla_historial_merma():
    """Verifica si la tabla historial_merma existe en la base de datos."""
    with connection.cursor() as cursor:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'historial_merma'
        """)
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            print("✅ La tabla 'historial_merma' EXISTE en la base de datos.")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM historial_merma")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM historial_merma WHERE activo = 1")
            activos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM historial_merma WHERE activo = 0")
            inactivos = cursor.fetchone()[0]
            
            print(f"   - Total de registros: {total}")
            print(f"   - Registros activos: {activos}")
            print(f"   - Registros inactivos: {inactivos}")
        else:
            print("❌ La tabla 'historial_merma' NO EXISTE en la base de datos.")
            print("   Debes ejecutar el script SQL: sql_crear_historial_merma.sql")
            print("   En phpMyAdmin o desde la línea de comandos MySQL.")

if __name__ == '__main__':
    verificar_tabla_historial_merma()

