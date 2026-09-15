from datetime import date
from uuid import uuid4

import pytest

from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import SesionEntrenamiento
from src.persistencia.conexion_bd import ConexionBD
from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO
from src.servicios.gestor_seguridad import GestorSeguridad


@pytest.fixture
def dao():
    return SesionEntrenamientoDAO()


@pytest.fixture
def id_cliente_prueba():
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()

    correo = f"sesion.{uuid4().hex}@example.com"
    contrasenia_hash = GestorSeguridad.generar_hash("Clave123!")

    with bd._conexion.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO usuarios (
                nombre,
                apellido,
                correo_electronico,
                "contraseña_hash",
                edad,
                tipo_usuario
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_usuario
            """,
            (
                "Test",
                "Sesion",
                correo,
                contrasenia_hash,
                30,
                "cliente",
            ),
        )
        id_cliente = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO clientes (
                id_usuario,
                peso,
                altura,
                objetivo
            )
            VALUES (%s, %s, %s, %s)
            """,
            (id_cliente, 70.0, 1.75, "Mantener condición"),
        )

    bd._conexion.commit()

    yield id_cliente

    try:
        with bd._conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM sesiones_entrenamiento
                WHERE id_cliente = %s
                """,
                (id_cliente,),
            )
            cursor.execute(
                """
                DELETE FROM usuarios
                WHERE id_usuario = %s
                """,
                (id_cliente,),
            )
        bd._conexion.commit()
    except Exception:
        bd._conexion.rollback()
        raise


def crear_sesion(
    id_cliente: int,
    duracion: int = 45,
    intensidad: Intensidad = Intensidad.MEDIA,
) -> SesionEntrenamiento:
    return SesionEntrenamiento(
        id_sesion=None,
        id_cliente=id_cliente,
        fecha=date.today(),
        duracion_real=duracion,
        intensidad_real=intensidad,
        calorias_quemadas=300,
        observaciones="Sesión de prueba",
        completada=True,
    )


def test_dao_guardar_sesion(dao, id_cliente_prueba):
    sesion = crear_sesion(id_cliente=id_cliente_prueba)

    guardada = dao.guardar(sesion)

    assert guardada.id_sesion is not None
    assert guardada.id_cliente == id_cliente_prueba
    assert guardada.duracion_real == 45
    assert guardada.intensidad_real == Intensidad.MEDIA


def test_dao_listar_por_cliente_con_join(dao, id_cliente_prueba):
    sesion_1 = crear_sesion(
        id_cliente=id_cliente_prueba,
        duracion=30,
        intensidad=Intensidad.BAJA,
    )
    sesion_2 = crear_sesion(
        id_cliente=id_cliente_prueba,
        duracion=60,
        intensidad=Intensidad.ALTA,
    )

    dao.guardar(sesion_1)
    dao.guardar(sesion_2)

    sesiones = dao.listar_por_cliente(id_cliente_prueba)

    assert len(sesiones) == 2
    assert {sesion.duracion_real for sesion in sesiones} == {30, 60}
    assert {sesion.intensidad_real for sesion in sesiones} == {
        Intensidad.BAJA,
        Intensidad.ALTA,
    }


def test_dao_eliminar_por_id(dao, id_cliente_prueba):
    sesion = crear_sesion(id_cliente=id_cliente_prueba)
    guardada = dao.guardar(sesion)

    eliminado = dao.eliminar_por_id(guardada.id_sesion)

    assert eliminado is True
    assert dao.buscar_por_id(guardada.id_sesion) is None
