from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_registro_sesion import (
    InterfazRegistroSesion,
)


class WidgetFalso:
    """
    Widget falso para simular widgets ttk.
    """

    def __init__(self, valor="", *args, **kwargs):
        self.valor = valor
        self.args = args
        self.kwargs = kwargs
        self.eliminaciones = []
        self.configuraciones = []

    def pack(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass

    def get(self):
        return self.valor

    def delete(self, *args, **kwargs):
        self.eliminaciones.append((args, kwargs))
        self.valor = ""

    def set(self, valor):
        self.valor = valor


class FrameFalso(WidgetFalso):
    pass


class LabelFalso(WidgetFalso):
    pass


class LabelFrameFalso(WidgetFalso):
    pass


class EntryFalso(WidgetFalso):
    pass


class ComboboxFalso(WidgetFalso):
    pass


class ButtonFalso(WidgetFalso):
    pass


class TestInterfazRegistroSesion:

    @pytest.fixture
    def control_sesiones(self):
        """
        Crea un controlador de sesiones simulado.
        """
        return MagicMock()

    @pytest.fixture
    def interfaz(self, control_sesiones):
        """
        Crea la interfaz sin ejecutar el constructor real.
        """
        interfaz = object.__new__(InterfazRegistroSesion)

        interfaz._controlador = control_sesiones
        interfaz._id_cliente = 10

        return interfaz

    @pytest.fixture
    def widgets_formulario(self):
        """
        Crea los widgets falsos del formulario.
        """
        return {
            "duracion": EntryFalso(),
            "intensidad": ComboboxFalso(),
            "calorias": EntryFalso(),
            "observaciones": EntryFalso(),
        }

    def asignar_widgets_formulario(
        self,
        interfaz,
        widgets,
    ):
        """
        Asigna los widgets falsos a la interfaz.
        """
        interfaz._ent_duracion = widgets["duracion"]
        interfaz._cb_intensidad = widgets["intensidad"]
        interfaz._ent_calorias = widgets["calorias"]
        interfaz._ent_observaciones = widgets["observaciones"]

    def test_propiedad_id_cliente(
        self,
        interfaz,
    ):
        """
        Verifica la propiedad id_cliente.
        """
        assert interfaz.id_cliente == 10

    def test_mostrar_formulario_sesion_crea_widgets(
        self,
        interfaz,
    ):
        """
        Verifica que se creen los widgets del formulario.
        """
        with patch(
            "src.interfaz.interfaz_registro_sesion.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_registro_sesion.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_registro_sesion.ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_registro_sesion.ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_registro_sesion.ttk.Combobox",
            side_effect=ComboboxFalso,
        ), patch(
            "src.interfaz.interfaz_registro_sesion.ttk.Button",
            side_effect=ButtonFalso,
        ):
            interfaz.mostrarFormularioSesion()

        assert hasattr(interfaz, "_ent_duracion")
        assert hasattr(interfaz, "_cb_intensidad")
        assert hasattr(interfaz, "_ent_calorias")
        assert hasattr(interfaz, "_ent_observaciones")

        assert isinstance(interfaz._ent_duracion, EntryFalso)
        assert isinstance(interfaz._cb_intensidad, ComboboxFalso)
        assert isinstance(interfaz._ent_calorias, EntryFalso)
        assert isinstance(interfaz._ent_observaciones, EntryFalso)

    def test_registrar_sesion_correctamente(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el registro correcto de una sesión.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = "ALTA"
        widgets_formulario["calorias"].valor = "500.5"
        widgets_formulario["observaciones"].valor = (
            "Entrenamiento completado"
        )

        fecha_prueba = date(2026, 9, 19)

        with patch(
            "src.interfaz.interfaz_registro_sesion.date"
        ) as mock_date, patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "cancelarRegistro",
        ) as mock_cancelar:

            mock_date.today.return_value = fecha_prueba

            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_called_once_with(
            id_cliente=10,
            duracion_real=45,
            intensidad_real="ALTA",
            calorias_quemadas=500.5,
            observaciones="Entrenamiento completado",
            fecha=fecha_prueba,
        )

        mock_mensaje.assert_called_once_with(
            "Sesion registrada exitosamente."
        )

        mock_cancelar.assert_called_once_with()

    def test_registrar_sesion_sin_duracion(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el error cuando falta la duración.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = ""
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "300"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Los campos Duracion, Intensidad y Calorias son obligatorios."
        )

    def test_registrar_sesion_sin_intensidad(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el error cuando falta la intensidad.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = ""
        widgets_formulario["calorias"].valor = "300"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Los campos Duracion, Intensidad y Calorias son obligatorios."
        )

    def test_registrar_sesion_sin_calorias(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el error cuando faltan las calorías.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = ""

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Los campos Duracion, Intensidad y Calorias son obligatorios."
        )

    def test_registrar_sesion_sin_campos_obligatorios(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el error cuando faltan todos los campos obligatorios.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = ""
        widgets_formulario["intensidad"].valor = ""
        widgets_formulario["calorias"].valor = ""

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Los campos Duracion, Intensidad y Calorias son obligatorios."
        )

    def test_registrar_sesion_con_duracion_invalida(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el error cuando la duración no es un entero.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "cuarenta"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "300"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Duracion debe ser entero y Calorias decimal."
        )

    def test_registrar_sesion_con_calorias_invalidas(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el error cuando las calorías no son numéricas.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "muchas"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Duracion debe ser entero y Calorias decimal."
        )

    def test_registrar_sesion_maneja_value_error_del_controlador(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el manejo de ValueError lanzado por el controlador.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "300"

        control_sesiones.registrar_sesion.side_effect = ValueError(
            "La intensidad no es válida"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        mock_error.assert_called_once_with(
            "La intensidad no es válida"
        )

    def test_registrar_sesion_maneja_error_inesperado(
        self,
        interfaz,
        control_sesiones,
        widgets_formulario,
    ):
        """
        Verifica el manejo de errores inesperados.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "300"

        control_sesiones.registrar_sesion.side_effect = RuntimeError(
            "Error de base de datos"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        mock_error.assert_called_once_with(
            "Error inesperado: Error de base de datos"
        )

    def test_cancelar_registro_limpia_formulario(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica que cancelarRegistro limpie todos los campos.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["duracion"].valor = "45"
        widgets_formulario["intensidad"].valor = "ALTA"
        widgets_formulario["calorias"].valor = "400"
        widgets_formulario["observaciones"].valor = "Buen entrenamiento"

        interfaz.cancelarRegistro()

        assert widgets_formulario["duracion"].valor == ""
        assert widgets_formulario["intensidad"].valor == ""
        assert widgets_formulario["calorias"].valor == ""
        assert widgets_formulario["observaciones"].valor == ""