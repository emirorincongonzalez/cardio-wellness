from unittest.mock import Mock
import pytest

from src.controladores.control_autenticacion import ControlAutenticacion


@pytest.fixture
def mock_usuario_dao():
    return Mock()


@pytest.fixture
def controlador(mock_usuario_dao, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return ControlAutenticacion(usuario_dao=mock_usuario_dao, ruta_log=str(log_file))


def test_iniciar_sesion_exitoso_registra_auditoria(controlador, mock_usuario_dao):
    usuario_esperado = Mock()
    usuario_esperado.correo_electronico = "usuario@example.com"
    mock_usuario_dao.iniciar_sesion.return_value = usuario_esperado

    resultado = controlador.iniciar_sesion("usuario@example.com", "Secreto123")

    assert resultado is usuario_esperado
    mock_usuario_dao.iniciar_sesion.assert_called_once_with("usuario@example.com", "Secreto123")

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "usuario@example.com" in contenido_log
    assert "LOGIN_EXITOSO" in contenido_log


def test_iniciar_sesion_fallido_registra_auditoria(controlador, mock_usuario_dao):
    mock_usuario_dao.iniciar_sesion.return_value = None

    resultado = controlador.iniciar_sesion("desconocido@example.com", "ClaveErronea")

    assert resultado is None
    mock_usuario_dao.iniciar_sesion.assert_called_once_with("desconocido@example.com", "ClaveErronea")

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "desconocido@example.com" in contenido_log
    assert "LOGIN_FALLIDO" in contenido_log


def test_validar_credenciales_camel_case(controlador, mock_usuario_dao):
    usuario_esperado = Mock(correo_electronico="test@example.com")
    mock_usuario_dao.iniciar_sesion.return_value = usuario_esperado

    res = controlador.validarCredenciales("test@example.com", "12345")

    assert res is usuario_esperado


def test_cerrar_sesion(controlador):
    usuario = Mock(correo_electronico="activo@example.com")
    assert controlador.cerrarSesion(usuario) is True
    assert controlador.cerrar_sesion(None) is True


@pytest.mark.parametrize("correo", ["", "   ", None, 123])
def test_iniciar_sesion_rechaza_correo_invalido(controlador, correo):
    with pytest.raises(ValueError, match="correo"):
        controlador.iniciar_sesion(correo, "Secreto123")


@pytest.mark.parametrize("contrasenia", ["", None, 123])
def test_iniciar_sesion_rechaza_contrasenia_invalida(controlador, contrasenia):
    with pytest.raises(ValueError, match="contraseña"):
        controlador.iniciar_sesion("usuario@example.com", contrasenia)