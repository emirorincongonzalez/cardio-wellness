from datetime import date
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

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

    def asignar_widgets_completos(
        self,
        interfaz,
        nombre="Caminata",
        duracion="45",
        intensidad="MEDIA",
        calorias="300",
        planificadas="3",
        realizadas="2",
        observaciones="Entrenamiento normal",
    ):
        """
        Asigna todos los widgets requeridos por el formulario actual.
        """
        interfaz._id_rutina = 25

        interfaz._ent_nombre_ejercicio = EntryFalso(nombre)
        interfaz._ent_duracion = EntryFalso(duracion)
        interfaz._cb_intensidad = ComboboxFalso(intensidad)
        interfaz._ent_calorias = EntryFalso(calorias)
        interfaz._ent_veces_planificadas = EntryFalso(planificadas)
        interfaz._ent_veces_realizadas = EntryFalso(realizadas)
        interfaz._ent_observaciones = EntryFalso(observaciones)


    def test_propiedad_id_rutina_devuelve_valor_asignado(
        self,
        interfaz,
    ):
        """
        Verifica que id_rutina devuelva la rutina configurada.
        """
        interfaz._id_rutina = 15

        assert interfaz.id_rutina == 15


    def test_propiedad_id_rutina_devuelve_none_si_no_existe(
        self,
        interfaz,
    ):
        """
        Verifica compatibilidad cuando no se ejecutó __init__.
        """
        assert interfaz.id_rutina is None


    def test_obtener_texto_devuelve_texto_limpio(
        self,
        interfaz,
    ):
        """
        Verifica que _obtener_texto elimine espacios laterales.
        """
        interfaz._ent_prueba = EntryFalso("  texto de prueba  ")

        resultado = interfaz._obtener_texto("_ent_prueba")

        assert resultado == "texto de prueba"


    def test_obtener_texto_devuelve_vacio_si_widget_no_existe(
        self,
        interfaz,
    ):
        """
        Verifica que un widget inexistente se trate como texto vacío.
        """
        resultado = interfaz._obtener_texto("_widget_inexistente")

        assert resultado == ""


    def test_modo_compatibilidad_es_verdadero_sin_campos_completos(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica el modo usado por pruebas antiguas.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        assert interfaz._es_modo_compatibilidad_tests() is True


    def test_modo_compatibilidad_es_falso_con_formulario_completo(
        self,
        interfaz,
    ):
        """
        Verifica el modo real de la aplicación.
        """
        self.asignar_widgets_completos(interfaz)

        assert interfaz._es_modo_compatibilidad_tests() is False


    def test_registrar_sesion_modo_completo_correctamente(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica el registro usando todos los campos del formulario.
        """
        self.asignar_widgets_completos(
            interfaz,
            nombre="Sentadillas",
            duracion="30",
            intensidad="ALTA",
            calorias="420.5",
            planificadas="4",
            realizadas="4",
            observaciones="Serie completada",
        )

        fecha_prueba = date(2026, 9, 25)

        sesion = SimpleNamespace(
            completada=True,
            veces_realizadas=4,
            veces_planificadas=4,
        )

        control_sesiones.registrar_sesion.return_value = sesion

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
            cliente=10,
            rutina=25,
            fecha=fecha_prueba,
            nombre_ejercicio="Sentadillas",
            duracion_real=30,
            intensidad_real="ALTA",
            calorias_quemadas=420.5,
            observaciones="Serie completada",
            veces_planificadas=4,
            veces_realizadas=4,
        )

        mock_mensaje.assert_called_once_with(
            "Sesión registrada correctamente.\n"
            "Estado: completada\n"
            "Cumplimiento: 4/4"
        )

        mock_cancelar.assert_called_once_with()


    def test_registrar_sesion_completa_muestra_estado_pendiente(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica el mensaje cuando la sesión queda pendiente.
        """
        self.asignar_widgets_completos(
            interfaz,
            planificadas="5",
            realizadas="2",
        )

        control_sesiones.registrar_sesion.return_value = (
            SimpleNamespace(
                completada=False,
                veces_realizadas=2,
                veces_planificadas=5,
            )
        )

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "cancelarRegistro",
        ):
            interfaz.registrarSesion()

        mock_mensaje.assert_called_once_with(
            "Sesión registrada correctamente.\n"
            "Estado: pendiente\n"
            "Cumplimiento: 2/5"
        )


    def test_registrar_sesion_completa_sin_nombre(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que el nombre del ejercicio sea obligatorio.
        """
        self.asignar_widgets_completos(
            interfaz,
            nombre="",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "El nombre del ejercicio es obligatorio."
        )


    def test_registrar_sesion_completa_nombre_mayor_a_100(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica el límite de longitud del nombre del ejercicio.
        """
        self.asignar_widgets_completos(
            interfaz,
            nombre="E" * 101,
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "El nombre del ejercicio no puede superar "
            "100 caracteres."
        )


    def test_registrar_sesion_completa_sin_repeticiones(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que las repeticiones sean obligatorias.
        """
        self.asignar_widgets_completos(
            interfaz,
            planificadas="",
            realizadas="",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Complete duración, intensidad, calorías, "
            "veces planificadas y veces realizadas."
        )


    def test_registrar_sesion_duracion_cero(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que la duración sea mayor que cero.
        """
        self.asignar_widgets_completos(
            interfaz,
            duracion="0",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "La duración debe ser mayor que cero."
        )


    def test_registrar_sesion_calorias_negativas(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que las calorías no sean negativas.
        """
        self.asignar_widgets_completos(
            interfaz,
            calorias="-25.5",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Las calorías no pueden ser negativas."
        )


    def test_registrar_sesion_planificadas_cero(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que las veces planificadas sean mayores que cero.
        """
        self.asignar_widgets_completos(
            interfaz,
            planificadas="0",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Las veces planificadas deben ser mayores que cero."
        )


    def test_registrar_sesion_realizadas_negativas(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que las veces realizadas no sean negativas.
        """
        self.asignar_widgets_completos(
            interfaz,
            realizadas="-1",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Las veces realizadas no pueden ser negativas."
        )


    def test_registrar_sesion_realizadas_superan_planificadas(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que las repeticiones realizadas no superen las planificadas.
        """
        self.asignar_widgets_completos(
            interfaz,
            planificadas="3",
            realizadas="4",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Las veces realizadas no pueden superar "
            "las planificadas."
        )


    def test_registrar_sesion_repeticiones_no_numericas(
        self,
        interfaz,
        control_sesiones,
    ):
        """
        Verifica que repeticiones no numéricas se manejen como ValueError.
        """
        self.asignar_widgets_completos(
            interfaz,
            planificadas="tres",
            realizadas="dos",
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarSesion()

        control_sesiones.registrar_sesion.assert_not_called()

        mock_error.assert_called_once_with(
            "Duracion debe ser entero y Calorias decimal."
        )


    def test_cancelar_registro_limpia_formulario_completo(
        self,
        interfaz,
    ):
        """
        Verifica que cancelarRegistro limpie todos los widgets actuales.
        """
        self.asignar_widgets_completos(
            interfaz,
            nombre="Bicicleta",
            duracion="50",
            intensidad="ALTA",
            calorias="600",
            planificadas="5",
            realizadas="3",
            observaciones="Observación",
        )

        interfaz.cancelarRegistro()

        assert interfaz._ent_nombre_ejercicio.valor == ""
        assert interfaz._ent_duracion.valor == ""
        assert interfaz._cb_intensidad.valor == ""
        assert interfaz._ent_calorias.valor == ""
        assert interfaz._ent_veces_planificadas.valor == ""
        assert interfaz._ent_veces_realizadas.valor == ""
        assert interfaz._ent_observaciones.valor == ""

    def test_constructor_inicializa_interfaz_y_muestra_formulario(
        self,
        control_sesiones,
    ):
        """
        Verifica que el constructor configure la interfaz completa.
        """
        master = MagicMock()

        with patch(
            "src.interfaz.interfaz_registro_sesion.InterfazBase.__init__",
            return_value=None,
        ) as mock_base_init, patch.object(
            InterfazRegistroSesion,
            "pack",
        ) as mock_pack, patch.object(
            InterfazRegistroSesion,
            "mostrarFormularioSesion",
        ) as mock_formulario:
            interfaz = InterfazRegistroSesion(
                master=master,
                control_sesiones=control_sesiones,
                id_cliente=10,
                id_rutina=25,
            )

        mock_base_init.assert_called_once_with(
            master,
            controlador=control_sesiones,
            padding=10,
        )

        mock_pack.assert_called_once_with(
            fill="both",
            expand=True,
        )

        mock_formulario.assert_called_once_with()

        assert interfaz.id_cliente == 10
        assert interfaz.id_rutina == 25
        