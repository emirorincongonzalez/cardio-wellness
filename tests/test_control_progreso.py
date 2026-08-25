from src.controladores.control_progreso import ControlProgreso


def test_control_progreso_existe():
    controlador = ControlProgreso()

    assert controlador is not None