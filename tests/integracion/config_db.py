"""
Configuración de base de datos para pruebas de integración.
Adaptado a la clase ConexionBD existente.
"""

import sys
from pathlib import Path

# Agregar la raíz del proyecto al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.persistencia.conexion_bd import ConexionBD


def get_connection() -> ConexionBD:
    """Obtiene una instancia de ConexionBD."""
    return ConexionBD.obtener_instancia()


def ejecutar_consulta(sql: str, params=None):
    """
    Ejecuta una consulta SELECT y retorna los resultados.
    
    Args:
        sql: Consulta SQL
        params: Parámetros para la consulta
    
    Returns:
        Lista de diccionarios con los resultados
    """
    conn = get_connection()
    conn.abrir_conexion()
    try:
        return conn.ejecutar_consulta(sql, params)
    finally:
        conn.cerrar_conexion()


def ejecutar_actualizacion(sql: str, params=None):
    """
    Ejecuta una sentencia INSERT, UPDATE o DELETE.
    
    Args:
        sql: Sentencia SQL
        params: Parámetros para la sentencia
    
    Returns:
        True si afectó al menos una fila
    """
    conn = get_connection()
    conn.abrir_conexion()
    try:
        return conn.ejecutar_actualizacion(sql, params)
    finally:
        conn.cerrar_conexion()


def ejecutar_con_retorno(sql: str, params=None):
    """
    Ejecuta una sentencia con RETURNING y retorna el valor.
    
    Args:
        sql: Sentencia SQL con RETURNING
        params: Parámetros para la sentencia
    
    Returns:
        El primer valor retornado o None
    """
    conn = get_connection()
    conn.abrir_conexion()
    try:
        with conn._obtener_cursor() as cursor:
            cursor.execute(sql, params or ())
            resultado = cursor.fetchone()
            conn._conexion.commit()
            return resultado[0] if resultado else None
    except Exception as e:
        conn._conexion.rollback()
        raise e
    finally:
        conn.cerrar_conexion()