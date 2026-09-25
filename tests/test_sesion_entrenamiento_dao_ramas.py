from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import SesionEntrenamiento
from src.persistencia.sesion_entrenamiento_dao import (
    SesionEntrenamientoDAO,
)


class ErrorIntegridadSimulado(Exception):
    def __init__(
        self,
        pgcode,
        mensaje="Error de integridad simulado",
    ):
        super().__init__(mensaje)
        self.pgcode = pgcode


@pytest.fixture
def recursos():
    dao = SesionEntrenamientoDAO()

    cursor = MagicMock()
    conexion = MagicMock()

    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False

    dao._bd = MagicMock()
    dao._bd._conexion = conexion

    return dao, cursor, conexion


def crear_sesion(
    id_sesion=None,
    id_cliente=1,
    id_rutina=None,
    veces_planificadas=1,
    veces_realizadas=0,
):
    return SesionEntrenamiento(
        id_sesion=id_sesion,
        id_cliente=id_cliente,
        id_rutina=id_rutina,
        fecha=date(2026, 9, 15),
        nombre_ejercicio="Caminata",
        duracion_real=45,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=300,
        observaciones="Sesión de prueba",
        completada=True,
        veces_planificadas=veces_planificadas,
        veces_realizadas=veces_realizadas,
    )


def crear_fila(
    id_sesion=1,
    id_cliente=1,
    intensidad="MEDIA",
):
    return {
        "id_sesion": id_sesion,
        "id_cliente": id_cliente,
        "id_rutina": None,
        "fecha": date(2026, 9, 15),
        "nombre_ejercicio": "Caminata",
        "duracion_real": 45,
        "intensidad_real": intensidad,
        "calorias_quemadas": 300,
        "observaciones": "Sesión de prueba",
        "completada": True,
        "veces_planificadas": 1,
        "veces_realizadas": 0,
    }


def test_guardar_falla_si_no_recibe_sesion_insertada(recursos):
    dao, cursor, conexion = recursos
    cursor.fetchone.return_value = None

    with pytest.raises(
        RuntimeError,
        match="No se recibió la sesión insertada",
    ):
        dao.guardar(crear_sesion())

    conexion.rollback.assert_called_once()


def test_guardar_convierte_error_integridad_veces_invalidas(
    recursos,
):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado("23514")

    with patch(
        "src.persistencia.sesion_entrenamiento_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="Las veces realizadas deben ser",
        ):
            dao.guardar(crear_sesion())

    conexion.rollback.assert_called_once()


def test_guardar_convierte_error_integridad_generico(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado("99999")

    with patch(
        "src.persistencia.sesion_entrenamiento_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="No se pudo guardar la sesión",
        ):
            dao.guardar(crear_sesion())

    conexion.rollback.assert_called_once()


def test_guardar_hace_rollback_en_error_inesperado(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError("Error inesperado")

    with pytest.raises(RuntimeError, match="Error inesperado"):
        dao.guardar(crear_sesion())

    conexion.rollback.assert_called_once()


def test_buscar_por_id_crea_sesion_desde_fila(recursos):
    dao, cursor, _ = recursos
    cursor.fetchone.return_value = crear_fila()

    resultado = dao.buscar_por_id(1)

    assert isinstance(resultado, SesionEntrenamiento)
    assert resultado.id_sesion == 1
    assert resultado.intensidad_real == Intensidad.MEDIA


def test_buscar_por_id_hace_rollback_si_falla_cursor(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError("Error buscando sesión")

    with pytest.raises(RuntimeError, match="Error buscando sesión"):
        dao.buscar_por_id(1)

    conexion.rollback.assert_called_once()


def test_listar_por_cliente_convierte_error_de_fila_a_runtime_error(
    recursos,
):
    dao, cursor, conexion = recursos
    cursor.fetchall.return_value = [
        {
            "id_sesion": 1,
            "id_cliente": 1,
            "fecha": None,
        }
    ]

    with pytest.raises(
        RuntimeError,
        match="Error al convertir la sesión recibida",
    ):
        dao.listar_por_cliente(1)

    conexion.rollback.assert_called_once()


def test_listar_por_cliente_hace_rollback_si_falla_cursor(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError("Error listando sesiones")

    with pytest.raises(RuntimeError, match="Error listando sesiones"):
        dao.listar_por_cliente(1)

    conexion.rollback.assert_called_once()


def test_buscar_por_cliente_es_alias_de_listar_por_cliente(recursos):
    dao, _, _ = recursos

    with patch.object(
        dao,
        "listar_por_cliente",
        return_value=[],
    ) as listar:
        resultado = dao.buscar_por_cliente(10)

    assert resultado == []
    listar.assert_called_once_with(10)


def test_actualizar_rechaza_objeto_que_no_es_sesion(recursos):
    dao, _, _ = recursos

    with pytest.raises(
        TypeError,
        match="Debe proporcionar una instancia",
    ):
        dao.actualizar(object())


def test_actualizar_retorna_sesion_actualizada(recursos):
    dao, cursor, conexion = recursos
    cursor.fetchone.return_value = crear_fila(id_sesion=10)

    resultado = dao.actualizar(
        crear_sesion(id_sesion=10)
    )

    assert isinstance(resultado, SesionEntrenamiento)
    assert resultado.id_sesion == 10
    conexion.commit.assert_called_once()


def test_actualizar_convierte_error_cliente_inexistente(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado("23503")

    with patch(
        "src.persistencia.sesion_entrenamiento_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="El cliente referenciado no existe",
        ):
            dao.actualizar(crear_sesion(id_sesion=1))

    conexion.rollback.assert_called_once()


def test_actualizar_convierte_error_veces_invalidas(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado("23514")

    with patch(
        "src.persistencia.sesion_entrenamiento_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="Las veces realizadas no pueden superar",
        ):
            dao.actualizar(crear_sesion(id_sesion=1))

    conexion.rollback.assert_called_once()


def test_actualizar_convierte_error_integridad_generico(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado("99999")

    with patch(
        "src.persistencia.sesion_entrenamiento_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="No se pudo actualizar la sesión",
        ):
            dao.actualizar(crear_sesion(id_sesion=1))

    conexion.rollback.assert_called_once()


def test_eliminar_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError("Error eliminando")

    with pytest.raises(RuntimeError, match="Error eliminando"):
        dao.eliminar_por_id(1)

    conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    "valor",
    [
        None,
        True,
        False,
        "texto",
        0,
        -1,
    ],
)
def test_validar_id_rechaza_valores_invalidos(valor):
    with pytest.raises(ValueError):
        SesionEntrenamientoDAO._validar_id(
            valor,
            "El ID de prueba",
        )


def test_validar_id_convierte_texto_numerico_positivo():
    resultado = SesionEntrenamientoDAO._validar_id(
        "25",
        "El ID de prueba",
    )

    assert resultado == 25


def test_validar_sesion_rechaza_objeto_invalido():
    with pytest.raises(
        TypeError,
        match="Debe proporcionar una instancia",
    ):
        SesionEntrenamientoDAO._validar_sesion(object())


def test_validar_sesion_rechaza_cliente_none():
    sesion = MagicMock(spec=SesionEntrenamiento)
    sesion.id_cliente = None

    with pytest.raises(
        ValueError,
        match="La sesión debe tener un cliente",
    ):
        SesionEntrenamientoDAO._validar_sesion(sesion)


def test_validar_sesion_rechaza_rutina_invalida():
    sesion = MagicMock(spec=SesionEntrenamiento)
    sesion.id_cliente = 1
    sesion.id_rutina = 0

    with pytest.raises(ValueError):
        SesionEntrenamientoDAO._validar_sesion(sesion)


def test_validar_sesion_rechaza_veces_planificadas_cero():
    sesion = MagicMock(spec=SesionEntrenamiento)
    sesion.id_cliente = 1
    sesion.id_rutina = None
    sesion.veces_planificadas = 0
    sesion.veces_realizadas = 0

    with pytest.raises(
        ValueError,
        match="Las veces planificadas deben ser mayores",
    ):
        SesionEntrenamientoDAO._validar_sesion(sesion)


def test_validar_sesion_rechaza_veces_realizadas_negativas():
    sesion = MagicMock(spec=SesionEntrenamiento)
    sesion.id_cliente = 1
    sesion.id_rutina = None
    sesion.veces_planificadas = 1
    sesion.veces_realizadas = -1

    with pytest.raises(
        ValueError,
        match="Las veces realizadas no pueden ser negativas",
    ):
        SesionEntrenamientoDAO._validar_sesion(sesion)


def test_validar_sesion_rechaza_veces_realizadas_mayores():
    sesion = MagicMock(spec=SesionEntrenamiento)
    sesion.id_cliente = 1
    sesion.id_rutina = None
    sesion.veces_planificadas = 1
    sesion.veces_realizadas = 2

    with pytest.raises(
        ValueError,
        match="Las veces realizadas no pueden superar",
    ):
        SesionEntrenamientoDAO._validar_sesion(sesion)


def test_crear_sesion_rechaza_fila_no_diccionario():
    with pytest.raises(
        TypeError,
        match="La fila no es un diccionario",
    ):
        SesionEntrenamientoDAO._crear_sesion_desde_fila(
            ("fila", "invalida")
        )


@pytest.mark.parametrize(
    ("campo", "mensaje"),
    [
        ("fecha", "La sesión no tiene fecha"),
        ("duracion_real", "La sesión no tiene duración"),
        ("intensidad_real", "La sesión no tiene intensidad"),
    ],
)
def test_crear_sesion_rechaza_campos_obligatorios_ausentes(
    campo,
    mensaje,
):
    fila = crear_fila()
    fila[campo] = None

    with pytest.raises(ValueError, match=mensaje):
        SesionEntrenamientoDAO._crear_sesion_desde_fila(fila)


def test_convertir_intensidad_retorna_enum_si_ya_es_enum():
    assert (
        SesionEntrenamientoDAO._convertir_intensidad(
            Intensidad.ALTA
        )
        is Intensidad.ALTA
    )


def test_convertir_intensidad_rechaza_none():
    with pytest.raises(
        ValueError,
        match="La intensidad no puede ser NULL",
    ):
        SesionEntrenamientoDAO._convertir_intensidad(None)


def test_convertir_intensidad_rechaza_texto_invalido():
    with pytest.raises(
        ValueError,
        match="Intensidad inválida recibida",
    ):
        SesionEntrenamientoDAO._convertir_intensidad("EXTREMA")


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("baja", Intensidad.BAJA),
        ("MEDIA", Intensidad.MEDIA),
        (" Alta ", Intensidad.ALTA),
    ],
)
def test_convertir_intensidad_convierte_texto_valido(
    valor,
    esperado,
):
    assert (
        SesionEntrenamientoDAO._convertir_intensidad(valor)
        is esperado
    )


def test_valor_intensidad_convierte_enum():
    assert (
        SesionEntrenamientoDAO._valor_intensidad(
            Intensidad.MEDIA
        )
        == "MEDIA"
    )


@pytest.mark.parametrize(
    "valor",
    [
        "baja",
        "MEDIA",
        " Alta ",
    ],
)
def test_valor_intensidad_normaliza_texto_valido(valor):
    assert SesionEntrenamientoDAO._valor_intensidad(
        valor
    ) in {"BAJA", "MEDIA", "ALTA"}


def test_valor_intensidad_rechaza_texto_invalido():
    with pytest.raises(
        ValueError,
        match="Intensidad inválida",
    ):
        SesionEntrenamientoDAO._valor_intensidad("EXTREMA")