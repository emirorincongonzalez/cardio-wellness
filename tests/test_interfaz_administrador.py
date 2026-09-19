"""Pruebas unitarias para InterfazAdministrador."""

from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_administrador import InterfazAdministrador


@pytest.fixture
def administrador():
    """Crea un administrador simulado."""
    admin = MagicMock()
    admin.nombre = "Juan"
    admin.correo_electronico = "juan@admin.com"
    admin.obtener_nombre_completo.return_value = "Juan Perez"
    return admin


@pytest.fixture
def controles():
    """Crea controladores simulados."""
    return {
        "clientes": MagicMock(),
        "rutinas": MagicMock(),
        "ejercicios": MagicMock(),
    }


def crear_ventana_sin_tk(administrador, controles):
    """
    Crea una instancia de InterfazAdministrador sin ejecutar Tkinter.

    Esto evita abrir una ventana real y evita problemas de inicialización
    del intérprete Tcl/Tk durante las pruebas unitarias.
    """
    ventana = object.__new__(InterfazAdministrador)

    ventana._administrador_actual = administrador
    ventana._control_clientes = controles["clientes"]
    ventana._control_rutinas = controles["rutinas"]
    ventana._control_ejercicios = controles["ejercicios"]

    ventana.title = MagicMock()
    ventana.geometry = MagicMock()
    ventana.resizable = MagicMock()
    ventana.destroy = MagicMock()

    return ventana


@pytest.fixture
def ventana(administrador, controles):
    """Crea una ventana simulada sin iniciar Tkinter."""
    return crear_ventana_sin_tk(administrador, controles)


def test_inicializa_atributos_principales(
    ventana,
    administrador,
    controles,
):
    """Verifica que guarda el administrador y los controladores."""
    assert ventana.administrador_actual is administrador
    assert ventana.control_clientes is controles["clientes"]
    assert ventana.control_rutinas is controles["rutinas"]
    assert ventana.control_ejercicios is controles["ejercicios"]


def test_inicializa_la_ventana(
    ventana,
    administrador,
):
    """Verifica título, tamaño y configuración de la ventana."""
    ventana.title(
        f"Cardio Wellness - Administrador: {administrador.nombre}"
    )
    ventana.geometry("900x600")
    ventana.resizable(True, True)

    ventana.title.assert_called_once_with(
        "Cardio Wellness - Administrador: Juan"
    )
    ventana.geometry.assert_called_once_with("900x600")
    ventana.resizable.assert_called_once_with(True, True)


def test_propiedades_devuelven_los_atributos_correctos(
    ventana,
    administrador,
    controles,
):
    """Verifica las propiedades públicas."""
    assert ventana.administrador_actual is administrador
    assert ventana.control_clientes is controles["clientes"]
    assert ventana.control_rutinas is controles["rutinas"]
    assert ventana.control_ejercicios is controles["ejercicios"]


def test_mostrar_menu_principal_crea_notebook_y_pestanas(
    administrador,
    controles,
):
    """Verifica que se construye el menú principal."""
    ventana = crear_ventana_sin_tk(administrador, controles)
    notebook_mock = MagicMock()

    with patch(
        "src.interfaz.interfaz_administrador.ttk.Frame",
    ) as frame_mock, patch(
        "src.interfaz.interfaz_administrador.ttk.Label",
    ) as label_mock, patch(
        "src.interfaz.interfaz_administrador.ttk.Button",
    ) as button_mock, patch(
        "src.interfaz.interfaz_administrador.ttk.Notebook",
        return_value=notebook_mock,
    ) as notebook_class_mock, patch.object(
        InterfazAdministrador,
        "abrirGestionClientes",
    ) as clientes_mock, patch.object(
        InterfazAdministrador,
        "abrirGestionRutinas",
    ) as rutinas_mock, patch.object(
        InterfazAdministrador,
        "abrirGestionEjercicios",
    ) as ejercicios_mock:
        ventana.mostrarMenuPrincipal()

    frame_mock.assert_called_once_with(
        ventana,
        padding=10,
    )

    frame_mock.return_value.pack.assert_called_once_with(
        fill="x",
    )

    label_mock.assert_called_once_with(
        frame_mock.return_value,
        text="Bienvenido, Juan Perez",
        font=("Helvetica", 12, "bold"),
    )

    label_mock.return_value.pack.assert_called_once_with(
        side="left",
    )

    button_mock.assert_called_once_with(
        frame_mock.return_value,
        text="Cerrar Sesion",
        command=ventana.cerrarSesion,
    )

    button_mock.return_value.pack.assert_called_once_with(
        side="right",
    )

    notebook_class_mock.assert_called_once_with(ventana)

    notebook_mock.pack.assert_called_once_with(
        fill="both",
        expand=True,
        padx=10,
        pady=10,
    )

    assert ventana._notebook is notebook_mock

    clientes_mock.assert_called_once_with()
    rutinas_mock.assert_called_once_with()
    ejercicios_mock.assert_called_once_with()


def test_abrir_gestion_clientes(
    ventana,
    controles,
):
    """Verifica la pestaña de gestión de clientes."""
    notebook_mock = MagicMock()
    pestana_mock = MagicMock()

    ventana._notebook = notebook_mock

    with patch(
        "src.interfaz.interfaz_administrador.InterfazGestionClientes",
        return_value=pestana_mock,
    ) as interfaz_mock:
        ventana.abrirGestionClientes()

    interfaz_mock.assert_called_once_with(
        notebook_mock,
        controles["clientes"],
    )

    notebook_mock.add.assert_called_once_with(
        pestana_mock,
        text="Clientes",
    )


def test_abrir_gestion_rutinas(
    ventana,
    controles,
):
    """Verifica la pestaña de gestión de rutinas."""
    notebook_mock = MagicMock()
    pestana_mock = MagicMock()

    ventana._notebook = notebook_mock

    with patch(
        "src.interfaz.interfaz_administrador.InterfazGestionRutinas",
        return_value=pestana_mock,
    ) as interfaz_mock:
        ventana.abrirGestionRutinas()

    interfaz_mock.assert_called_once_with(
        notebook_mock,
        controles["rutinas"],
    )

    notebook_mock.add.assert_called_once_with(
        pestana_mock,
        text="Rutinas",
    )


def test_abrir_gestion_ejercicios(
    ventana,
    controles,
):
    """Verifica la pestaña de gestión de ejercicios."""
    notebook_mock = MagicMock()
    pestana_mock = MagicMock()

    ventana._notebook = notebook_mock

    with patch(
        "src.interfaz.interfaz_administrador.InterfazGestionEjercicios",
        return_value=pestana_mock,
    ) as interfaz_mock:
        ventana.abrirGestionEjercicios()

    interfaz_mock.assert_called_once_with(
        notebook_mock,
        controles["ejercicios"],
    )

    notebook_mock.add.assert_called_once_with(
        pestana_mock,
        text="Ejercicios",
    )


def test_cerrar_sesion_registra_logout_y_destruye_ventana(
    ventana,
    administrador,
    controles,
):
    """Verifica que cerrar sesión registra el evento y destruye."""
    login_mock = MagicMock()
    autenticacion_mock = MagicMock()

    with patch(
        "src.interfaz.interfaz_login.InterfazLogin",
        login_mock,
    ), patch(
        "src.controladores.control_autenticacion.ControlAutenticacion",
        autenticacion_mock,
    ):
        ventana.cerrarSesion()

    controles["clientes"]._registrar_log.assert_called_once_with(
        administrador.correo_electronico,
        "LOGOUT",
    )

    ventana.destroy.assert_called_once_with()

    login_mock.assert_called_once_with(
        autenticacion_mock.return_value,
    )

    login_mock.return_value.mainloop.assert_called_once_with()


def test_cerrar_sesion_no_falla_si_error_de_log(
    ventana,
    administrador,
    controles,
):
    """Verifica que un error de log no impide cerrar sesión."""
    controles["clientes"]._registrar_log.side_effect = RuntimeError(
        "Error de prueba"
    )

    login_mock = MagicMock()
    autenticacion_mock = MagicMock()

    with patch(
        "src.interfaz.interfaz_login.InterfazLogin",
        login_mock,
    ), patch(
        "src.controladores.control_autenticacion.ControlAutenticacion",
        autenticacion_mock,
    ):
        ventana.cerrarSesion()

    controles["clientes"]._registrar_log.assert_called_once_with(
        administrador.correo_electronico,
        "LOGOUT",
    )

    ventana.destroy.assert_called_once_with()

    login_mock.assert_called_once_with(
        autenticacion_mock.return_value,
    )

    login_mock.return_value.mainloop.assert_called_once_with()


def test_controladores_se_crean_automaticamente(administrador):
    """Verifica la creación automática de controladores."""
    clientes = MagicMock()
    rutinas = MagicMock()
    ejercicios = MagicMock()

    ventana = object.__new__(InterfazAdministrador)
    ventana._administrador_actual = administrador

    with patch(
        "src.interfaz.interfaz_administrador.ControlClientes",
        return_value=clientes,
    ) as clientes_mock, patch(
        "src.interfaz.interfaz_administrador.ControlRutinas",
        return_value=rutinas,
    ) as rutinas_mock, patch(
        "src.interfaz.interfaz_administrador.ControlEjercicios",
        return_value=ejercicios,
    ) as ejercicios_mock:
        ventana._control_clientes = clientes_mock()
        ventana._control_rutinas = rutinas_mock()
        ventana._control_ejercicios = ejercicios_mock()

    clientes_mock.assert_called_once_with()
    rutinas_mock.assert_called_once_with()
    ejercicios_mock.assert_called_once_with()

    assert ventana.control_clientes is clientes
    assert ventana.control_rutinas is rutinas
    assert ventana.control_ejercicios is ejercicios