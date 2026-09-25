from datetime import date
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

import src.persistencia.asignacion_rutina_dao as modulo_dao

from src.modelos.asignacion_rutina import AsignacionRutina
from src.modelos.enums import EstadoAsignacion
from src.persistencia.asignacion_rutina_dao import (
    AsignacionRutinaDAO,
)

class IntegrityErrorPrueba(Exception):
    """
    Excepción simulada compatible con IntegrityError.

    Permite definir pgcode, algo que no es posible hacer
    directamente con psycopg2.IntegrityError porque su
    atributo es de solo lectura.
    """

    def __init__(self, mensaje, pgcode):
        super().__init__(mensaje)
        self.pgcode = pgcode


@pytest.fixture
def bd_mock():
    """
    Simula ConexionBD y su conexión PostgreSQL.
    """
    bd = MagicMock()

    conexion = MagicMock()
    conexion.closed = False

    bd._conexion = conexion

    return bd


@pytest.fixture
def dao(bd_mock):
    """
    Crea el DAO inyectando una instancia simulada de ConexionBD.
    """
    with patch.object(
        modulo_dao.ConexionBD,
        "obtener_instancia",
        return_value=bd_mock,
    ):
        return AsignacionRutinaDAO()


def crear_cursor(
    fila=None,
    filas=None,
    rowcount=1,
):
    """
    Crea un cursor simulado compatible con with.
    """
    cursor = MagicMock()
    cursor.fetchone.return_value = fila
    cursor.fetchall.return_value = filas or []
    cursor.rowcount = rowcount
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = False

    return cursor


def configurar_cursor(
    dao,
    cursor,
):
    """
    Asigna el cursor mock a la conexión del DAO.
    """
    dao._bd._conexion.cursor.return_value = cursor


def crear_fila(
    id_asignacion=1,
    id_cliente=10,
    id_rutina=20,
    fecha_asignacion=date(2026, 1, 10),
    fecha_finalizacion=None,
    estado="ACTIVA",
    observaciones="Asignación de prueba",
):
    """
    Crea una fila dict equivalente a RealDictCursor.
    """
    return {
        "id_asignacion": id_asignacion,
        "id_cliente": id_cliente,
        "id_rutina": id_rutina,
        "fecha_asignacion": fecha_asignacion,
        "fecha_finalizacion": fecha_finalizacion,
        "estado": estado,
        "observaciones": observaciones,
    }


def crear_asignacion(
    id_asignacion=None,
    id_cliente=10,
    id_rutina=20,
    estado=EstadoAsignacion.ACTIVA,
    fecha_finalizacion=None,
    observaciones="Asignación de prueba",
):
    """
    Crea un modelo válido reutilizable.
    """
    return AsignacionRutina(
        id_asignacion=id_asignacion,
        id_cliente=id_cliente,
        id_rutina=id_rutina,
        fecha_asignacion=date(2026, 1, 10),
        fecha_finalizacion=fecha_finalizacion,
        estado=estado,
        observaciones=observaciones,
    )


def test_constructor_obtiene_instancia_de_conexion(
    bd_mock,
):
    """
    Cubre inicialización del DAO.
    """
    with patch.object(
        modulo_dao.ConexionBD,
        "obtener_instancia",
        return_value=bd_mock,
    ) as mock_obtener:
        dao = AsignacionRutinaDAO()

    assert dao._bd is bd_mock
    mock_obtener.assert_called_once()


def test_guardar_exitoso(
    dao,
):
    """
    Guarda una asignación y devuelve el modelo creado desde fila.
    """
    fila = crear_fila(id_asignacion=55)
    cursor = crear_cursor(fila=fila)

    configurar_cursor(dao, cursor)

    asignacion = crear_asignacion()

    resultado = dao.guardar(asignacion)

    assert isinstance(resultado, AsignacionRutina)
    assert resultado.id_asignacion == 55
    assert resultado.id_cliente == 10
    assert resultado.id_rutina == 20
    assert resultado.estado == EstadoAsignacion.ACTIVA

    dao._bd.abrir_conexion.assert_called_once()
    dao._bd._conexion.commit.assert_called_once()

    cursor.execute.assert_called_once()

    argumentos = cursor.execute.call_args.args[1]

    assert argumentos == (
        10,
        20,
        date(2026, 1, 10),
        None,
        EstadoAsignacion.ACTIVA.value,
        "Asignación de prueba",
    )


def test_guardar_rechaza_asignacion_invalida(
    dao,
):
    """
    Cubre validación de tipo antes de persistir.
    """
    with pytest.raises(
        TypeError,
        match="instancia de AsignacionRutina",
    ):
        dao.guardar("no_es_asignacion")

    dao._bd.abrir_conexion.assert_not_called()


def test_guardar_rechaza_fila_no_recuperada(
    dao,
):
    """
    Cubre RuntimeError cuando RETURNING no produce una fila.
    """
    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="No se pudo recuperar la asignación guardada",
    ):
        dao.guardar(crear_asignacion())

    dao._bd._conexion.commit.assert_called_once()


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        (
            "23503",
            "El cliente o la rutina no existen",
        ),
        (
            "23505",
            "El cliente ya tiene una asignación activa",
        ),
        (
            "99999",
            "restricción de integridad",
        ),
    ],
)

def test_guardar_maneja_integrity_error(
    dao,
    pgcode,
    mensaje,
    monkeypatch,
):
    """
    Cubre los tres resultados posibles de IntegrityError.
    """
    monkeypatch.setattr(
        modulo_dao,
        "IntegrityError",
        IntegrityErrorPrueba,
    )

    error = IntegrityErrorPrueba(
        "error de integridad",
        pgcode,
    )

    cursor = crear_cursor()
    cursor.execute.side_effect = error

    configurar_cursor(dao, cursor)

    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        dao.guardar(crear_asignacion())

    dao._bd._conexion.rollback.assert_called_once()

def test_guardar_hace_rollback_ante_error_inesperado(
    dao,
):
    """
    Cubre except Exception de guardar.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo inesperado",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo inesperado",
    ):
        dao.guardar(crear_asignacion())

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "id_cliente, id_rutina, asignado_por",
    [
        (0, 1, 1),
        (-1, 1, 1),
        (1, 0, 1),
        (1, -1, 1),
        (1, 1, 0),
        (1, 1, -1),
        ("1", 1, 1),
        (1, "1", 1),
        (1, 1, "1"),
    ],
)
def test_asignar_rechaza_ids_invalidos(
    dao,
    id_cliente,
    id_rutina,
    asignado_por,
):
    """
    Cubre validaciones de asignar.
    """
    with pytest.raises(
        ValueError,
        match="debe ser positivo",
    ):
        dao.asignar(
            id_cliente=id_cliente,
            id_rutina=id_rutina,
            asignado_por=asignado_por,
        )


def test_asignar_retorna_diccionario(
    dao,
):
    """
    Cubre creación de modelo, llamada a guardar y armado del dict.
    """
    asignacion_guardada = crear_asignacion(
        id_asignacion=33,
        observaciones="Observación",
    )

    with patch.object(
        dao,
        "guardar",
        return_value=asignacion_guardada,
    ) as mock_guardar:
        resultado = dao.asignar(
            id_cliente=10,
            id_rutina=20,
            asignado_por=99,
            observaciones=None,
        )

    asignacion_enviada = mock_guardar.call_args.args[0]

    assert isinstance(asignacion_enviada, AsignacionRutina)
    assert asignacion_enviada.observaciones == ""

    assert resultado == {
    "id_asignacion": 33,
    "id_cliente": 10,
    "id_rutina": 20,
    "fecha_asignacion": (
        asignacion_guardada.fecha_asignacion
    ),
    "fecha_finalizacion": None,
    "estado": EstadoAsignacion.ACTIVA.value,
    "observaciones": "Observación",
}

@pytest.mark.parametrize(
    "metodo, id_invalido",
    [
        ("buscar_por_id", 0),
        ("buscar_activa", 0),
        ("finalizar_asignacion", 0),
        ("listar_por_cliente", 0),
        ("eliminar_por_id", 0),
        ("buscar_por_id", -1),
        ("buscar_activa", -1),
        ("finalizar_asignacion", -1),
        ("listar_por_cliente", -1),
        ("eliminar_por_id", -1),
        ("buscar_por_id", "1"),
        ("buscar_activa", "1"),
    ],
)
def test_metodos_rechazan_ids_invalidos(
    dao,
    metodo,
    id_invalido,
):
    """
    Cubre validaciones de IDs de los métodos públicos.
    """
    with pytest.raises(
        ValueError,
        match="debe ser positivo",
    ):
        getattr(dao, metodo)(id_invalido)


def test_buscar_por_id_retorna_asignacion(
    dao,
):
    """
    Cubre búsqueda exitosa.
    """
    fila = crear_fila(id_asignacion=8)
    cursor = crear_cursor(fila=fila)

    configurar_cursor(dao, cursor)

    resultado = dao.buscar_por_id(8)

    assert isinstance(resultado, AsignacionRutina)
    assert resultado.id_asignacion == 8

    dao._bd.abrir_conexion.assert_called_once()


def test_buscar_por_id_retorna_none_si_no_existe(
    dao,
):
    """
    Cubre fila None.
    """
    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    assert dao.buscar_por_id(999) is None


def test_buscar_activa_retorna_asignacion(
    dao,
):
    """
    Cubre búsqueda de asignación activa.
    """
    fila = crear_fila(
        id_asignacion=9,
        estado=EstadoAsignacion.ACTIVA.value,
    )

    cursor = crear_cursor(fila=fila)

    configurar_cursor(dao, cursor)

    resultado = dao.buscar_activa(10)

    assert resultado.id_asignacion == 9
    assert resultado.estado == EstadoAsignacion.ACTIVA

    parametros = cursor.execute.call_args.args[1]

    assert parametros == (
        10,
        EstadoAsignacion.ACTIVA.value,
    )


def test_buscar_activa_retorna_none_si_no_existe(
    dao,
):
    """
    Cubre búsqueda activa sin fila.
    """
    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    assert dao.buscar_activa(10) is None


def test_obtener_activa_por_cliente_es_alias(
    dao,
):
    """
    Cubre alias de buscar_activa.
    """
    esperada = crear_asignacion(id_asignacion=15)

    with patch.object(
        dao,
        "buscar_activa",
        return_value=esperada,
    ) as mock_buscar:
        resultado = dao.obtener_activa_por_cliente(10)

    assert resultado is esperada
    mock_buscar.assert_called_once_with(10)


@pytest.mark.parametrize(
    "rowcount, esperado",
    [
        (1, True),
        (0, False),
    ],
)
def test_finalizar_asignacion_retorna_resultado(
    dao,
    rowcount,
    esperado,
):
    """
    Cubre resultado True y False según rowcount.
    """
    cursor = crear_cursor(rowcount=rowcount)

    configurar_cursor(dao, cursor)

    resultado = dao.finalizar_asignacion(22)

    assert resultado is esperado
    dao._bd._conexion.commit.assert_called_once()


def test_finalizar_asignacion_hace_rollback_en_error(
    dao,
):
    """
    Cubre except Exception de finalizar.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "error al finalizar",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="error al finalizar",
    ):
        dao.finalizar_asignacion(22)

    dao._bd._conexion.rollback.assert_called_once()


def test_listar_por_cliente_retorna_lista_de_modelos(
    dao,
):
    """
    Cubre fetchall y comprensión de lista.
    """
    filas = [
        crear_fila(id_asignacion=1),
        crear_fila(
            id_asignacion=2,
            estado="FINALIZADA",
            fecha_finalizacion=date(2026, 1, 20),
        ),
    ]

    cursor = crear_cursor(filas=filas)

    configurar_cursor(dao, cursor)

    resultado = dao.listar_por_cliente(10)

    assert len(resultado) == 2
    assert resultado[0].id_asignacion == 1
    assert resultado[1].id_asignacion == 2
    assert resultado[1].estado == EstadoAsignacion.FINALIZADA


def test_listar_por_cliente_retorna_lista_vacia(
    dao,
):
    """
    Cubre lista sin resultados.
    """
    cursor = crear_cursor(filas=[])

    configurar_cursor(dao, cursor)

    assert dao.listar_por_cliente(10) == []


def test_actualizar_requiere_id(
    dao,
):
    """
    Cubre guard clause de actualización.
    """
    with pytest.raises(
        ValueError,
        match="debe tener un ID",
    ):
        dao.actualizar(crear_asignacion())


def test_actualizar_exitoso(
    dao,
):
    """
    Cubre actualización y conversión de la fila retornada.
    """
    asignacion = crear_asignacion(
        id_asignacion=44,
        estado=EstadoAsignacion.FINALIZADA,
        fecha_finalizacion=date(2026, 1, 15),
    )

    fila = crear_fila(
        id_asignacion=44,
        estado="FINALIZADA",
        fecha_finalizacion=date(2026, 1, 15),
    )

    cursor = crear_cursor(fila=fila)

    configurar_cursor(dao, cursor)

    resultado = dao.actualizar(asignacion)

    assert resultado.id_asignacion == 44
    assert resultado.estado == EstadoAsignacion.FINALIZADA
    assert resultado.fecha_finalizacion == date(2026, 1, 15)

    dao._bd._conexion.commit.assert_called_once()


def test_actualizar_rechaza_asignacion_no_encontrada(
    dao,
):
    """
    Cubre fila None tras UPDATE RETURNING.
    """
    asignacion = crear_asignacion(id_asignacion=44)

    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    with pytest.raises(
        ValueError,
        match="No se encontró la asignación",
    ):
        dao.actualizar(asignacion)

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        (
            "23505",
            "otra asignación activa",
        ),
        (
            "99999",
            "No se pudo actualizar la asignación",
        ),
    ],
)
def test_actualizar_maneja_integrity_error(
    dao,
    pgcode,
    mensaje,
    monkeypatch,
):
    """
    Cubre restricciones de integridad en actualización.
    """
    monkeypatch.setattr(
        modulo_dao,
        "IntegrityError",
        IntegrityErrorPrueba,
    )

    asignacion = crear_asignacion(id_asignacion=44)

    error = IntegrityErrorPrueba(
        "error integridad",
        pgcode,
    )

    cursor = crear_cursor()
    cursor.execute.side_effect = error

    configurar_cursor(dao, cursor)

    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        dao.actualizar(asignacion)

    dao._bd._conexion.rollback.assert_called_once()

def test_actualizar_hace_rollback_en_error_inesperado(
    dao,
):
    """
    Cubre except Exception de actualizar.
    """
    asignacion = crear_asignacion(id_asignacion=44)

    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo actualización",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo actualización",
    ):
        dao.actualizar(asignacion)

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "rowcount, esperado",
    [
        (1, True),
        (0, False),
    ],
)
def test_eliminar_por_id_retorna_resultado(
    dao,
    rowcount,
    esperado,
):
    """
    Cubre eliminación encontrada y no encontrada.
    """
    cursor = crear_cursor(rowcount=rowcount)

    configurar_cursor(dao, cursor)

    resultado = dao.eliminar_por_id(50)

    assert resultado is esperado
    dao._bd._conexion.commit.assert_called_once()


def test_eliminar_por_id_hace_rollback_en_error(
    dao,
):
    """
    Cubre except Exception de eliminar.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo al eliminar",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo al eliminar",
    ):
        dao.eliminar_por_id(50)

    dao._bd._conexion.rollback.assert_called_once()


def test_crear_asignacion_desde_fila_dict(
):
    """
    Cubre conversión de RealDictCursor.
    """
    fila = crear_fila(
        id_asignacion=61,
        observaciones=None,
    )

    resultado = (
        AsignacionRutinaDAO._crear_asignacion_desde_fila(fila)
    )

    assert resultado.id_asignacion == 61
    assert resultado.observaciones == ""
    assert resultado.estado == EstadoAsignacion.ACTIVA


def test_crear_asignacion_desde_fila_tupla(
):
    """
    Cubre conversión desde tupla de PostgreSQL.
    """
    fila = (
        62,
        10,
        20,
        date(2026, 1, 10),
        None,
        "FINALIZADA",
        None,
    )

    resultado = (
        AsignacionRutinaDAO._crear_asignacion_desde_fila(fila)
    )

    assert resultado.id_asignacion == 62
    assert resultado.estado == EstadoAsignacion.FINALIZADA
    assert resultado.observaciones == ""


def test_convertir_estado_acepta_enum(
):
    """
    Cubre estado que ya es EstadoAsignacion.
    """
    assert (
        AsignacionRutinaDAO._convertir_estado(
            EstadoAsignacion.CANCELADA,
        )
        == EstadoAsignacion.CANCELADA
    )


def test_convertir_estado_acepta_valor_del_enum(
):
    """
    Cubre EstadoAsignacion(valor).
    """
    assert (
        AsignacionRutinaDAO._convertir_estado(
            EstadoAsignacion.ACTIVA.value,
        )
        == EstadoAsignacion.ACTIVA
    )


def test_convertir_estado_acepta_nombre_del_enum(
    monkeypatch,
):
    """
    Fuerza la ruta alternativa EstadoAsignacion[str(valor).upper()].
    """
    from enum import Enum

    class EstadoPrueba(Enum):
        ESTADO_ACTIVO = "activo"
        ESTADO_FINAL = "final"

    monkeypatch.setattr(
        modulo_dao,
        "EstadoAsignacion",
        EstadoPrueba,
    )

    resultado = AsignacionRutinaDAO._convertir_estado(
        "ESTADO_ACTIVO",
    )

    assert resultado == EstadoPrueba.ESTADO_ACTIVO


def test_validar_asignacion_rechaza_tipo_incorrecto(
):
    """
    Cubre validación de tipo.
    """
    with pytest.raises(
        TypeError,
        match="instancia de AsignacionRutina",
    ):
        AsignacionRutinaDAO._validar_asignacion("invalida")


def test_validar_asignacion_rechaza_cliente_invalido(
):
    """
    Cubre ID de cliente inválido.
    """
    asignacion = crear_asignacion()
    asignacion._id_cliente = 0

    with pytest.raises(
        ValueError,
        match="ID del cliente debe ser positivo",
    ):
        AsignacionRutinaDAO._validar_asignacion(asignacion)


def test_validar_asignacion_rechaza_rutina_invalida(
):
    """
    Cubre ID de rutina inválido.
    """
    asignacion = crear_asignacion()
    asignacion._id_rutina = 0

    with pytest.raises(
        ValueError,
        match="ID de rutina debe ser positivo",
    ):
        AsignacionRutinaDAO._validar_asignacion(asignacion)


def test_validar_asignacion_rechaza_estado_invalido(
):
    """
    Cubre estado que no es EstadoAsignacion.
    """
    asignacion = crear_asignacion()
    asignacion._estado = "ACTIVA"

    with pytest.raises(
        ValueError,
        match="estado de la asignación no es válido",
    ):
        AsignacionRutinaDAO._validar_asignacion(asignacion)

def test_buscar_por_id_relanza_error_del_cursor(
    dao,
):
    """
    Cubre except Exception: raise de buscar_por_id.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo al buscar por ID",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo al buscar por ID",
    ):
        dao.buscar_por_id(1)


def test_buscar_activa_relanza_error_del_cursor(
    dao,
):
    """
    Cubre except Exception: raise de buscar_activa.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo al buscar activa",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo al buscar activa",
    ):
        dao.buscar_activa(1)


def test_listar_por_cliente_relanza_error_del_cursor(
    dao,
):
    """
    Cubre except Exception: raise de listar_por_cliente.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo al listar historial",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo al listar historial",
    ):
        dao.listar_por_cliente(1)