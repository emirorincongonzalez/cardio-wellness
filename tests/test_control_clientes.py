from unittest.mock import Mock
import pytest

from src.controladores.control_clientes import ControlClientes
from src.modelos.cliente import Cliente


@pytest.fixture
def mock_cliente_dao():
    return Mock()


@pytest.fixture
def controlador(mock_cliente_dao):
    return ControlClientes(cliente_dao=mock_cliente_dao)


def test_registrar_cliente_exitoso(controlador, mock_cliente_dao):
    mock_cliente_dao.guardar.side_effect = lambda c: c

    cliente = controlador.registrar_cliente(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@example.com",
        contrasenia_plana="Password123",
        edad=28,
        peso=75.5,
        altura=1.78,
        objetivo="Ganar masa muscular",
    )

    assert isinstance(cliente, Cliente)
    assert cliente.nombre == "Carlos"
    mock_cliente_dao.guardar.assert_called_once()


@pytest.mark.parametrize("clave_invalida", ["", None, 12345])
def test_registrar_cliente_clave_invalida(controlador, clave_invalida):
    with pytest.raises((ValueError, TypeError)):
        controlador.registrar_cliente(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana=clave_invalida,
            edad=28,
            peso=75.5,
            altura=1.78,
            objetivo="Perder peso",
        )


def test_obtener_por_id_valido(controlador, mock_cliente_dao):
    mock_cliente_dao.buscar_por_id.return_value = "cliente_dummy"

    res = controlador.obtener_por_id(10)

    assert res == "cliente_dummy"
    mock_cliente_dao.buscar_por_id.assert_called_once_with(10)


@pytest.mark.parametrize("id_invalido", [0, -5, "10", None, True, False])
def test_obtener_por_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.obtener_por_id(id_invalido)


def test_obtener_por_correo_valido(controlador, mock_cliente_dao):
    mock_cliente_dao.buscar_por_correo.return_value = "cliente_dummy"

    res = controlador.obtener_por_correo(" carlos@example.com ")

    assert res == "cliente_dummy"
    mock_cliente_dao.buscar_por_correo.assert_called_once_with("carlos@example.com")


@pytest.mark.parametrize("correo_invalido", ["", "   ", None, 123])
def test_obtener_por_correo_invalido(controlador, correo_invalido):
    with pytest.raises(ValueError):
        controlador.obtener_por_correo(correo_invalido)


def test_listar_clientes(controlador, mock_cliente_dao):
    mock_cliente_dao.listar.return_value = ["c1", "c2"]

    res = controlador.listar_clientes()

    assert len(res) == 2
    mock_cliente_dao.listar.assert_called_once()


def test_actualizar_cliente_valido(controlador, mock_cliente_dao):
    cliente = Cliente(
        id_usuario=1,
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@example.com",
        contrasenia_hash="hash",
        edad=29,
        peso=74.0,
        altura=1.78,
        objetivo="Mantenimiento",
    )
    mock_cliente_dao.actualizar.return_value = cliente

    res = controlador.actualizar_cliente(cliente)

    assert res.edad == 29
    mock_cliente_dao.actualizar.assert_called_once_with(cliente)


def test_actualizar_cliente_tipo_invalido(controlador):
    with pytest.raises(TypeError):
        controlador.actualizar_cliente("no_es_cliente")


def test_cambiar_contrasenia_exitoso(controlador, mock_cliente_dao):
    mock_cliente_dao.actualizar_contrasenia.return_value = True

    res = controlador.cambiar_contrasenia(1, "Vieja123", "Nueva456")

    assert res is True
    mock_cliente_dao.actualizar_contrasenia.assert_called_once_with(1, "Vieja123", "Nueva456")


@pytest.mark.parametrize("id_invalido", [0, -1, "abc", None, False])
def test_cambiar_contrasenia_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.cambiar_contrasenia(id_invalido, "Vieja123", "Nueva456")


def test_eliminar_cliente_valido(controlador, mock_cliente_dao):
    mock_cliente_dao.eliminar_por_id.return_value = None

    controlador.eliminar_cliente(5)

    mock_cliente_dao.eliminar_por_id.assert_called_once_with(5)


@pytest.mark.parametrize("id_invalido", [0, -2, "5", None, True])
def test_eliminar_cliente_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.eliminar_cliente(id_invalido)