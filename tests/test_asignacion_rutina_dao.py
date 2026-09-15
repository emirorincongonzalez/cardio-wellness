from datetime import date
from uuid import uuid4

import pytest

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
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()

    correo = f"asignacion.{uuid4().hex}@example.com"
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
                "Asignacion",
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

        cursor.execute(
            """
            INSERT INTO rutinas (
                nombre,
                descripcion,
                objetivo,
                nivel,
                duracion_semanas
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_rutina
            """,
            (
                f"Rutina test {uuid4().hex[:8]}",
                "Rutina temporal para pruebas",
                "Mantener condición",
                "INTERMEDIO",
                8,
            ),
        )
        id_rutina = cursor.fetchone()[0]

    bd._conexion.commit()

    yield {
        "id_cliente": id_cliente,
        "id_rutina": id_rutina,
    }

    try:
        with bd._conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM asignaciones_rutina
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
            cursor.execute(
                """
                DELETE FROM rutinas
                WHERE id_rutina = %s
                """,
                (id_rutina,),
            )
        bd._conexion.commit()
    except Exception:
        bd._conexion.rollback()
        raise


def crear_asignacion(
    id_cliente: int,
    id_rutina: int,
    estado: EstadoAsignacion = EstadoAsignacion.ACTIVA,
) -> AsignacionRutina:
    return AsignacionRutina(
        id_asignacion=None,
        id_cliente=id_cliente,
        id_rutina=id_rutina,
        fecha_asignacion=date.today(),
        fecha_finalizacion=None,
        estado=estado,
        observaciones="Asignación de prueba",
    )


def test_dao_asignar_y_obtener_activa(dao, datos_prueba):
    asignacion = crear_asignacion(
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
    )

    asignacion_guardada = dao.guardar(asignacion)

    assert asignacion_guardada.id_asignacion is not None

    activa = dao.buscar_activa(datos_prueba["id_cliente"])

    assert activa is not None
    assert activa.id_asignacion == asignacion_guardada.id_asignacion
    assert activa.id_cliente == datos_prueba["id_cliente"]
    assert activa.id_rutina == datos_prueba["id_rutina"]
    assert activa.estado == EstadoAsignacion.ACTIVA


def test_dao_finalizar_asignacion(dao, datos_prueba):
    asignacion = crear_asignacion(
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
    )

    asignacion_guardada = dao.guardar(asignacion)

    asignacion_guardada.estado = EstadoAsignacion.FINALIZADA
    asignacion_guardada.fecha_finalizacion = date.today()

    asignacion_actualizada = dao.actualizar(asignacion_guardada)

    assert asignacion_actualizada.estado == EstadoAsignacion.FINALIZADA
    assert asignacion_actualizada.fecha_finalizacion == date.today()
    assert dao.buscar_activa(datos_prueba["id_cliente"]) is None


def test_dao_listar_por_cliente(dao, datos_prueba):
    asignacion_1 = crear_asignacion(
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
    )
    asignacion_1 = dao.guardar(asignacion_1)

    asignacion_1.estado = EstadoAsignacion.FINALIZADA
    asignacion_1.fecha_finalizacion = date.today()
    dao.actualizar(asignacion_1)

    asignacion_2 = crear_asignacion(
        id_cliente=datos_prueba["id_cliente"],
        id_rutina=datos_prueba["id_rutina"],
        estado=EstadoAsignacion.ACTIVA,
    )
    asignacion_2 = dao.guardar(asignacion_2)

    historial = dao.listar_por_cliente(datos_prueba["id_cliente"])

    assert len(historial) == 2
    ids = {asignacion.id_asignacion for asignacion in historial}
    assert asignacion_1.id_asignacion in ids
    assert asignacion_2.id_asignacion in ids
