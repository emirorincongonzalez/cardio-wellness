from decimal import Decimal
from unittest.mock import Mock
import pytest

from src.controladores.control_ejercicios import ControlEjercicios
from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.enums import Intensidad


@pytest.fixture
def mock_ejercicio_dao():
    return Mock()


@pytest.fixture
def controlador(mock_ejercicio_dao):
    return ControlEjercicios(ejercicio_dao=mock_ejercicio_dao)


def test_crear_ejercicio_exitoso(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.guardar.side_effect = lambda e: e

    ejercicio = controlador.crear_ejercicio(
        nombre="Cinta HIIT",
        descripcion="Intervalos en cinta de correr",
        tipo="Cardio",
        duracion_minutos=30,
        intensidad=Intensidad.ALTA,
        calorias_estimadas=350,
        creado_por=1,
    )

    assert isinstance(ejercicio, EjercicioCardio)
    assert ejercicio.nombre == "Cinta HIIT"
    assert ejercicio.duracion_minutos == 30
    mock_ejercicio_dao.guardar.assert_called_once()


@pytest.mark.parametrize("duracion_invalida", [0, -10, "30", None, False])
def test_crear_ejercicio_duracion_invalida(controlador, duracion_invalida):
    with pytest.raises(ValueError):
        controlador.crear_ejercicio(
            nombre="Bicicleta",
            descripcion="Pedaleo continuo",
            tipo="Cardio",
            duracion_minutos=duracion_invalida,
            intensidad=Intensidad.MEDIA,
            calorias_estimadas=200,
        )


def test_obtener_por_id_valido(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.buscar_por_id.return_value = "ejercicio_mock"

    res = controlador.obtener_por_id(4)

    assert res == "ejercicio_mock"
    mock_ejercicio_dao.buscar_por_id.assert_called_once_with(4)


@pytest.mark.parametrize("id_invalido", [0, -3, "4", None, True])
def test_obtener_por_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.obtener_por_id(id_invalido)


def test_listar_ejercicios(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.listar.return_value = ["e1", "e2", "e3"]

    res = controlador.listar_ejercicios()

    assert len(res) == 3
    mock_ejercicio_dao.listar.assert_called_once()


def test_actualizar_ejercicio_valido(controlador, mock_ejercicio_dao):
    ejercicio = EjercicioCardio(
        id_ejercicio=1,
        nombre="Remo Indoor",
        descripcion="Cardio total",
        tipo="Cardio",
        duracion_minutos=25,
        intensidad=Intensidad.ALTA,
        calorias_estimadas=300,
    )
    mock_ejercicio_dao.actualizar.return_value = ejercicio

    res = controlador.actualizar_ejercicio(ejercicio)

    assert res.nombre == "Remo Indoor"
    mock_ejercicio_dao.actualizar.assert_called_once_with(ejercicio)


def test_actualizar_ejercicio_tipo_invalido(controlador):
    with pytest.raises(TypeError):
        controlador.actualizar_ejercicio("no_es_ejercicio")


def test_eliminar_ejercicio_valido(controlador, mock_ejercicio_dao):
    mock_ejercicio_dao.eliminar_por_id.return_value = True

    res = controlador.eliminar_ejercicio(7)

    assert res is True
    mock_ejercicio_dao.eliminar_por_id.assert_called_once_with(7)


@pytest.mark.parametrize("id_invalido", [0, -1, "7", None, False])
def test_eliminar_ejercicio_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.eliminar_ejercicio(id_invalido)