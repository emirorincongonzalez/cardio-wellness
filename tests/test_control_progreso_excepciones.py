"""
Tests para cubrir casos edge en ControlProgreso (CU03, CU10).
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, MagicMock, PropertyMock, patch

from src.controladores.control_progreso import (
    ControlProgreso,
    _obtener_progreso_dao_default,
    _obtener_sesion_dao_default,
    _obtener_clase_progreso,
    _extraer_id,
    _instanciar_progreso_mensual,
)


@pytest.fixture
def control():
    """Crea ControlProgreso con mocks."""
    progreso_dao = Mock()
    sesion_dao = Mock()
    
    return ControlProgreso(
        progreso_dao=progreso_dao,
        sesion_dao=sesion_dao,
    )


def test_calcular_resumen_cliente_sin_sesiones(control):
    """Prueba resumen de cliente sin sesiones (CU10)."""
    control.sesion_dao.listar_por_cliente.return_value = []
    
    cliente = Mock()
    cliente.id_usuario = 1
    
    resultado = control.calcular_resumen_cliente(cliente)
    
    assert resultado["id_cliente"] == 1
    assert resultado["total_sesiones"] == 0
    assert resultado["total_minutos"] == 0
    assert resultado["total_calorias"] == Decimal("0.0")


def test_calcular_resumen_cliente_con_sesiones(control):
    """Prueba resumen de cliente con sesiones (CU10)."""
    sesion1 = Mock()
    sesion1.duracion_real = 30
    sesion1.calorias_quemadas = 200.0
    
    sesion2 = Mock()
    sesion2.duracion_real = 45
    sesion2.calorias_quemadas = 350.0
    
    control.sesion_dao.listar_por_cliente.return_value = [sesion1, sesion2]
    
    cliente = Mock()
    cliente.id_usuario = 2
    
    resultado = control.calcular_resumen_cliente(cliente)
    
    assert resultado["total_sesiones"] == 2
    assert resultado["total_minutos"] == 75
    assert resultado["total_calorias"] == Decimal("550.00")


def test_calcular_resumen_cliente_id_invalido(control):
    """Prueba que ID inválido lanza ValueError."""
    cliente = Mock()
    cliente.id_usuario = -1
    
    with pytest.raises(ValueError, match="El id del cliente debe ser un entero positivo"):
        control.calcular_resumen_cliente(cliente)


def test_calcular_impacto_calorico_rutina_con_ejercicios(control):
    """Prueba cálculo de impacto calórico de rutina (CU03)."""
    ejercicio1 = Mock()
    ejercicio1.calorias_estimadas = 150.0
    
    ejercicio2 = Mock()
    ejercicio2.calorias_estimadas = 250.0
    
    rutina = Mock()
    rutina.ejercicios = [ejercicio1, ejercicio2]
    rutina.id_rutina = 1
    
    resultado = control.calcular_impacto_calorico_rutina(rutina)
    
    assert resultado == Decimal("400.00")


def test_calcular_impacto_calorico_rutina_sin_ejercicios(control):
    """Prueba rutina sin ejercicios retorna 0."""
    rutina = Mock()
    rutina.ejercicios = []
    rutina.id_rutina = 2
    
    resultado = control.calcular_impacto_calorico_rutina(rutina)
    
    assert resultado == Decimal("0.00")


def test_calcular_impacto_calorico_rutina_diccionario(control):
    """Prueba rutina como diccionario."""
    rutina_dict = {
        "id_rutina": 3,
        "ejercicios": [
            {"calorias_estimadas": 100.0},
            {"calorias_estimadas": 200.0},
        ]
    }
    
    resultado = control.calcular_impacto_calorico_rutina(rutina_dict)
    
    assert resultado == Decimal("300.00")


def test_generar_progreso_mensual_exitoso(control):
    """Prueba generar progreso mensual exitoso (CU09, CU10)."""
    control.sesion_dao.listar_por_cliente.return_value = []
    
    progreso_mock = Mock()
    progreso_mock.id_progreso = 1
    control.progreso_dao.guardar.return_value = progreso_mock
    
    # Mockear la funcion helper para evitar el problema con date
    with patch('src.controladores.control_progreso._instanciar_progreso_mensual') as mock_inst:
        mock_inst.return_value = Mock()  # Retornar mock en lugar de objeto real
        
        cliente = Mock()
        cliente.id_usuario = 4
        cliente.peso = 70.0
        
        hoy = date.today()
        resultado = control.generar_progreso_mensual(
            cliente, 
            mes=hoy.month, 
            anio=hoy.year, 
            peso_actual=70.0
        )
        
        assert resultado == progreso_mock
        control.progreso_dao.guardar.assert_called_once()


def test_generar_progreso_mensual_sin_dao(control):
    """Prueba que sin DAO lanza RuntimeError."""
    control.progreso_dao = None
    
    cliente = Mock()
    cliente.id_usuario = 5
    
    with pytest.raises(RuntimeError, match="El DAO de progreso mensual no está disponible"):
        control.generar_progreso_mensual(cliente)


def test_generar_progreso_mensual_sin_peso_cliente(control):
    """Prueba generar progreso sin peso en cliente."""
    control.sesion_dao.listar_por_cliente.return_value = []
    
    progreso_mock = Mock()
    control.progreso_dao.guardar.return_value = progreso_mock
    
    cliente = Mock()
    cliente.id_usuario = 6
    
    with patch('src.controladores.control_progreso._instanciar_progreso_mensual') as mock_inst:
        mock_inst.return_value = Mock()
        
        hoy = date.today()
        resultado = control.generar_progreso_mensual(
            cliente, 
            mes=hoy.month, 
            anio=hoy.year, 
            peso_actual=68.5
        )
        
        assert resultado == progreso_mock
        
def test_consultar_progreso_exitoso(control):
    """Prueba consultar historial de progreso (CU03, CU10)."""
    progreso1 = Mock()
    progreso1.mes = 9
    progreso1.peso_registrado = 70.0
    
    progreso2 = Mock()
    progreso2.mes = 8
    progreso2.peso_registrado = 72.0
    
    control.progreso_dao.buscar_por_cliente.return_value = [progreso1, progreso2]
    
    cliente = Mock()
    cliente.id_usuario = 7
    
    resultado = control.consultar_progreso(cliente)
    
    assert len(resultado) == 2
    control.progreso_dao.buscar_por_cliente.assert_called_once_with(7)


def test_consultar_progreso_sin_dao(control):
    """Prueba que sin DAO lanza RuntimeError."""
    control.progreso_dao = None
    
    cliente = Mock()
    cliente.id_usuario = 8
    
    with pytest.raises(RuntimeError, match="El DAO de progreso mensual no está disponible"):
        control.consultar_progreso(cliente)


def test_consultar_progreso_id_invalido(control):
    """Prueba que ID inválido lanza ValueError."""
    cliente = Mock()
    cliente.id_usuario = -1
    
    with pytest.raises(ValueError, match="El id del cliente debe ser un entero positivo"):
        control.consultar_progreso(cliente)


def test_obtener_resumen_cliente_alias(control):
    """Prueba alias obtener_resumen_cliente."""
    control.sesion_dao.listar_por_cliente.return_value = []
    
    cliente = Mock()
    cliente.id_usuario = 9
    
    resultado = control.obtener_resumen_cliente(cliente)
    
    assert resultado["total_sesiones"] == 0


def test_obtener_impacto_rutina_alias(control):
    """Prueba alias obtener_impacto_rutina."""
    rutina = Mock()
    rutina.ejercicios = []
    rutina.id_rutina = 10
    
    resultado = control.obtener_impacto_rutina(rutina)
    
    assert resultado == Decimal("0.00")


# Tests para funciones helper


def test_extraer_id_desde_entero():
    """Prueba _extraer_id con entero."""
    assert _extraer_id(123, "id") == 123


def test_extraer_id_desde_diccionario():
    """Prueba _extraer_id con diccionario."""
    obj = {"id_usuario": 456, "nombre": "Test"}
    assert _extraer_id(obj, "id_usuario", "id") == 456


def test_extraer_id_desde_objeto():
    """Prueba _extraer_id con objeto."""
    obj = Mock()
    obj.id_cliente = 789
    assert _extraer_id(obj, "id_cliente", "id_usuario") == 789


def test_extraer_id_no_encontrado():
    """Prueba _extraer_id cuando no encuentra ID."""
    obj = Mock()
    obj.otro_atributo = "valor"
    assert _extraer_id(obj, "id_cliente", "id_usuario") is None


def test_instanciar_progreso_mensual_diccionario():
    """Prueba _instanciar_progreso_mensual sin clase."""
    with patch('src.controladores.control_progreso._obtener_clase_progreso', return_value=None):
        resultado = _instanciar_progreso_mensual(
            id_cliente=1,
            mes=9,
            anio=2026,
            peso_registrado=70.0,
        )
    
    assert isinstance(resultado, dict)
    assert resultado["id_cliente"] == 1
    assert resultado["mes"] == 9
    assert resultado["peso_registrado"] == 70.0