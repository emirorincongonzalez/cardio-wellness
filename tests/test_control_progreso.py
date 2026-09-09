from decimal import Decimal
from datetime import date
from unittest.mock import Mock
import pytest


from src.controladores.control_progreso import ControlProgreso




@pytest.fixture
def mock_progreso_dao():
    return Mock()




@pytest.fixture
def mock_sesion_dao():
    return Mock()




@pytest.fixture
def controlador(mock_progreso_dao, mock_sesion_dao, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return ControlProgreso(
        progreso_dao=mock_progreso_dao,
        sesion_dao=mock_sesion_dao,
        ruta_log=str(log_file),
    )




def test_calcular_resumen_cliente_y_auditoria(controlador, mock_sesion_dao):
    mock_sesion_dao.listar_por_cliente.return_value = [
        {"duracion_real": 30, "calorias_quemadas": 250.5},
        {"duracion_real": 45, "calorias_quemadas": 300.0},
    ]


    cliente_mock = Mock()
    cliente_mock.id_usuario = 10


    resumen = controlador.calcular_resumen_cliente(cliente_mock)


    assert resumen["total_sesiones"] == 2
    assert resumen["total_minutos"] == 75
    assert resumen["total_calorias"] == Decimal("550.5")


    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "CLIENTE_10, CONSULTA_PROGRESO" in contenido_log




def test_calcular_impacto_calorico_rutina_precision_decimal_y_auditoria(controlador):
    ej1 = Mock(calorias_estimadas=Decimal("150.25"))
    ej2 = Mock(calorias_estimadas=Decimal("200.50"))
    rutina_mock = Mock(id_rutina=5, ejercicios=[ej1, ej2])


    impacto = controlador.calcular_impacto_calorico_rutina(rutina_mock, usuario_consulta="entrenador1")


    assert impacto == Decimal("350.75")
    assert isinstance(impacto, Decimal)


    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "entrenador1, CONSULTA_IMPACTO" in contenido_log




def test_generar_progreso_mensual(controlador, mock_progreso_dao, mock_sesion_dao):
    mock_sesion_dao.listar_por_cliente.return_value = [
        {"duracion_real": 60, "calorias_quemadas": 500}
    ]
    mock_progreso_dao.guardar.side_effect = lambda p: p


    cliente_mock = Mock(id_usuario=8, peso=72.0)


    progreso = controlador.generar_progreso_mensual(
        cliente=cliente_mock,
        mes=date(2026, 8, 1),
        anio=2026,
        observaciones="Buen progreso",
    )


    assert progreso is not None
    mock_progreso_dao.guardar.assert_called_once()


    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "CLIENTE_8, GENERAR_PROGRESO" in contenido_log



def test_consultar_progreso(controlador, mock_progreso_dao):
    mock_progreso_dao.buscar_por_cliente.return_value = [{"id_progreso": 1, "mes": 8}]


    historial = controlador.consultar_progreso(cliente=12)


    assert len(historial) == 1
    mock_progreso_dao.buscar_por_cliente.assert_called_once_with(12)


    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "CLIENTE_12, CONSULTA_PROGRESO" in contenido_log