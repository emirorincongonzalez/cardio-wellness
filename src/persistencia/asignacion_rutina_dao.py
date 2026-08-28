from datetime import date
import importlib
from pathlib import Path
import sqlite3


def _obtener_conexion_default():
    try:
        modulo = importlib.import_module("src.persistencia.conexion")
        if hasattr(modulo, "ConexionBD"):
            return getattr(modulo, "ConexionBD")()
    except Exception:
        pass
    Path("database").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect("database/cardio.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class AsignacionRutinaDAO:

    def __init__(self, conexion_bd=None):
        self.conexion_bd = conexion_bd if conexion_bd is not None else _obtener_conexion_default()

    def _get_connection(self):
        if hasattr(self.conexion_bd, "obtener_conexion"):
            return self.conexion_bd.obtener_conexion()
        return self.conexion_bd

    def asignar(self, id_cliente, id_rutina, asignado_por=None, fecha_inicio=None):
        conn = self._get_connection()
        cursor = conn.cursor()

        fecha_val = str(fecha_inicio or date.today())
        sql = """
            INSERT INTO asignaciones_rutinas (
                id_cliente, id_rutina, asignado_por, fecha_inicio, activa
            ) VALUES (?, ?, ?, ?, 1)
        """
        cursor.execute(sql, (id_cliente, id_rutina, asignado_por, fecha_val))
        conn.commit()

        id_asignacion = cursor.lastrowid
        return {
            "id_asignacion": id_asignacion,
            "id_cliente": id_cliente,
            "id_rutina": id_rutina,
            "asignado_por": asignado_por,
            "fecha_inicio": fecha_val,
            "activa": 1,
        }

    def obtener_activa_por_cliente(self, id_cliente):
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                a.id_asignacion, a.id_cliente, a.id_rutina, a.asignado_por,
                a.fecha_inicio, a.fecha_fin, a.activa, r.nombre AS nombre_rutina
            FROM asignaciones_rutinas a
            LEFT JOIN rutinas r ON a.id_rutina = r.id_rutina
            WHERE a.id_cliente = ? AND a.activa = 1
            LIMIT 1
        """
        cursor.execute(sql, (id_cliente,))
        fila = cursor.fetchone()
        if not fila:
            return None

        if isinstance(fila, sqlite3.Row):
            return dict(fila)
        if isinstance(fila, dict):
            return fila

        columnas = [
            "id_asignacion", "id_cliente", "id_rutina", "asignado_por",
            "fecha_inicio", "fecha_fin", "activa", "nombre_rutina",
        ]
        return dict(zip(columnas, fila))

    def finalizar_asignacion(self, id_asignacion, fecha_fin=None):
        conn = self._get_connection()
        cursor = conn.cursor()

        fecha_val = str(fecha_fin or date.today())
        sql = """
            UPDATE asignaciones_rutinas
            SET activa = 0, fecha_fin = ?
            WHERE id_asignacion = ?
        """
        cursor.execute(sql, (fecha_val, id_asignacion))
        conn.commit()
        return cursor.rowcount > 0

    def listar_por_cliente(self, id_cliente):
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                a.id_asignacion, a.id_cliente, a.id_rutina, a.asignado_por,
                a.fecha_inicio, a.fecha_fin, a.activa, r.nombre AS nombre_rutina
            FROM asignaciones_rutinas a
            LEFT JOIN rutinas r ON a.id_rutina = r.id_rutina
            WHERE a.id_cliente = ?
            ORDER BY a.id_asignacion DESC
        """
        cursor.execute(sql, (id_cliente,))
        filas = cursor.fetchall()

        columnas = [
            "id_asignacion", "id_cliente", "id_rutina", "asignado_por",
            "fecha_inicio", "fecha_fin", "activa", "nombre_rutina",
        ]

        resultado = []
        for fila in filas:
            if isinstance(fila, sqlite3.Row):
                resultado.append(dict(fila))
            elif isinstance(fila, dict):
                resultado.append(fila)
            else:
                resultado.append(dict(zip(columnas, fila)))

        return resultado