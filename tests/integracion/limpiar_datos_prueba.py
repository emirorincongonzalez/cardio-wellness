"""
Script para limpiar datos de prueba de la base de datos.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tests.integracion.config_db import get_connection


def limpiar_datos_prueba():
    """Elimina los datos creados durante las pruebas."""
    print("Limpiando datos de prueba...")
    
    conn = get_connection()
    conn.abrir_conexion()
    
    try:
        with conn._obtener_cursor() as cur:
            # Eliminar sesiones
            cur.execute("""
                DELETE FROM sesiones_entrenamiento 
                WHERE observaciones LIKE '%prueba de integración%'
            """)
            print(f"✅ {cur.rowcount} sesiones eliminadas")
            
            # Eliminar asignaciones
            cur.execute("""
                DELETE FROM asignaciones_rutina 
                WHERE observaciones LIKE '%prueba de integración%'
            """)
            print(f"✅ {cur.rowcount} asignaciones eliminadas")
            
            # Eliminar rutinas
            cur.execute("""
                DELETE FROM rutinas 
                WHERE nombre LIKE '%Test Integración%'
            """)
            print(f"✅ {cur.rowcount} rutinas eliminadas")
            
            # Eliminar clientes y usuarios de prueba
            cur.execute("""
                DELETE FROM clientes 
                WHERE id_usuario IN (
                    SELECT id_usuario FROM usuarios 
                    WHERE correo_electronico = 'test.integracion@wellness.com'
                )
            """)
            print(f"✅ {cur.rowcount} clientes eliminados")
            
            cur.execute("""
                DELETE FROM usuarios 
                WHERE correo_electronico = 'test.integracion@wellness.com'
            """)
            print(f"✅ {cur.rowcount} usuarios eliminados")
            
            conn._conexion.commit()
            print("\n✅ Datos de prueba eliminados correctamente")
        
    except Exception as e:
        conn._conexion.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.cerrar_conexion()


if __name__ == "__main__":
    limpiar_datos_prueba()