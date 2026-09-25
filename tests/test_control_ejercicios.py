from unittest.mock import Mock

import pytest

from src.controladores.control_ejercicios import (
    ControlEjercicios,
    _instanciar_ejercicio,
)
from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
    Intensidad,
)


@pytest.fixture
def mock_ejercicio_dao():
    """
    Crea un DAO de ejercicios simulado.
    """
    return Mock()


@pytest.fixture
def controlador(
    mock_ejercicio_dao,
    tmp_path,
):
    """
    Crea un controlador con archivo temporal de auditoría.
    """
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlEjercicios(
        ejercicio_dao=mock_ejercicio_dao,
        ruta_log=str(log_file),
    )


def test_propiedad_ejercicio_dao(
    controlador,
    mock_ejercicio_dao,
):
    """
    Verifica que la propiedad exponga el DAO inyectado.
    Cubre el return de la propiedad ejercicio_dao.
    """
    assert controlador.ejercicio_dao is mock_ejercicio_dao


def test_instanciar_ejercicio_sin_id():
    """
    Prueba helper sin identificador de ejercicio.
    """
    ejercicio = _instanciar_ejercicio(
        nombre="Caminata",
        descripcion="Caminata suave",
        duracion_minutos=20,
        calorias_estimadas=120,
    )

    assert isinstance(ejercicio, EjercicioCardio)
    assert ejercicio.nombre == "Caminata"
    assert ejercicio.descripcion == "Caminata suave"
    assert ejercicio.duracion_minutos == 20
    assert ejercicio.calorias_estimadas == 120
    assert ejercicio.id_ejercicio is None


def test_instanciar_ejercicio_con_id():
    """
    Prueba helper con identificador de ejercicio.
    """
    ejercicio = _instanciar_ejercicio(
        id_ejercicio=99,
        nombre="Bicicleta",
        descripcion="Bicicleta moderada",
        duracion_minutos=40,
        calorias_estimadas=350,
        creado_por=5,
    )

    assert isinstance(ejercicio, EjercicioCardio)
    assert ejercicio.id_ejercicio == 99
    assert ejercicio.creado_por == 5


def test_crear_ejercicio_exitoso_y_auditoria(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba creación exitosa de ejercicio y auditoría.
    """

    def guardar_ejercicio(ejercicio):
        ejercicio.id_ejercicio = 1
        return ejercicio

    mock_ejercicio_dao.guardar.side_effect = (
        guardar_ejercicio
    )

    ejercicio = controlador.crear_ejercicio(
        nombre="Cinta de correr",
        descripcion="Trote continuo ritmo medio",
        duracion_minutos=30,
        calorias_estimadas=300,
        usuario_creador=1,
    )

    assert isinstance(ejercicio, EjercicioCardio)
    assert ejercicio.id_ejercicio == 1
    assert ejercicio.nombre == "Cinta de correr"

    mock_ejercicio_dao.guardar.assert_called_once()

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "1" in contenido_log
    assert "CREACION_EJERCICIO" in contenido_log
    assert "ID: 1" in contenido_log


def test_crear_ejercicio_sin_usuario_creador(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba creación sin usuario creador.
    """

    def guardar_ejercicio(ejercicio):
        ejercicio.id_ejercicio = 20
        return ejercicio

    mock_ejercicio_dao.guardar.side_effect = (
        guardar_ejercicio
    )

    resultado = controlador.crear_ejercicio(
        nombre="Elíptica",
        descripcion="Ejercicio cardiovascular moderado",
        duracion_minutos=35,
        calorias_estimadas=280,
    )

    assert resultado.id_ejercicio == 20
    assert resultado.creado_por is None

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "sistema" in contenido_log
    assert "CREACION_EJERCICIO" in contenido_log
    assert "ID: 20" in contenido_log


def test_crear_ejercicio_acepta_intensidad_texto(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba creación usando intensidad enviada como texto.
    """

    def guardar_ejercicio(ejercicio):
        ejercicio.id_ejercicio = 30
        return ejercicio

    mock_ejercicio_dao.guardar.side_effect = (
        guardar_ejercicio
    )

    ejercicio = controlador.crear_ejercicio(
        nombre="Spinning",
        descripcion="Intervalos de bicicleta estática",
        duracion_minutos=45,
        calorias_estimadas=450,
        intensidad="ALTA",
        usuario_creador=3,
    )

    assert ejercicio.intensidad == Intensidad.ALTA


def test_crear_ejercicio_acepta_intensidad_enum(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba creación usando intensidad enviada como enum.
    """

    def guardar_ejercicio(ejercicio):
        ejercicio.id_ejercicio = 31
        return ejercicio

    mock_ejercicio_dao.guardar.side_effect = (
        guardar_ejercicio
    )

    ejercicio = controlador.crear_ejercicio(
        nombre="Remo",
        descripcion="Remo de intensidad moderada",
        duracion_minutos=25,
        calorias_estimadas=220,
        intensidad=Intensidad.MEDIA,
        usuario_creador=3,
    )

    assert ejercicio.intensidad == Intensidad.MEDIA


@pytest.mark.parametrize(
    "nombre, descripcion, duracion, calorias",
    [
        ("", "Desc", 30, 200),
        ("   ", "Desc", 30, 200),
        ("Cinta", "", 30, 200),
        ("Cinta", "Desc", 0, 200),
        ("Cinta", "Desc", -10, 200),
        ("Cinta", "Desc", "30", 200),
        ("Cinta", "Desc", 30, 0),
        ("Cinta", "Desc", 30, -50),
        ("Cinta", "Desc", 30, "200"),
    ],
)
def test_crear_ejercicio_validaciones_incorrectas(
    controlador,
    nombre,
    descripcion,
    duracion,
    calorias,
):
    """
    Prueba validaciones de creación inválida.
    """
    with pytest.raises(ValueError):
        controlador.crear_ejercicio(
            nombre=nombre,
            descripcion=descripcion,
            duracion_minutos=duracion,
            calorias_estimadas=calorias,
        )


def test_buscar_por_id_y_alias(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba búsqueda por ID y alias obtener_por_id.
    """
    mock_ejercicio_dao.buscar_por_id.return_value = (
        "ejercicio_mock"
    )

    assert controlador.buscar_por_id(5) == "ejercicio_mock"

    assert (
        controlador.obtener_por_id(5)
        == "ejercicio_mock"
    )

    assert mock_ejercicio_dao.buscar_por_id.call_count == 2


@pytest.mark.parametrize(
    "id_ejercicio",
    [
        0,
        -1,
        -10,
    ],
)
def test_buscar_por_id_rechaza_id_invalido(
    controlador,
    mock_ejercicio_dao,
    id_ejercicio,
):
    """
    Prueba IDs no positivos.
    """
    with pytest.raises(
        ValueError,
        match="ID debe ser positivo",
    ):
        controlador.buscar_por_id(id_ejercicio)

    mock_ejercicio_dao.buscar_por_id.assert_not_called()


def test_listar_y_alias(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba listado y alias listar_ejercicios.
    """
    mock_ejercicio_dao.listar.return_value = [
        "e1",
        "e2",
    ]

    assert len(controlador.listar()) == 2
    assert len(controlador.listar_ejercicios()) == 2
    assert mock_ejercicio_dao.listar.call_count == 2


def test_actualizar_ejercicio_con_creador(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba actualización de ejercicio con autor conocido.
    """
    ejercicio = _instanciar_ejercicio(
        id_ejercicio=1,
        nombre="Spinning",
        descripcion="Intervalos",
        duracion_minutos=45,
        calorias_estimadas=450,
        creado_por=7,
    )

    mock_ejercicio_dao.actualizar.return_value = ejercicio

    resultado = controlador.actualizar_ejercicio(
        ejercicio,
    )

    assert resultado == ejercicio

    mock_ejercicio_dao.actualizar.assert_called_once_with(
        ejercicio,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "7" in contenido_log
    assert "ACTUALIZACION_EJERCICIO" in contenido_log
    assert "ID: 1" in contenido_log


def test_actualizar_ejercicio_sin_creador(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba auditoría cuando no existe creador.
    """
    ejercicio = _instanciar_ejercicio(
        id_ejercicio=2,
        nombre="Caminata",
        descripcion="Caminata rápida",
        duracion_minutos=25,
        calorias_estimadas=180,
        creado_por=None,
    )

    mock_ejercicio_dao.actualizar.return_value = ejercicio

    resultado = controlador.actualizar_ejercicio(
        ejercicio,
    )

    assert resultado is ejercicio

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "sistema" in contenido_log
    assert "ACTUALIZACION_EJERCICIO" in contenido_log
    assert "ID: 2" in contenido_log


def test_actualizar_ejercicio_rechaza_tipo_incorrecto(
    controlador,
):
    """
    Prueba que actualizar rechace objetos no válidos.
    """
    with pytest.raises(
        TypeError,
        match="EjercicioCardio",
    ):
        controlador.actualizar_ejercicio(
            "no_es_instancia_ejercicio",
        )


def test_eliminar_ejercicio_y_auditoria(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba eliminación exitosa y auditoría.
    """
    mock_ejercicio_dao.eliminar_por_id.return_value = True

    resultado = controlador.eliminar_ejercicio(
        8,
        usuario_accion=1,
    )

    assert resultado is True

    mock_ejercicio_dao.eliminar_por_id.assert_called_once_with(
        8,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "1" in contenido_log
    assert "ELIMINACION_EJERCICIO" in contenido_log
    assert "ID: 8" in contenido_log


def test_eliminar_ejercicio_sin_usuario_accion(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba eliminación exitosa sin usuario.
    """
    mock_ejercicio_dao.eliminar_por_id.return_value = True

    resultado = controlador.eliminar_ejercicio(9)

    assert resultado is True

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "sistema" in contenido_log
    assert "ELIMINACION_EJERCICIO" in contenido_log
    assert "ID: 9" in contenido_log


def test_eliminar_ejercicio_sin_resultado_no_registra_log(
    controlador,
    mock_ejercicio_dao,
):
    """
    Prueba la rama donde el DAO no elimina el ejercicio.
    """
    mock_ejercicio_dao.eliminar_por_id.return_value = False

    resultado = controlador.eliminar_ejercicio(
        10,
        usuario_accion=3,
    )

    assert resultado is False

    mock_ejercicio_dao.eliminar_por_id.assert_called_once_with(
        10,
    )

    assert not controlador.ruta_log.exists()