from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.controladores.control_autenticacion import (
    ControlAutenticacion,
)


@pytest.fixture
def mock_usuario_dao():
    """
    Crea un DAO de usuarios simulado.
    """
    return Mock()


@pytest.fixture
def controlador(
    mock_usuario_dao,
    tmp_path,
):
    """
    Crea el controlador con un archivo de auditoría temporal.
    """
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlAutenticacion(
        usuario_dao=mock_usuario_dao,
        ruta_log=str(log_file),
    )


def test_iniciar_sesion_exitoso_registra_auditoria(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba inicio de sesión exitoso y auditoría.
    """
    usuario_esperado = Mock()
    usuario_esperado.correo_electronico = (
        "usuario@example.com"
    )

    mock_usuario_dao.iniciar_sesion.return_value = (
        usuario_esperado
    )

    resultado = controlador.iniciar_sesion(
        "usuario@example.com",
        "Secreto123",
    )

    assert resultado is usuario_esperado
    assert controlador.obtener_usuario_actual() is usuario_esperado
    assert controlador.esta_autenticado() is True

    mock_usuario_dao.iniciar_sesion.assert_called_once_with(
        "usuario@example.com",
        "Secreto123",
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "usuario@example.com" in contenido_log
    assert "LOGIN_EXITOSO" in contenido_log


def test_iniciar_sesion_normaliza_correo(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba que el correo se convierta a minúsculas y se limpien
    espacios antes de enviarlo al DAO.
    """
    usuario_esperado = Mock()
    usuario_esperado.correo_electronico = (
        "correo@ejemplo.com"
    )

    mock_usuario_dao.iniciar_sesion.return_value = (
        usuario_esperado
    )

    resultado = controlador.iniciar_sesion(
        "  CORREO@EJEMPLO.COM  ",
        "Clave123!",
    )

    assert resultado is usuario_esperado

    mock_usuario_dao.iniciar_sesion.assert_called_once_with(
        "correo@ejemplo.com",
        "Clave123!",
    )


def test_iniciar_sesion_fallido_registra_auditoria(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba inicio de sesión fallido y auditoría.
    """
    mock_usuario_dao.iniciar_sesion.return_value = None

    resultado = controlador.iniciar_sesion(
        "desconocido@example.com",
        "ClaveErronea",
    )

    assert resultado is None
    assert controlador.obtener_usuario_actual() is None
    assert controlador.esta_autenticado() is False

    mock_usuario_dao.iniciar_sesion.assert_called_once_with(
        "desconocido@example.com",
        "ClaveErronea",
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "desconocido@example.com" in contenido_log
    assert "LOGIN_FALLIDO" in contenido_log


def test_validar_credenciales_camel_case(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba el alias validarCredenciales.
    """
    usuario_esperado = Mock(
        correo_electronico="test@example.com"
    )

    mock_usuario_dao.iniciar_sesion.return_value = (
        usuario_esperado
    )

    resultado = controlador.validarCredenciales(
        "test@example.com",
        "12345",
    )

    assert resultado is usuario_esperado

    mock_usuario_dao.iniciar_sesion.assert_called_once_with(
        "test@example.com",
        "12345",
    )


def test_validar_credenciales_normaliza_correo(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba validar_credenciales con un correo válido que requiere
    eliminación de espacios y conversión a minúsculas.
    """
    usuario_esperado = Mock()

    mock_usuario_dao.iniciar_sesion.return_value = (
        usuario_esperado
    )

    resultado = controlador.validar_credenciales(
        "  PRUEBA@EJEMPLO.COM  ",
        "Clave123!",
    )

    assert resultado is usuario_esperado

    mock_usuario_dao.iniciar_sesion.assert_called_once_with(
        "prueba@ejemplo.com",
        "Clave123!",
    )


@pytest.mark.parametrize(
    "correo",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_validar_credenciales_rechaza_correo_invalido(
    controlador,
    mock_usuario_dao,
    correo,
):
    """
    Prueba que validar_credenciales retorne None si el correo no es
    válido y no consulte el DAO.
    """
    resultado = controlador.validar_credenciales(
        correo,
        "Clave123!",
    )

    assert resultado is None

    mock_usuario_dao.iniciar_sesion.assert_not_called()


@pytest.mark.parametrize(
    "contrasenia",
    [
        "",
        None,
        123,
    ],
)
def test_validar_credenciales_rechaza_contrasenia_invalida(
    controlador,
    mock_usuario_dao,
    contrasenia,
):
    """
    Prueba que validar_credenciales retorne None si la contraseña no
    es válida y no consulte el DAO.
    """
    resultado = controlador.validar_credenciales(
        "usuario@example.com",
        contrasenia,
    )

    assert resultado is None

    mock_usuario_dao.iniciar_sesion.assert_not_called()


def test_cerrar_sesion_sin_usuario(
    controlador,
):
    """
    Prueba cierre de sesión cuando no hay usuario autenticado.
    """
    assert controlador.obtener_usuario_actual() is None
    assert controlador.esta_autenticado() is False

    resultado = controlador.cerrar_sesion()

    assert resultado is True
    assert controlador.obtener_usuario_actual() is None
    assert controlador.esta_autenticado() is False


def test_cerrar_sesion_con_usuario_actual_registra_logout(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba que cerrar sesión use el usuario almacenado, lo elimine
    de la sesión y escriba un evento LOGOUT en auditoría.
    """
    usuario = Mock()
    usuario.correo_electronico = "activo@example.com"

    mock_usuario_dao.iniciar_sesion.return_value = usuario

    controlador.iniciar_sesion(
        "activo@example.com",
        "Clave123!",
    )

    assert controlador.obtener_usuario_actual() is usuario
    assert controlador.esta_autenticado() is True

    resultado = controlador.cerrar_sesion()

    assert resultado is True
    assert controlador.obtener_usuario_actual() is None
    assert controlador.esta_autenticado() is False

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "activo@example.com" in contenido_log
    assert "LOGOUT" in contenido_log


def test_cerrar_sesion_con_usuario_recibido_registra_logout(
    controlador,
):
    """
    Prueba cerrar_sesion cuando recibe explícitamente el usuario.
    """
    usuario = Mock()
    usuario.correo_electronico = "manual@example.com"

    resultado = controlador.cerrarSesion(usuario)

    assert resultado is True
    assert controlador.obtener_usuario_actual() is None

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "manual@example.com" in contenido_log
    assert "LOGOUT" in contenido_log


@pytest.mark.parametrize(
    "correo",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_iniciar_sesion_rechaza_correo_invalido(
    controlador,
    correo,
):
    """
    Prueba que correo inválido lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="correo",
    ):
        controlador.iniciar_sesion(
            correo,
            "Secreto123",
        )


@pytest.mark.parametrize(
    "contrasenia",
    [
        "",
        None,
        123,
    ],
)
def test_iniciar_sesion_rechaza_contrasenia_invalida(
    controlador,
    contrasenia,
):
    """
    Prueba que contraseña inválida lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="contraseña",
    ):
        controlador.iniciar_sesion(
            "usuario@example.com",
            contrasenia,
        )


def test_registrar_administrador_exitoso(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba registro exitoso de administrador.
    """
    from src.modelos.administrador import (
        Administrador,
    )

    correo = (
        f"test.admin.{uuid4().hex[:8]}"
        "@example.com"
    )

    administrador_guardado = Administrador(
        nombre="Test",
        apellido="Admin",
        correo_electronico=correo,
        contrasenia_hash="hash123",
        edad=30,
    )

    administrador_guardado.id_usuario = 1

    mock_usuario_dao.guardar.return_value = (
        administrador_guardado
    )

    administrador = controlador.registrar_administrador(
        nombre="  Test  ",
        apellido="  Admin  ",
        correo_electronico=f"  {correo.upper()}  ",
        contrasenia_plana="Clave123!",
        edad=30,
    )

    assert administrador is administrador_guardado
    assert administrador.nombre == "Test"

    mock_usuario_dao.guardar.assert_called_once()

    argumentos, _ = mock_usuario_dao.guardar.call_args

    administrador_enviado = argumentos[0]
    contrasenia_enviada = argumentos[1]

    assert administrador_enviado.nombre == "Test"
    assert administrador_enviado.apellido == "Admin"
    assert administrador_enviado.correo_electronico == (
        correo.lower()
    )
    assert contrasenia_enviada == "Clave123!"


def test_registrar_administrador_registra_log_si_se_guarda(
    controlador,
    mock_usuario_dao,
    caplog,
):
    """
    Prueba que se registre auditoría mediante el logger global si
    el DAO guarda correctamente al administrador.
    """
    administrador_guardado = Mock()
    administrador_guardado.id_usuario = 1

    mock_usuario_dao.guardar.return_value = (
        administrador_guardado
    )

    with caplog.at_level("INFO"):
        resultado = controlador.registrar_administrador(
            nombre="Ana",
            apellido="Pérez",
            correo_electronico="ana@example.com",
            contrasenia_plana="Clave123!",
            edad=28,
        )

    assert resultado is administrador_guardado

    assert "ana@example.com" in caplog.text
    assert "REGISTRO_ADMINISTRADOR" in caplog.text
    assert "Nuevo administrador registrado" in caplog.text


def test_registrar_administrador_no_registra_log_si_no_guarda(
    controlador,
    mock_usuario_dao,
):
    """
    Prueba la rama donde el DAO no devuelve un administrador.
    """
    mock_usuario_dao.guardar.return_value = None

    resultado = controlador.registrar_administrador(
        nombre="Ana",
        apellido="Pérez",
        correo_electronico="ana@example.com",
        contrasenia_plana="Clave123!",
        edad=28,
    )

    assert resultado is None

    mock_usuario_dao.guardar.assert_called_once()


@pytest.mark.parametrize(
    "nombre",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_registrar_administrador_nombre_invalido(
    controlador,
    nombre,
):
    """
    Prueba que nombre inválido lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="nombre",
    ):
        controlador.registrar_administrador(
            nombre=nombre,
            apellido="Admin",
            correo_electronico="test@example.com",
            contrasenia_plana="Clave123!",
            edad=30,
        )


@pytest.mark.parametrize(
    "apellido",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_registrar_administrador_apellido_invalido(
    controlador,
    apellido,
):
    """
    Prueba que apellido inválido lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="apellido",
    ):
        controlador.registrar_administrador(
            nombre="Test",
            apellido=apellido,
            correo_electronico="test@example.com",
            contrasenia_plana="Clave123!",
            edad=30,
        )


@pytest.mark.parametrize(
    "correo",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_registrar_administrador_correo_invalido(
    controlador,
    correo,
):
    """
    Prueba que correo inválido lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="correo",
    ):
        controlador.registrar_administrador(
            nombre="Test",
            apellido="Admin",
            correo_electronico=correo,
            contrasenia_plana="Clave123!",
            edad=30,
        )


@pytest.mark.parametrize(
    "contrasenia",
    [
        "",
        None,
        123,
    ],
)
def test_registrar_administrador_contrasenia_invalida(
    controlador,
    contrasenia,
):
    """
    Prueba que contraseña inválida lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="contraseña",
    ):
        controlador.registrar_administrador(
            nombre="Test",
            apellido="Admin",
            correo_electronico="test@example.com",
            contrasenia_plana=contrasenia,
            edad=30,
        )


@pytest.mark.parametrize(
    "edad",
    [
        0,
        -1,
        None,
        "30",
        25.5,
        True,
        False,
    ],
)
def test_registrar_administrador_edad_invalida(
    controlador,
    edad,
):
    """
    Prueba que una edad inválida lance ValueError.
    """
    with pytest.raises(
        ValueError,
        match="[Ee]dad",
    ):
        controlador.registrar_administrador(
            nombre="Test",
            apellido="Admin",
            correo_electronico="test@example.com",
            contrasenia_plana="Clave123!",
            edad=edad,
        )