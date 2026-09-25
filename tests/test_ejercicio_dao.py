from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

import src.persistencia.ejercicio_dao as modulo_dao

from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
    Intensidad,
)
from src.persistencia.ejercicio_dao import EjercicioDAO


class IntegrityErrorPrueba(Exception):
    """
    Error simulado con pgcode configurable.
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
    Crea EjercicioDAO sin conectarse a PostgreSQL.
    """
    with patch.object(
        modulo_dao.ConexionBD,
        "obtener_instancia",
        return_value=bd_mock,
    ):
        return EjercicioDAO()


def crear_cursor(
    fila=None,
    filas=None,
    rowcount=1,
):
    """
    Crea cursor simulado compatible con with.
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
    Configura el cursor retornado por la conexión simulada.
    """
    dao._bd._conexion.cursor.return_value = cursor


def crear_fila(
    id_ejercicio=1,
    nombre="Caminata",
    descripcion="Caminata moderada",
    tipo="cardio",
    duracion=30,
    intensidad="MEDIA",
    calorias=Decimal("250.50"),
    creado_por=10,
):
    """
    Crea una tupla equivalente a una fila de PostgreSQL.
    """
    return (
        id_ejercicio,
        nombre,
        descripcion,
        tipo,
        duracion,
        intensidad,
        calorias,
        creado_por,
    )


def crear_ejercicio(
    id_ejercicio=None,
    creado_por=10,
):
    """
    Crea un ejercicio válido reutilizable.
    """
    return EjercicioCardio(
        id_ejercicio=id_ejercicio,
        nombre="Caminata",
        descripcion="Caminata moderada",
        tipo="cardio",
        duracion_minutos=30,
        intensidad=Intensidad.MEDIA,
        calorias_estimadas=250.50,
        creado_por=creado_por,
    )


def test_constructor_obtiene_instancia_conexion(
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
        dao = EjercicioDAO()

    assert dao._bd is bd_mock
    mock_obtener.assert_called_once()


def test_guardar_exitoso(
    dao,
):
    """
    Guarda un ejercicio, asigna el ID retornado y hace commit.
    """
    cursor = crear_cursor(fila=(55,))

    configurar_cursor(dao, cursor)

    ejercicio = crear_ejercicio()

    resultado = dao.guardar(ejercicio)

    assert resultado is ejercicio
    assert resultado.id_ejercicio == 55

    dao._bd.abrir_conexion.assert_called_once()
    dao._bd._conexion.commit.assert_called_once()

    cursor.execute.assert_called_once()

    parametros = cursor.execute.call_args.args[1]

    assert parametros == (
        "Caminata",
        "Caminata moderada",
        "cardio",
        30,
        Intensidad.MEDIA.value,
        Decimal("250.50"),
        10,
    )


def test_guardar_rechaza_objeto_invalido(
    dao,
):
    """
    Cubre _validar_ejercicio.
    """
    with pytest.raises(
        TypeError,
        match="instancia de EjercicioCardio",
    ):
        dao.guardar("ejercicio inválido")

    dao._bd.abrir_conexion.assert_not_called()


def test_guardar_rechaza_resultado_sin_id(
    dao,
):
    """
    Cubre resultado None de INSERT RETURNING.
    """
    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="No se pudo obtener el ID",
    ):
        dao.guardar(crear_ejercicio())

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        (
            "23503",
            "creador del ejercicio no existe",
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
    Cubre restricciones de integridad de guardar.
    """
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

    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        dao.guardar(crear_ejercicio())

    dao._bd._conexion.rollback.assert_called_once()


def test_guardar_hace_rollback_error_inesperado(
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
        dao.guardar(crear_ejercicio())

    dao._bd._conexion.rollback.assert_called_once()


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
def test_buscar_por_id_rechaza_id_invalido(
    dao,
    valor,
):
    """
    Cubre _validar_id desde buscar_por_id.
    """
    with pytest.raises(
        ValueError,
        match="ID del ejercicio debe ser un entero positivo",
    ):
        dao.buscar_por_id(valor)


def test_buscar_por_id_retorna_ejercicio(
    dao,
):
    """
    Cubre búsqueda exitosa y creación desde tupla.
    """
    cursor = crear_cursor(
        fila=crear_fila(id_ejercicio=8),
    )

    configurar_cursor(dao, cursor)

    resultado = dao.buscar_por_id(8)

    assert isinstance(resultado, EjercicioCardio)
    assert resultado.id_ejercicio == 8
    assert resultado.nombre == "Caminata"
    assert resultado.intensidad == Intensidad.MEDIA
    assert resultado.calorias_estimadas == Decimal("250.50")

    dao._bd.abrir_conexion.assert_called_once()


def test_buscar_por_id_retorna_none(
    dao,
):
    """
    Cubre búsqueda sin fila.
    """
    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    assert dao.buscar_por_id(999) is None


def test_buscar_por_id_relanza_error(
    dao,
):
    """
    Cubre except Exception: raise de buscar_por_id.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo de búsqueda",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo de búsqueda",
    ):
        dao.buscar_por_id(1)


def test_listar_retorna_ejercicios(
    dao,
):
    """
    Cubre fetchall y comprensión de lista.
    """
    cursor = crear_cursor(
        filas=[
            crear_fila(id_ejercicio=1),
            crear_fila(
                id_ejercicio=2,
                nombre="Bicicleta",
                intensidad="ALTA",
            ),
        ],
    )

    configurar_cursor(dao, cursor)

    resultado = dao.listar()

    assert len(resultado) == 2
    assert resultado[0].id_ejercicio == 1
    assert resultado[1].id_ejercicio == 2
    assert resultado[1].nombre == "Bicicleta"
    assert resultado[1].intensidad == Intensidad.ALTA


def test_listar_retorna_lista_vacia(
    dao,
):
    """
    Cubre lista sin resultados.
    """
    cursor = crear_cursor(filas=[])

    configurar_cursor(dao, cursor)

    assert dao.listar() == []


def test_listar_relanza_error(
    dao,
):
    """
    Cubre except Exception: raise de listar.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo al listar",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo al listar",
    ):
        dao.listar()


def test_listar_ejercicios_es_alias(
    dao,
):
    """
    Cubre alias listar_ejercicios.
    """
    ejercicios = [crear_ejercicio(id_ejercicio=3)]

    with patch.object(
        dao,
        "listar",
        return_value=ejercicios,
    ) as mock_listar:
        resultado = dao.listar_ejercicios()

    assert resultado is ejercicios
    mock_listar.assert_called_once()


def test_actualizar_exitoso(
    dao,
):
    """
    Cubre UPDATE, commit y conversión de fila.
    """
    ejercicio = crear_ejercicio(id_ejercicio=25)

    ejercicio.nombre = "Caminata actualizada"

    cursor = crear_cursor(
        fila=crear_fila(
            id_ejercicio=25,
            nombre="Caminata actualizada",
        ),
    )

    configurar_cursor(dao, cursor)

    resultado = dao.actualizar(ejercicio)

    assert isinstance(resultado, EjercicioCardio)
    assert resultado.id_ejercicio == 25
    assert resultado.nombre == "Caminata actualizada"

    dao._bd._conexion.commit.assert_called_once()


@pytest.mark.parametrize(
    "id_ejercicio",
    [
        None,
        0,
        -1,
        True,
        "1",
        1.5,
    ],
)
def test_actualizar_requiere_id_valido(
    dao,
    id_ejercicio,
):
    """
    Cubre todas las ramas de ID inválido para actualizar.
    """
    ejercicio = crear_ejercicio()

    if id_ejercicio is not None:
        ejercicio._id_ejercicio = id_ejercicio

    with pytest.raises(
        ValueError,
        match="debe tener un id válido",
    ):
        dao.actualizar(ejercicio)


def test_actualizar_rechaza_objeto_invalido(
    dao,
):
    """
    Cubre validación de tipo desde actualizar.
    """
    with pytest.raises(
        TypeError,
        match="instancia de EjercicioCardio",
    ):
        dao.actualizar("objeto inválido")


def test_actualizar_rechaza_ejercicio_no_encontrado(
    dao,
):
    """
    Cubre fila None después de UPDATE RETURNING.
    """
    cursor = crear_cursor(fila=None)

    configurar_cursor(dao, cursor)

    with pytest.raises(
        ValueError,
        match="No se encontró el ejercicio",
    ):
        dao.actualizar(
            crear_ejercicio(id_ejercicio=25),
        )

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        (
            "23503",
            "creador del ejercicio no existe",
        ),
        (
            "99999",
            "restricción de integridad",
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
    Cubre IntegrityError de actualizar.
    """
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

    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        dao.actualizar(
            crear_ejercicio(id_ejercicio=25),
        )

    dao._bd._conexion.rollback.assert_called_once()


def test_actualizar_hace_rollback_error_inesperado(
    dao,
):
    """
    Cubre except Exception de actualizar.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "fallo al actualizar",
    )

    configurar_cursor(dao, cursor)

    with pytest.raises(
        RuntimeError,
        match="fallo al actualizar",
    ):
        dao.actualizar(
            crear_ejercicio(id_ejercicio=25),
        )

    dao._bd._conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "rowcount, esperado",
    [
        (1, True),
        (3, True),
        (0, False),
    ],
)
def test_eliminar_por_id_retorna_resultado(
    dao,
    rowcount,
    esperado,
):
    """
    Cubre resultado de eliminación según rowcount.
    """
    cursor = crear_cursor(rowcount=rowcount)

    configurar_cursor(dao, cursor)

    resultado = dao.eliminar_por_id(50)

    assert resultado is esperado
    dao._bd._conexion.commit.assert_called_once()


@pytest.mark.parametrize(
    "valor",
    [
        None,
        0,
        -1,
        True,
        "1",
    ],
)
def test_eliminar_por_id_rechaza_id_invalido(
    dao,
    valor,
):
    """
    Cubre validación de ID desde eliminar_por_id.
    """
    with pytest.raises(
        ValueError,
        match="ID del ejercicio debe ser un entero positivo",
    ):
        dao.eliminar_por_id(valor)


@pytest.mark.parametrize(
    "pgcode, mensaje",
    [
        (
            "23503",
            "está asociado a una rutina",
        ),
        (
            "99999",
            "restricción de integridad",
        ),
    ],
)
def test_eliminar_maneja_integrity_error(
    dao,
    pgcode,
    mensaje,
    monkeypatch,
):
    """
    Cubre IntegrityError de eliminar.
    """
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

    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        dao.eliminar_por_id(50)

    dao._bd._conexion.rollback.assert_called_once()


def test_eliminar_hace_rollback_error_inesperado(
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


def test_crear_ejercicio_desde_fila_rechaza_fila_incompleta():
    """
    Cubre validación de longitud de fila.
    """
    with pytest.raises(
        ValueError,
        match="fila del ejercicio está incompleta",
    ):
        EjercicioDAO._crear_ejercicio_desde_fila(
            (1, "Caminata"),
        )


def test_crear_ejercicio_desde_fila_completa():
    """
    Cubre creación de modelo desde fila válida.
    """
    resultado = EjercicioDAO._crear_ejercicio_desde_fila(
        crear_fila(
            id_ejercicio=77,
            intensidad="BAJA",
            calorias=Decimal("123.456"),
        ),
    )

    assert isinstance(resultado, EjercicioCardio)
    assert resultado.id_ejercicio == 77
    assert resultado.intensidad == Intensidad.BAJA
    assert resultado.calorias_estimadas == Decimal("123.46")


def test_validar_ejercicio_acepta_instancia_valida():
    """
    Cubre validación exitosa.
    """
    EjercicioDAO._validar_ejercicio(crear_ejercicio())


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
        [],
    ],
)
def test_validar_id_rechaza_valores_invalidos(
    valor,
):
    """
    Cubre todas las condiciones de _validar_id.
    """
    with pytest.raises(
        ValueError,
        match="ID del ejercicio debe ser un entero positivo",
    ):
        EjercicioDAO._validar_id(valor)


def test_validar_id_acepta_entero_positivo():
    """
    Cubre _validar_id con valor correcto.
    """
    assert EjercicioDAO._validar_id(10) is None