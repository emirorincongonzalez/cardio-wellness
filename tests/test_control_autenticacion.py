from unittest.mock import Mock
import pytest
from uuid import uuid4

from src.controladores.control_autenticacion import ControlAutenticacion


@pytest.fixture
def mock_usuario_dao():
    return Mock()


@pytest.fixture
def controlador(mock_usuario_dao, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return ControlAutenticacion(usuario_dao=mock_usuario_dao, ruta_log=str(log_file))


def test_iniciar_sesion_exitoso_registra_auditoria(controlador, mock_usuario_dao):
    """Prueba iniciar sesión exitoso que registra auditoría."""
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
    """Prueba iniciar sesión fallido que registra auditoría."""
    mock_usuario_dao.iniciar_sesion.return_value = None

    resultado = controlador.iniciar_sesion("desconocido@example.com", "ClaveErronea")

    assert resultado is None
    mock_usuario_dao.iniciar_sesion.assert_called_once_with("desconocido@example.com", "ClaveErronea")

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "desconocido@example.com" in contenido_log
    assert "LOGIN_FALLIDO" in contenido_log


def test_validar_credenciales_camel_case(controlador, mock_usuario_dao):
    """Prueba validar credenciales con método camelCase."""
    usuario_esperado = Mock(correo_electronico="test@example.com")
    mock_usuario_dao.iniciar_sesion.return_value = usuario_esperado

    res = controlador.validarCredenciales("test@example.com", "12345")

    assert res is usuario_esperado


def test_cerrar_sesion(controlador):
    """Prueba cerrar sesión."""
    usuario = Mock(correo_electronico="activo@example.com")
    assert controlador.cerrarSesion(usuario) is True
    assert controlador.cerrar_sesion(None) is True


@pytest.mark.parametrize("correo", ["", "   ", None, 123])
def test_iniciar_sesion_rechaza_correo_invalido(controlador, correo):
    """Prueba que correo inválido lanza ValueError."""
    with pytest.raises(ValueError, match="correo"):
        controlador.iniciar_sesion(correo, "Secreto123")


@pytest.mark.parametrize("contrasenia", ["", None, 123])
def test_iniciar_sesion_rechaza_contrasenia_invalida(controlador, contrasenia):
    """Prueba que contraseña inválida lanza ValueError."""
    with pytest.raises(ValueError, match="contraseña"):
        controlador.iniciar_sesion("usuario@example.com", contrasenia)


def test_registrar_administrador_exitoso(controlador, mock_usuario_dao):
    """Prueba registrar administrador exitoso."""
    from src.modelos.administrador import Administrador
    
    # Mock del administrador que se guardará
    admin_mock = Administrador(
        nombre="Test",
        apellido="Admin",
        correo_electronico=f"test.admin.{uuid4().hex[:8]}@example.com",
        contrasenia_hash="hash123",
        edad=30,
    )
    admin_mock.id_usuario = 1
    
    mock_usuario_dao.guardar.return_value = admin_mock
    
    control = ControlAutenticacion(usuario_dao=mock_usuario_dao)
    
    admin = control.registrar_administrador(
        nombre="Test",
        apellido="Admin",
        correo_electronico=admin_mock.correo_electronico,
        contrasenia_plana="Clave123",
        edad=30,
    )
    
    assert admin is not None
    assert admin.nombre == "Test"
    mock_usuario_dao.guardar.assert_called_once()


def test_registrar_administrador_nombre_vacio(controlador, mock_usuario_dao):
    """Prueba que nombre vacío lanza ValueError."""
    control = ControlAutenticacion(usuario_dao=mock_usuario_dao)
    
    with pytest.raises(ValueError, match="El nombre no puede estar vacío"):
        control.registrar_administrador(
            nombre="",
            apellido="Admin",
            correo_electronico="test@example.com",
            contrasenia_plana="Clave123",
            edad=30,
        )


def test_registrar_administrador_apellido_vacio(controlador, mock_usuario_dao):
    """Prueba que apellido vacío lanza ValueError."""
    control = ControlAutenticacion(usuario_dao=mock_usuario_dao)
    
    with pytest.raises(ValueError, match="El apellido no puede estar vacío"):
        control.registrar_administrador(
            nombre="Test",
            apellido="",
            correo_electronico="test@example.com",
            contrasenia_plana="Clave123",
            edad=30,
        )


def test_registrar_administrador_edad_invalida(controlador, mock_usuario_dao):
    """Prueba que edad inválida lanza ValueError."""
    control = ControlAutenticacion(usuario_dao=mock_usuario_dao)
    
    with pytest.raises(ValueError, match="La edad debe ser un número entero mayor que cero"):
        control.registrar_administrador(
            nombre="Test",
            apellido="Admin",
            correo_electronico="test@example.com",
            contrasenia_plana="Clave123",
            edad=0,
        )