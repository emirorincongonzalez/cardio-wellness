from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from src.modelos.progreso_mensual import ProgresoMensual
from src.persistencia.conexion_bd import ConexionBD
from src.persistencia.progreso_mensual_dao import ProgresoMensualDAO
from src.servicios.gestor_seguridad import GestorSeguridad


@pytest.fixture
def dao():
    return ProgresoMensualDAO()


@pytest.fixture
def id_cliente_prueba():
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()

    correo = f"progreso.{uuid4().hex}@example.com"
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
                "Progreso",
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
                DELETE FROM progreso_mensual
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


def crear_progreso(
    id_cliente: int,
    mes: date,
    peso: float,
) -> ProgresoMensual:
    return ProgresoMensual(
        id_progreso=None,
        id_cliente=id_cliente,
        mes=mes,
        peso=peso,
        sesiones_completadas=0,
        sesiones_planificadas=12,
        porcentaje_cumplimiento=0.0,
    )


def test_dao_guardar_y_buscar_por_cliente(dao, id_cliente_prueba):
    progreso = crear_progreso(
        id_cliente=id_cliente_prueba,
        mes=date(2026, 8, 1),
        peso=72.5,
    )

    guardado = dao.guardar(progreso)

    assert guardado.id_progreso is not None

    historial = dao.buscar_por_cliente(id_cliente_prueba)

    assert len(historial) == 1
    assert historial[0].id_progreso == guardado.id_progreso
    assert historial[0].id_cliente == id_cliente_prueba
    assert historial[0].mes == date(2026, 8, 1)
    assert historial[0].peso == Decimal("72.5")


def test_dao_actualizar_progreso(dao, id_cliente_prueba):
    progreso = crear_progreso(
        id_cliente=id_cliente_prueba,
        mes=date(2026, 9, 1),
        peso=70.0,
    )

    guardado = dao.guardar(progreso)

    guardado.peso = 69.5
    guardado.sesiones_completadas = 8
    guardado.sesiones_planificadas = 10
    guardado.actualizar_progreso()

    actualizado = dao.actualizar(guardado)

    assert actualizado.peso == Decimal("69.5")
    assert actualizado.sesiones_completadas == 8
    assert actualizado.sesiones_planificadas == 10
    assert actualizado.porcentaje_cumplimiento == 80.0

    encontrado = dao.buscar_por_id(guardado.id_progreso)

    assert encontrado is not None
    assert encontrado.peso == Decimal("69.5")
    assert encontrado.sesiones_completadas == 8
    assert encontrado.sesiones_planificadas == 10
    assert encontrado.porcentaje_cumplimiento == 80.0
