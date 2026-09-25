import importlib
import runpy
import sys
from unittest.mock import MagicMock, patch

import pytest

from src import main as modulo_main


def test_inicializar_sistema_muestra_advertencia_si_integridad_falla():
    with patch(
        "src.main.ConexionBD"
    ) as mock_bd_cls, patch(
        "src.main.RutinaDAO"
    ), patch(
        "src.main.AsignacionRutinaDAO"
    ), patch(
        "src.main.UsuarioDAO"
    ), patch(
        "src.main.ClienteDAO"
    ), patch(
        "src.main.EjercicioDAO"
    ), patch(
        "src.main.SesionEntrenamientoDAO"
    ), patch(
        "src.main.ProgresoMensualDAO"
    ), patch(
        "src.main.ControlAutenticacion"
    ), patch(
        "src.main.ControlClientes"
    ), patch(
        "src.main.ControlEjercicios"
    ), patch(
        "src.main.ControlRutinas"
    ), patch(
        "src.main.ControlSesiones"
    ), patch(
        "src.main.ControlProgreso"
    ), patch(
        "src.main.print"
    ) as mock_print:

        bd = MagicMock()
        bd.verificar_integridad.return_value = False
        mock_bd_cls.obtener_instancia.return_value = bd

        resultado = modulo_main.inicializar_sistema()

    assert "control_auth" in resultado
    mock_print.assert_any_call(
        "Advertencia: verificacion de "
        "integridad fallida"
    )


def test_iniciar_interfaz_crea_ventana_y_ejecuta_mainloop():
    control_auth = MagicMock()
    controladores = {
        "control_auth": control_auth,
    }

    with patch(
        "src.main.InterfazLogin"
    ) as mock_interfaz_login:
        app = MagicMock()
        mock_interfaz_login.return_value = app

        modulo_main.iniciar_interfaz(controladores)

    mock_interfaz_login.assert_called_once_with(
        control_autenticacion=control_auth,
        controladores=controladores,
    )
    app.mainloop.assert_called_once()


def test_registrar_cliente_consola_maneja_excepcion_generica():
    control_clientes = MagicMock()
    control_clientes.registrar_cliente.side_effect = RuntimeError(
        "Fallo inesperado"
    )

    entradas = [
        "Ana",
        "Prueba",
        "ana@example.com",
        "Clave123!",
        "25",
        "70",
        "1.70",
        "Mejorar resistencia",
    ]

    with patch(
        "src.main.input",
        side_effect=entradas,
    ), patch(
        "src.main.print"
    ) as mock_print:
        modulo_main.registrar_cliente_consola(
            control_clientes
        )

    mock_print.assert_any_call(
        "✗ Error: Fallo inesperado"
    )


def test_main_iniciar_gui_abre_interfaz_y_cierra_bd():
    controladores = {
        "control_auth": MagicMock(),
        "control_clientes": MagicMock(),
        "control_rutinas": MagicMock(),
    }

    bd = MagicMock()

    with patch(
        "src.main.inicializar_sistema",
        return_value=controladores,
    ), patch(
        "src.main.ConexionBD.obtener_instancia",
        return_value=bd,
    ), patch(
        "src.main.iniciar_interfaz"
    ) as mock_iniciar_interfaz, patch(
        "src.main.print"
    ) as mock_print:

        modulo_main.main(iniciar_gui=True)

    mock_iniciar_interfaz.assert_called_once_with(
        controladores
    )
    bd.cerrar_conexion.assert_called_once()
    mock_print.assert_any_call(
        "Conexion a base de datos cerrada"
    )


def test_main_continua_si_no_puede_obtener_bd_despues_de_inicializar():
    controladores = {
        "control_auth": MagicMock(),
        "control_clientes": MagicMock(),
        "control_rutinas": MagicMock(),
    }

    with patch(
        "src.main.inicializar_sistema",
        return_value=controladores,
    ), patch(
        "src.main.ConexionBD.obtener_instancia",
        side_effect=RuntimeError("BD no disponible"),
    ), patch(
        "src.main.input",
        side_effect=["4"],
    ), patch(
        "src.main.print"
    ) as mock_print:

        modulo_main.main()

    mock_print.assert_any_call("\nSaliendo...")


def test_main_ignora_error_al_cerrar_conexion():
    controladores = {
        "control_auth": MagicMock(),
        "control_clientes": MagicMock(),
        "control_rutinas": MagicMock(),
    }

    bd = MagicMock()
    bd.cerrar_conexion.side_effect = RuntimeError(
        "No se pudo cerrar"
    )

    with patch(
        "src.main.inicializar_sistema",
        return_value=controladores,
    ), patch(
        "src.main.ConexionBD.obtener_instancia",
        return_value=bd,
    ), patch(
        "src.main.input",
        side_effect=["4"],
    ), patch(
        "src.main.print"
    ) as mock_print:

        modulo_main.main()

    bd.cerrar_conexion.assert_called_once()

    assert not any(
        "Conexion a base de datos cerrada"
        in str(llamada)
        for llamada in mock_print.call_args_list
    )

def test_main_agrega_raiz_del_proyecto_a_sys_path():
    raiz = str(modulo_main.ROOT_PROYECTO)
    sys_path_original = sys.path.copy()

    try:
        while raiz in sys.path:
            sys.path.remove(raiz)

        importlib.reload(modulo_main)

        assert raiz in sys.path

    finally:
        sys.path[:] = sys_path_original
        importlib.reload(modulo_main)

def test_ejecutar_main_como_script_inicia_gui(
    monkeypatch,
):
    """
    Verifica que src.main inicie la interfaz
    cuando se ejecuta como script.
    """
    monkeypatch.delitem(
        sys.modules,
        "src.main",
        raising=False,
    )

    with patch(
        "src.persistencia.conexion_bd.ConexionBD"
    ) as mock_bd_cls, patch(
        "src.persistencia.rutina_dao.RutinaDAO"
    ), patch(
        "src.persistencia.asignacion_rutina_dao."
        "AsignacionRutinaDAO"
    ), patch(
        "src.persistencia.usuario_dao.UsuarioDAO"
    ), patch(
        "src.persistencia.cliente_dao.ClienteDAO"
    ), patch(
        "src.persistencia.ejercicio_dao.EjercicioDAO"
    ), patch(
        "src.persistencia.sesion_entrenamiento_dao."
        "SesionEntrenamientoDAO"
    ), patch(
        "src.persistencia.progreso_mensual_dao."
        "ProgresoMensualDAO"
    ), patch(
        "src.controladores.control_autenticacion."
        "ControlAutenticacion"
    ), patch(
        "src.controladores.control_clientes.ControlClientes"
    ), patch(
        "src.controladores.control_ejercicios."
        "ControlEjercicios"
    ), patch(
        "src.controladores.control_rutinas.ControlRutinas"
    ), patch(
        "src.controladores.control_sesiones.ControlSesiones"
    ), patch(
        "src.controladores.control_progreso.ControlProgreso"
    ), patch(
        "src.interfaz.interfaz_login.InterfazLogin"
    ) as mock_interfaz_login, patch(
        "builtins.print"
    ):
        bd = MagicMock()
        bd.verificar_integridad.return_value = True
        mock_bd_cls.obtener_instancia.return_value = bd

        app = MagicMock()
        mock_interfaz_login.return_value = app

        runpy.run_module(
            "src.main",
            run_name="__main__",
        )

    mock_interfaz_login.assert_called_once()
    app.mainloop.assert_called_once()