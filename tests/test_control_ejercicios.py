from unittest.mock import Mock
import pytest

from src.controladores.control_ejercicios import ControlEjercicios, _instanciar_ejercicio
from src.modelos.ejercicio_cardio import EjercicioCardio


@pytest.fixture
def mock_ejercicio_dao():
    return Mock()


@pytest.fixture
def controlador(mock_ejercicio_dao, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return ControlEjercicios(ejercicio_dao=mock_ejercicio_dao, ruta_log=str(log_file))


def test_crear_ejercicio_exitoso_y_auditoria(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.guardar.side_effect = lambda e: e

    ejercicio = controlador.crear_ejercicio(
        nombre="Cinta de correr",
        descripcion="Trote continuo ritmo medio",
        duracion_minutos=30,
        calorias_estimadas=300,
        usuario_creador=1,
    )

    assert isinstance(ejercicio, EjercicioCardio)
    mock_ejercicio_dao.guardar.assert_called_once()

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "1, CREACION_EJERCICIO" in contenido_log


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
    controlador, nombre, descripcion, duracion, calorias
):
    with pytest.raises(ValueError):
        controlador.crear_ejercicio(
            nombre=nombre,
            descripcion=descripcion,
            duracion_minutos=duracion,
            calorias_estimadas=calorias,
        )


def test_buscar_por_id_y_alias(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.buscar_por_id.return_value = "ejercicio_mock"

    assert controlador.buscar_por_id(5) == "ejercicio_mock"
    assert controlador.obtener_por_id(5) == "ejercicio_mock"
    assert mock_ejercicio_dao.buscar_por_id.call_count == 2


def test_listar_y_alias(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.listar.return_value = ["e1", "e2"]

    assert len(controlador.listar()) == 2
    assert len(controlador.listar_ejercicios()) == 2
    assert mock_ejercicio_dao.listar.call_count == 2


def test_actualizar_ejercicio(controlador, mock_ejercicio_dao):
    ejercicio = _instanciar_ejercicio(
        id_ejercicio=1,
        nombre="Spinning",
        descripcion="Intervalos",
        duracion_minutos=45,
        calorias_estimadas=450,
    )
    mock_ejercicio_dao.actualizar.return_value = ejercicio

    resultado = controlador.actualizar_ejercicio(ejercicio)
    assert resultado == ejercicio
    mock_ejercicio_dao.actualizar.assert_called_once_with(ejercicio)

    with pytest.raises(TypeError):
        controlador.actualizar_ejercicio("no_es_instancia_ejercicio")


def test_eliminar_ejercicio_y_auditoria(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.eliminar_por_id.return_value = True

    res = controlador.eliminar_ejercicio(8, usuario_accion=1)

    assert res is True
    mock_ejercicio_dao.eliminar_por_id.assert_called_once_with(8)

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "1, ELIMINACION_EJERCICIO" in contenido_log