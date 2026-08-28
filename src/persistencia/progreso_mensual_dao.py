from datetime import date
from decimal import Decimal
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


class ProgresoMensualDAO:

    def __init__(self, conexion_bd=None):
        self.conexion_bd = conexion_bd if conexion_bd is not None else _obtener_conexion_default()

    def _get_connection(self):
        if hasattr(self.conexion_bd, "obtener_conexion"):
            return self.conexion_bd.obtener_conexion()
        return self.conexion_bd

    def guardar(self, progreso):
        id_cliente = getattr(progreso, "id_cliente", None) or getattr(progreso, "id_usuario", None)
        mes = getattr(progreso, "mes", None) or date.today().month
        anio = getattr(progreso, "anio", None) or getattr(progreso, "año", None) or date.today().year
        peso_registrado = getattr(progreso, "peso_registrado", None) or getattr(progreso, "peso", None) or Decimal("0.0")
        total_sesiones = getattr(progreso, "total_sesiones", None) or getattr(progreso, "sesiones_completadas", 0)
        total_minutos = getattr(progreso, "total_minutos", None) or getattr(progreso, "minutos_entrenados", 0)
        total_calorias = getattr(progreso, "total_calorias", None) or getattr(progreso, "calorias_quemadas", Decimal("0.0"))
        observaciones = getattr(progreso, "observaciones", "") or ""

        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO progreso_mensual (
                id_cliente, mes, anio, peso_registrado, total_sesiones,
                total_minutos, total_calorias, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            sql,
            (
                id_cliente,
                mes,
                anio,
                float(peso_registrado),
                total_sesiones,
                total_minutos,
                float(total_calorias),
                observaciones,
            ),
        )
        conn.commit()

        id_generado = cursor.lastrowid
        try:
            setattr(progreso, "id_progreso", id_generado)
        except Exception:
            pass

        return progreso

    def actualizar(self, progreso):
        id_progreso = getattr(progreso, "id_progreso", None) or getattr(progreso, "id", None)
        peso_registrado = getattr(progreso, "peso_registrado", None) or getattr(progreso, "peso", None)
        total_sesiones = getattr(progreso, "total_sesiones", None) or getattr(progreso, "sesiones_completadas", 0)
        total_minutos = getattr(progreso, "total_minutos", None) or getattr(progreso, "minutos_entrenados", 0)
        total_calorias = getattr(progreso, "total_calorias", None) or getattr(progreso, "calorias_quemadas", Decimal("0.0"))
        observaciones = getattr(progreso, "observaciones", "") or ""

        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE progreso_mensual
            SET peso_registrado = ?, total_sesiones = ?, total_minutos = ?,
                total_calorias = ?, observaciones = ?
            WHERE id_progreso = ?
        """
        cursor.execute(
            sql,
            (
                float(peso_registrado) if peso_registrado is not None else None,
                total_sesiones,
                total_minutos,
                float(total_calorias) if total_calorias is not None else None,
                observaciones,
                id_progreso,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def buscar_por_cliente(self, id_cliente):
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                id_progreso, id_cliente, mes, anio, peso_registrado,
                total_sesiones, total_minutos, total_calorias, observaciones
            FROM progreso_mensual
            WHERE id_cliente = ?
            ORDER BY anio DESC, mes DESC, id_progreso DESC
        """
        cursor.execute(sql, (id_cliente,))
        filas = cursor.fetchall()

        columnas = [
            "id_progreso", "id_cliente", "mes", "anio", "peso_registrado",
            "total_sesiones", "total_minutos", "total_calorias", "observaciones",
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

    # Alias
    def listar_por_cliente(self, id_cliente):
        return self.buscar_por_cliente(id_cliente)