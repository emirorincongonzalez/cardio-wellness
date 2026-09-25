"""Pruebas unitarias para InterfazAdministrador."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import tkinter as tk

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

def crear_administrador_real():
    """
    Crea un administrador simple sin MagicMock para pruebas puntuales.
    """
    return SimpleNamespace(
        nombre="Ana",
        correo_electronico="ana@admin.com",
        obtener_nombre_completo=lambda: "Ana López",
    )


def test_constructor_configura_ventana_con_controladores_explicitos(
    administrador,
    controles,
):
    """
    Verifica el constructor real sin iniciar una ventana Tk.
    """
    control_autenticacion = MagicMock()

    with patch.object(
        tk.Tk,
        "__init__",
        return_value=None,
    ) as mock_tk_init, patch.object(
        InterfazAdministrador,
        "title",
    ) as mock_title, patch.object(
        InterfazAdministrador,
        "geometry",
    ) as mock_geometry, patch.object(
        InterfazAdministrador,
        "resizable",
    ) as mock_resizable, patch.object(
        InterfazAdministrador,
        "mostrarMenuPrincipal",
    ) as mock_menu:
        ventana = InterfazAdministrador(
            administrador_actual=administrador,
            control_clientes=controles["clientes"],
            control_rutinas=controles["rutinas"],
            control_ejercicios=controles["ejercicios"],
            control_autenticacion=control_autenticacion,
        )

    mock_tk_init.assert_called_once_with()

    mock_title.assert_called_once_with(
        "Cardio Wellness - Administrador: Juan Perez"
    )

    mock_geometry.assert_called_once_with("900x600")
    mock_resizable.assert_called_once_with(True, True)
    mock_menu.assert_called_once_with()

    assert ventana.administrador_actual is administrador
    assert ventana.control_clientes is controles["clientes"]
    assert ventana.control_rutinas is controles["rutinas"]
    assert ventana.control_ejercicios is controles["ejercicios"]
    assert ventana.control_autenticacion is control_autenticacion

    assert ventana.controladores == {
        "control_auth": control_autenticacion,
        "control_autenticacion": control_autenticacion,
        "control_clientes": controles["clientes"],
        "control_rutinas": controles["rutinas"],
        "control_ejercicios": controles["ejercicios"],
    }


def test_constructor_usa_diccionario_controladores(
    administrador,
):
    """
    Verifica que el constructor obtenga dependencias desde controladores.
    """
    clientes = MagicMock()
    rutinas = MagicMock()
    ejercicios = MagicMock()
    autenticacion = MagicMock()

    controladores = {
        "control_clientes": clientes,
        "control_rutinas": rutinas,
        "control_ejercicios": ejercicios,
        "control_auth": autenticacion,
        "configuracion_extra": "valor",
    }

    with patch.object(
        tk.Tk,
        "__init__",
        return_value=None,
    ), patch.object(
        InterfazAdministrador,
        "title",
    ), patch.object(
        InterfazAdministrador,
        "geometry",
    ), patch.object(
        InterfazAdministrador,
        "resizable",
    ), patch.object(
        InterfazAdministrador,
        "mostrarMenuPrincipal",
    ):
        ventana = InterfazAdministrador(
            administrador_actual=administrador,
            controladores=controladores,
        )

    assert ventana.control_clientes is clientes
    assert ventana.control_rutinas is rutinas
    assert ventana.control_ejercicios is ejercicios
    assert ventana.control_autenticacion is autenticacion

    assert ventana.controladores["control_auth"] is autenticacion

    assert (
        ventana.controladores["control_autenticacion"]
        is autenticacion
    )

    assert ventana.controladores["configuracion_extra"] == "valor"


@pytest.mark.parametrize(
    ("argumentos", "mensaje"),
    [
        (
            {
                "administrador_actual": None,
                "control_clientes": MagicMock(),
                "control_rutinas": MagicMock(),
                "control_ejercicios": MagicMock(),
                "control_autenticacion": MagicMock(),
            },
            "Debe existir un administrador autenticado.",
        ),
        (
            {
                "administrador_actual": MagicMock(),
                "control_clientes": None,
                "control_rutinas": MagicMock(),
                "control_ejercicios": MagicMock(),
                "control_autenticacion": MagicMock(),
            },
            "InterfazAdministrador requiere un "
            "ControlClientes inicializado.",
        ),
        (
            {
                "administrador_actual": MagicMock(),
                "control_clientes": MagicMock(),
                "control_rutinas": None,
                "control_ejercicios": MagicMock(),
                "control_autenticacion": MagicMock(),
            },
            "InterfazAdministrador requiere un "
            "ControlRutinas inicializado.",
        ),
        (
            {
                "administrador_actual": MagicMock(),
                "control_clientes": MagicMock(),
                "control_rutinas": MagicMock(),
                "control_ejercicios": None,
                "control_autenticacion": MagicMock(),
            },
            "InterfazAdministrador requiere un "
            "ControlEjercicios inicializado.",
        ),
        (
            {
                "administrador_actual": MagicMock(),
                "control_clientes": MagicMock(),
                "control_rutinas": MagicMock(),
                "control_ejercicios": MagicMock(),
                "control_autenticacion": None,
            },
            "InterfazAdministrador requiere un "
            "ControlAutenticacion inicializado.",
        ),
    ],
)
def test_constructor_valida_dependencias_obligatorias(
    argumentos,
    mensaje,
):
    """
    Verifica los errores de validación del constructor.
    """
    with patch.object(
        tk.Tk,
        "__init__",
        return_value=None,
    ):
        with pytest.raises(ValueError) as error:
            InterfazAdministrador(**argumentos)

    assert str(error.value) == mensaje

def test_obtener_nombre_administrador_usa_atributo_nombre(
    controles,
):
    """
    Verifica el fallback a nombre cuando no existe un método utilizable.
    """
    administrador_simple = SimpleNamespace(nombre="Carlos")

    ventana = crear_ventana_sin_tk(
        administrador_simple,
        controles,
    )

    assert ventana._obtener_nombre_administrador() == "Carlos"


def test_es_modo_pruebas_es_verdadero_sin_control_autenticacion(
    ventana,
):
    """
    Verifica detección de instancia parcial de pruebas.
    """
    assert ventana._es_modo_pruebas() is True


def test_es_modo_pruebas_es_verdadero_sin_diccionario_controladores(
    ventana,
):
    """
    Verifica detección cuando falta el diccionario de controladores.
    """
    ventana._control_autenticacion = MagicMock()

    assert ventana._es_modo_pruebas() is True


def test_es_modo_pruebas_es_falso_con_atributos_reales(
    ventana,
):
    """
    Verifica detección de instancia creada por la aplicación.
    """
    ventana._control_autenticacion = MagicMock()
    ventana._controladores = {
        "control_auth": ventana._control_autenticacion,
    }

    assert ventana._es_modo_pruebas() is False


def test_abrir_gestion_rutinas_modo_real(
    ventana,
    controles,
):
    """
    Verifica que rutinas reciba todas las dependencias en modo real.
    """
    notebook_mock = MagicMock()
    autenticacion = MagicMock()
    pestana_mock = MagicMock()

    ventana._notebook = notebook_mock
    ventana._control_autenticacion = autenticacion
    ventana._controladores = {
        "control_auth": autenticacion,
    }

    with patch(
        "src.interfaz.interfaz_administrador."
        "InterfazGestionRutinas",
        return_value=pestana_mock,
    ) as interfaz_mock:
        ventana.abrirGestionRutinas()

    interfaz_mock.assert_called_once_with(
        master=notebook_mock,
        control_rutinas=controles["rutinas"],
        control_autenticacion=autenticacion,
        control_ejercicios=controles["ejercicios"],
    )

    notebook_mock.add.assert_called_once_with(
        pestana_mock,
        text="Rutinas",
    )


def test_cerrar_sesion_modo_real_reutiliza_controladores(
    ventana,
    administrador,
    controles,
):
    """
    Verifica que el cierre real reutilice autenticación y dependencias.
    """
    autenticacion = MagicMock()

    ventana._control_autenticacion = autenticacion
    ventana._controladores = {
        "control_auth": autenticacion,
        "control_clientes": controles["clientes"],
    }

    login_mock = MagicMock()

    with patch(
        "src.interfaz.interfaz_login.InterfazLogin",
        login_mock,
    ):
        ventana.cerrarSesion()

    controles["clientes"]._registrar_log.assert_called_once_with(
        administrador.correo_electronico,
        "LOGOUT",
    )

    ventana.destroy.assert_called_once_with()

    login_mock.assert_called_once_with(
        control_autenticacion=autenticacion,
        controladores=ventana._controladores,
    )

    login_mock.return_value.mainloop.assert_called_once_with()