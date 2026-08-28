from decimal import Decimal
import sqlite3
import pytest

from src.persistencia.progreso_mensual_dao import ProgresoMensualDAO


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progreso_mensual (
            id_progreso INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            peso_registrado REAL,
            total_sesiones INTEGER NOT NULL,
            total_minutos INTEGER NOT NULL,
            total_calorias REAL NOT NULL,
            observaciones TEXT
        )
    """)
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def dao(db_conn):
    return ProgresoMensualDAO(conexion_bd=db_conn)


def test_dao_guardar_y_buscar_por_cliente(dao):
    class MockProgreso:
        def __init__(self):
            self.id_cliente = 1
            self.mes = 8
            self.anio = 2026
            self.peso_registrado = Decimal("74.5")
            self.total_sesiones = 12
            self.total_minutos = 480
            self.total_calorias = Decimal("3600.0")
            self.observaciones = "Excelente mes"

    prog = dao.guardar(MockProgreso())
    assert hasattr(prog, "id_progreso")
    assert prog.id_progreso == 1

    lista = dao.buscar_por_cliente(1)
    assert len(lista) == 1
    assert lista[0]["id_cliente"] == 1
    assert lista[0]["mes"] == 8
    assert lista[0]["total_sesiones"] == 12


def test_dao_actualizar_progreso(dao):
    class MockProgreso:
        def __init__(self):
            self.id_cliente = 2
            self.mes = 7
            self.anio = 2026
            self.peso_registrado = 80.0
            self.total_sesiones = 5
            self.total_minutos = 150
            self.total_calorias = 1200.0
            self.observaciones = "Inicio"

    prog = dao.guardar(MockProgreso())

    prog.peso_registrado = 78.5
    prog.total_sesiones = 8
    prog.observaciones = "Ajustado"

    actualizado = dao.actualizar(prog)
    assert actualizado is True

    lista = dao.buscar_por_cliente(2)
    assert lista[0]["peso_registrado"] == 78.5
    assert lista[0]["total_sesiones"] == 8