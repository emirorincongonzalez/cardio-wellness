from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

import src.persistencia.progreso_mensual_dao as modulo_dao

from src.modelos.progreso_mensual import ProgresoMensual
from src.persistencia.progreso_mensual_dao import (
    ProgresoMensualDAO,
)


class IntegrityErrorPrueba(Exception):
    """
    Error simulado con pgcode configurable.
    """

    def __init__(self, mensaje, pgcode):
        super().__init__(mensaje)
        self.pgcode = pgcode


@pytest.fixture
def bd_mock():
    bd = MagicMock()

    conexion = MagicMock()
    conexion.closed = False

    bd._conexion = conexion

    return bd


@pytest.fixture
def dao(bd_mock):
    with patch.object(
        modulo_dao.ConexionBD,
        "obtener_instancia",
        return_value=bd_mock,
    ):
        return ProgresoMensualDAO()


def crear_cursor(
    fila=None,
    filas=None,
    rowcount=1,
):
    cursor = MagicMock()
    cursor.fetchone.return_value = fila
    cursor.fetchall.return_value = filas or []
    cursor.rowcount = rowcount
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = False

    return cursor


def configurar_cursor(dao, cursor):
    dao._bd._conexion.cursor.return_value = cursor


def crear_fila(
    id_progreso=1,
    id_cliente=10,
    mes=date(2026, 1, 1),
    peso=Decimal("70.50"),
    completadas=4,
    planificadas=5,
    porcentaje=Decimal("80.00"),
):
    return {
        "id_progreso": id_progreso,
        "id_cliente": id_cliente,
        "mes": mes,
        "peso": peso,
        "sesiones_completadas": completadas,
        "sesiones_planificadas": planificadas,
        "porcentaje_cumplimiento": porcentaje,
    }


def crear_progreso(
    id_progreso=None,
    id_cliente=10,
    mes=date(2026, 1, 15),
    peso=70.5,
    completadas=4,
    planificadas=5,
):
    return ProgresoMensual(
        id_progreso=id_progreso,
        id_cliente=id_cliente,
        mes=mes,
        peso=peso,
        sesiones_completadas=completadas,
        sesiones_planificadas=planificadas,
        porcentaje_cumplimiento=80,
    )


def test_guardar_exitoso_normaliza_mes_y_calcula_porcentaje(
    dao,
):
    fila = crear_fila()
    cursor = crear_cursor(fila=fila)

    configurar_cursor(dao, cursor)

    resultado = dao.guardar(crear_progreso())

    assert resultado.id_progreso == 1
    assert resultado.mes == date(2026, 1, 1)
    assert resultado.peso == Decimal("70.50")

    parametros = cursor.execute.call_args.args[1]

    assert parametros == (
        10,
        date(2026, 1, 1),
        Decimal("70.50"),
        4,
        5,
        Decimal("80.00"),
    )

    dao._bd._conexion.commit.assert_called_once()


def test_guardar_rechaza_fila_none(
    dao,
):
    cursor = crear_cursor(fila=None)
    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="No se pudo recuperar el progreso",
    ):
        dao.guardar(crear_progreso())

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        ("23505", "Ya existe un registro de progreso"),
        ("23503", "cliente referenciado no existe"),
        ("99999", "No se pudo guardar el progreso"),
    ],
)
def test_guardar_maneja_integrity_error(
    dao,
    pgcode,
    mensaje,
    monkeypatch,
):
    monkeypatch.setattr(
        modulo_dao,
        "IntegrityError",
        IntegrityErrorPrueba,
    )

    cursor = crear_cursor()
    cursor.execute.side_effect = IntegrityErrorPrueba(
        "error de integridad",
        pgcode,
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(ValueError, match=mensaje):
        dao.guardar(crear_progreso())

    dao._bd._conexion.rollback.assert_called_once()


def test_guardar_hace_rollback_en_error_inesperado(
    dao,
):
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError("fallo guardar")

    configurar_cursor(dao, cursor)

    with pytest.raises(RuntimeError, match="fallo guardar"):
        dao.guardar(crear_progreso())

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "metodo, valor",
    [
        ("buscar_por_id", None),
        ("buscar_por_id", 0),
        ("buscar_por_id", -1),
        ("buscar_por_id", True),
        ("buscar_por_cliente", 0),
        ("buscar_por_cliente", "1"),
        ("eliminar_por_id", 0),
    ],
)
def test_metodos_rechazan_ids_invalidos(
    dao,
    metodo,
    valor,
):
    with pytest.raises(ValueError, match="debe ser positivo"):
        getattr(dao, metodo)(valor)


def test_buscar_por_id_exitoso_y_none(
    dao,
):
    cursor = crear_cursor(fila=crear_fila(id_progreso=7))
    configurar_cursor(dao, cursor)

    assert dao.buscar_por_id(7).id_progreso == 7

    cursor.fetchone.return_value = None

    assert dao.buscar_por_id(999) is None


def test_buscar_por_id_relanza_error(
    dao,
):
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError("fallo buscar")

    configurar_cursor(dao, cursor)

    with pytest.raises(RuntimeError, match="fallo buscar"):
        dao.buscar_por_id(1)


def test_buscar_por_cliente_lista_y_error(
    dao,
):
    cursor = crear_cursor(
        filas=[
            crear_fila(id_progreso=1),
            crear_fila(id_progreso=2),
        ],
    )

    configurar_cursor(dao, cursor)

    resultado = dao.buscar_por_cliente(10)

    assert [item.id_progreso for item in resultado] == [1, 2]

    cursor.execute.side_effect = RuntimeError("fallo historial")

    with pytest.raises(RuntimeError, match="fallo historial"):
        dao.buscar_por_cliente(10)


def test_listar_por_cliente_es_alias(
    dao,
):
    esperado = [crear_progreso(id_progreso=1)]

    with patch.object(
        dao,
        "buscar_por_cliente",
        return_value=esperado,
    ) as mock_buscar:
        assert dao.listar_por_cliente(10) is esperado

    mock_buscar.assert_called_once_with(10)


def test_actualizar_requiere_id(
    dao,
):
    with pytest.raises(ValueError, match="debe tener un ID"):
        dao.actualizar(crear_progreso())


def test_actualizar_exitoso_y_no_encontrado(
    dao,
):
    progreso = crear_progreso(id_progreso=20)
    cursor = crear_cursor(fila=crear_fila(id_progreso=20))

    configurar_cursor(dao, cursor)

    assert dao.actualizar(progreso).id_progreso == 20

    cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="No se encontró"):
        dao.actualizar(progreso)

    assert dao._bd._conexion.rollback.called


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        ("23505", "Ya existe un registro de progreso"),
        ("23503", "cliente referenciado no existe"),
        ("99999", "No se pudo actualizar el progreso"),
    ],
)
def test_actualizar_maneja_integrity_error(
    dao,
    pgcode,
    mensaje,
    monkeypatch,
):
    monkeypatch.setattr(
        modulo_dao,
        "IntegrityError",
        IntegrityErrorPrueba,
    )

    cursor = crear_cursor()
    cursor.execute.side_effect = IntegrityErrorPrueba(
        "error actualización",
        pgcode,
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(ValueError, match=mensaje):
        dao.actualizar(crear_progreso(id_progreso=20))

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "rowcount, esperado",
    [
        (1, True),
        (0, False),
    ],
)
def test_eliminar_por_id(
    dao,
    rowcount,
    esperado,
):
    cursor = crear_cursor(rowcount=rowcount)
    configurar_cursor(dao, cursor)

    assert dao.eliminar_por_id(1) is esperado

    dao._bd._conexion.commit.assert_called_once()


def test_eliminar_por_id_hace_rollback(
    dao,
):
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError("fallo eliminar")

    configurar_cursor(dao, cursor)

    with pytest.raises(RuntimeError, match="fallo eliminar"):
        dao.eliminar_por_id(1)

    dao._bd._conexion.rollback.assert_called_once()


def test_crear_progreso_desde_fila_y_tipo_invalido():
    fila = crear_fila(id_progreso=50)

    resultado = ProgresoMensualDAO._crear_progreso_desde_fila(
        fila,
    )

    assert resultado.id_progreso == 50
    assert resultado.peso == Decimal("70.50")

    with pytest.raises(TypeError, match="tipo diccionario"):
        ProgresoMensualDAO._crear_progreso_desde_fila(
            (1, 2, 3),
        )


def test_normalizar_mes(
):
    assert ProgresoMensualDAO._normalizar_mes(
        date(2026, 9, 24),
    ) == date(2026, 9, 1)

    assert ProgresoMensualDAO._normalizar_mes(
        datetime(2026, 10, 15, 13, 0),
    ) == date(2026, 10, 1)

    with pytest.raises(ValueError, match="mes debe ser"):
        ProgresoMensualDAO._normalizar_mes("2026-01-01")


def test_calcular_porcentaje(
):
    assert ProgresoMensualDAO._calcular_porcentaje(
        0,
        0,
    ) == Decimal("0.00")

    assert ProgresoMensualDAO._calcular_porcentaje(
        1,
        3,
    ) == Decimal("33.33")

    assert ProgresoMensualDAO._calcular_porcentaje(
        15,
        10,
    ) == Decimal("100.00")


@pytest.mark.parametrize(
    "progreso, mensaje",
    [
        ("invalido", "objeto ProgresoMensual"),
        (None, "objeto ProgresoMensual"),
    ],
)
def test_validar_progreso_rechaza_tipo(
    progreso,
    mensaje,
):
    with pytest.raises(TypeError, match=mensaje):
        ProgresoMensualDAO._validar_progreso(progreso)


def test_validar_progreso_rechaza_campos_invalidos():
    progreso = crear_progreso()

    progreso._id_cliente = None

    with pytest.raises(ValueError, match="debe tener un cliente"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._id_cliente = "texto"

    with pytest.raises(ValueError, match="ID del cliente no es válido"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._id_cliente = 0

    with pytest.raises(ValueError, match="cliente debe ser positivo"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._mes = None

    with pytest.raises(ValueError, match="debe tener un mes"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._peso = None

    with pytest.raises(ValueError, match="debe tener un peso"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._peso = Decimal("-1")

    with pytest.raises(ValueError, match="peso debe ser mayor"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._peso = Decimal("1000")

    with pytest.raises(ValueError, match="supera el máximo"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._sesiones_completadas = -1

    with pytest.raises(ValueError, match="completadas no pueden"):
        ProgresoMensualDAO._validar_progreso(progreso)

    progreso = crear_progreso()
    progreso._sesiones_planificadas = -1

    with pytest.raises(ValueError, match="planificadas no pueden"):
        ProgresoMensualDAO._validar_progreso(progreso)


@pytest.mark.parametrize(
    "valor",
    [
        None,
        0,
        -1,
        True,
        False,
        "1",
        1.5,
    ],
)
def test_validar_id_rechaza_valores_invalidos(
    valor,
):
    with pytest.raises(ValueError, match="ID de prueba debe ser positivo"):
        ProgresoMensualDAO._validar_id(
            valor,
            "ID de prueba",
        )


def test_validar_id_acepta_entero_positivo():
    assert ProgresoMensualDAO._validar_id(1, "ID") is None

def test_validar_progreso_rechaza_peso_no_convertible():
    """
    Cubre el bloque except al convertir el peso a Decimal.

    El objeto pasa la validación peso is not None, pero su
    método __str__ lanza ValueError al intentar convertirlo.
    """

    class PesoNoConvertible:
        def __str__(self):
            raise ValueError(
                "No se puede convertir el peso",
            )

    progreso = crear_progreso()

    progreso._peso = PesoNoConvertible()

    with pytest.raises(
        ValueError,
        match="El peso no es válido",
    ):
        ProgresoMensualDAO._validar_progreso(progreso)