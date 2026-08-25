from unittest.mock import Mock

import pytest

from src.controladores.control_autenticacion import ControlAutenticacion


def test_iniciar_sesion_delega_en_usuario_dao():
    usuario_dao = Mock()
    usuario_esperado = object()

    usuario_dao.iniciar_sesion.return_value = usuario_esperado

    controlador = ControlAutenticacion(usuario_dao)

    resultado = controlador.iniciar_sesion(
        " usuario@example.com ",
        "Secreto123",
    )

    assert resultado is usuario_esperado
    usuario_dao.iniciar_sesion.assert_called_once_with(
        "usuario@example.com",
        "Secreto123",
    )


@pytest.mark.parametrize("correo", ["", "   ", None, 123])
def test_iniciar_sesion_rechaza_correo_invalido(correo):
    usuario_dao = Mock()
    controlador = ControlAutenticacion(usuario_dao)

    with pytest.raises(ValueError, match="correo"):
        controlador.iniciar_sesion(correo, "Secreto123")

    usuario_dao.iniciar_sesion.assert_not_called()


@pytest.mark.parametrize("contrasenia", ["", None, 123])
def test_iniciar_sesion_rechaza_contrasenia_invalida(contrasenia):
    usuario_dao = Mock()
    controlador = ControlAutenticacion(usuario_dao)

    with pytest.raises(ValueError, match="contraseña"):
        controlador.iniciar_sesion(
            "usuario@example.com",
            contrasenia,
        )

    usuario_dao.iniciar_sesion.assert_not_called()