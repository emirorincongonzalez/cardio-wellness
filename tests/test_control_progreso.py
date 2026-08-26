from unittest.mock import Mock
import pytest

from src.controladores.control_progreso import ControlProgreso


@pytest.fixture
def mock_cliente_dao():
    return Mock()


@pytest.fixture
def mock_rutina_dao():
    return Mock()


@pytest.fixture
def controlador(mock_cliente_dao, mock_rutina_dao):
    return ControlProgreso(
        cliente_dao=mock_cliente_dao,
        rutina_dao=mock_rutina_dao,
    )


def test_calcular_resumen_cliente_exitoso(controlador, mock_cliente_dao):
    mock_cliente = Mock()
    mock_cliente.id_usuario = 5
    mock_cliente.obtener_nombre_completo.return_value = "Laura Gómez"
    mock_cliente.peso = 62.0
    mock_cliente.altura = 1.65
    mock_cliente.objetivo = "Tonificar"
    mock_cliente.fecha_ingreso = "2026-01-10"
    mock_cliente_dao.buscar_por_id.return_value = mock_cliente

    resumen = controlador.calcular_resumen_cliente(5)

    assert resumen["id_cliente"] == 5
    assert resumen["nombre_completo"] == "Laura Gómez"
    assert resumen["peso_actual"] == 62.0


@pytest.mark.parametrize("id_invalido", [0, -1, "5", None, False])
def test_calcular_resumen_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.calcular_resumen_cliente(id_invalido)


def test_calcular_resumen_cliente_no_existe(controlador, mock_cliente_dao):
    mock_cliente_dao.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="cliente"):
        controlador.calcular_resumen_cliente(999)


def test_calcular_impacto_calorico_rutina_exitoso(controlador, mock_rutina_dao):
    ej1 = Mock(calorias_estimadas=150)
    ej2 = Mock(calorias_estimadas=200)

    mock_rutina = Mock()
    mock_rutina.nombre = "Cardio Intenso"
    mock_rutina.ejercicios = [ej1, ej2]
    mock_rutina.calcular_duracion_total.return_value = 35
    mock_rutina_dao.buscar_por_id.return_value = mock_rutina

    impacto = controlador.calcular_impacto_calorico_rutina(2)

    assert impacto["id_rutina"] == 2
    assert impacto["cantidad_ejercicios"] == 2
    assert impacto["duracion_total_minutos"] == 35
    assert impacto["calorias_estimadas_totales"] == 350.0


@pytest.mark.parametrize("id_invalido", [0, -3, "2", None, True])
def test_calcular_impacto_id_invalido(controlador, id_invalido):
    with pytest.raises(ValueError):
        controlador.calcular_impacto_calorico_rutina(id_invalido)


def test_calcular_impacto_rutina_no_existe(controlador, mock_rutina_dao):
    mock_rutina_dao.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="rutina"):
        controlador.calcular_impacto_calorico_rutina(999)