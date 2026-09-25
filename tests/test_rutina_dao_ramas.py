from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.modelos.enums import NivelRutina
from src.modelos.rutina import Rutina
from src.persistencia.rutina_dao import RutinaDAO


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
    dao = RutinaDAO()

    cursor = MagicMock()
    conexion = MagicMock()

    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False

    dao._bd = MagicMock()
    dao._bd._conexion = conexion

    return dao, cursor, conexion


def crear_rutina(
    id_rutina=None,
    creado_por=None,
):
    return Rutina(
        id_rutina=id_rutina,
        nombre="Rutina de prueba",
        descripcion="Descripción de prueba",
        objetivo="Mejorar resistencia",
        nivel=NivelRutina.BASICO,
        duracion_semanas=4,
        creado_por=creado_por,
        fecha_creacion=date(2026, 1, 1),
    )


def crear_fila_rutina(
    id_rutina=1,
    nivel="BASICO",
):
    return (
        id_rutina,
        "Rutina de prueba",
        "Descripción de prueba",
        "Mejorar resistencia",
        nivel,
        4,
        None,
        date(2026, 1, 1),
    )


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
        RutinaDAO._validar_id(
            valor,
            "El ID de prueba",
        )


def test_validar_id_convierte_texto_numerico():
    assert RutinaDAO._validar_id(
        "15",
        "El ID de prueba",
    ) == 15


def test_crear_rutina_rechaza_fila_incompleta():
    with pytest.raises(
        ValueError,
        match="La fila de rutina está incompleta",
    ):
        RutinaDAO._crear_rutina_desde_fila(
            (1, "Nombre")
        )


@pytest.mark.parametrize(
    "nivel",
    [
        None,
        "",
        "FACIL",
        "EXPERTO",
    ],
)
def test_obtener_valor_nivel_rechaza_nivel_invalido(nivel):
    with pytest.raises(ValueError):
        RutinaDAO._obtener_valor_nivel(nivel)


@pytest.mark.parametrize(
    ("nivel", "esperado"),
    [
        ("basico", "BASICO"),
        (" INTERMEDIO ", "INTERMEDIO"),
        ("AVANZADO", "AVANZADO"),
        (NivelRutina.BASICO, "BASICO"),
    ],
)
def test_obtener_valor_nivel_normaliza_valor_valido(
    nivel,
    esperado,
):
    assert RutinaDAO._obtener_valor_nivel(
        nivel
    ) == esperado


@pytest.mark.parametrize(
    "rutina",
    [
        None,
        object(),
    ],
)
def test_validar_rutina_guardar_rechaza_tipo_invalido(rutina):
    with pytest.raises(
        TypeError,
        match="Debe proporcionar una instancia de Rutina",
    ):
        RutinaDAO._validar_rutina_para_guardar(rutina)


def test_validar_rutina_actualizar_rechaza_tipo_invalido():
    with pytest.raises(
        TypeError,
        match="Debe proporcionar una instancia de Rutina",
    ):
        RutinaDAO._validar_rutina_para_actualizar(object())


def test_validar_rutina_actualizar_rechaza_sin_id():
    rutina = crear_rutina(id_rutina=None)

    with pytest.raises(
        ValueError,
        match="La rutina debe tener un id",
    ):
        RutinaDAO._validar_rutina_para_actualizar(rutina)


@pytest.fixture
def rutina_mock_valida():
    rutina = MagicMock(spec=Rutina)

    rutina.nombre = "Rutina válida"
    rutina.descripcion = "Descripción válida"
    rutina.objetivo = "Mejorar resistencia"
    rutina.nivel = NivelRutina.BASICO
    rutina.duracion_semanas = 4
    rutina.id_rutina = 1
    rutina.creado_por = None

    return rutina


def test_validar_campos_rutina_rechaza_nombre_vacio(
    rutina_mock_valida,
):
    rutina_mock_valida.nombre = ""

    with pytest.raises(
        ValueError,
        match="El nombre es obligatorio",
    ):
        RutinaDAO._validar_campos_rutina(
            rutina_mock_valida
        )


def test_validar_campos_rutina_rechaza_descripcion_vacia(
    rutina_mock_valida,
):
    rutina_mock_valida.descripcion = ""

    with pytest.raises(
        ValueError,
        match="La descripción es obligatoria",
    ):
        RutinaDAO._validar_campos_rutina(
            rutina_mock_valida
        )


def test_validar_campos_rutina_rechaza_objetivo_vacio(
    rutina_mock_valida,
):
    rutina_mock_valida.objetivo = ""

    with pytest.raises(
        ValueError,
        match="El objetivo es obligatorio",
    ):
        RutinaDAO._validar_campos_rutina(
            rutina_mock_valida
        )


@pytest.mark.parametrize(
    "duracion_invalida",
    [
        0,
        -1,
        True,
        "4",
    ],
)
def test_validar_campos_rutina_rechaza_duracion_invalida(
    rutina_mock_valida,
    duracion_invalida,
):
    rutina_mock_valida.duracion_semanas = duracion_invalida

    with pytest.raises(
        ValueError,
        match="La duración debe ser un entero",
    ):
        RutinaDAO._validar_campos_rutina(
            rutina_mock_valida
        )

def test_guardar_falla_si_postgresql_no_devuelve_rutina(recursos):
    dao, cursor, conexion = recursos
    cursor.fetchone.return_value = None

    with pytest.raises(
        RuntimeError,
        match="La base de datos no devolvió",
    ):
        dao.guardar(crear_rutina())

    conexion.rollback.assert_called_once()


def test_guardar_usa_insert_sin_creador(recursos):
    dao, cursor, conexion = recursos
    cursor.fetchone.return_value = (
        10,
        None,
        date(2026, 1, 1),
    )

    rutina = dao.guardar(crear_rutina(creado_por=None))

    assert rutina.id_rutina == 10
    conexion.commit.assert_called_once()

    _, parametros = cursor.execute.call_args.args

    assert len(parametros) == 5
    assert parametros[-1] == 4


def test_guardar_usa_insert_con_creador(recursos):
    dao, cursor, conexion = recursos
    cursor.fetchone.return_value = (
        11,
        5,
        date(2026, 1, 1),
    )

    rutina = dao.guardar(crear_rutina(creado_por=5))

    assert rutina.id_rutina == 11
    assert rutina.creado_por == 5

    _, parametros = cursor.execute.call_args.args

    assert len(parametros) == 6
    assert parametros[-1] == 5
    conexion.commit.assert_called_once()


def test_guardar_convierte_error_integridad_generico(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado(
        "99999"
    )

    with patch(
        "src.persistencia.rutina_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="No se pudo guardar la rutina",
        ):
            dao.guardar(crear_rutina())

    conexion.rollback.assert_called_once()


def test_guardar_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error inesperado"
    )

    with pytest.raises(RuntimeError, match="Error inesperado"):
        dao.guardar(crear_rutina())

    conexion.rollback.assert_called_once()


def test_buscar_por_id_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError("Error buscando")

    with pytest.raises(RuntimeError, match="Error buscando"):
        dao.buscar_por_id(1)

    conexion.rollback.assert_called_once()


def test_listar_convierte_rutinas_y_ejercicios(recursos):
    dao, cursor, _ = recursos
    cursor.fetchall.side_effect = [
        [crear_fila_rutina(1)],
        [],
    ]

    resultado = dao.listar()

    assert len(resultado) == 1
    assert resultado[0].id_rutina == 1
    assert list(resultado[0].ejercicios) == []


def test_listar_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError("Error listando")

    with pytest.raises(RuntimeError, match="Error listando"):
        dao.listar()

    conexion.rollback.assert_called_once()


def test_listar_rutinas_es_alias_de_listar(recursos):
    dao, _, _ = recursos

    with patch.object(
        dao,
        "listar",
        return_value=[],
    ) as listar:
        resultado = dao.listar_rutinas()

    assert resultado == []
    listar.assert_called_once()


def test_actualizar_convierte_error_integridad(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado(
        "23514"
    )

    with patch(
        "src.persistencia.rutina_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="Los datos no cumplen una restricción",
        ):
            dao.actualizar(crear_rutina(id_rutina=1))

    conexion.rollback.assert_called_once()


def test_actualizar_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error actualizando"
    )

    with pytest.raises(RuntimeError, match="Error actualizando"):
        dao.actualizar(crear_rutina(id_rutina=1))

    conexion.rollback.assert_called_once()


def test_agregar_ejercicio_falla_sin_resultado(recursos):
    dao, cursor, conexion = recursos
    cursor.fetchone.return_value = None

    with pytest.raises(
        RuntimeError,
        match="No se creó la asociación",
    ):
        dao.agregar_ejercicio(1, 2, 1)

    conexion.rollback.assert_called_once()


def test_agregar_ejercicio_convierte_error_integridad_generico(
    recursos,
):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado(
        "99999"
    )

    with patch(
        "src.persistencia.rutina_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="No se pudo asociar el ejercicio",
        ):
            dao.agregar_ejercicio(1, 2, 1)

    conexion.rollback.assert_called_once()


def test_agregar_ejercicio_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error asociando"
    )

    with pytest.raises(RuntimeError, match="Error asociando"):
        dao.agregar_ejercicio(1, 2, 1)

    conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    ("fila", "esperado"),
    [
        ((1, 2), True),
        (None, False),
    ],
)
def test_ejercicio_asociado_retorna_estado(
    recursos,
    fila,
    esperado,
):
    dao, cursor, _ = recursos
    cursor.fetchone.return_value = fila

    assert dao.ejercicio_asociado(1, 2) is esperado


def test_ejercicio_asociado_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error consultando asociación"
    )

    with pytest.raises(
        RuntimeError,
        match="Error consultando asociación",
    ):
        dao.ejercicio_asociado(1, 2)

    conexion.rollback.assert_called_once()


def test_eliminar_ejercicio_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error eliminando asociación"
    )

    with pytest.raises(
        RuntimeError,
        match="Error eliminando asociación",
    ):
        dao.eliminar_ejercicio(1, 2)

    conexion.rollback.assert_called_once()


def test_listar_ejercicios_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error obteniendo ejercicios"
    )

    with pytest.raises(
        RuntimeError,
        match="Error obteniendo ejercicios",
    ):
        dao.listar_ejercicios(1)

    conexion.rollback.assert_called_once()


def test_eliminar_rutina_convierte_error_integridad(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = ErrorIntegridadSimulado(
        "23503"
    )

    with patch(
        "src.persistencia.rutina_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="El registro relacionado no existe",
        ):
            dao.eliminar_por_id(1)

    conexion.rollback.assert_called_once()


def test_eliminar_rutina_hace_rollback_si_falla(recursos):
    dao, cursor, conexion = recursos
    cursor.execute.side_effect = RuntimeError(
        "Error eliminando rutina"
    )

    with pytest.raises(
        RuntimeError,
        match="Error eliminando rutina",
    ):
        dao.eliminar_por_id(1)

    conexion.rollback.assert_called_once()


@pytest.mark.parametrize(
    ("codigo", "mensaje"),
    [
        ("23503", "El registro relacionado no existe"),
        ("23505", "La asociación o el registro ya existe"),
        (
            "23514",
            "Los datos no cumplen una restricción",
        ),
        ("23502", "Falta un dato obligatorio"),
        ("99999", "Mensaje personalizado"),
    ],
)
def test_convertir_error_integridad(
    codigo,
    mensaje,
):
    error = ErrorIntegridadSimulado(codigo)

    resultado = RutinaDAO._convertir_error_integridad(
        error,
        "Mensaje personalizado",
    )

    assert isinstance(resultado, ValueError)
    assert mensaje in str(resultado)