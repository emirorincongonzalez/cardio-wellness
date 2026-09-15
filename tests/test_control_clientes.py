from unittest.mock import Mock
import pytest

from src.controladores.control_clientes import ControlClientes
from src.modelos.cliente import Cliente


@pytest.fixture
def mock_cliente_dao():
    return Mock()


@pytest.fixture
def controlador(mock_cliente_dao, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return ControlClientes(cliente_dao=mock_cliente_dao, ruta_log=str(log_file))


def test_registrar_cliente_exitoso_y_auditoria(controlador, mock_cliente_dao):
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

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "carlos@example.com" in contenido_log
    assert "REGISTRO_CLIENTE" in contenido_log


def test_registrar_cliente_error_dao_amigable(controlador, mock_cliente_dao):
    mock_cliente_dao.guardar.side_effect = ValueError("El correo ya está registrado.")

    with pytest.raises(ValueError, match="Error al registrar el cliente"):
        controlador.registrar_cliente(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana="Password123",
            edad=28,
            peso=75.5,
            altura=1.78,
            objetivo="Perder peso",
        )


@pytest.mark.parametrize(
    "edad, peso, altura",
    [
        (0, 70, 1.75),
        (-5, 70, 1.75),
        ("28", 70, 1.75),
        (28, 0, 1.75),
        (28, -70, 1.75),
        (28, "70", 1.75),
        (28, 70, 0),
        (28, 70, -1.75),
        (28, 70, "1.75"),
    ],
)
def test_registrar_cliente_validaciones_numericas(controlador, edad, peso, altura):
    with pytest.raises(ValueError):
        controlador.registrar_cliente(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana="Password123",
            edad=edad,
            peso=peso,
            altura=altura,
            objetivo="Salud",
        )


def test_buscar_por_id_y_alias(controlador, mock_cliente_dao):
    mock_cliente_dao.buscar_por_id.return_value = "cliente_dummy"

    assert controlador.buscar_por_id(10) == "cliente_dummy"
    assert controlador.obtener_por_id(10) == "cliente_dummy"
    assert mock_cliente_dao.buscar_por_id.call_count == 2


def test_buscar_por_correo_y_alias(controlador, mock_cliente_dao):
    mock_cliente_dao.buscar_por_correo.return_value = "cliente_dummy"

    assert controlador.buscar_por_correo("carlos@example.com") == "cliente_dummy"
    assert controlador.obtener_por_correo("carlos@example.com") == "cliente_dummy"
    assert mock_cliente_dao.buscar_por_correo.call_count == 2


def test_listar_y_alias(controlador, mock_cliente_dao):
    mock_cliente_dao.listar.return_value = ["c1", "c2"]

    assert len(controlador.listar()) == 2
    assert len(controlador.listar_clientes()) == 2
    assert mock_cliente_dao.listar.call_count == 2


def test_eliminar_cliente_y_auditoria(controlador, mock_cliente_dao):
    mock_cliente_dao.eliminar_por_id.return_value = True

    res = controlador.eliminar_cliente(5)

    assert res is True
    mock_cliente_dao.eliminar_por_id.assert_called_once_with(5)

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "ID_5" in contenido_log
    assert "ELIMINACION_CLIENTE" in contenido_log

    # ============================================================================
# TESTS ADICIONALES PARA COBERTURA COMPLETA
# ============================================================================

def test_buscar_por_id_con_id_invalido():
    """Testea buscar_por_id con ID inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.buscar_por_id(-1)
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.buscar_por_id(0)
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.buscar_por_id(True)


def test_buscar_por_correo_con_correo_invalido():
    """Testea buscar_por_correo con correo inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="correo"):
        control.buscar_por_correo("")
    
    with pytest.raises(ValueError, match="correo"):
        control.buscar_por_correo("   ")


def test_listar_clientes():
    """Testea listar() cuando retorna lista vacía."""
    from src.controladores.control_clientes import ControlClientes
    from unittest.mock import MagicMock
    
    mock_dao = MagicMock()
    mock_dao.listar.return_value = []
    
    control = ControlClientes(cliente_dao=mock_dao)
    resultado = control.listar()
    
    assert resultado == []
    assert mock_dao.listar.called


def test_actualizar_cliente_con_tipo_invalido():
    """Testea actualizar_cliente con objeto que no es Cliente."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(TypeError, match="Cliente"):
        control.actualizar_cliente("no es un cliente")
    
    with pytest.raises(TypeError, match="Cliente"):
        control.actualizar_cliente(123)
    
    with pytest.raises(TypeError, match="Cliente"):
        control.actualizar_cliente(None)


def test_cambiar_contrasenia_con_id_invalido():
    """Testea cambiar_contrasenia con ID inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.cambiar_contrasenia(-1, "Clave123!", "NuevaClave123!")
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.cambiar_contrasenia(0, "Clave123!", "NuevaClave123!")
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.cambiar_contrasenia(True, "Clave123!", "NuevaClave123!")


def test_cambiar_contrasenia_con_nueva_contrasenia_vacia():
    """Testea cambiar_contrasenia con nueva contraseña vacía."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="contraseña"):
        control.cambiar_contrasenia(1, "Clave123!", "")
    
    with pytest.raises(ValueError, match="contraseña"):
        control.cambiar_contrasenia(1, "Clave123!", None)


def test_eliminar_cliente_con_id_invalido():
    """Testea eliminar_cliente con ID inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.eliminar_cliente(-1)
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.eliminar_cliente(0)
    
    with pytest.raises(ValueError, match="id de usuario"):
        control.eliminar_cliente(True)


def test_consultar_progreso_con_id_invalido():
    """Testea consultar_progreso con ID inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.consultar_progreso(-1)
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.consultar_progreso(0)
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.consultar_progreso(True)


def test_generar_progreso_mensual_con_id_invalido():
    """Testea generar_progreso_mensual con ID inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.generar_progreso_mensual(-1)
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.generar_progreso_mensual(0)
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.generar_progreso_mensual(True)


def test_calcular_diferencia_peso_con_id_invalido():
    """Testea calcular_diferencia_peso con ID inválido."""
    from src.controladores.control_clientes import ControlClientes
    
    control = ControlClientes()
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.calcular_diferencia_peso(-1)
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.calcular_diferencia_peso(0)
    
    with pytest.raises(ValueError, match="id de cliente"):
        control.calcular_diferencia_peso(True)