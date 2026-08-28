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


class SesionEntrenamientoDAO:

    def __init__(self, conexion_bd=None):
        self.conexion_bd = conexion_bd if conexion_bd is not None else _obtener_conexion_default()

    def _get_connection(self):
        if hasattr(self.conexion_bd, "obtener_conexion"):
            return self.conexion_bd.obtener_conexion()
        return self.conexion_bd

    def guardar(self, sesion):
        id_cliente = getattr(sesion, "id_cliente", None) or getattr(sesion, "id_usuario", None)
        id_rutina = getattr(sesion, "id_rutina", None)
        fecha_sesion = getattr(sesion, "fecha_sesion", None) or getattr(sesion, "fecha", None) or date.today()
        duracion_real = getattr(sesion, "duracion_real", None) or getattr(sesion, "duracion_minutos", 0)
        intensidad_real = getattr(sesion, "intensidad_real", None) or getattr(sesion, "intensidad", "MEDIA")
        calorias_quemadas = getattr(sesion, "calorias_quemadas", None) or getattr(sesion, "calorias", 0)
        observaciones = getattr(sesion, "observaciones", "") or ""

        if hasattr(intensidad_real, "name"):
            intensidad_real = intensidad_real.name
        elif hasattr(intensidad_real, "value"):
            intensidad_real = str(intensidad_real.value)

        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO sesiones_entrenamiento (
                id_cliente, id_rutina, fecha_sesion, duracion_real,
                intensidad_real, calorias_quemadas, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            sql,
            (
                id_cliente,
                id_rutina,
                str(fecha_sesion),
                duracion_real,
                str(intensidad_real),
                calorias_quemadas,
                observaciones,
            ),
        )
        conn.commit()

        id_generado = cursor.lastrowid
        try:
            setattr(sesion, "id_sesion", id_generado)
        except Exception:
            pass

        return sesion

    def listar_por_cliente(self, id_cliente):
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                s.id_sesion, s.id_cliente, s.id_rutina, s.fecha_sesion,
                s.duracion_real, s.intensidad_real, s.calorias_quemadas,
                s.observaciones, r.nombre AS nombre_rutina
            FROM sesiones_entrenamiento s
            LEFT JOIN rutinas r ON s.id_rutina = r.id_rutina
            WHERE s.id_cliente = ?
            ORDER BY s.fecha_sesion DESC, s.id_sesion DESC
        """
        cursor.execute(sql, (id_cliente,))
        filas = cursor.fetchall()

        columnas = [
            "id_sesion", "id_cliente", "id_rutina", "fecha_sesion",
            "duracion_real", "intensidad_real", "calorias_quemadas",
            "observaciones", "nombre_rutina",
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

    def eliminar_por_id(self, id_sesion):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sesiones_entrenamiento WHERE id_sesion = ?", (id_sesion,))
        conn.commit()
        return cursor.rowcount > 0