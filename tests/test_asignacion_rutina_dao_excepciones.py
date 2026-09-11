"""
Tests para cubrir excepciones y casos edge en AsignacionRutinaDAO.
"""

import pytest
from datetime import date
from uuid import uuid4

from src.modelos.asignacion_rutina import AsignacionRutina
from src.modelos.enums import EstadoAsignacion
from src.persistencia.asignacion_rutina_dao import AsignacionRutinaDAO
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


@pytest.fixture
def dao():
    return AsignacionRutinaDAO()


@pytest.fixture
def datos_prueba():
    """Crea cliente y rutina reales para pruebas."""
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()

    correo = f"test.excepcion.{uuid4().hex}@example.com"
    contrasenia_hash = GestorSeguridad.generar_hash("Clave123")

    with bd._conexion.cursor() as cursor:
        # Crear usuario y cliente
        cursor.execute(
            """
            INSERT INTO usuarios (
                nombre, apellido, correo_electronico, "contraseña_hash", edad, tipo_usuario
            )
            VALUES (%s, %s, %s, %s, %s, 'cliente')
            RETURNING id_usuario
            """,
            ("Test", "Excepcion", correo, contrasenia_hash, 30),
        )
        id_cliente = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO clientes (id_usuario, peso, altura, objetivo)
            VALUES (%s, %s, %s, %s)
            """,
            (id_cliente, 70.0, 1.75, "Pruebas excepciones"),
        )

        # Crear rutina
        cursor.execute(
            """
            INSERT INTO rutinas (nombre, descripcion, objetivo, nivel, duracion_semanas)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_rutina
            """,
            (f"Rutina test {uuid4().hex[:8]}", "Test", "Test", "INTERMEDIO", 8),
        )
        id_rutina = cursor.fetchone()[0]

    bd._conexion.commit()
    yield {"id_cliente": id_cliente, "id_rutina": id_rutina}

    # Cleanup
    try:
        with bd._conexion.cursor() as cursor:
            cursor.execute("DELETE FROM asignaciones_rutina WHERE id_cliente = %s", (id_cliente,))
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_cliente,))
            cursor.execute("DELETE FROM rutinas WHERE id_rutina = %s", (id_rutina,))
        bd._conexion.commit()
    except Exception:
        bd._conexion.rollback()
        raise


def test_dao_guardar_con_cliente_inexistente(dao):
    """Prueba que guarda con cliente que no existe lanza ValueError."""
    asignacion = AsignacionRutina(
        id_asignacion=None,
        id_cliente=999999,  # Cliente inexistente
        id_rutina=1,
        fecha_asignacion=date.today(),
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Test",
    )

    with pytest.raises(ValueError, match="El cliente o la rutina no existen"):
        dao.guardar(asignacion)


def test_dao_guardar_con_rutina_inexistente(dao, datos_prueba):
    """Prueba que guarda con rutina que no existe lanza ValueError."""
    asignacion = AsignacionRutina(
        id_asignacion=None,
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=999999,  # Rutina inexistente
        fecha_asignacion=date.today(),
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Test",
    )

    with pytest.raises(ValueError, match="El cliente o la rutina no existen"):
        dao.guardar(asignacion)


def test_dao_guardar_duplicado_activa(dao, datos_prueba):
    """Prueba que guarda segunda asignación con misma rutina funciona (no hay restricción de unicidad)."""
    # Crear primera asignación activa
    asignacion1 = AsignacionRutina(
        id_asignacion=None,
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
        fecha_asignacion=date.today(),
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Primera",
    )
    guardada1 = dao.guardar(asignacion1)
    assert guardada1.id_asignacion is not None

    # Crear segunda asignación activa (debería permitirlo, no hay restricción de unicidad)
    asignacion2 = AsignacionRutina(
        id_asignacion=None,
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
        fecha_asignacion=date.today(),
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Segunda",
    )
    guardada2 = dao.guardar(asignacion2)
    assert guardada2.id_asignacion is not None
    assert guardada2.id_asignacion != guardada1.id_asignacion

def test_dao_buscar_por_id_inexistente(dao):
    """Prueba que buscar ID inexistente retorna None."""
    resultado = dao.buscar_por_id(999999)
    assert resultado is None


def test_dao_actualizar_sin_id(dao, datos_prueba):
    """Prueba que actualizar sin ID lanza ValueError."""
    asignacion = AsignacionRutina(
        id_asignacion=None,  # Sin ID
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
        fecha_asignacion=date.today(),
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Test",
    )

    with pytest.raises(ValueError, match="La asignación debe tener un ID"):
        dao.actualizar(asignacion)


def test_dao_actualizar_id_inexistente(dao):
    """Prueba que actualizar ID inexistente lanza ValueError."""
    asignacion = AsignacionRutina(
        id_asignacion=999999,  # ID inexistente
        id_cliente=1,
        id_rutina=1,
        fecha_asignacion=date.today(),
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Test",
    )

    with pytest.raises(ValueError, match="No se encontró la asignación"):
        dao.actualizar(asignacion)


def test_dao_eliminar_id_inexistente(dao):
    """Prueba que eliminar ID inexistente retorna False."""
    resultado = dao.eliminar_por_id(999999)
    assert resultado is False


def test_dao_listar_cliente_sin_asignaciones(dao, datos_prueba):
    """Prueba que listar cliente sin asignaciones retorna lista vacía."""
    resultado = dao.listar_por_cliente(datos_prueba["id_cliente"])
    assert isinstance(resultado, list)
    assert len(resultado) == 0


def test_dao_buscar_activa_sin_resultado(dao, datos_prueba):
    """Prueba que buscar activa sin resultado retorna None."""
    resultado = dao.buscar_activa(datos_prueba["id_cliente"])
    assert resultado is None