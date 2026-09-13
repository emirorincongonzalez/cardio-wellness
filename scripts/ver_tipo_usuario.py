"""
Script para ver valores existentes de tipo_usuario.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persistencia.conexion_bd import ConexionBD

bd = ConexionBD.obtener_instancia()
bd.abrir_conexion()

with bd._conexion.cursor() as cursor:
    # Ver valores existentes
    cursor.execute("SELECT DISTINCT tipo_usuario FROM usuarios")
    
    print("\n=== Valores existentes de tipo_usuario ===")
    for valor in cursor.fetchall():
        print(f"- '{valor[0]}'")

bd.cerrar_conexion()