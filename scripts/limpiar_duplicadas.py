"""
Script para limpiar rutinas duplicadas.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persistencia.conexion_bd import ConexionBD

bd = ConexionBD.obtener_instancia()
bd.abrir_conexion()

with bd._conexion.cursor() as cursor:
    # Mantener solo las últimas 2 rutinas (una de cada tipo)
    cursor.execute("""
        DELETE FROM rutina_ejercicios 
        WHERE id_rutina NOT IN (
            SELECT id_rutina FROM (
                SELECT DISTINCT ON (nombre) id_rutina
                FROM rutinas
                ORDER BY nombre, id_rutina DESC
            ) AS unicas
        )
    """)
    
    cursor.execute("""
        DELETE FROM rutinas 
        WHERE id_rutina NOT IN (
            SELECT id_rutina FROM (
                SELECT DISTINCT ON (nombre) id_rutina
                FROM rutinas
                ORDER BY nombre, id_rutina DESC
            ) AS unicas
        )
    """)
    
    eliminadas = cursor.rowcount
    bd._conexion.commit()
    
    print(f"✓ Rutinas duplicadas eliminadas: {eliminadas}")
    
    # Verificar cuántas quedan
    cursor.execute("SELECT id_rutina, nombre FROM rutinas ORDER BY id_rutina")
    print("\nRutinas restantes:")
    for fila in cursor.fetchall():
        print(f"  - ID {fila[0]}: {fila[1]}")

bd.cerrar_conexion()