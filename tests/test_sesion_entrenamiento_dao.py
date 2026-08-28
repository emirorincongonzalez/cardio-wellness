import sqlite3
import pytest

from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE rutinas (
            id_rutina INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE sesiones_entrenamiento (
            id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_rutina INTEGER,
            fecha_sesion TEXT NOT NULL,
            duracion_real INTEGER NOT NULL,
            intensidad_real TEXT NOT NULL,
            calorias_quemadas REAL NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (id_rutina) REFERENCES rutinas(id_rutina)
        )
    """)

    cursor.execute("INSERT INTO rutinas (nombre) VALUES ('Rutina Cardio Intensa')")
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def dao(db_conn):
    return SesionEntrenamientoDAO(conexion_bd=db_conn)


def test_dao_guardar_sesion(dao):
    class MockSesion:
        def __init__(self):
            self.id_cliente = 1
            self.id_rutina = 1
            self.duracion_real = 45
            self.intensidad_real = "ALTA"
            self.calorias_quemadas = 350
            self.observaciones = "Completado sin pausas"

    sesion = MockSesion()
    resultado = dao.guardar(sesion)

    assert hasattr(resultado, "id_sesion")
    assert resultado.id_sesion == 1


def test_dao_listar_por_cliente_con_join(dao):
    class MockSesion:
        def __init__(self, id_cliente, id_rutina):
            self.id_cliente = id_cliente
            self.id_rutina = id_rutina
            self.duracion_real = 30
            self.intensidad_real = "MEDIA"
            self.calorias_quemadas = 200
            self.observaciones = "Buen ritmo"

    dao.guardar(MockSesion(id_cliente=1, id_rutina=1))
    dao.guardar(MockSesion(id_cliente=2, id_rutina=1))

    sesiones_cliente_1 = dao.listar_por_cliente(1)
    assert len(sesiones_cliente_1) == 1
    assert sesiones_cliente_1[0]["id_cliente"] == 1
    assert sesiones_cliente_1[0]["nombre_rutina"] == "Rutina Cardio Intensa"


def test_dao_eliminar_por_id(dao):
    class MockSesion:
        def __init__(self):
            self.id_cliente = 1
            self.id_rutina = 1
            self.duracion_real = 20
            self.intensidad_real = "BAJA"
            self.calorias_quemadas = 120
            self.observaciones = "Recuperación"

    sesion = dao.guardar(MockSesion())
    id_sesion = sesion.id_sesion

    borrado = dao.eliminar_por_id(id_sesion)
    assert borrado is True

    # Verificar que ya no existe
    sesiones = dao.listar_por_cliente(1)
    assert len(sesiones) == 0