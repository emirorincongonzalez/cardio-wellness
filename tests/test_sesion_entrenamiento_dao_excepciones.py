"""
Tests para cubrir excepciones y casos edge en SesionEntrenamientoDAO.
"""

import pytest
from datetime import date
from uuid import uuid4

from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import SesionEntrenamiento
from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


@pytest.fixture
def dao():
    return SesionEntrenamientoDAO()


@pytest.fixture
def datos_prueba():
    """Crea cliente real para pruebas."""
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()

    correo = f"test.sesion.{uuid4().hex}@example.com"
    contrasenia_hash = GestorSeguridad.generar_hash("Clave123")

    with bd._conexion.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO usuarios (
                nombre, apellido, correo_electronico, "contraseña_hash", edad, tipo_usuario
            )
            VALUES (%s, %s, %s, %s, %s, 'cliente')
            RETURNING id_usuario
            """,
            ("Test", "Sesion", correo, contrasenia_hash, 30),
        )
        id_cliente = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO clientes (id_usuario, peso, altura, objetivo)
            VALUES (%s, %s, %s, %s)
            """,
            (id_cliente, 70.0, 1.75, "Pruebas excepciones"),
        )

    bd._conexion.commit()
    yield {"id_cliente": id_cliente}

    try:
        with bd._conexion.cursor() as cursor:
            cursor.execute("DELETE FROM sesiones_entrenamiento WHERE id_cliente = %s", (id_cliente,))
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_cliente,))
        bd._conexion.commit()
    except Exception:
        bd._conexion.rollback()
        raise


def test_dao_guardar_con_cliente_inexistente(dao):
    """Prueba que guarda con cliente inexistente lanza ValueError."""
    sesion = SesionEntrenamiento(
        id_sesion=None,
        id_cliente=999999,  # Cliente inexistente
        fecha=date(2026, 9, 11),
        duracion_real=30,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=200.0,
        observaciones="Test",
        completada=True,
    )

    with pytest.raises(ValueError, match="El cliente referenciado no existe"):
        dao.guardar(sesion)


def test_dao_buscar_por_id_inexistente(dao):
    """Prueba que buscar ID inexistente retorna None."""
    resultado = dao.buscar_por_id(999999)
    assert resultado is None


def test_dao_actualizar_sin_id(dao, datos_prueba):
    """Prueba que actualizar sin ID lanza ValueError."""
    sesion = SesionEntrenamiento(
        id_sesion=None,  # Sin ID
        id_cliente=datos_prueba["id_cliente"],
        fecha=date(2026, 9, 11),
        duracion_real=30,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=200.0,
        observaciones="Test",
        completada=True,
    )

    with pytest.raises(ValueError, match="La sesión debe tener un ID"):
        dao.actualizar(sesion)


def test_dao_actualizar_id_inexistente(dao):
    """Prueba que actualizar ID inexistente lanza ValueError."""
    sesion = SesionEntrenamiento(
        id_sesion=999999,  # ID inexistente
        id_cliente=1,
        fecha=date(2026, 9, 11),
        duracion_real=30,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=200.0,
        observaciones="Test",
        completada=True,
    )

    with pytest.raises(ValueError, match="No se encontró la sesión"):
        dao.actualizar(sesion)


def test_dao_eliminar_id_inexistente(dao):
    """Prueba que eliminar ID inexistente retorna False."""
    resultado = dao.eliminar_por_id(999999)
    assert resultado is False


def test_dao_listar_cliente_sin_sesiones(dao, datos_prueba):
    """Prueba que listar cliente sin sesiones retorna lista vacía."""
    resultado = dao.listar_por_cliente(datos_prueba["id_cliente"])
    assert isinstance(resultado, list)
    assert len(resultado) == 0