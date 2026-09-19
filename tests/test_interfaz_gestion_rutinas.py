from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_gestion_rutinas import (
    InterfazGestionRutinas,
)


class WidgetFalso:
    """
    Widget genérico falso para simular widgets ttk.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.valor = ""
        self.eliminaciones = []
        self.insertados = []
        self.seleccion_actual = []
        self.items = {}

    def pack(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        self.eliminaciones.append((args, kwargs))
        self.valor = ""

    def get(self):
        return self.valor

    def insert(self, *args, **kwargs):
        self.insertados.append((args, kwargs))

    def selection(self):
        return self.seleccion_actual

    def item(self, item_id):
        return self.items.get(
            item_id,
            {"values": []},
        )

    def heading(self, *args, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def config(self, *args, **kwargs):
        pass

    def set(self, valor):
        self.valor = valor

    def get_children(self):
        return list(self.items.keys())


class FrameFalso(WidgetFalso):
    pass


class LabelFalso(WidgetFalso):
    pass


class LabelFrameFalso(WidgetFalso):
    pass


class EntryFalso(WidgetFalso):
    pass


class ButtonFalso(WidgetFalso):
    pass


class ComboboxFalso(WidgetFalso):
    pass


class TreeviewFalso(WidgetFalso):
    pass


class TestInterfazGestionRutinas:

    @pytest.fixture
    def control_rutinas(self):
        """
        Crea un controlador de rutinas simulado.
        """
        controlador = MagicMock()
        controlador.listar.return_value = []

        return controlador

    @pytest.fixture
    def rutina(self):
        """
        Crea una rutina simulada.
        """
        rutina = MagicMock()

        rutina.id_rutina = 1
        rutina.nombre = "Rutina inicial"
        rutina.objetivo = "Mejorar resistencia"
        rutina.duracion_semanas = 8
        rutina.nivel.value = "BASICO"

        return rutina

    @pytest.fixture
    def interfaz(self, control_rutinas):
        """
        Crea la interfaz sin ejecutar el constructor real.
        """
        interfaz = object.__new__(InterfazGestionRutinas)

        interfaz._controlador = control_rutinas
        interfaz._control_rutinas = control_rutinas

        return interfaz

    @pytest.fixture
    def widgets_formulario(self):
        """
        Crea los widgets falsos del formulario.
        """
        return {
            "nombre": EntryFalso(),
            "nivel": ComboboxFalso(),
            "descripcion": EntryFalso(),
            "objetivo": EntryFalso(),
            "duracion": EntryFalso(),
        }

    def asignar_widgets_formulario(
        self,
        interfaz,
        widgets,
    ):
        """
        Asigna los widgets falsos a la interfaz.
        """
        interfaz._ent_nombre = widgets["nombre"]
        interfaz._cb_nivel = widgets["nivel"]
        interfaz._ent_descripcion = widgets["descripcion"]
        interfaz._ent_objetivo = widgets["objetivo"]
        interfaz._ent_duracion = widgets["duracion"]

    def test_control_rutinas_devuelve_el_controlador(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica la propiedad control_rutinas.
        """
        assert interfaz.control_rutinas is control_rutinas

    def test_mostrar_formulario_rutina_crea_widgets(
        self,
        interfaz,
    ):
        """
        Verifica que se creen los widgets del formulario.
        """
        with patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Combobox",
            side_effect=ComboboxFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Button",
            side_effect=ButtonFalso,
        ):
            interfaz.mostrarFormularioRutina()

        assert hasattr(interfaz, "_ent_nombre")
        assert hasattr(interfaz, "_cb_nivel")
        assert hasattr(interfaz, "_ent_descripcion")
        assert hasattr(interfaz, "_ent_objetivo")
        assert hasattr(interfaz, "_ent_duracion")

        assert isinstance(interfaz._ent_nombre, EntryFalso)
        assert isinstance(interfaz._cb_nivel, ComboboxFalso)
        assert isinstance(interfaz._ent_descripcion, EntryFalso)
        assert isinstance(interfaz._ent_objetivo, EntryFalso)
        assert isinstance(interfaz._ent_duracion, EntryFalso)

    def test_mostrar_rutinas_carga_rutinas(
        self,
        interfaz,
        control_rutinas,
        rutina,
    ):
        """
        Verifica que las rutinas se carguen en la tabla.
        """
        interfaz._tree = TreeviewFalso()
        control_rutinas.listar.return_value = [rutina]

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarRutinas()

        control_rutinas.listar.assert_called_once_with()

        assert interfaz._tree.insertados == [
            (
                ("", "end"),
                {
                    "values": (
                        1,
                        "Rutina inicial",
                        "Mejorar resistencia",
                        "BASICO",
                        "8 sem",
                    )
                },
            )
        ]

        mock_error.assert_not_called()

    def test_mostrar_rutinas_elimina_datos_anteriores(
        self,
        interfaz,
        control_rutinas,
        rutina,
    ):
        """
        Verifica que se eliminen los datos anteriores
        antes de cargar las rutinas.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.items = {
            "item1": {
                "values": (
                    1,
                    "Rutina anterior",
                )
            }
        }

        control_rutinas.listar.return_value = [rutina]

        interfaz.mostrarRutinas()

        assert len(interfaz._tree.eliminaciones) == 1
        assert interfaz._tree.eliminaciones[0][0] == ("item1",)

    def test_mostrar_rutinas_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica el manejo de errores al listar rutinas.
        """
        interfaz._tree = TreeviewFalso()

        control_rutinas.listar.side_effect = RuntimeError(
            "Error de base de datos"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarRutinas()

        mock_error.assert_called_once_with(
            "Error al cargar rutinas: Error de base de datos"
        )

    def test_crear_rutina_correctamente(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        """
        Verifica la creación correcta de una rutina.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = " Rutina inicial "
        widgets_formulario["nivel"].valor = " BASICO "
        widgets_formulario["descripcion"].valor = "Rutina de inicio"
        widgets_formulario["objetivo"].valor = "Mejorar resistencia"
        widgets_formulario["duracion"].valor = "8"

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarRutinas",
        ) as mock_mostrar_rutinas:

            interfaz.crearRutina()

        control_rutinas.crear_rutina.assert_called_once_with(
            nombre="Rutina inicial",
            descripcion="Rutina de inicio",
            objetivo="Mejorar resistencia",
            nivel="BASICO",
            duracion_semanas=8,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina creada exitosamente."
        )

        mock_mostrar_rutinas.assert_called_once_with()

        assert widgets_formulario["nombre"].valor == ""
        assert widgets_formulario["nivel"].valor == ""
        assert widgets_formulario["descripcion"].valor == ""
        assert widgets_formulario["objetivo"].valor == ""
        assert widgets_formulario["duracion"].valor == ""

    def test_crear_rutina_maneja_value_error(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        """
        Verifica el manejo de errores de conversión.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Rutina inicial"
        widgets_formulario["nivel"].valor = "BASICO"
        widgets_formulario["descripcion"].valor = "Rutina de inicio"
        widgets_formulario["objetivo"].valor = "Resistencia"
        widgets_formulario["duracion"].valor = "duración inválida"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.crearRutina()

        control_rutinas.crear_rutina.assert_not_called()
        mock_error.assert_called_once()

    def test_crear_rutina_maneja_error_del_controlador(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        """
        Verifica el manejo de errores inesperados.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Rutina inicial"
        widgets_formulario["nivel"].valor = "BASICO"
        widgets_formulario["descripcion"].valor = "Rutina de inicio"
        widgets_formulario["objetivo"].valor = "Resistencia"
        widgets_formulario["duracion"].valor = "8"

        control_rutinas.crear_rutina.side_effect = RuntimeError(
            "Error inesperado"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.crearRutina()

        mock_error.assert_called_once_with(
            "Error inesperado: Error inesperado"
        )

    def test_editar_rutina_sin_seleccion(
        self,
        interfaz,
    ):
        """
        Verifica el error cuando no se selecciona
        ninguna rutina para editar.
        """
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarRutina()

        mock_error.assert_called_once_with(
            "Seleccione una rutina para editar."
        )

    def test_editar_rutina_con_seleccion(
        self,
        interfaz,
    ):
        """
        Verifica el mensaje actual de edición pendiente.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.editarRutina()

        mock_mensaje.assert_called_once_with(
            "Funcionalidad de edicion pendiente de implementar."
        )

    def test_eliminar_rutina_sin_seleccion(
        self,
        interfaz,
    ):
        """
        Verifica el error cuando no se selecciona
        ninguna rutina para eliminar.
        """
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarRutina()

        mock_error.assert_called_once_with(
            "Seleccione una rutina para eliminar."
        )

    def test_eliminar_rutina_usuario_cancela(
        self,
        interfaz,
    ):
        """
        Verifica que no se elimine al cancelar la confirmación.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=False,
        ) as mock_confirmar:
            interfaz.eliminarRutina()

        mock_confirmar.assert_called_once_with(
            "Eliminar la rutina con ID 5?"
        )

    def test_eliminar_rutina_correctamente(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica la eliminación correcta de una rutina.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarRutinas",
        ) as mock_mostrar_rutinas:

            interfaz.eliminarRutina()

        control_rutinas.eliminar_rutina.assert_called_once_with(5)

        mock_mensaje.assert_called_once_with(
            "Rutina eliminada correctamente."
        )

        mock_mostrar_rutinas.assert_called_once_with()

    def test_eliminar_rutina_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica el manejo de errores al eliminar.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        control_rutinas.eliminar_rutina.side_effect = RuntimeError(
            "No se pudo eliminar"
        )

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.eliminarRutina()

        mock_error.assert_called_once_with(
            "Error al eliminar: No se pudo eliminar"
        )

    def test_asignar_rutina_sin_seleccion(
        self,
        interfaz,
    ):
        """
        Verifica el error cuando no se selecciona
        ninguna rutina para asignar.
        """
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.asignarRutina()

        mock_error.assert_called_once_with(
            "Seleccione una rutina para asignar."
        )

    def test_asignar_rutina_cancelada(
        self,
        interfaz,
    ):
        """
        Verifica que no se asigne la rutina cuando
        se cancela el diálogo.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        with patch(
            "tkinter.simpledialog.askinteger",
            return_value=None,
        ) as mock_dialogo:
            interfaz.asignarRutina()

        mock_dialogo.assert_called_once_with(
            "Asignar Rutina",
            "Ingrese el ID del cliente:",
            parent=interfaz,
        )

        interfaz.control_rutinas.asignar_rutina.assert_not_called()

    def test_asignar_rutina_correctamente(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica la asignación correcta de una rutina.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        with patch(
            "tkinter.simpledialog.askinteger",
            return_value=10,
        ) as mock_dialogo, patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:

            interfaz.asignarRutina()

        mock_dialogo.assert_called_once_with(
            "Asignar Rutina",
            "Ingrese el ID del cliente:",
            parent=interfaz,
        )

        control_rutinas.asignar_rutina.assert_called_once_with(
            id_cliente=10,
            id_rutina=5,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina 5 asignada al cliente 10."
        )

    def test_asignar_rutina_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
        """
        Verifica el manejo de errores al asignar una rutina.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        control_rutinas.asignar_rutina.side_effect = RuntimeError(
            "No se pudo asignar"
        )

        with patch(
            "tkinter.simpledialog.askinteger",
            return_value=10,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.asignarRutina()

        mock_error.assert_called_once_with(
            "Error al asignar rutina: No se pudo asignar"
        )

    def test_limpiar_formulario(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica que se limpien todos los campos del formulario.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        campos_entry = (
            widgets_formulario["nombre"],
            widgets_formulario["descripcion"],
            widgets_formulario["objetivo"],
            widgets_formulario["duracion"],
        )

        for entry in campos_entry:
            entry.valor = "dato"

        widgets_formulario["nivel"].valor = "BASICO"

        interfaz._limpiar_formulario()

        for entry in campos_entry:
            assert entry.valor == ""

        assert widgets_formulario["nivel"].valor == ""