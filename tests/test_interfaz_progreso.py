from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_progreso import InterfazProgreso


class WidgetFalso:
    """
    Widget falso para simular widgets ttk.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.configuraciones = []
        self.insertados = []
        self.items = {}

    def pack(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass

    def heading(self, *args, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def config(self, *args, **kwargs):
        self.configuraciones.append((args, kwargs))

    def insert(self, *args, **kwargs):
        self.insertados.append((args, kwargs))

    def get_children(self):
        return list(self.items.keys())

    def delete(self, item_id):
        self.items.pop(item_id, None)


class FrameFalso(WidgetFalso):
    pass


class LabelFalso(WidgetFalso):
    pass


class LabelFrameFalso(WidgetFalso):
    pass


class TreeviewFalso(WidgetFalso):
    pass


class TestInterfazProgreso:

    @pytest.fixture
    def cliente(self):
        """
        Crea un cliente simulado.
        """
        cliente = MagicMock()

        cliente.id_usuario = 10
        cliente.peso = 70
        cliente.objetivo = "Mejorar resistencia"

        return cliente

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
        control_progreso,
    ):
        """
        Crea la interfaz sin ejecutar el constructor real.
        """
        interfaz = object.__new__(InterfazProgreso)

        interfaz._controlador = control_progreso
        interfaz._cliente = cliente

        return interfaz

    def test_propiedad_cliente(
        self,
        interfaz,
        cliente,
    ):
        """
        Verifica la propiedad cliente.
        """
        assert interfaz.cliente is cliente

    def test_mostrar_resumen_correctamente(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica que se cargue correctamente el resumen.
        """
        resumen = {
            "total_sesiones": 12,
            "total_minutos": 360,
            "total_calorias": 2500,
        }

        control_progreso.calcular_resumen_cliente.return_value = resumen

        lbl_sesiones = MagicMock()
        lbl_minutos = MagicMock()
        lbl_calorias = MagicMock()
        lbl_meta = MagicMock()

        widgets_label = iter(
            [
                lbl_sesiones,
                lbl_minutos,
                lbl_calorias,
                lbl_meta,
            ]
        )

        with patch(
            "src.interfaz.interfaz_progreso.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Label",
            side_effect=lambda *args, **kwargs: next(widgets_label),
        ), patch.object(
            interfaz,
            "_evaluar_meta",
        ) as mock_evaluar_meta:

            interfaz.mostrarResumen()

        control_progreso.calcular_resumen_cliente.assert_called_once_with(
            interfaz.cliente.id_usuario
        )

        lbl_sesiones.config.assert_called_once_with(
            text="Sesiones: 12"
        )

        lbl_minutos.config.assert_called_once_with(
            text="Minutos: 360"
        )

        lbl_calorias.config.assert_called_once_with(
            text="Calorias: 2500"
        )

        mock_evaluar_meta.assert_called_once_with(resumen)

    def test_mostrar_resumen_maneja_error(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica el manejo de errores al cargar el resumen.
        """
        control_progreso.calcular_resumen_cliente.side_effect = (
            RuntimeError("Error de base de datos")
        )

        lbl_sesiones = MagicMock()
        lbl_minutos = MagicMock()
        lbl_calorias = MagicMock()
        lbl_meta = MagicMock()

        widgets_label = iter(
            [
                lbl_sesiones,
                lbl_minutos,
                lbl_calorias,
                lbl_meta,
            ]
        )

        with patch(
            "src.interfaz.interfaz_progreso.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Label",
            side_effect=lambda *args, **kwargs: next(widgets_label),
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarResumen()

        mock_error.assert_called_once_with(
            "Error al cargar resumen: Error de base de datos"
        )

    def test_mostrar_progreso_mensual_carga_historial(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica que se cargue el historial mensual.
        """
        progreso = MagicMock()

        progreso.mes = datetime(2026, 1, 15)
        progreso.peso = 70.5
        progreso.sesiones_completadas = 8
        progreso.sesiones_planificadas = 12
        progreso.porcentaje_cumplimiento = 66.67

        control_progreso.consultar_progreso.return_value = [
            progreso
        ]

        with patch(
            "src.interfaz.interfaz_progreso.ttk.Treeview",
            side_effect=TreeviewFalso,
        ):
            interfaz.mostrarProgresoMensual()

        control_progreso.consultar_progreso.assert_called_once_with(
            interfaz.cliente.id_usuario
        )

        assert interfaz._tree.insertados == [
            (
                ("", "end"),
                {
                    "values": (
                        "January 2026",
                        "70.5 kg",
                        8,
                        12,
                        "66.67%",
                    )
                },
            )
        ]

    def test_mostrar_progreso_mensual_sin_datos(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica el comportamiento cuando no hay historial.
        """
        control_progreso.consultar_progreso.return_value = []

        with patch(
            "src.interfaz.interfaz_progreso.ttk.Treeview",
            side_effect=TreeviewFalso,
        ):
            interfaz.mostrarProgresoMensual()

        control_progreso.consultar_progreso.assert_called_once_with(
            interfaz.cliente.id_usuario
        )

        assert interfaz._tree.insertados == []

    def test_mostrar_progreso_mensual_maneja_error(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Verifica el manejo de errores al cargar el historial.
        """
        control_progreso.consultar_progreso.side_effect = RuntimeError(
            "Error de base de datos"
        )

        with patch(
            "src.interfaz.interfaz_progreso.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarProgresoMensual()

        mock_error.assert_called_once_with(
            "Error al cargar historial: Error de base de datos"
        )

    def test_mostrar_historial_llama_a_mostrar_progreso_mensual(
        self,
        interfaz,
    ):
        """
        Verifica que mostrarHistorial sea un alias correcto.
        """
        with patch.object(
            interfaz,
            "mostrarProgresoMensual",
        ) as mock_mostrar:

            interfaz.mostrarHistorial()

        mock_mostrar.assert_called_once_with()

    def test_evaluar_meta_sesiones_alcanzada(
        self,
        interfaz,
    ):
        """
        Verifica una meta alcanzada por cantidad de sesiones.
        """
        interfaz._lbl_meta = MagicMock()
        interfaz._cliente.objetivo = "Mejorar resistencia"

        resumen = {
            "total_sesiones": 12,
        }

        interfaz._evaluar_meta(resumen)

        interfaz._lbl_meta.config.assert_called_once_with(
            text="META ALCANZADA! Sigue asi!",
            foreground="green",
        )

    def test_evaluar_meta_sesiones_no_alcanzada(
        self,
        interfaz,
    ):
        """
        Verifica una meta no alcanzada por cantidad de sesiones.
        """
        interfaz._lbl_meta = MagicMock()
        interfaz._cliente.objetivo = "Mejorar resistencia"

        resumen = {
            "total_sesiones": 5,
        }

        interfaz._evaluar_meta(resumen)

        interfaz._lbl_meta.config.assert_called_once_with(
            text="Progreso: 5/12 sesiones",
            foreground="red",
        )

    def test_evaluar_meta_bajar_peso_alcanzada(
        self,
        interfaz,
    ):
        """
        Verifica una meta alcanzada de reducción de peso.
        """
        interfaz._lbl_meta = MagicMock()
        interfaz._cliente.objetivo = "Bajar de peso"
        interfaz._cliente.peso = 70

        resumen = {
            "total_sesiones": 2,
        }

        interfaz._evaluar_meta(resumen)

        interfaz._lbl_meta.config.assert_called_once_with(
            text="META ALCANZADA! Peso: 70.0 kg",
            foreground="green",
        )

    def test_evaluar_meta_bajar_peso_no_alcanzada(
        self,
        interfaz,
    ):
        """
        Verifica una meta no alcanzada de reducción de peso.
        """
        interfaz._lbl_meta = MagicMock()
        interfaz._cliente.objetivo = "Perder peso"
        interfaz._cliente.peso = 80

        resumen = {
            "total_sesiones": 2,
        }

        interfaz._evaluar_meta(resumen)

        interfaz._lbl_meta.config.assert_called_once_with(
            text="Meta no alcanzada. Peso: 80.0 kg (Meta: 75 kg)",
            foreground="red",
        )