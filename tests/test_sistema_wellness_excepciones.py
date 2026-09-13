"""
Tests para cubrir casos edge en SistemaWellness (CU02 - Sugerir Rutina Inicial).
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from src.servicios.sistema_wellness import SistemaWellness, _normalizar_texto
from src.modelos.cliente import Cliente
from src.modelos.rutina import Rutina
from src.modelos.enums import NivelRutina


@pytest.fixture
def sistema():
    """Crea SistemaWellness con mocks."""
    control_clientes = Mock()
    control_rutinas = Mock()
    control_progreso = Mock()
    generador_pdf = Mock()
    
    return SistemaWellness(
        control_clientes=control_clientes,
        control_rutinas=control_rutinas,
        control_progreso=control_progreso,
        generador_pdf=generador_pdf,
    )


def test_sugerir_rutina_sin_rutinas_disponibles(sistema):
    """Prueba que sugerir rutina sin rutinas retorna None."""
    sistema.control_rutinas.listar.return_value = []
    
    cliente = Mock()
    cliente.objetivo = "Perder peso"
    
    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(cliente)
    assert resultado is None


def test_sugerir_rutina_objetivo_perder_peso(sistema):
    """Prueba sugerencia para objetivo de perder peso."""
    rutina_cardio = Mock()
    rutina_cardio.nombre = "Cardio Quema Grasa"
    rutina_cardio.descripcion = "Rutina para quemar grasa"
    
    sistema.control_rutinas.listar.return_value = [rutina_cardio]
    
    cliente = Mock()
    cliente.objetivo = "Perder peso y quemar grasa"
    cliente.id_usuario = 1
    
    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(cliente)
    assert resultado == rutina_cardio
    sistema.control_rutinas.listar.assert_called_once()


def test_sugerir_rutina_objetivo_fuerza(sistema):
    """Prueba sugerencia para objetivo de fuerza/hipertrofia."""
    rutina_fuerza = Mock()
    rutina_fuerza.nombre = "Fuerza e Hipertrofia"
    rutina_fuerza.descripcion = "Rutina de fuerza"
    
    sistema.control_rutinas.listar.return_value = [rutina_fuerza]
    
    cliente = Mock()
    cliente.objetivo = "Ganar musculo y fuerza"
    cliente.id_usuario = 2
    
    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(cliente)
    assert resultado == rutina_fuerza


def test_sugerir_rutina_fallback_primera_rutina(sistema):
    """Prueba que retorna primera rutina cuando no hay coincidencia."""
    rutina_generic = Mock()
    rutina_generic.nombre = "Rutina General"
    rutina_generic.descripcion = "Rutina basica"
    
    sistema.control_rutinas.listar.return_value = [rutina_generic]
    
    cliente = Mock()
    cliente.objetivo = "Objetivo sin coincidencia"
    cliente.id_usuario = 3
    
    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(cliente)
    assert resultado == rutina_generic


def test_calcular_diferencia_peso_sin_historial(sistema):
    """Prueba calcular diferencia con menos de 2 registros."""
    sistema.control_progreso.consultar_progreso.return_value = []
    
    resultado = sistema.calcular_diferencia_peso_mensual(1)
    assert resultado == Decimal("0.0")


def test_calcular_diferencia_peso_un_solo_registro(sistema):
    """Prueba calcular diferencia con solo 1 registro."""
    sistema.control_progreso.consultar_progreso.return_value = [
        {"peso_registrado": 70.0}
    ]
    
    resultado = sistema.calcular_diferencia_peso_mensual(1)
    assert resultado == Decimal("0.0")


def test_calcular_diferencia_peso_con_historial(sistema):
    """Prueba calcular diferencia con 2+ registros."""
    sistema.control_progreso.consultar_progreso.return_value = [
        {"peso_registrado": 68.0},  # Actual
        {"peso_registrado": 70.0},  # Anterior
    ]
    
    resultado = sistema.calcular_diferencia_peso_mensual(1)
    assert resultado == Decimal("-2.0")


def test_emitir_reporte_pdf_con_id_cliente(sistema):
    """Prueba generar reporte PDF con ID de cliente."""
    cliente_mock = Mock()
    cliente_mock.id_usuario = 1
    cliente_mock.correo_electronico = "test@example.com"
    
    sistema.control_clientes.buscar_por_id.return_value = cliente_mock
    sistema.control_progreso.calcular_resumen_cliente.return_value = {"total_sesiones": 10}
    sistema.control_progreso.consultar_progreso.return_value = []
    sistema.generador_pdf.generar_reporte_progreso_cliente.return_value = "reporte.pdf"
    
    resultado = sistema.emitir_reporte_pdf_cliente(1)
    assert resultado == "reporte.pdf"
    sistema.control_clientes.buscar_por_id.assert_called_once_with(1)


def test_normalizar_texto_con_tildes():
    """Prueba normalización de texto con tildes."""
    assert _normalizar_texto("PÉSO") == "PESO"
    assert _normalizar_texto("MÚSCULO") == "MUSCULO"
    assert _normalizar_texto("cardio") == "CARDIO"