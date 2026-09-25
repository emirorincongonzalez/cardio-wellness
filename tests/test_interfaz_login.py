from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_login import InterfazLogin


class EntryFalso:
    """
    Campo falso para simular ttk.Entry.
    Acepta argumentos como width y show.
    """

    def __init__(self, valor="", *args, **kwargs):
        self.valor = valor
        self.args = args
        self.kwargs = kwargs

    def get(self):
        return self.valor

    def grid(self, *args, **kwargs):
        pass

    def pack(self, *args, **kwargs):
        pass


class WidgetFalso:
    """
    Widget falso para simular Label, Frame y Button.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass


class TestInterfazLogin:

    @pytest.fixture
    def control_autenticacion(self):
        """
        Crea un controlador de autenticaciÃ³n simulado.
        """
        return MagicMock()

    @pytest.fixture
    def interfaz(self, control_autenticacion):
        """
        Crea la interfaz sin ejecutar tk.Tk.__init__.
        """
        interfaz = object.__new__(InterfazLogin)

        interfaz._correo = ""
        interfaz._contrasenia = ""
        interfaz._control = control_autenticacion

        return interfaz

    def test_propiedad_correo(
        self,
        interfaz,
    ):
        """
        Verifica la propiedad correo.
        """
        interfaz._correo = "ana@example.com"

        assert interfaz.correo == "ana@example.com"

    def test_propiedad_contrasenia(
        self,
        interfaz,
    ):
        """
        Verifica la propiedad contrasenia.
        """
        interfaz._contrasenia = "123456"

        assert interfaz.contrasenia == "123456"

    def test_propiedad_control(
        self,
        interfaz,
        control_autenticacion,
    ):
        """
        Verifica la propiedad control.
        """
        assert interfaz.control is control_autenticacion

    def test_mostrar_formulario_crea_widgets(
        self,
        interfaz,
    ):
        """
        Verifica que se creen los widgets del formulario.
        """
        with patch(
            "src.interfaz.interfaz_login.ttk.Label",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_login.ttk.Frame",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_login.ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_login.ttk.Button",
            side_effect=WidgetFalso,
        ):
            interfaz.mostrarFormulario()

        assert hasattr(interfaz, "_ent_correo")
        assert hasattr(interfaz, "_ent_contrasenia")

        assert isinstance(interfaz._ent_correo, EntryFalso)
        assert isinstance(interfaz._ent_contrasenia, EntryFalso)

        assert interfaz._ent_correo.kwargs["width"] == 32
        assert interfaz._ent_contrasenia.kwargs["width"] == 32
        assert interfaz._ent_contrasenia.kwargs["show"] == "*"

    def test_capturar_credenciales_correctamente(
        self,
        interfaz,
    ):
        """
        Verifica que se capturen correctamente
        el correo y la contraseÃ±a.
        """
        interfaz._ent_correo = EntryFalso(
            " ana@example.com "
        )

        interfaz._ent_contrasenia = EntryFalso(
            " 123456 "
        )

        resultado = interfaz.capturarCredenciales()

        assert resultado is True
        assert interfaz.correo == "ana@example.com"
        assert interfaz.contrasenia == "123456"

    def test_capturar_credenciales_sin_correo(
        self,
        interfaz,
    ):
        """
        Verifica que falle la captura cuando el correo estÃ¡ vacÃ­o.
        """
        interfaz._ent_correo = EntryFalso("")
        interfaz._ent_contrasenia = EntryFalso("123456")

        with patch(
            "src.interfaz.interfaz_login.messagebox.showwarning"
        ) as mock_warning:
            resultado = interfaz.capturarCredenciales()

        assert resultado is False

        mock_warning.assert_called_once_with(
            "Campos Vacios",
            "Por favor complete todos los campos.",
        )

    def test_capturar_credenciales_sin_contrasenia(
        self,
        interfaz,
    ):
        """
        Verifica que falle la captura cuando la contraseÃ±a estÃ¡ vacÃ­a.
        """
        interfaz._ent_correo = EntryFalso("ana@example.com")
        interfaz._ent_contrasenia = EntryFalso("")

        with patch(
            "src.interfaz.interfaz_login.messagebox.showwarning"
        ) as mock_warning:
            resultado = interfaz.capturarCredenciales()

        assert resultado is False

        mock_warning.assert_called_once_with(
            "Campos Vacios",
            "Por favor complete todos los campos.",
        )

    def test_capturar_credenciales_sin_datos(
        self,
        interfaz,
    ):
        """
        Verifica que falle la captura cuando ambos campos estÃ¡n vacÃ­os.
        """
        interfaz._ent_correo = EntryFalso("   ")
        interfaz._ent_contrasenia = EntryFalso("   ")

        with patch(
            "src.interfaz.interfaz_login.messagebox.showwarning"
        ) as mock_warning:
            resultado = interfaz.capturarCredenciales()

        assert resultado is False

        mock_warning.assert_called_once_with(
            "Campos Vacios",
            "Por favor complete todos los campos.",
        )

    def test_iniciar_sesion_no_continua_con_credenciales_vacias(
        self,
        interfaz,
        control_autenticacion,
    ):
        """
        Verifica que no se llame al controlador si faltan datos.
        """
        interfaz._ent_correo = EntryFalso("")
        interfaz._ent_contrasenia = EntryFalso("")

        with patch.object(
            interfaz,
            "capturarCredenciales",
            return_value=False,
        ) as mock_capturar:
            interfaz.iniciarSesion()

        mock_capturar.assert_called_once_with()
        control_autenticacion.iniciar_sesion.assert_not_called()

    def test_iniciar_sesion_credenciales_incorrectas(
        self,
        interfaz,
        control_autenticacion,
    ):
        """
        Verifica el comportamiento cuando el controlador
        no encuentra al usuario.
        """
        interfaz._correo = "ana@example.com"
        interfaz._contrasenia = "incorrecta"

        control_autenticacion.iniciar_sesion.return_value = None

        with patch.object(
            interfaz,
            "capturarCredenciales",
            return_value=True,
        ), patch(
            "src.interfaz.interfaz_login.messagebox.showerror"
        ) as mock_error:
            interfaz.iniciarSesion()

        control_autenticacion.iniciar_sesion.assert_called_once_with(
            "ana@example.com",
            "incorrecta",
        )

        mock_error.assert_called_once_with(
            "Error",
            "Credenciales incorrectas.",
        )

    def test_iniciar_sesion_correcta(
        self,
        interfaz,
        control_autenticacion,
    ):
        """
        Verifica que se destruya la ventana y se abra
        la interfaz correspondiente.
        """
        usuario = MagicMock()
        usuario.tipo_usuario = "cliente"

        interfaz._correo = "ana@example.com"
        interfaz._contrasenia = "123456"

        control_autenticacion.iniciar_sesion.return_value = usuario

        with patch.object(
            interfaz,
            "capturarCredenciales",
            return_value=True,
        ), patch.object(
            interfaz,
            "destroy",
        ) as mock_destroy, patch.object(
            interfaz,
            "_abrir_interfaz_por_rol",
        ) as mock_abrir:

            interfaz.iniciarSesion()

        control_autenticacion.iniciar_sesion.assert_called_once_with(
            "ana@example.com",
            "123456",
        )

        mock_destroy.assert_called_once_with()
        mock_abrir.assert_called_once_with(usuario)

    def test_iniciar_sesion_maneja_error(
        self,
        interfaz,
        control_autenticacion,
    ):
        """
        Verifica el manejo de errores durante la autenticaciÃ³n.
        """
        interfaz._correo = "ana@example.com"
        interfaz._contrasenia = "123456"

        control_autenticacion.iniciar_sesion.side_effect = RuntimeError(
            "Error de conexiÃ³n"
        )

        with patch.object(
            interfaz,
            "capturarCredenciales",
            return_value=True,
        ), patch(
            "src.interfaz.interfaz_login.messagebox.showerror"
        ) as mock_error:
            interfaz.iniciarSesion()

        mock_error.assert_called_once_with(
            "Error",
            "Error al iniciar sesion: Error de conexiÃ³n",
        )

    def test_abrir_interfaz_por_rol_administrador(
        self,
        interfaz,
    ):
        """
        Verifica que el rol administrador abra
        InterfazAdministrador.
        """
        usuario = MagicMock()
        usuario.tipo_usuario = "administrador"

        app = MagicMock()

        with patch(
            "src.interfaz.interfaz_administrador.InterfazAdministrador",
            return_value=app,
        ) as mock_interfaz:

            interfaz._abrir_interfaz_por_rol(usuario)

        mock_interfaz.assert_called_once_with(usuario)
        app.mainloop.assert_called_once_with()

    def test_abrir_interfaz_por_rol_cliente(
        self,
        interfaz,
    ):
        """
        Verifica que un usuario no administrador abra
        InterfazCliente.
        """
        usuario = MagicMock()
        usuario.tipo_usuario = "cliente"

        app = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.InterfazCliente",
            return_value=app,
        ) as mock_interfaz:

            interfaz._abrir_interfaz_por_rol(usuario)

        mock_interfaz.assert_called_once_with(usuario)
        app.mainloop.assert_called_once_with()


def crear_interfaz_sin_tk():
    interfaz = object.__new__(InterfazLogin)
    interfaz._correo = ""
    interfaz._contrasenia = ""
    interfaz._control = MagicMock()

    return interfaz


def test_init_configura_interfaz_con_controladores_por_defecto():
    control_autenticacion = MagicMock()

    with patch(
        "src.interfaz.interfaz_login.tk.Tk.__init__",
        return_value=None,
    ), patch(
        "src.interfaz.interfaz_login.tk.Tk.title"
    ) as mock_title, patch(
        "src.interfaz.interfaz_login.tk.Tk.geometry"
    ) as mock_geometry, patch(
        "src.interfaz.interfaz_login.tk.Tk.resizable"
    ) as mock_resizable, patch.object(
        InterfazLogin,
        "mostrarFormulario",
    ) as mock_formulario:

        interfaz = InterfazLogin(
            control_autenticacion,
        )

    assert interfaz._correo == ""
    assert interfaz._contrasenia == ""
    assert interfaz._control is control_autenticacion

    assert interfaz._controladores == {
        "control_auth": control_autenticacion,
        "control_autenticacion": control_autenticacion,
    }

    mock_title.assert_called_once_with(
        "Cardio Wellness - Iniciar Sesion"
    )
    mock_geometry.assert_called_once_with("400x350")
    mock_resizable.assert_called_once_with(False, False)
    mock_formulario.assert_called_once()


def test_init_conserva_controladores_recibidos():
    control_autenticacion = MagicMock()

    controladores = {
        "control_auth": control_autenticacion,
        "control_clientes": MagicMock(),
        "control_rutinas": MagicMock(),
    }

    with patch(
        "src.interfaz.interfaz_login.tk.Tk.__init__",
        return_value=None,
    ), patch(
        "src.interfaz.interfaz_login.tk.Tk.title"
    ), patch(
        "src.interfaz.interfaz_login.tk.Tk.geometry"
    ), patch(
        "src.interfaz.interfaz_login.tk.Tk.resizable"
    ), patch.object(
        InterfazLogin,
        "mostrarFormulario",
    ):

        interfaz = InterfazLogin(
            control_autenticacion,
            controladores=controladores,
        )

    assert interfaz._controladores is controladores
    assert interfaz._control is control_autenticacion


def test_es_modo_pruebas_detecta_instancia_sin_controladores():
    interfaz = crear_interfaz_sin_tk()

    assert interfaz._es_modo_pruebas() is True

    interfaz._controladores = {}

    assert interfaz._es_modo_pruebas() is False


def test_abrir_interfaz_administrador_con_controladores():
    interfaz = crear_interfaz_sin_tk()

    usuario = MagicMock()
    usuario.tipo_usuario = "administrador"

    controladores = {
        "control_auth": MagicMock(),
        "control_clientes": MagicMock(),
        "control_rutinas": MagicMock(),
    }

    interfaz._controladores = controladores

    app = MagicMock()

    with patch(
        "src.interfaz.interfaz_administrador.InterfazAdministrador",
        return_value=app,
    ) as mock_interfaz:

        interfaz._abrir_interfaz_por_rol(usuario)

    mock_interfaz.assert_called_once_with(
        administrador_actual=usuario,
        controladores=controladores,
    )

    app.mainloop.assert_called_once()


def test_abrir_interfaz_cliente_con_controladores():
    interfaz = crear_interfaz_sin_tk()

    usuario = MagicMock()
    usuario.tipo_usuario = "cliente"

    controladores = {
        "control_auth": MagicMock(),
        "control_clientes": MagicMock(),
        "control_rutinas": MagicMock(),
    }

    interfaz._controladores = controladores

    app = MagicMock()

    with patch(
        "src.interfaz.interfaz_cliente.InterfazCliente",
        return_value=app,
    ) as mock_interfaz:

        interfaz._abrir_interfaz_por_rol(usuario)

    mock_interfaz.assert_called_once_with(
        cliente_actual=usuario,
        controladores=controladores,
    )

    app.mainloop.assert_called_once()
