from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import tkinter as tk

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

    def configurar_modo_real(
        self,
        interfaz,
    ):
        """
        Configura una instancia parcial como ventana real.
        """
        interfaz._control_autenticacion = MagicMock()

        interfaz._controladores = {
            "control_auth": interfaz._control_autenticacion,
            "control_autenticacion": (
                interfaz._control_autenticacion
            ),
            "control_rutinas": interfaz._control_rutinas,
            "control_sesiones": interfaz._control_sesiones,
            "control_progreso": interfaz._control_progreso,
        }


    def test_obtener_master_widgets_devuelve_tk_si_existe(
        self,
        interfaz,
    ):
        """
        Verifica que se use el padre falso en pruebas.
        """
        padre = PadreFalso()
        interfaz._tk = padre

        assert interfaz._obtener_master_widgets() is padre


    def test_obtener_master_widgets_devuelve_self_si_no_existe_tk(
        self,
        interfaz,
    ):
        """
        Verifica que self sea el master fuera del modo de pruebas.
        """
        assert interfaz._obtener_master_widgets() is interfaz


    def test_es_modo_pruebas_por_falta_autenticacion(
        self,
        interfaz,
    ):
        """
        Verifica detección de instancia parcial.
        """
        assert interfaz._es_modo_pruebas() is True


    def test_es_modo_pruebas_por_falta_controladores(
        self,
        interfaz,
    ):
        """
        Verifica detección si falta el diccionario de controladores.
        """
        interfaz._control_autenticacion = MagicMock()

        assert interfaz._es_modo_pruebas() is True


    def test_es_modo_pruebas_con_notebook_falso(
        self,
        interfaz,
    ):
        """
        Verifica que un notebook falso se detecte como modo pruebas.
        """
        self.configurar_modo_real(interfaz)
        interfaz._notebook = NotebookFalso()

        assert interfaz._es_modo_pruebas() is True


    def test_es_modo_pruebas_es_falso_con_notebook_real(
        self,
        interfaz,
    ):
        """
        Verifica detección del modo normal de aplicación.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook

        assert interfaz._es_modo_pruebas() is False


    @pytest.mark.parametrize(
        ("valor", "resultado"),
        [
            (None, "-"),
            ("", "-"),
            (1.75, "1.75"),
            ("70", "70.00"),
            ("no numerico", "no numerico"),
        ],
    )
    def test_formatear_decimal(
        self,
        valor,
        resultado,
    ):
        """
        Verifica formato de valores decimales y datos inválidos.
        """
        assert (
            InterfazCliente._formatear_decimal(valor)
            == resultado
        )


    def test_crear_datos_personales(
        self,
        interfaz,
        cliente,
    ):
        """
        Verifica construcción de datos personales del cliente.
        """
        cliente.edad = 28
        cliente.altura = 1.68
        cliente.genero = "FEMENINO"
        cliente.peso = 65.5
        cliente.peso_objetivo = 60
        cliente.objetivo = "Bajar de peso"

        frame = MagicMock()
        etiquetas = []

        def crear_label(*args, **kwargs):
            label = MagicMock()
            label.args = args
            label.kwargs = kwargs
            etiquetas.append(label)
            return label

        with patch(
            "src.interfaz.interfaz_cliente.ttk.LabelFrame",
            return_value=frame,
        ) as mock_frame, patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            side_effect=crear_label,
        ):
            interfaz._crear_datos_personales()

        mock_frame.assert_called_once_with(
            interfaz,
            text="Datos personales",
            padding=10,
        )

        frame.pack.assert_called_once_with(
            fill="x",
            padx=10,
            pady=(0, 5),
        )

        assert len(etiquetas) == 16

        valores = [
            etiqueta.kwargs["text"]
            for etiqueta in etiquetas
            if "text" in etiqueta.kwargs
        ]

        assert "Ana Pérez" in valores
        assert "ana@example.com" in valores
        assert "28 años" in valores
        assert "1.68 m" in valores
        assert "FEMENINO" in valores
        assert "65.50 kg" in valores
        assert "60.00 kg" in valores
        assert "Bajar de peso" in valores


    def test_mostrar_inicio_modo_real_crea_datos_personales(
        self,
        interfaz,
    ):
        """
        Verifica que mostrarInicio incluya datos personales
        cuando se ejecuta fuera del modo de pruebas.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()

        with patch.object(
            interfaz,
            "_obtener_master_widgets",
            return_value=interfaz,
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            return_value=MagicMock(),
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=MagicMock(),
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Button",
            return_value=MagicMock(),
        ), patch(
            "src.interfaz.interfaz_cliente.ttk.Notebook",
            return_value=notebook,
        ), patch.object(
            interfaz,
            "_crear_datos_personales",
        ) as mock_datos, patch.object(
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

        mock_datos.assert_called_once_with()
        mock_rutina.assert_called_once_with()
        mock_sesion.assert_called_once_with()
        mock_progreso.assert_called_once_with()

        assert interfaz._notebook is notebook


    def test_consultar_progreso_modo_real(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica la pestaña de progreso en modo normal.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook

        pestania = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.InterfazProgreso",
            return_value=pestania,
        ) as mock_progreso:
            interfaz.consultarProgreso()

        mock_progreso.assert_called_once_with(
            master=notebook,
            control_progreso=control_progreso,
            cliente=interfaz.cliente_actual,
        )

        notebook.add.assert_called_once_with(
            pestania,
            text="Mi progreso",
        )


    def test_registrar_sesion_modo_real_sin_rutina(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica aviso si no existe una rutina activa.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook

        control_rutinas.asignacion_dao.buscar_activa.return_value = None

        with patch.object(
            interfaz,
            "_mostrar_sin_rutina_activa",
        ) as mock_aviso:
            interfaz.registrarSesion()

        mock_aviso.assert_called_once_with()


    @pytest.mark.parametrize(
        "asignacion",
        [
            SimpleNamespace(id_rutina=None),
            SimpleNamespace(id_rutina=0),
            SimpleNamespace(id_rutina=-1),
            {"id_rutina": "invalida"},
        ],
    )
    def test_registrar_sesion_modo_real_con_rutina_invalida(
        self,
        interfaz,
        control_rutinas,
        asignacion,
    ):
        """
        Verifica aviso cuando la asignación no tiene rutina válida.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook

        control_rutinas.asignacion_dao.buscar_activa.return_value = (
            asignacion
        )

        with patch.object(
            interfaz,
            "_mostrar_error_rutina",
        ) as mock_error:
            interfaz.registrarSesion()

        mock_error.assert_called_once_with()


    def test_registrar_sesion_modo_real_correctamente(
        self,
        interfaz,
        control_rutinas,
        control_sesiones,
    ):
        """
        Verifica creación de pestaña de sesión con rutina válida.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook

        control_rutinas.asignacion_dao.buscar_activa.return_value = (
            SimpleNamespace(id_rutina=20)
        )

        pestania = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.InterfazRegistroSesion",
            return_value=pestania,
        ) as mock_registro:
            interfaz.registrarSesion()

        mock_registro.assert_called_once_with(
            notebook,
            control_sesiones,
            interfaz.cliente_actual.id_usuario,
            20,
        )

        notebook.add.assert_called_once_with(
            pestania,
            text="Registrar sesión",
        )


    def test_registrar_sesion_modo_real_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica creación de mensaje visual si falla el formulario.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook

        control_rutinas.asignacion_dao.buscar_activa.side_effect = (
            RuntimeError("Fallo de rutina")
        )

        pestania_error = MagicMock()
        etiqueta_error = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            return_value=pestania_error,
        ) as mock_frame, patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=etiqueta_error,
        ) as mock_label:
            interfaz.registrarSesion()

        mock_frame.assert_called_once_with(
            notebook,
            padding=10,
        )

        mock_label.assert_called_once_with(
            pestania_error,
            text=(
                "No se pudo cargar el formulario "
                "de sesiones: Fallo de rutina"
            ),
            foreground="red",
            wraplength=600,
        )

        notebook.add.assert_called_once_with(
            pestania_error,
            text="Registrar sesión",
        )


    def test_mostrar_sin_rutina_activa(
        self,
        interfaz,
    ):
        """
        Verifica la pestaña informativa sin rutina activa.
        """
        interfaz._notebook = MagicMock()

        pestania = MagicMock()
        etiqueta = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            return_value=pestania,
        ) as mock_frame, patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=etiqueta,
        ) as mock_label:
            interfaz._mostrar_sin_rutina_activa()

        mock_frame.assert_called_once_with(
            interfaz._notebook,
            padding=10,
        )

        mock_label.assert_called_once_with(
            pestania,
            text=(
                "No puedes registrar una sesión "
                "porque no tienes una rutina activa "
                "asignada."
            ),
            foreground="red",
            wraplength=600,
            justify="center",
        )

        interfaz._notebook.add.assert_called_once_with(
            pestania,
            text="Registrar sesión",
        )


    def test_mostrar_error_rutina(
        self,
        interfaz,
    ):
        """
        Verifica la pestaña informativa de rutina inválida.
        """
        interfaz._notebook = MagicMock()

        pestania = MagicMock()
        etiqueta = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.ttk.Frame",
            return_value=pestania,
        ) as mock_frame, patch(
            "src.interfaz.interfaz_cliente.ttk.Label",
            return_value=etiqueta,
        ) as mock_label:
            interfaz._mostrar_error_rutina()

        mock_frame.assert_called_once_with(
            interfaz._notebook,
            padding=10,
        )

        mock_label.assert_called_once_with(
            pestania,
            text=(
                "La asignación activa no contiene "
                "una rutina válida."
            ),
            foreground="red",
            wraplength=600,
            justify="center",
        )

        interfaz._notebook.add.assert_called_once_with(
            pestania,
            text="Registrar sesión",
        )


    @pytest.mark.parametrize(
        ("asignacion", "resultado"),
        [
            (
                {"id_rutina": 15},
                15,
            ),
            (
                {"id_rutina": "21"},
                21,
            ),
            (
                SimpleNamespace(id_rutina=30),
                30,
            ),
            (
                SimpleNamespace(id_rutina="45"),
                45,
            ),
            (
                {},
                None,
            ),
            (
                SimpleNamespace(),
                None,
            ),
            (
                {"id_rutina": "abc"},
                None,
            ),
            (
                {"id_rutina": None},
                None,
            ),
        ],
    )
    def test_obtener_id_rutina(
        self,
        asignacion,
        resultado,
    ):
        """
        Verifica lectura de ID desde objeto, diccionario
        y valores inválidos.
        """
        assert (
            InterfazCliente._obtener_id_rutina(asignacion)
            == resultado
        )


    def test_cargar_datos_rutina_asignacion_sin_id(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica mensaje si la asignación no contiene ID.
        """
        interfaz._lbl_rutina_nombre = MagicMock()
        interfaz._tree_ejercicios = MagicMock()

        control_rutinas.asignacion_dao.buscar_activa.return_value = (
            SimpleNamespace()
        )

        interfaz._cargar_datos_rutina()

        interfaz._lbl_rutina_nombre.config.assert_called_once_with(
            text=(
                "La asignación no contiene "
                "una rutina válida."
            )
        )


    def test_cargar_datos_rutina_sin_ejercicios(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica fila informativa si la rutina está vacía.
        """
        interfaz._lbl_rutina_nombre = MagicMock()
        interfaz._tree_ejercicios = MagicMock()

        control_rutinas.asignacion_dao.buscar_activa.return_value = (
            SimpleNamespace(id_rutina=5)
        )

        control_rutinas.buscar_por_id.return_value = (
            SimpleNamespace(
                nombre="Rutina vacía",
                nivel="Básico",
                ejercicios=[],
            )
        )

        interfaz._cargar_datos_rutina()

        interfaz._tree_ejercicios.insert.assert_called_once_with(
            "",
            "end",
            values=(
                "Sin ejercicios",
                "",
                "",
                "",
            ),
        )


    def test_cargar_datos_rutina_usa_fallbacks_de_ejercicio(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica atributos alternativos para rutina y ejercicio.
        """
        interfaz._lbl_rutina_nombre = MagicMock()
        interfaz._tree_ejercicios = MagicMock()

        control_rutinas.asignacion_dao.buscar_activa.return_value = {
            "id_rutina": "7",
        }

        ejercicio = SimpleNamespace(
            nombre="Bicicleta",
            tipo="LISS",
            duracion=45,
            intensidad="MEDIA",
        )

        control_rutinas.buscar_por_id.return_value = (
            SimpleNamespace(
                nombre="Rutina cardio",
                nivel="INTERMEDIO",
                ejercicios=[ejercicio],
            )
        )

        interfaz._cargar_datos_rutina()

        interfaz._tree_ejercicios.insert.assert_called_once_with(
            "",
            "end",
            values=(
                "Bicicleta",
                "LISS",
                "45 min",
                "MEDIA",
            ),
        )


    def test_cerrar_sesion_modo_real(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que el modo normal reutilice autenticación
        y el diccionario de controladores.
        """
        self.configurar_modo_real(interfaz)

        notebook = MagicMock()
        notebook.tk = MagicMock()

        interfaz._notebook = notebook
        interfaz.destroy = MagicMock()

        login = MagicMock()

        with patch(
            "src.interfaz.interfaz_login.InterfazLogin",
            return_value=login,
        ) as mock_login:
            interfaz.cerrarSesion()

        control_sesiones._registrar_log.assert_called_once_with(
            interfaz.cliente_actual.correo_electronico,
            "LOGOUT",
        )

        interfaz.destroy.assert_called_once_with()

        mock_login.assert_called_once_with(
            control_autenticacion=(
                interfaz._control_autenticacion
            ),
            controladores=interfaz._controladores,
        )

        login.mainloop.assert_called_once_with()

    def test_constructor_configura_ventana_y_dependencias(
        self,
        control_rutinas,
        control_sesiones,
        control_progreso,
    ):
        """
        Verifica el constructor real sin iniciar Tkinter.
        """

        class ClienteFalso:
            def __init__(self):
                self.nombre = "Ana"
                self.id_usuario = 10
                self.correo_electronico = "ana@example.com"

        cliente_real = ClienteFalso()
        control_autenticacion = MagicMock()

        with patch(
            "src.interfaz.interfaz_cliente.Cliente",
            ClienteFalso,
        ), patch.object(
            tk.Tk,
            "__init__",
            return_value=None,
        ) as mock_tk_init, patch.object(
            InterfazCliente,
            "title",
        ) as mock_title, patch.object(
            InterfazCliente,
            "geometry",
        ) as mock_geometry, patch.object(
            InterfazCliente,
            "minsize",
        ) as mock_minsize, patch.object(
            InterfazCliente,
            "resizable",
        ) as mock_resizable, patch.object(
            InterfazCliente,
            "protocol",
        ) as mock_protocol, patch.object(
            InterfazCliente,
            "mostrarInicio",
        ) as mock_inicio:
            ventana = InterfazCliente(
                cliente_actual=cliente_real,
                control_rutinas=control_rutinas,
                control_sesiones=control_sesiones,
                control_progreso=control_progreso,
                control_autenticacion=control_autenticacion,
            )

        mock_tk_init.assert_called_once_with()

        mock_title.assert_called_once_with(
            "Cardio Wellness - Cliente: Ana"
        )

        mock_geometry.assert_called_once_with("1050x780")
        mock_minsize.assert_called_once_with(900, 650)
        mock_resizable.assert_called_once_with(True, True)

        mock_protocol.assert_called_once_with(
            "WM_DELETE_WINDOW",
            ventana.cerrarSesion,
        )

        mock_inicio.assert_called_once_with()

        assert ventana.cliente_actual is cliente_real
        assert ventana.control_rutinas is control_rutinas
        assert ventana.control_sesiones is control_sesiones
        assert ventana.control_progreso is control_progreso

        assert ventana._control_autenticacion is control_autenticacion

        assert ventana._controladores == {
            "control_auth": control_autenticacion,
            "control_autenticacion": control_autenticacion,
            "control_rutinas": control_rutinas,
            "control_sesiones": control_sesiones,
            "control_progreso": control_progreso,
        }


    def test_constructor_usa_diccionario_controladores(
        self,
        control_rutinas,
        control_sesiones,
        control_progreso,
    ):
        """
        Verifica que controladores sobrescriba dependencias directas.
        """

        class ClienteFalso:
            def __init__(self):
                self.nombre = "Ana"

        cliente_real = ClienteFalso()
        control_autenticacion = MagicMock()

        controladores = {
            "control_rutinas": control_rutinas,
            "control_sesiones": control_sesiones,
            "control_progreso": control_progreso,
            "control_auth": control_autenticacion,
            "configuracion_extra": "valor",
        }

        with patch(
            "src.interfaz.interfaz_cliente.Cliente",
            ClienteFalso,
        ), patch.object(
            tk.Tk,
            "__init__",
            return_value=None,
        ), patch.object(
            InterfazCliente,
            "title",
        ), patch.object(
            InterfazCliente,
            "geometry",
        ), patch.object(
            InterfazCliente,
            "minsize",
        ), patch.object(
            InterfazCliente,
            "resizable",
        ), patch.object(
            InterfazCliente,
            "protocol",
        ), patch.object(
            InterfazCliente,
            "mostrarInicio",
        ):
            ventana = InterfazCliente(
                cliente_actual=cliente_real,
                controladores=controladores,
            )

        assert ventana.control_rutinas is control_rutinas
        assert ventana.control_sesiones is control_sesiones
        assert ventana.control_progreso is control_progreso

        assert (
            ventana._control_autenticacion
            is control_autenticacion
        )

        assert ventana._controladores is controladores

        assert (
            ventana._controladores["configuracion_extra"]
            == "valor"
        )


    @pytest.mark.parametrize(
        ("cliente_actual", "tipo_error", "mensaje"),
        [
            (
                None,
                ValueError,
                "Debe existir un cliente autenticado.",
            ),
            (
                MagicMock(),
                TypeError,
                "El usuario autenticado debe ser Cliente.",
            ),
        ],
    )
    def test_constructor_valida_cliente(
        self,
        cliente_actual,
        tipo_error,
        mensaje,
    ):
        """
        Verifica cliente inexistente y cliente de tipo incorrecto.
        """
        with patch.object(
            tk.Tk,
            "__init__",
            return_value=None,
        ):
            with pytest.raises(tipo_error) as error:
                InterfazCliente(
                    cliente_actual=cliente_actual,
                    control_rutinas=MagicMock(),
                    control_sesiones=MagicMock(),
                    control_progreso=MagicMock(),
                    control_autenticacion=MagicMock(),
                )

        assert str(error.value) == mensaje


    @pytest.mark.parametrize(
        ("rutinas", "sesiones", "progreso", "auth", "mensaje"),
        [
            (
                None,
                MagicMock(),
                MagicMock(),
                MagicMock(),
                "InterfazCliente requiere un "
                "ControlRutinas inicializado.",
            ),
            (
                MagicMock(),
                None,
                MagicMock(),
                MagicMock(),
                "InterfazCliente requiere un "
                "ControlSesiones inicializado.",
            ),
            (
                MagicMock(),
                MagicMock(),
                None,
                MagicMock(),
                "InterfazCliente requiere un "
                "ControlProgreso inicializado.",
            ),
            (
                MagicMock(),
                MagicMock(),
                MagicMock(),
                None,
                "InterfazCliente requiere un "
                "ControlAutenticacion inicializado.",
            ),
        ],
    )
    def test_constructor_valida_controladores_requeridos(
        self,
        rutinas,
        sesiones,
        progreso,
        auth,
        mensaje,
    ):
        """
        Verifica que cada controlador obligatorio sea validado.
        """

        class ClienteFalso:
            pass

        cliente_real = ClienteFalso()
        cliente_real.nombre = "Ana"

        with patch(
            "src.interfaz.interfaz_cliente.Cliente",
            ClienteFalso,
        ), patch.object(
            tk.Tk,
            "__init__",
            return_value=None,
        ):
            with pytest.raises(ValueError) as error:
                InterfazCliente(
                    cliente_actual=cliente_real,
                    control_rutinas=rutinas,
                    control_sesiones=sesiones,
                    control_progreso=progreso,
                    control_autenticacion=auth,
                )

        assert str(error.value) == mensaje