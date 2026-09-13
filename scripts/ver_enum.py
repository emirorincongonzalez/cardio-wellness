"""
Script para ver valores del ENUM tipo_usuario.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persistencia.conexion_bd import ConexionBD

bd = ConexionBD.obtener_instancia()
bd.abrir_conexion()

with bd._conexion.cursor() as cursor:
    cursor.execute("""
        SELECT e.enumlabel
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid  
        WHERE t.typname = 'tipo_usuario_enum'
        ORDER BY e.enumsortorder
    """)
    
    print("\n=== Valores válidos para tipo_usuario ===")
    for valor in cursor.fetchall():
        print(f"- {valor[0]}")

bd.cerrar_conexion()