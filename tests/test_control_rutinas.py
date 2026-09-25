from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.controladores.control_rutinas import (
    ControlRutinas,
    _convertir_nivel,
    _instanciar_rutina,
    _validar_id,
)
from src.modelos.enums import NivelRutina
from src.modelos.rutina import Rutina


@pytest.fixture
def mock_rutina_dao():
    return Mock()


@pytest.fixture
def mock_asignacion_dao():
    return Mock()


@pytest.fixture
def controlador(
    mock_rutina_dao,
    mock_asignacion_dao,
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlRutinas(
        rutina_dao=mock_rutina_dao,
        asignacion_dao=mock_asignacion_dao,
        ruta_log=str(log_file),
    )


@pytest.fixture
def rutina_valida():
    return _instanciar_rutina(
        id_rutina=1,
        nombre="Fuerza Básica",
        descripcion="Rutina para principiantes",
        nivel_dificultad="BASICO",
        duracion_estimada=4,
        objetivo="cardio",
        creado_por=10,
    )


def test_convertir_nivel_acepta_enum():
    resultado = _convertir_nivel(NivelRutina.BASICO)

    assert resultado == NivelRutina.BASICO


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("BASICO", NivelRutina.BASICO),
        ("basico", NivelRutina.BASICO),
        ("  BASICO  ", NivelRutina.BASICO),
        ("INTERMEDIO", NivelRutina.INTERMEDIO),
        ("intermedio", NivelRutina.INTERMEDIO),
        ("AVANZADO", NivelRutina.AVANZADO),
        ("avanzado", NivelRutina.AVANZADO),
    ],
)
def test_convertir_nivel_acepta_texto_valido(
    valor,
    esperado,
):
    assert _convertir_nivel(valor) == esperado


@pytest.mark.parametrize(
    "valor",
    [
        None,
        1,
        1.5,
        True,
        False,
        [],
        {},
        "",
        "FACIL",
        "EXPERTO",
        "NINGUNO",
    ],
)
def test_convertir_nivel_rechaza_valores_invalidos(
    valor,
):
    with pytest.raises(ValueError):
        _convertir_nivel(valor)


@pytest.mark.parametrize(
    "valor, esperado",
    [
        (1, 1),
        ("1", 1),
        (2.0, 2),
        ("20", 20),
    ],
)
def test_validar_id_acepta_enteros_positivos(
    valor,
    esperado,
):
    assert _validar_id(
        valor,
        "El ID de prueba",
    ) == esperado


@pytest.mark.parametrize(
    "valor",
    [
        None,
        True,
        False,
        0,
        -1,
        -100,
        0.0,
        -2.5,
        "0",
        "-1",
        "texto",
        [],
        {},
    ],
)
def test_validar_id_rechaza_valores_invalidos(
    valor,
):
    with pytest.raises(
        ValueError,
        match="debe ser un entero positivo",
    ):
        _validar_id(
            valor,
            "El ID de prueba",
        )


def test_instanciar_rutina_exitoso():
    rutina = _instanciar_rutina(
        id_rutina=5,
        nombre="Cardio inicial",
        descripcion="Rutina de prueba",
        nivel_dificultad="INTERMEDIO",
        duracion_estimada=6,
        objetivo="resistencia",
        creado_por=3,
    )

    assert isinstance(rutina, Rutina)
    assert rutina.id_rutina == 5
    assert rutina.nombre == "Cardio inicial"
    assert rutina.descripcion == "Rutina de prueba"
    assert rutina.nivel == NivelRutina.INTERMEDIO
    assert rutina.duracion_semanas == 6
    assert rutina.objetivo == "resistencia"
    assert rutina.creado_por == 3


def test_instanciar_rutina_sin_id():
    rutina = _instanciar_rutina(
        nombre="Rutina nueva",
        descripcion="Sin ID todavía",
        nivel_dificultad=NivelRutina.AVANZADO,
        duracion_estimada=8.0,
        creado_por=7,
    )

    assert rutina.id_rutina is None
    assert rutina.nivel == NivelRutina.AVANZADO
    assert rutina.duracion_semanas == 8


@pytest.mark.parametrize(
    "duracion",
    [
        True,
        False,
        "4",
        None,
        [],
        0,
        -1,
        2.5,
        3.7,
    ],
)
def test_instanciar_rutina_rechaza_duracion_invalida(
    duracion,
):
    with pytest.raises(ValueError):
        _instanciar_rutina(
            nombre="Rutina",
            descripcion="Descripción",
            nivel_dificultad="BASICO",
            duracion_estimada=duracion,
            creado_por=1,
        )


@pytest.mark.parametrize(
    "creado_por",
    [
        None,
        0,
        -1,
        True,
        "texto",
    ],
)
def test_instanciar_rutina_rechaza_creador_invalido(
    creado_por,
):
    with pytest.raises(ValueError):
        _instanciar_rutina(
            nombre="Rutina",
            descripcion="Descripción",
            nivel_dificultad="BASICO",
            duracion_estimada=4,
            creado_por=creado_por,
        )


@pytest.mark.parametrize(
    "id_rutina",
    [
        0,
        -1,
        True,
        "texto",
    ],
)
def test_instanciar_rutina_rechaza_id_invalido(
    id_rutina,
):
    with pytest.raises(ValueError):
        _instanciar_rutina(
            id_rutina=id_rutina,
            nombre="Rutina",
            descripcion="Descripción",
            nivel_dificultad="BASICO",
            duracion_estimada=4,
            creado_por=1,
        )


def test_constructor_requiere_dao_rutinas(
    mock_asignacion_dao,
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="DAO de rutinas es obligatorio",
    ):
        ControlRutinas(
            rutina_dao=None,
            asignacion_dao=mock_asignacion_dao,
            ruta_log=str(tmp_path / "log.txt"),
        )


def test_constructor_requiere_dao_asignaciones(
    mock_rutina_dao,
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="DAO de asignaciones es obligatorio",
    ):
        ControlRutinas(
            rutina_dao=mock_rutina_dao,
            asignacion_dao=None,
            ruta_log=str(tmp_path / "log.txt"),
        )


def test_propiedades_de_daos(
    controlador,
    mock_rutina_dao,
    mock_asignacion_dao,
):
    assert controlador.rutina_dao is mock_rutina_dao
    assert controlador.asignacion_dao is mock_asignacion_dao


def test_crear_rutina_exitoso_y_auditoria(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.guardar.side_effect = (
        lambda rutina: rutina
    )

    rutina = controlador.crear_rutina(
        nombre="  Fuerza Básica  ",
        descripcion="  Rutina para principiantes  ",
        nivel_dificultad="BASICO",
        duracion_estimada=4,
        creado_por=10,
        objetivo="  cardio  ",
    )

    assert isinstance(rutina, Rutina)
    assert rutina.nombre == "Fuerza Básica"
    assert rutina.descripcion == "Rutina para principiantes"
    assert rutina.objetivo == "cardio"

    mock_rutina_dao.guardar.assert_called_once()

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "10, CREACION_RUTINA" in contenido_log


@pytest.mark.parametrize(
    "nombre, descripcion, nivel, duracion, creador, objetivo",
    [
        ("", "Descripción", "BASICO", 4, 1, "cardio"),
        ("   ", "Descripción", "BASICO", 4, 1, "cardio"),
        (None, "Descripción", "BASICO", 4, 1, "cardio"),
        ("Rutina", "", "BASICO", 4, 1, "cardio"),
        ("Rutina", "   ", "BASICO", 4, 1, "cardio"),
        ("Rutina", None, "BASICO", 4, 1, "cardio"),
        ("Rutina", "Descripción", "BASICO", 4, 1, ""),
        ("Rutina", "Descripción", "BASICO", 4, 1, "   "),
        ("Rutina", "Descripción", "BASICO", 4, 1, None),
        ("Rutina", "Descripción", "BASICO", True, 1, "cardio"),
        ("Rutina", "Descripción", "BASICO", "4", 1, "cardio"),
        ("Rutina", "Descripción", "BASICO", 0, 1, "cardio"),
        ("Rutina", "Descripción", "BASICO", -1, 1, "cardio"),
        ("Rutina", "Descripción", "BASICO", 2.5, 1, "cardio"),
        ("Rutina", "Descripción", "BASICO", 4, 0, "cardio"),
        ("Rutina", "Descripción", "BASICO", 4, -1, "cardio"),
        ("Rutina", "Descripción", "BASICO", 4, True, "cardio"),
        ("Rutina", "Descripción", "FACIL", 4, 1, "cardio"),
    ],
)
def test_crear_rutina_validaciones_incorrectas(
    controlador,
    nombre,
    descripcion,
    nivel,
    duracion,
    creador,
    objetivo,
):
    with pytest.raises(ValueError):
        controlador.crear_rutina(
            nombre=nombre,
            descripcion=descripcion,
            nivel_dificultad=nivel,
            duracion_estimada=duracion,
            creado_por=creador,
            objetivo=objetivo,
        )


def test_buscar_por_id_y_alias(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.buscar_por_id.return_value = (
        "rutina_mock"
    )

    assert controlador.buscar_por_id(1) == "rutina_mock"
    assert controlador.obtener_por_id(1) == "rutina_mock"

    assert mock_rutina_dao.buscar_por_id.call_count == 2

    with pytest.raises(ValueError):
        controlador.buscar_por_id(-1)


def test_listar_y_alias(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.listar.return_value = ["r1", "r2"]

    assert controlador.listar() == ["r1", "r2"]
    assert controlador.listar_rutinas() == ["r1", "r2"]

    assert mock_rutina_dao.listar.call_count == 2


def test_actualizar_rutina_con_creador_como_usuario(
    controlador,
    mock_rutina_dao,
    rutina_valida,
):
    mock_rutina_dao.actualizar.return_value = rutina_valida

    resultado = controlador.actualizar_rutina(rutina_valida)

    assert resultado is rutina_valida

    mock_rutina_dao.actualizar.assert_called_once_with(
        rutina_valida,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "10, ACTUALIZACION_RUTINA" in contenido_log


def test_actualizar_rutina_con_usuario_explicito(
    controlador,
    mock_rutina_dao,
    rutina_valida,
):
    mock_rutina_dao.actualizar.return_value = rutina_valida

    controlador.actualizar_rutina(
        rutina_valida,
        usuario_accion=99,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "99, ACTUALIZACION_RUTINA" in contenido_log


def test_actualizar_rutina_rechaza_objeto_incorrecto(
    controlador,
):
    with pytest.raises(TypeError):
        controlador.actualizar_rutina(
            "no_es_objeto_rutina",
        )


def test_actualizar_rutina_requiere_id(
    controlador,
):
    rutina_sin_id = _instanciar_rutina(
        nombre="Rutina",
        descripcion="Descripción",
        nivel_dificultad="BASICO",
        duracion_estimada=4,
        creado_por=1,
    )

    with pytest.raises(
        ValueError,
        match="debe tener un ID",
    ):
        controlador.actualizar_rutina(rutina_sin_id)


def test_eliminar_rutina_y_auditoria(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.eliminar_por_id.return_value = True

    resultado = controlador.eliminar_rutina(
        4,
        usuario_accion=1,
    )

    assert resultado is True

    mock_rutina_dao.eliminar_por_id.assert_called_once_with(
        4,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "1, ELIMINACION_RUTINA" in contenido_log


def test_eliminar_rutina_sin_eliminacion_no_registra_log(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.eliminar_por_id.return_value = False

    resultado = controlador.eliminar_rutina(
        4,
        usuario_accion=1,
    )

    assert resultado is False

    assert not controlador.ruta_log.exists()


@pytest.mark.parametrize(
    "id_rutina, usuario",
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
        (True, 1),
        (1, True),
    ],
)
def test_eliminar_rutina_rechaza_ids_invalidos(
    controlador,
    id_rutina,
    usuario,
):
    with pytest.raises(ValueError):
        controlador.eliminar_rutina(
            id_rutina,
            usuario_accion=usuario,
        )


def test_agregar_ejercicio_a_rutina_y_auditoria(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.agregar_ejercicio.return_value = True

    resultado = controlador.agregar_ejercicio_a_rutina(
        1,
        10,
        orden=2,
        usuario_accion=5,
    )

    assert resultado is True

    mock_rutina_dao.agregar_ejercicio.assert_called_once_with(
        id_rutina=1,
        id_ejercicio=10,
        orden_ejercicio=2,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "5, AGREGAR_EJERCICIO_A_RUTINA" in contenido_log


def test_agregar_ejercicio_sin_resultado_no_registra_log(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.agregar_ejercicio.return_value = False

    resultado = controlador.agregar_ejercicio_a_rutina(
        1,
        10,
        usuario_accion=5,
    )

    assert resultado is False
    assert not controlador.ruta_log.exists()


def test_agregar_ejercicio_requiere_usuario(
    controlador,
):
    with pytest.raises(
        ValueError,
        match="Debe indicar el usuario",
    ):
        controlador.agregar_ejercicio_a_rutina(
            1,
            10,
        )


@pytest.mark.parametrize(
    "id_rutina, id_ejercicio, orden, usuario",
    [
        (0, 1, 1, 1),
        (1, 0, 1, 1),
        (1, 1, 0, 1),
        (1, 1, 1, 0),
        (True, 1, 1, 1),
        (1, True, 1, 1),
        (1, 1, True, 1),
        (1, 1, 1, True),
    ],
)
def test_agregar_ejercicio_rechaza_ids_invalidos(
    controlador,
    id_rutina,
    id_ejercicio,
    orden,
    usuario,
):
    with pytest.raises(ValueError):
        controlador.agregar_ejercicio_a_rutina(
            id_rutina,
            id_ejercicio,
            orden=orden,
            usuario_accion=usuario,
        )


def test_eliminar_ejercicio_de_rutina_y_auditoria(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.eliminar_ejercicio.return_value = True

    resultado = controlador.eliminar_ejercicio_de_rutina(
        1,
        10,
        usuario_accion=5,
    )

    assert resultado is True

    mock_rutina_dao.eliminar_ejercicio.assert_called_once_with(
        id_rutina=1,
        id_ejercicio=10,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "5, ELIMINAR_EJERCICIO_DE_RUTINA" in contenido_log


def test_eliminar_ejercicio_sin_resultado_no_registra_log(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.eliminar_ejercicio.return_value = False

    resultado = controlador.eliminar_ejercicio_de_rutina(
        1,
        10,
        usuario_accion=5,
    )

    assert resultado is False
    assert not controlador.ruta_log.exists()


def test_eliminar_ejercicio_requiere_usuario(
    controlador,
):
    with pytest.raises(
        ValueError,
        match="Debe indicar el usuario",
    ):
        controlador.eliminar_ejercicio_de_rutina(
            1,
            10,
        )


def test_listar_ejercicios_y_alias(
    controlador,
    mock_rutina_dao,
):
    ejercicios = ["ejercicio_1", "ejercicio_2"]

    mock_rutina_dao.listar_ejercicios.return_value = ejercicios

    assert controlador.listar_ejercicios_de_rutina(1) == ejercicios

    assert (
        controlador.obtener_ejercicios_de_rutina(1)
        == ejercicios
    )

    assert mock_rutina_dao.listar_ejercicios.call_count == 2


def test_ejercicio_asociado_usa_metodo_del_dao(
    controlador,
    mock_rutina_dao,
):
    mock_rutina_dao.ejercicio_asociado.return_value = True

    resultado = controlador.ejercicio_asociado(1, 10)

    assert resultado is True

    mock_rutina_dao.ejercicio_asociado.assert_called_once_with(
        1,
        10,
    )


def test_ejercicio_asociado_usa_lista_si_dao_no_tiene_metodo(
    mock_asignacion_dao,
    tmp_path,
):
    rutina_dao = SimpleNamespace(
        listar_ejercicios=Mock(
            return_value=[
                SimpleNamespace(id_ejercicio=10),
                SimpleNamespace(id_ejercicio=20),
            ],
        ),
    )

    controlador_local = ControlRutinas(
        rutina_dao=rutina_dao,
        asignacion_dao=mock_asignacion_dao,
        ruta_log=str(tmp_path / "log.txt"),
    )

    assert controlador_local.ejercicio_asociado(1, 10) is True
    assert controlador_local.ejercicio_asociado(1, 99) is False

    assert rutina_dao.listar_ejercicios.call_count == 2


def test_asignar_rutina_con_rutina_activa_previa(
    controlador,
    mock_asignacion_dao,
):
    asignacion_activa = Mock()
    asignacion_activa.id_asignacion = 55

    mock_asignacion_dao.obtener_activa_por_cliente.return_value = (
        asignacion_activa
    )

    mock_asignacion_dao.asignar.return_value = {
        "id_asignacion": 56,
        "activa": True,
    }

    cliente_mock = SimpleNamespace(id_usuario=3)
    rutina_mock = SimpleNamespace(id_rutina=9)

    resultado = controlador.asignar_rutina(
        cliente_mock,
        rutina_mock,
        asignado_por=1,
        observaciones="  Nueva asignación  ",
    )

    mock_asignacion_dao.obtener_activa_por_cliente.assert_called_once_with(
        3,
    )

    mock_asignacion_dao.finalizar_asignacion.assert_called_once_with(
        55,
    )

    mock_asignacion_dao.asignar.assert_called_once_with(
        id_cliente=3,
        id_rutina=9,
        asignado_por=1,
        observaciones="Nueva asignación",
    )

    assert resultado == {
        "id_asignacion": 56,
        "activa": True,
    }

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "1, ASIGNACION_RUTINA" in contenido_log


def test_asignar_rutina_sin_activa_y_con_ids(
    controlador,
    mock_asignacion_dao,
):
    mock_asignacion_dao.obtener_activa_por_cliente.return_value = (
        None
    )

    mock_asignacion_dao.asignar.return_value = {
        "id_asignacion": 70,
        "activa": True,
    }

    resultado = controlador.asignar_rutina(
        cliente=7,
        rutina=12,
        asignado_por=2,
        observaciones=None,
    )

    mock_asignacion_dao.obtener_activa_por_cliente.assert_called_once_with(
        7,
    )

    mock_asignacion_dao.finalizar_asignacion.assert_not_called()

    mock_asignacion_dao.asignar.assert_called_once_with(
        id_cliente=7,
        id_rutina=12,
        asignado_por=2,
        observaciones="",
    )

    assert resultado == {
        "id_asignacion": 70,
        "activa": True,
    }


def test_asignar_rutina_rechaza_observaciones_no_texto(
    controlador,
):
    with pytest.raises(
        ValueError,
        match="observaciones deben ser texto",
    ):
        controlador.asignar_rutina(
            cliente=1,
            rutina=2,
            asignado_por=3,
            observaciones=123,
        )


@pytest.mark.parametrize(
    "cliente, rutina, asignado_por",
    [
        (0, 2, 3),
        (1, 0, 3),
        (1, 2, 0),
        (True, 2, 3),
        (1, True, 3),
        (1, 2, True),
        (SimpleNamespace(id_usuario=0), 2, 3),
        (1, SimpleNamespace(id_rutina=0), 3),
    ],
)
def test_asignar_rutina_rechaza_ids_invalidos(
    controlador,
    cliente,
    rutina,
    asignado_por,
):
    with pytest.raises(ValueError):
        controlador.asignar_rutina(
            cliente=cliente,
            rutina=rutina,
            asignado_por=asignado_por,
        )


def test_sugerir_rutina_exitoso(
    controlador,
    mock_rutina_dao,
):
    rutina_sugerida = Mock()

    mock_rutina_dao.sugerir_rutina.return_value = (
        rutina_sugerida
    )

    resultado = controlador.sugerir_rutina(
        id_cliente=4,
        tipo_sugerencia="  resistencia  ",
    )

    assert resultado is rutina_sugerida

    mock_rutina_dao.sugerir_rutina.assert_called_once_with(
        4,
        "RESISTENCIA",
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "CLIENTE_4, SUGERENCIA_RUTINA" in contenido_log


def test_sugerir_rutina_rechaza_tipo_invalido(
    controlador,
):
    for tipo in (
        None,
        "",
        "   ",
        1,
        True,
        [],
    ):
        with pytest.raises(ValueError):
            controlador.sugerir_rutina(
                id_cliente=1,
                tipo_sugerencia=tipo,
            )


def test_sugerir_rutina_requiere_metodo_en_dao(
    mock_asignacion_dao,
    tmp_path,
):
    rutina_dao = SimpleNamespace()

    controlador_local = ControlRutinas(
        rutina_dao=rutina_dao,
        asignacion_dao=mock_asignacion_dao,
        ruta_log=str(tmp_path / "log.txt"),
    )

    with pytest.raises(
        NotImplementedError,
        match="no implementa",
    ):
        controlador_local.sugerir_rutina(1)


def test_obtener_id_objeto_desde_atributo():
    cliente = SimpleNamespace(id_usuario=8)

    resultado = ControlRutinas._obtener_id_objeto(
        cliente,
        "El ID del cliente",
        "id_usuario",
    )

    assert resultado == 8


def test_obtener_id_objeto_desde_entero():
    resultado = ControlRutinas._obtener_id_objeto(
        9,
        "El ID de la rutina",
        "id_rutina",
    )

    assert resultado == 9