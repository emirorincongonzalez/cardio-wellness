from src.controladores.control_ejercicios import ControlEjercicios


def test_control_ejercicios_existe():
    controlador = ControlEjercicios()

    assert controlador is not None