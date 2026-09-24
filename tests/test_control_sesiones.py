from unittest.mock import Mock

import pytest

from src.controladores.control_sesiones import (
    ControlSesiones,
)
from src.modelos.sesion_entrenamiento import (
    Intensidad,
)


@pytest.fixture
def mock_sesion_dao():
    """
    Crea un DAO de sesiones simulado.
    """
    return Mock()


@pytest.fixture
def controlador(
    mock_sesion_dao,
    tmp_path,
):
    """
    Crea el controlador con un archivo de auditoría temporal.
    """
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlSesiones(
        sesion_dao=mock_sesion_dao,
        ruta_log=str(log_file),
    )


def test_registrar_sesion_exitoso_y_auditoria(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica registro correcto usando objetos cliente y rutina.
    """
    mock_sesion_dao.guardar.side_effect = (
        lambda sesion: sesion
    )

    cliente_mock = Mock()
    cliente_mock.id_usuario = 15

    rutina_mock = Mock()
    rutina_mock.id_rutina = 3

    sesion = controlador.registrar_sesion(
        cliente=cliente_mock,
        rutina=rutina_mock,
        nombre_ejercicio="Circuito cardio",
        duracion_real=45,
        intensidad_real=Intensidad.ALTA,
        calorias_quemadas=400,
        observaciones="Completó todo el circuito",
    )

    assert sesion is not None

    mock_sesion_dao.guardar.assert_called_once()

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert (
        "CLIENTE_15, REGISTRO_SESION"
        in contenido_log
    )


def test_registrar_sesion_con_ids_directos(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica registro correcto usando IDs directos.
    """
    mock_sesion_dao.guardar.side_effect = (
        lambda sesion: sesion
    )

    sesion = controlador.registrar_sesion(
        cliente=5,
        rutina=2,
        nombre_ejercicio="Caminata",
        duracion_real=30,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=250,
    )

    assert sesion is not None

    mock_sesion_dao.guardar.assert_called_once()


@pytest.mark.parametrize(
    "cliente, rutina, duracion, calorias",
    [
        (0, 1, 30, 200),
        (-1, 1, 30, 200),
        ("cinco", 1, 30, 200),
        (1, -2, 30, 200),
        (1, 1, 0, 200),
        (1, 1, -30, 200),
        (1, 1, "30", 200),
        (1, 1, 30, -50),
        (1, 1, 30, "200"),
    ],
)
def test_registrar_sesion_validaciones_incorrectas(
    controlador,
    cliente,
    rutina,
    duracion,
    calorias,
):
    """
    Verifica validaciones de cliente, rutina, duración
    y calorías inválidas.
    """
    with pytest.raises(ValueError):
        controlador.registrar_sesion(
            cliente=cliente,
            rutina=rutina,
            nombre_ejercicio="Caminata",
            duracion_real=duracion,
            intensidad_real="MEDIA",
            calorias_quemadas=calorias,
        )


def test_obtener_sesiones_cliente_y_alias(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica consulta de sesiones y alias listar_por_cliente.
    """
    mock_sesion_dao.listar_por_cliente.return_value = [
        {"id_sesion": 1},
        {"id_sesion": 2},
    ]

    res1 = controlador.obtener_sesiones_cliente(10)

    res2 = controlador.listar_por_cliente(10)

    assert len(res1) == 2
    assert len(res2) == 2

    assert (
        mock_sesion_dao.listar_por_cliente.call_count
        == 2
    )


def test_eliminar_sesion_y_auditoria(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica eliminación y registro en auditoría.
    """
    mock_sesion_dao.eliminar_por_id.return_value = True

    resultado = controlador.eliminar_sesion(
        99,
        usuario_accion="admin",
    )

    assert resultado is True

    mock_sesion_dao.eliminar_por_id.assert_called_once_with(
        99
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert (
        "admin, ELIMINACION_SESION"
        in contenido_log
    )