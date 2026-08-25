from src.controladores.control_sesiones import ControlSesiones


def test_control_sesiones_existe():
    controlador = ControlSesiones()

    assert controlador is not None