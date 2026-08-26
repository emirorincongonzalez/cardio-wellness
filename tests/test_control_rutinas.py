from unittest.mock import Mock
import pytest

from src.controladores.control_rutinas import ControlRutinas
from src.modelos.enums import NivelRutina
from src.modelos.rutina import Rutina


@pytest.fixture
def mock_rutina_dao():
    return Mock()


@pytest.fixture
def controlador(mock_rutina_dao):
    return ControlRutinas(rutina_dao=mock_rutina_dao)


def test_crear_rutina_exitosa(controlador, mock_rutina_dao):
    mock_rutina_dao.guardar.side_effect = lambda r: r

    rutina = controlador.crear_rutina(
        nombre="Cardio Quema Grasa",
        descripcion="Rutina intensa de intervalos",
        objetivo="Bajar de peso",
        nivel=NivelRutina.INTERMEDIO,
        duracion_semanas=6,
        creado_por=1,
    )

    assert isinstance(rutina, Rutina)
    assert rutina.nombre == "Cardio Quema Grasa"
    mock_rutina_dao.guardar.assert_called_once()


@pytest.mark.parametrize("duracion_invalida", [0, -2, "6", None, False])
def test_crear_rutina_duracion_invalida(controlador, duracion_invalida):
    with pytest.raises(ValueError):
        controlador.crear_rutina(
            nombre="Cardio Quema Grasa",
            descripcion="Rutina intensa de intervalos",
            objetivo="Bajar de peso",
            nivel="INTERMEDIO",
            duracion_semanas=duracion_invalida,
        )


def test_obtener_por_id_valido(controlador, mock_rutina_dao):
    mock_rutina_dao.buscar_por_id.return_value = "rutina_mock"

    res = controlador.obtener_por_id(3)

    assert res == "rutina_mock"
    mock_rutina_dao.buscar_por_id.assert_called_once_with(3)


@pytest.mark.parametrize("id_invalido", [0, -1, "3", None, True])
def test_obtener_por_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.obtener_por_id(id_invalido)


def test_listar_rutinas(controlador, mock_rutina_dao):
    mock_rutina_dao.listar.return_value = ["r1", "r2", "r3"]

    res = controlador.listar_rutinas()

    assert len(res) == 3
    mock_rutina_dao.listar.assert_called_once()


def test_actualizar_rutina_valida(controlador, mock_rutina_dao):
    rutina = Rutina(
        id_rutina=1,
        nombre="Rutina Pro",
        descripcion="Avanzada",
        objetivo="Resistencia",
        nivel=NivelRutina.AVANZADO,
        duracion_semanas=8,
    )
    mock_rutina_dao.actualizar.return_value = rutina

    res = controlador.actualizar_rutina(rutina)

    assert res.nombre == "Rutina Pro"
    mock_rutina_dao.actualizar.assert_called_once_with(rutina)


def test_actualizar_rutina_tipo_invalido(controlador):
    with pytest.raises(TypeError):
        controlador.actualizar_rutina("no_es_rutina")


def test_agregar_ejercicio_a_rutina_exitoso(controlador, mock_rutina_dao):
    mock_rutina_dao.agregar_ejercicio.return_value = True

    res = controlador.agregar_ejercicio_a_rutina(
        id_rutina=1,
        id_ejercicio=5,
        orden_ejercicio=2,
    )

    assert res is True
    mock_rutina_dao.agregar_ejercicio.assert_called_once_with(
        id_rutina=1,
        id_ejercicio=5,
        orden_ejercicio=2,
    )


@pytest.mark.parametrize(
    "id_r, id_e, orden",
    [
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 0),
        ("1", 1, 1),
        (1, "1", 1),
        (1, 1, "1"),
        (None, 1, 1),
        (True, 1, 1),
    ],
)
def test_agregar_ejercicio_parametros_invalidos(controlador, id_r, id_e, orden):
    with pytest.raises(ValueError):
        controlador.agregar_ejercicio_a_rutina(id_r, id_e, orden)


def test_eliminar_ejercicio_de_rutina(controlador, mock_rutina_dao):
    mock_rutina_dao.eliminar_ejercicio.return_value = True

    res = controlador.eliminar_ejercicio_de_rutina(id_rutina=1, id_ejercicio=5)

    assert res is True
    mock_rutina_dao.eliminar_ejercicio.assert_called_once_with(
        id_rutina=1,
        id_ejercicio=5,
    )


@pytest.mark.parametrize("id_invalido", [0, -1, "1", None, False])
def test_eliminar_ejercicio_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.eliminar_ejercicio_de_rutina(id_invalido, 5)


def test_listar_ejercicios_de_rutina(controlador, mock_rutina_dao):
    mock_rutina_dao.listar_ejercicios.return_value = ["e1", "e2"]

    res = controlador.listar_ejercicios_de_rutina(1)

    assert len(res) == 2
    mock_rutina_dao.listar_ejercicios.assert_called_once_with(1)


def test_eliminar_rutina_valida(controlador, mock_rutina_dao):
    mock_rutina_dao.eliminar_por_id.return_value = True

    res = controlador.eliminar_rutina(2)

    assert res is True
    mock_rutina_dao.eliminar_por_id.assert_called_once_with(2)


@pytest.mark.parametrize("id_invalido", [0, -5, "2", None, True])
def test_eliminar_rutina_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.eliminar_rutina(id_invalido)