from unittest.mock import Mock
import pytest

from src.controladores.control_sesiones import ControlSesiones


@pytest.fixture
def mock_cliente_dao():
    return Mock()


@pytest.fixture
def mock_rutina_dao():
    return Mock()


@pytest.fixture
def controlador(mock_cliente_dao, mock_rutina_dao):
    return ControlSesiones(
        cliente_dao=mock_cliente_dao,
        rutina_dao=mock_rutina_dao,
    )


def test_iniciar_sesion_exitosa(controlador, mock_cliente_dao, mock_rutina_dao):
    mock_cliente = Mock()
    mock_cliente.obtener_nombre_completo.return_value = "Carlos Pérez"
    mock_cliente_dao.buscar_por_id.return_value = mock_cliente

    mock_rutina = Mock()
    mock_rutina.nombre = "Cardio Quema Grasa"
    mock_rutina.calcular_duracion_total.return_value = 45
    mock_rutina_dao.buscar_por_id.return_value = mock_rutina

    sesion = controlador.iniciar_sesion_entrenamiento(1, 10)

    assert sesion["id_cliente"] == 1
    assert sesion["id_rutina"] == 10
    assert sesion["cliente_nombre"] == "Carlos Pérez"
    assert sesion["duracion_estimada_minutos"] == 45
    assert sesion["estado"] == "EN_PROGRESO"


@pytest.mark.parametrize("id_c, id_r", [(0, 1), (1, 0), ("1", 1), (1, None), (False, 1)])
def test_iniciar_sesion_ids_invalidos(controlador, id_c, id_r):
    with pytest.raises(ValueError):
        controlador.iniciar_sesion_entrenamiento(id_c, id_r)


def test_iniciar_sesion_cliente_no_existe(controlador, mock_cliente_dao, mock_rutina_dao):
    mock_cliente_dao.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="cliente"):
        controlador.iniciar_sesion_entrenamiento(99, 1)


def test_iniciar_sesion_rutina_no_existe(controlador, mock_cliente_dao, mock_rutina_dao):
    mock_cliente_dao.buscar_por_id.return_value = Mock()
    mock_rutina_dao.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="rutina"):
        controlador.iniciar_sesion_entrenamiento(1, 99)


def test_registrar_fin_sesion_exitoso(controlador):
    sesion = {"estado": "EN_PROGRESO", "id_cliente": 1}

    res = controlador.registrar_fin_sesion(
        sesion=sesion,
        minutos_reales=40,
        calorias_quemadas=320,
    )

    assert res["estado"] == "FINALIZADA"
    assert res["minutos_reales"] == 40
    assert res["calorias_quemadas"] == 320


@pytest.mark.parametrize(
    "sesion, min_reales, cal",
    [
        ({"estado": "FINALIZADA"}, 40, 300),
        ("no_dict", 40, 300),
        ({"estado": "EN_PROGRESO"}, 0, 300),
        ({"estado": "EN_PROGRESO"}, 40, -10),
        ({"estado": "EN_PROGRESO"}, "40", 300),
    ],
)
def test_registrar_fin_sesion_invalido(controlador, sesion, min_reales, cal):
    with pytest.raises(ValueError):
        controlador.registrar_fin_sesion(sesion, min_reales, cal)