"""
Script para debuggear el listar.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.controladores.control_rutinas import ControlRutinas
from src.persistencia.conexion_bd import ConexionBD

bd = ConexionBD.obtener_instancia()
bd.abrir_conexion()

control = ControlRutinas()
rutinas = control.listar()

print(f"\n=== Total rutinas: {len(rutinas)} ===\n")

for rutina in rutinas:
    print(f"ID: {rutina.id_rutina}")
    print(f"  Nombre: {rutina.nombre}")
    print(f"  Objetivo: {rutina.objetivo}")
    print(f"  Nivel: {rutina.nivel}")
    print(f"  Ejercicios: {len(rutina._ejercicios)}")
    print()

bd.cerrar_conexion()