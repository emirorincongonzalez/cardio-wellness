from src.controladores.control_rutinas import ControlRutinas


def test_control_rutinas_existe():
    controlador = ControlRutinas()

    assert controlador is not None