from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_cliente import InterfazCliente


class PadreFalso:
    """
    Padre mínimo para simular la ventana Tkinter.
    Evita utilizar MagicMock como master de widgets ttk.
    """

    def __init__(self):
        self._destroyed = False

    def destroy(self):
        self._destroyed = True


class BotonFalso:
    """
    Widget falso para probar ttk.Button.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        pass


class LabelFalso:
    """
    Widget falso para probar ttk.Label.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        pass

    def config(self, *args, **kwargs):
        pass


class FrameFalso:
    """
    Widget falso para probar ttk.Frame.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        pass


class NotebookFalso:
    """
    Widget falso para probar ttk.Notebook.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pestanas = []

    def pack(self, *args, **kwargs):
        pass

    def add(self, widget, **kwargs):
        self.pestanas.append((widget, kwargs))


class TestInterfazCliente:

    @pytest.fixture
    def cliente(self):
        """
        Crea un cliente simulado.
        """
        cliente = MagicMock()

        cliente.nombre = "Ana"
        cliente.id_usuario = 10
        cliente.correo_electronico = "ana@example.com"

        cliente.obtener_nombre_completo.return_value = "Ana Pérez"

        return cliente

    @pytest.fixture
    def control_rutinas(self):
        """
        Crea un controlador de rutinas simulado.
        """
        controlador = MagicMock()

        controlador.asignacion_dao.buscar_activa.return_value = None

        return controlador

    @pytest.fixture
    def control_sesiones(self):
        """
        Crea un controlador de sesiones simulado.
        """
        return MagicMock()

    @pytest.fixture
    def control_progreso(self):
        """
        Crea un controlador de progreso simulado.
        """
        return MagicMock()

    @pytest.fixture
    def interfaz(
        self,
        cliente,
        control_rutinas,
        control_sesiones,
        control_progreso,
    ):
        """
        Crea la instancia sin ejecutar tk.Tk.__init__.
        """
        interfaz = object.__new__(InterfazCliente)

        interfaz._cliente_actual = cliente
        interfaz._control_rutinas = control_rutinas
        interfaz._control_sesiones = control_sesiones
        interfaz._control_progreso = control_progreso

        return interfaz

    def test_inicializa_cliente_y_controladores(
        self,
        interfaz,
        cliente,
        control_rutinas,
        control_sesiones,
        control_progreso,
    ):
        """
        Verifica que se guarden correctamente
        el cliente y los controladores.
        """
        assert interfaz.cliente_actual is cliente
        assert interfaz.control_rutinas is control_rutinas
        assert interfaz.control_sesiones is control_sesiones
        assert interfaz.control_progreso is control_progreso

    def test_propiedad_cliente_actual(
        self,
        interfaz,
        cliente,
    ):
        """
        Verifica la propiedad cliente_actual.
        """
        assert interfaz.cliente_actual is cliente

    def test_propiedad_control_rutinas(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica la propiedad control_rutinas.
        """
        assert interfaz.control_rutinas is control_rutinas

    def test_propiedad_control_sesiones(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica la propiedad control_sesiones.
        """
        assert interfaz.control_sesiones is control_sesiones

    def test_propiedad_control_progreso(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica la propiedad control_progreso.
        """
        assert interfaz.control_progreso is control_progreso

    def test_mostrar_inicio_construye_la_interfaz(
        self,
        interfaz,
    ):
        """
        Verifica que mostrarInicio cree el notebook
        y llame a las tres funciones principales.
        """
        padre = PadreFalso()
        interfaz._tk = padre

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Button",
            side_effect=BotonFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Notebook",
            side_effect=NotebookFalso,
        ), patch.object(
            interfaz,
            "consultarRutinaActiva",
        ) as mock_rutina, patch.object(
            interfaz,
            "registrarSesion",
        ) as mock_sesion, patch.object(
            interfaz,
            "consultarProgreso",
        ) as mock_progreso:

            interfaz.mostrarInicio()

        assert isinstance(interfaz._notebook, NotebookFalso)

        mock_rutina.assert_called_once_with()
        mock_sesion.assert_called_once_with()
        mock_progreso.assert_called_once_with()

    def test_consultar_rutina_activa_sin_asignacion(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica el mensaje cuando no existe
        una rutina asignada.
        """
        interfaz._notebook = NotebookFalso()

        label_rutina = MagicMock()
        tree_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=label_rutina,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Treeview",
            return_value=tree_ejercicios,
        ):
            interfaz.consultarRutinaActiva()

        control_rutinas.asignacion_dao.buscar_activa.assert_called_once_with(
            interfaz.cliente_actual.id_usuario
        )

        label_rutina.config.assert_called_once_with(
            text="No tienes una rutina asignada actualmente."
        )

        tree_ejercicios.insert.assert_not_called()

    def test_consultar_rutina_activa_con_rutina(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica la carga de una rutina y sus ejercicios.
        """
        interfaz._notebook = NotebookFalso()

        asignacion = SimpleNamespace(
            id_rutina=25,
        )

        ejercicio = SimpleNamespace(
            nombre="Caminata",
            tipo="Cardio",
            duracion_minutos=30,
            intensidad=SimpleNamespace(value="Media"),
        )

        rutina = SimpleNamespace(
            nombre="Rutina inicial",
            nivel=SimpleNamespace(value="Básico"),
            ejercicios=[ejercicio],
        )

        control_rutinas.asignacion_dao.buscar_activa.return_value = (
            asignacion
        )

        control_rutinas.buscar_por_id.return_value = rutina

        label_rutina = MagicMock()
        tree_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=label_rutina,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Treeview",
            return_value=tree_ejercicios,
        ):
            interfaz.consultarRutinaActiva()

        control_rutinas.asignacion_dao.buscar_activa.assert_called_once_with(
            interfaz.cliente_actual.id_usuario
        )

        control_rutinas.buscar_por_id.assert_called_once_with(
            asignacion.id_rutina
        )

        label_rutina.config.assert_called_once_with(
            text="Rutina: Rutina inicial (Básico)"
        )

        tree_ejercicios.insert.assert_called_once_with(
            "",
            "end",
            values=(
                "Caminata",
                "Cardio",
                "30 min",
                "Media",
            ),
        )

    def test_consultar_rutina_activa_sin_rutina(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica el mensaje cuando no se encuentra
        la rutina asociada.
        """
        interfaz._notebook = NotebookFalso()

        asignacion = SimpleNamespace(
            id_rutina=99,
        )

        control_rutinas.asignacion_dao.buscar_activa.return_value = (
            asignacion
        )

        control_rutinas.buscar_por_id.return_value = None

        label_rutina = MagicMock()
        tree_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=label_rutina,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Treeview",
            return_value=tree_ejercicios,
        ):
            interfaz.consultarRutinaActiva()

        label_rutina.config.assert_called_once_with(
            text="No se encontro la rutina activa."
        )

        tree_ejercicios.insert.assert_not_called()

    def test_consultar_rutina_activa_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica el manejo de errores al cargar la rutina.
        """
        interfaz._notebook = NotebookFalso()

        control_rutinas.asignacion_dao.buscar_activa.side_effect = (
            RuntimeError("Error de base de datos")
        )

        label_rutina = MagicMock()
        tree_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=label_rutina,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Treeview",
            return_value=tree_ejercicios,
        ):
            interfaz.consultarRutinaActiva()

        label_rutina.config.assert_called_once_with(
            text="Error al cargar la rutina: Error de base de datos"
        )

    @patch("src.interfaz.interfaz_cliente.InterfazProgreso")
    def test_consultar_progreso(
        self,
        mock_interfaz_progreso,
        interfaz,
        control_progreso,
    ):
        """
        Verifica que se cree la pestaña de progreso.
        """
        interfaz._notebook = NotebookFalso()

        pestania_progreso = MagicMock()
        mock_interfaz_progreso.return_value = pestania_progreso

        interfaz.consultarProgreso()

        mock_interfaz_progreso.assert_called_once_with(
            interfaz._notebook,
            control_progreso,
            interfaz.cliente_actual,
        )

        assert interfaz._notebook.pestanas == [
            (
                pestania_progreso,
                {"text": "Mi Progreso"},
            )
        ]

    @patch("src.interfaz.interfaz_cliente.InterfazRegistroSesion")
    def test_registrar_sesion(
        self,
        mock_interfaz_registro,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que se cree la pestaña de registro de sesión.
        """
        interfaz._notebook = NotebookFalso()

        pestania_sesion = MagicMock()
        mock_interfaz_registro.return_value = pestania_sesion

        interfaz.registrarSesion()

        mock_interfaz_registro.assert_called_once_with(
            interfaz._notebook,
            control_sesiones,
            interfaz.cliente_actual.id_usuario,
        )

        assert interfaz._notebook.pestanas == [
            (
                pestania_sesion,
                {"text": "Registrar Sesion"},
            )
        ]

    def test_cerrar_sesion_registra_logout_y_destruye_ventana(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica el registro del logout, la destrucción
        de la ventana y la apertura del login.
        """
        controlador_autenticacion = MagicMock()
        interfaz_login = MagicMock()

        with patch.object(
            interfaz,
            "destroy",
        ) as mock_destroy, patch(
            "src.controladores.control_autenticacion.ControlAutenticacion",
            return_value=controlador_autenticacion,
        ) as mock_control_autenticacion, patch(
            "src.interfaz.interfaz_login.InterfazLogin",
            return_value=interfaz_login,
        ) as mock_interfaz_login:

            interfaz.cerrarSesion()

        control_sesiones._registrar_log.assert_called_once_with(
            interfaz.cliente_actual.correo_electronico,
            "LOGOUT",
        )

        mock_destroy.assert_called_once_with()

        mock_control_autenticacion.assert_called_once_with()

        mock_interfaz_login.assert_called_once_with(
            controlador_autenticacion
        )

        interfaz_login.mainloop.assert_called_once_with()

    def test_cerrar_sesion_no_falla_si_el_log_genera_error(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que el cierre continúe aunque falle el log.
        """
        control_sesiones._registrar_log.side_effect = RuntimeError(
            "Error al registrar log"
        )

        controlador_autenticacion = MagicMock()
        interfaz_login = MagicMock()

        with patch.object(
            interfaz,
            "destroy",
        ) as mock_destroy, patch(
            "src.controladores.control_autenticacion.ControlAutenticacion",
            return_value=controlador_autenticacion,
        ) as mock_control_autenticacion, patch(
            "src.interfaz.interfaz_login.InterfazLogin",
            return_value=interfaz_login,
        ) as mock_interfaz_login:

            interfaz.cerrarSesion()

        control_sesiones._registrar_log.assert_called_once_with(
            interfaz.cliente_actual.correo_electronico,
            "LOGOUT",
        )

        mock_destroy.assert_called_once_with()

        mock_control_autenticacion.assert_called_once_with()

        mock_interfaz_login.assert_called_once_with(
            controlador_autenticacion
        )

        interfaz_login.mainloop.assert_called_once_with()