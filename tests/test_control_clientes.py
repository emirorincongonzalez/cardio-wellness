from src.controladores.control_clientes import ControlClientes


def test_control_clientes_existe():
    controlador = ControlClientes()

    assert controlador is not None