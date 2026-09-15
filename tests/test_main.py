"""Tests para main.py - Punto de entrada de la aplicación."""
import pytest
from unittest.mock import patch, MagicMock, call
import sys


def test_main_importa_correctamente():
    """Testea que main puede importarse sin errores."""
    from src import main
    assert main is not None


def test_main_inicializar_sistema_exitoso():
    """Testea que inicializar_sistema() funciona correctamente."""
    with patch('src.main.ConexionBD') as mock_bd_cls:
        mock_bd = MagicMock()
        mock_bd_cls.obtener_instancia.return_value = mock_bd
        mock_bd.verificar_integridad.return_value = True
        
        with patch('src.main.ControlAutenticacion') as mock_auth:
            with patch('src.main.ControlClientes') as mock_clientes:
                with patch('src.main.ControlRutinas') as mock_rutinas:
                    from src.main import inicializar_sistema
                    
                    resultado = inicializar_sistema()
                    
                    assert "control_auth" in resultado
                    assert "control_clientes" in resultado
                    assert "control_rutinas" in resultado
                    assert mock_bd.abrir_conexion.called


def test_main_inicializar_sistema_falla_bd():
    """Testea que inicializar_sistema() maneja error de BD."""
    with patch('src.main.ConexionBD') as mock_bd_cls:
        mock_bd = MagicMock()
        mock_bd_cls.obtener_instancia.return_value = mock_bd
        mock_bd.abrir_conexion.side_effect = Exception("Error de BD")
        
        from src.main import inicializar_sistema
        
        with pytest.raises(Exception, match="Error de BD"):
            inicializar_sistema()


def test_main_inicializar_sistema_falla_controladores():
    """Testea que inicializar_sistema() maneja error de controladores."""
    with patch('src.main.ConexionBD') as mock_bd_cls:
        mock_bd = MagicMock()
        mock_bd_cls.obtener_instancia.return_value = mock_bd
        mock_bd.verificar_integridad.return_value = True
        
        with patch('src.main.ControlAutenticacion') as mock_auth:
            mock_auth.side_effect = Exception("Error al crear controlador")
            
            from src.main import inicializar_sistema
            
            with pytest.raises(Exception, match="Error al crear controlador"):
                inicializar_sistema()


def test_main_ejecucion_normal_salir_inmediatamente():
    """Testea que main() se ejecuta y puede salir inmediatamente."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": MagicMock(),
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['4']):  # Opción 4: Salir
            with patch('src.main.print'):
                from src.main import main
                main()
        
        assert mock_inicializar.called


def test_main_opcion_1_iniciar_sesion_exitoso():
    """Testea opción 1: Iniciar sesión exitoso."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_control_auth = MagicMock()
        mock_usuario = MagicMock()
        mock_usuario.nombre = "Juan"
        mock_usuario.apellido = "Perez"
        mock_control_auth.iniciar_sesion.return_value = mock_usuario
        
        mock_controles = {
            "control_auth": mock_control_auth,
            "control_clientes": MagicMock(),
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['1', 'juan@test.com', 'Clave123!', '4']):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                assert mock_control_auth.iniciar_sesion.called
                mock_print.assert_any_call("✓ Bienvenido, Juan Perez")


def test_main_opcion_1_iniciar_sesion_fallido():
    """Testea opción 1: Iniciar sesión fallido."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_control_auth = MagicMock()
        mock_control_auth.iniciar_sesion.return_value = None  # Login fallido
        
        mock_controles = {
            "control_auth": mock_control_auth,
            "control_clientes": MagicMock(),
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['1', 'juan@test.com', 'ClaveIncorrecta', '4']):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                mock_print.assert_any_call("✗ Credenciales inválidas")


def test_main_opcion_2_registrar_cliente_exitoso():
    """Testea opción 2: Registrar cliente exitoso."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_control_clientes = MagicMock()
        mock_cliente = MagicMock()
        mock_cliente.nombre = "Juan"
        mock_cliente.apellido = "Perez"
        mock_control_clientes.registrar_cliente.return_value = mock_cliente
        
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": mock_control_clientes,
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=[
            '2',  # Registrar cliente
            'Juan',
            'Perez',
            'juan@test.com',
            'Clave123!',
            '25',
            '70.5',
            '1.75',
            'Bajar de peso',
            '4'  # Salir
        ]):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                assert mock_control_clientes.registrar_cliente.called
                mock_print.assert_any_call("✓ Cliente registrado: Juan Perez")


def test_main_opcion_2_registrar_cliente_fallido():
    """Testea opción 2: Registrar cliente fallido."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_control_clientes = MagicMock()
        mock_control_clientes.registrar_cliente.side_effect = ValueError("Error en registro")
        
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": mock_control_clientes,
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=[
            '2', 'Juan', 'Perez', 'juan@test.com', 'Clave123!',
            '25', '70.5', '1.75', 'Bajar de peso', '4'
        ]):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                mock_print.assert_any_call("✗ Error: Error en registro")


def test_main_opcion_3_ver_rutinas_con_rutinas():
    """Testea opción 3: Ver rutinas disponibles (con rutinas)."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_control_rutinas = MagicMock()
        mock_rutina = MagicMock()
        mock_rutina.nombre = "Rutina Cardio"
        mock_rutina.objetivo = "Quemar grasa"
        mock_rutina.nivel = MagicMock()
        mock_rutina.nivel.value = "Intermedio"
        mock_control_rutinas.listar.return_value = [mock_rutina]
        
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": MagicMock(),
            "control_rutinas": mock_control_rutinas,
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['3', '4']):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                assert mock_control_rutinas.listar.called
                mock_print.assert_any_call("\n=== RUTINAS DISPONIBLES ===")


def test_main_opcion_3_ver_rutinas_sin_rutinas():
    """Testea opción 3: Ver rutinas disponibles (sin rutinas)."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_control_rutinas = MagicMock()
        mock_control_rutinas.listar.return_value = []  # Sin rutinas
        
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": MagicMock(),
            "control_rutinas": mock_control_rutinas,
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['3', '4']):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                mock_print.assert_any_call("No hay rutinas disponibles")


def test_main_opcion_4_salir():
    """Testea opción 4: Salir del sistema."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": MagicMock(),
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['4']):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                mock_print.assert_any_call("\nSaliendo...")


def test_main_opcion_invalida():
    """Testea opción inválida en el menú principal."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_controles = {
            "control_auth": MagicMock(),
            "control_clientes": MagicMock(),
            "control_rutinas": MagicMock(),
        }
        mock_inicializar.return_value = mock_controles
        
        with patch('src.main.input', side_effect=['99', '4']):
            with patch('src.main.print') as mock_print:
                from src.main import main
                main()
                
                mock_print.assert_any_call("Opción inválida. Intente nuevamente.")


def test_main_keyboard_interrupt():
    """Testea manejo de KeyboardInterrupt."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_inicializar.side_effect = KeyboardInterrupt()
        
        with patch('src.main.print') as mock_print:
            from src.main import main
            main()
            
            mock_print.assert_any_call("\n\nAplicación terminada por el usuario")


def test_main_excepcion_generica():
    """Testea manejo de excepciones genéricas."""
    with patch('src.main.inicializar_sistema') as mock_inicializar:
        mock_inicializar.side_effect = Exception("Error crítico")
        
        with patch('src.main.print') as mock_print:
            with patch('src.main.sys.exit') as mock_exit:
                from src.main import main
                main()
                
                mock_print.assert_any_call("\n✗ Error crítico: Error crítico")
                assert mock_exit.called