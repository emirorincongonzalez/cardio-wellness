from decimal import Decimal
from unittest.mock import Mock
import pytest

from src.servicios.sistema_wellness import SistemaWellness


@pytest.fixture
def mock_clientes():
    return Mock()


@pytest.fixture
def mock_rutinas():
    return Mock()


@pytest.fixture
def mock_progreso():
    return Mock()


@pytest.fixture
def mock_pdf():
    return Mock()


@pytest.fixture
def sistema(mock_clientes, mock_rutinas, mock_progreso, mock_pdf, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return SistemaWellness(
        control_clientes=mock_clientes,
        control_rutinas=mock_rutinas,
        control_progreso=mock_progreso,
        generador_pdf=mock_pdf,
        ruta_log=str(log_file),
    )


def test_evaluar_objetivo_y_sugerir_rutina_cardio(sistema, mock_rutinas):
    rutina_cardio = {"nombre": "Cardio Quema Grasa", "descripcion": "Alta quema"}
    rutina_fuerza = {"nombre": "Hipertrofia Muscular", "descripcion": "Pesas"}
    mock_rutinas.listar.return_value = [rutina_cardio, rutina_fuerza]

    cliente_peso = Mock(id_usuario=1, objetivo="Quiero perder peso y quemar grasa")
    sugerida = sistema.evaluar_objetivo_y_sugerir_rutina(cliente_peso)

    assert sugerida == rutina_cardio
    contenido_log = sistema.ruta_log.read_text(encoding="utf-8")
    assert "1, SUGERENCIA_RUTINA, CARDIO_QUEMA_GRASA" in contenido_log


def test_evaluar_objetivo_y_sugerir_rutina_fuerza(sistema, mock_rutinas):
    rutina_cardio = {"nombre": "Cardio Quema Grasa", "descripcion": "Alta quema"}
    rutina_fuerza = {"nombre": "Fuerza e Hipertrofia", "descripcion": "Pesas"}
    mock_rutinas.listar.return_value = [rutina_cardio, rutina_fuerza]

    cliente_musculo = Mock(id_usuario=2, objetivo="Aumentar volumen muscular")
    sugerida = sistema.evaluar_objetivo_y_sugerir_rutina(cliente_musculo)

    assert sugerida == rutina_fuerza
    contenido_log = sistema.ruta_log.read_text(encoding="utf-8")
    assert "2, SUGERENCIA_RUTINA, FUERZA_HIPERTROFIA" in contenido_log


def test_calcular_diferencia_peso_mensual(sistema, mock_progreso):
    mock_progreso.consultar_progreso.return_value = [
        {"mes": 8, "peso_registrado": Decimal("72.5")},
        {"mes": 7, "peso_registrado": Decimal("75.0")},
    ]

    diferencia = sistema.calcular_diferencia_peso_mensual(1)

    assert diferencia == Decimal("-2.5")
    contenido_log = sistema.ruta_log.read_text(encoding="utf-8")
    assert "CLIENTE_1, CALCULO_DIFERENCIA_PESO, DIF: -2.5" in contenido_log


def test_emitir_reporte_pdf_cliente(sistema, mock_clientes, mock_progreso, mock_pdf):
    cliente_mock = Mock(id_usuario=5, nombre="Juan", correo_electronico="juan@mail.com")
    mock_clientes.buscar_por_id.return_value = cliente_mock
    mock_progreso.calcular_resumen_cliente.return_value = {"total_sesiones": 10}
    mock_progreso.consultar_progreso.return_value = []
    mock_pdf.generar_reporte_progreso_cliente.return_value = "reportes/reporte.pdf"

    ruta = sistema.emitir_reporte_pdf_cliente(cliente_mock)

    assert ruta == "reportes/reporte.pdf"
    mock_pdf.generar_reporte_progreso_cliente.assert_called_once()
    contenido_log = sistema.ruta_log.read_text(encoding="utf-8")
    assert "juan@mail.com, REPORTE_PDF_GENERADO" in contenido_log