"""
Prueba simple con 1 usuario para depurar.
"""

import sys
from pathlib import Path
from datetime import datetime
import random
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from dotenv import load_dotenv


def test_1_usuario():
    """Prueba con 1 solo usuario."""
    
    print("=" * 70)
    print("PRUEBA SIMPLE - 1 USUARIO")
    print("=" * 70)
    
    load_dotenv()
    
    try:
        # Crear conexión
        print("\n📡 Conectando a la base de datos...")
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'cardio_wellness'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        print("✅ Conexión exitosa")
        
        cursor = conn.cursor()
        
        # 1. Listar clientes
        print("\n1️⃣  Listando clientes...")
        cursor.execute("SELECT id_cliente, nombre, email FROM clientes")
        clientes = cursor.fetchall()
        print(f"   ✅ {len(clientes)} clientes encontrados")
        
        # 2. Listar rutinas
        print("\n2️⃣  Listando rutinas...")
        cursor.execute("SELECT id_rutina, nombre FROM rutinas")
        rutinas = cursor.fetchall()
        print(f"   ✅ {len(rutinas)} rutinas encontradas")
        
        # 3. Registrar sesión
        print("\n3️⃣  Registrando sesión...")
        if clientes:
            cliente = random.choice(clientes)
            print(f"   📝 Cliente: {cliente[1]}")
            try:
                cursor.execute("""
                    INSERT INTO sesiones_entrenamiento 
                    (id_cliente, fecha, duracion, intensidad, notas)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    cliente[0],
                    datetime.now(),
                    45,
                    'MEDIA',
                    f'Sesión prueba 1 usuario - {datetime.now()}'
                ))
                conn.commit()
                print("   ✅ Sesión registrada exitosamente")
            except Exception as e:
                conn.rollback()
                print(f"   ❌ Error al registrar: {e}")
        else:
            print("   ⚠️  No hay clientes")
        
        # 4. Ver progreso
        print("\n4️⃣  Verificando progreso...")
        if clientes:
            cliente = random.choice(clientes)
            try:
                cursor.execute("""
                    SELECT * FROM progreso_mensual 
                    WHERE id_cliente = %s 
                    ORDER BY mes DESC 
                    LIMIT 1
                """, (cliente[0],))
                progreso = cursor.fetchone()
                if progreso:
                    print(f"   ✅ Progreso encontrado: {progreso}")
                else:
                    print("   ⚠️  No hay progreso mensual")
            except Exception as e:
                print(f"   ❌ Error al ver progreso: {e}")
        else:
            print("   ⚠️  No hay clientes")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_1_usuario()