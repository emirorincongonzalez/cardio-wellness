import sqlite3
import pytest

from src.persistencia.asignacion_rutina_dao import AsignacionRutinaDAO


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rutinas (
            id_rutina INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaciones_rutinas (
            id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_rutina INTEGER NOT NULL,
            asignado_por INTEGER,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT,
            activa INTEGER DEFAULT 1,
            FOREIGN KEY (id_rutina) REFERENCES rutinas(id_rutina)
        )
    """)

    cursor.execute("INSERT INTO rutinas (nombre) VALUES ('Rutina Quema Grasa')")
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def dao(db_conn):
    return AsignacionRutinaDAO(conexion_bd=db_conn)


def test_dao_asignar_y_obtener_activa(dao):
    asignacion = dao.asignar(id_cliente=1, id_rutina=1, asignado_por=5)
    assert asignacion["id_asignacion"] == 1
    assert asignacion["activa"] == 1

    activa = dao.obtener_activa_por_cliente(1)
    assert activa is not None
    assert activa["id_cliente"] == 1
    assert activa["nombre_rutina"] == "Rutina Quema Grasa"


def test_dao_finalizar_asignacion(dao):
    dao.asignar(id_cliente=2, id_rutina=1)
    activa = dao.obtener_activa_por_cliente(2)
    id_asig = activa["id_asignacion"]

    finalizado = dao.finalizar_asignacion(id_asig)
    assert finalizado is True

    # Ya no debe tener activa
    activa_post = dao.obtener_activa_por_cliente(2)
    assert activa_post is None


def test_dao_listar_por_cliente(dao):
    dao.asignar(id_cliente=3, id_rutina=1)
    dao.asignar(id_cliente=3, id_rutina=1)

    lista = dao.listar_por_cliente(3)
    assert len(lista) == 2