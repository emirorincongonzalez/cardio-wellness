from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_gestion_ejercicios import (
    InterfazGestionEjercicios,
)


class WidgetFalso:
    """
    Widget falso genérico para widgets ttk.
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


class TestInterfazGestionEjercicios:

    @pytest.fixture
    def control_ejercicios(self):
        controlador = MagicMock()
        controlador.listar.return_value = []
        return controlador

    @pytest.fixture
    def ejercicio(self):
        ejercicio = MagicMock()

        ejercicio.id_ejercicio = 1
        ejercicio.nombre = "Caminata"
        ejercicio.tipo = "LISS"
        ejercicio.descripcion = "Actividad suave"
        ejercicio.duracion_minutos = 30
        ejercicio.calorias_estimadas = 250.0
        ejercicio.intensidad.value = "MEDIA"

        return ejercicio

    @pytest.fixture
    def interfaz(self, control_ejercicios):
        interfaz = object.__new__(
            InterfazGestionEjercicios
        )

        interfaz._controlador = control_ejercicios
        interfaz._control_ejercicios = control_ejercicios
        interfaz._descripciones_ejercicios = {}
        interfaz._ejercicios_por_id = {}

        return interfaz

    @pytest.fixture
    def widgets_formulario(self):
        return {
            "nombre": EntryFalso(),
            "tipo": ComboboxFalso(),
            "descripcion": EntryFalso(),
            "duracion": EntryFalso(),
            "intensidad": ComboboxFalso(),
            "calorias": EntryFalso(),
            "buscar": EntryFalso(),
        }

    def asignar_widgets_formulario(
        self,
        interfaz,
        widgets,
    ):
        interfaz._ent_nombre = widgets["nombre"]
        interfaz._cb_tipo = widgets["tipo"]
        interfaz._ent_descripcion = widgets[
            "descripcion"
        ]
        interfaz._ent_duracion = widgets["duracion"]
        interfaz._cb_intensidad = widgets[
            "intensidad"
        ]
        interfaz._ent_calorias = widgets["calorias"]
        interfaz._ent_buscar = widgets["buscar"]

    def test_control_ejercicios_devuelve_el_controlador(
        self,
        interfaz,
        control_ejercicios,
    ):
        assert (
            interfaz.control_ejercicios
            is control_ejercicios
        )

    def test_mostrar_formulario_ejercicio_crea_widgets(
        self,
        interfaz,
    ):
        with patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.Combobox",
            side_effect=ComboboxFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.Button",
            side_effect=ButtonFalso,
        ):
            interfaz.mostrarFormularioEjercicio()

        assert isinstance(
            interfaz._ent_nombre,
            EntryFalso,
        )
        assert isinstance(
            interfaz._cb_tipo,
            ComboboxFalso,
        )
        assert isinstance(
            interfaz._ent_descripcion,
            EntryFalso,
        )
        assert isinstance(
            interfaz._ent_duracion,
            EntryFalso,
        )
        assert isinstance(
            interfaz._cb_intensidad,
            ComboboxFalso,
        )
        assert isinstance(
            interfaz._ent_calorias,
            EntryFalso,
        )
        assert isinstance(
            interfaz._ent_buscar,
            EntryFalso,
        )

    def test_mostrar_ejercicios_carga_ejercicios(
        self,
        interfaz,
        control_ejercicios,
        ejercicio,
    ):
        interfaz._tree = TreeviewFalso()
        control_ejercicios.listar.return_value = [
            ejercicio
        ]

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarEjercicios()

        control_ejercicios.listar.assert_called_once_with()

        assert interfaz._tree.insertados == [
            (
                ("", "end"),
                {
                    "values": (
                        1,
                        "Caminata",
                        "LISS",
                        "Actividad suave",
                        30,
                        "MEDIA",
                        250.0,
                    )
                },
            )
        ]

        mock_error.assert_not_called()

    def test_mostrar_ejercicios_elimina_datos_anteriores(
        self,
        interfaz,
        control_ejercicios,
        ejercicio,
    ):
        interfaz._tree = TreeviewFalso()

        interfaz._tree.items = {
            "item1": {
                "values": (
                    1,
                    "Ejercicio anterior",
                )
            }
        }

        control_ejercicios.listar.return_value = [
            ejercicio
        ]

        interfaz.mostrarEjercicios()

        assert len(
            interfaz._tree.eliminaciones
        ) == 1

        assert interfaz._tree.eliminaciones[0][0] == (
            "item1",
        )

    def test_mostrar_ejercicios_maneja_error(
        self,
        interfaz,
        control_ejercicios,
    ):
        interfaz._tree = TreeviewFalso()

        control_ejercicios.listar.side_effect = (
            RuntimeError("Error de base de datos")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarEjercicios()

        mock_error.assert_called_once_with(
            "Error al cargar ejercicios: "
            "Error de base de datos"
        )

    def test_crear_ejercicio_correctamente(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = (
            " Caminata "
        )
        widgets_formulario["tipo"].valor = " LISS "
        widgets_formulario["descripcion"].valor = (
            "Actividad suave"
        )
        widgets_formulario["duracion"].valor = "30"
        widgets_formulario["intensidad"].valor = (
            " MEDIA "
        )
        widgets_formulario["calorias"].valor = "250.5"

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarEjercicios",
        ) as mock_mostrar_ejercicios:
            interfaz.crearEjercicio()

        control_ejercicios.crear_ejercicio.assert_called_once_with(
            nombre="Caminata",
            descripcion="Actividad suave",
            tipo="LISS",
            duracion_minutos=30,
            intensidad="MEDIA",
            calorias_estimadas=250.5,
        )

        mock_mensaje.assert_called_once_with(
            "Ejercicio creado exitosamente."
        )

        mock_mostrar_ejercicios.assert_called_once_with()

        assert widgets_formulario["nombre"].valor == ""
        assert (
            widgets_formulario["descripcion"].valor
            == ""
        )
        assert widgets_formulario["duracion"].valor == ""
        assert widgets_formulario["calorias"].valor == ""
        assert widgets_formulario["tipo"].valor == ""
        assert (
            widgets_formulario["intensidad"].valor
            == ""
        )

    def test_crear_ejercicio_maneja_value_error(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Caminata"
        widgets_formulario["tipo"].valor = "LISS"
        widgets_formulario["descripcion"].valor = (
            "Actividad suave"
        )
        widgets_formulario["duracion"].valor = (
            "duración inválida"
        )
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "250"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.crearEjercicio()

        control_ejercicios.crear_ejercicio.assert_not_called()
        mock_error.assert_called_once()

    def test_crear_ejercicio_maneja_error_del_controlador(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Caminata"
        widgets_formulario["tipo"].valor = "LISS"
        widgets_formulario["descripcion"].valor = (
            "Actividad suave"
        )
        widgets_formulario["duracion"].valor = "30"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "250"

        control_ejercicios.crear_ejercicio.side_effect = (
            RuntimeError("Error inesperado")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.crearEjercicio()

        mock_error.assert_called_once_with(
            "Error inesperado: Error inesperado"
        )

    def test_editar_ejercicio_sin_seleccion(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarEjercicio()

        mock_error.assert_called_once_with(
            "Seleccione un ejercicio para editar."
        )

    def test_editar_ejercicio_con_seleccion(
        self,
        interfaz,
        control_ejercicios,
        ejercicio,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]

        interfaz._tree.items = {
            "item1": {
                "values": (
                    1,
                    "Caminata",
                    "LISS",
                    "Actividad suave",
                    30,
                    "MEDIA",
                    250.0,
                )
            }
        }

        interfaz._ejercicios_por_id = {
            1: ejercicio
        }

        widgets_formulario["nombre"].valor = (
            "Caminata rápida"
        )
        widgets_formulario["tipo"].valor = "HIIT"
        widgets_formulario["descripcion"].valor = (
            "Caminata con mayor intensidad"
        )
        widgets_formulario["duracion"].valor = "40"
        widgets_formulario["intensidad"].valor = "ALTA"
        widgets_formulario["calorias"].valor = "350"

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarEjercicios",
        ) as mock_mostrar_ejercicios:
            interfaz.editarEjercicio()

        control_ejercicios.actualizar_ejercicio.assert_called_once_with(
            ejercicio
        )

        assert ejercicio.nombre == "Caminata rápida"
        assert ejercicio.tipo == "HIIT"
        assert ejercicio.descripcion == (
            "Caminata con mayor intensidad"
        )
        assert ejercicio.duracion_minutos == 40
        assert ejercicio.intensidad == "ALTA"
        assert ejercicio.calorias_estimadas == 350.0

        mock_mensaje.assert_called_once_with(
            "Ejercicio actualizado correctamente."
        )

        mock_mostrar_ejercicios.assert_called_once_with()

    def test_eliminar_ejercicio_sin_seleccion(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarEjercicio()

        mock_error.assert_called_once_with(
            "Seleccione un ejercicio para eliminar."
        )

    def test_eliminar_ejercicio_usuario_cancela(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]

        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Caminata",
                )
            }
        }

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=False,
        ) as mock_confirmar:
            interfaz.eliminarEjercicio()

        mock_confirmar.assert_called_once_with(
            "Eliminar el ejercicio con ID 5?"
        )

    def test_eliminar_ejercicio_correctamente(
        self,
        interfaz,
        control_ejercicios,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]

        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Caminata",
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
            "mostrarEjercicios",
        ) as mock_mostrar_ejercicios:
            interfaz.eliminarEjercicio()

        control_ejercicios.eliminar_ejercicio.assert_called_once_with(
            5
        )

        mock_mensaje.assert_called_once_with(
            "Ejercicio eliminado correctamente."
        )

        mock_mostrar_ejercicios.assert_called_once_with()

    def test_eliminar_ejercicio_maneja_error(
        self,
        interfaz,
        control_ejercicios,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]

        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Caminata",
                )
            }
        }

        control_ejercicios.eliminar_ejercicio.side_effect = (
            RuntimeError("No se pudo eliminar")
        )

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarEjercicio()

        mock_error.assert_called_once_with(
            "Error al eliminar: No se pudo eliminar"
        )

    def test_buscar_ejercicio_sin_texto(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        widgets_formulario["buscar"].valor = "   "

        with patch.object(
            interfaz,
            "mostrarEjercicios",
        ) as mock_mostrar_ejercicios:
            interfaz.buscarEjercicio()

        mock_mostrar_ejercicios.assert_called_once_with()

        control = interfaz.control_ejercicios
        control.listar.assert_not_called()

    def test_buscar_ejercicio_encontrado(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
        ejercicio,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        widgets_formulario["buscar"].valor = "cami"

        control_ejercicios.listar.return_value = [
            ejercicio
        ]

        interfaz.buscarEjercicio()

        control_ejercicios.listar.assert_called_once_with()

        assert interfaz._tree.insertados == [
            (
                ("", "end"),
                {
                    "values": (
                        1,
                        "Caminata",
                        "LISS",
                        "Actividad suave",
                        30,
                        "MEDIA",
                        250.0,
                    )
                },
            )
        ]

    def test_buscar_ejercicio_no_encontrado(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        widgets_formulario["buscar"].valor = "natación"

        ejercicio = MagicMock()
        ejercicio.id_ejercicio = 1
        ejercicio.nombre = "Caminata"
        ejercicio.tipo = "LISS"
        ejercicio.descripcion = "Actividad suave"
        ejercicio.duracion_minutos = 30
        ejercicio.calorias_estimadas = 250.0
        ejercicio.intensidad.value = "MEDIA"

        control_ejercicios.listar.return_value = [
            ejercicio
        ]

        interfaz.buscarEjercicio()

        assert interfaz._tree.insertados == []

    def test_buscar_ejercicio_maneja_error(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        widgets_formulario["buscar"].valor = "cami"

        control_ejercicios.listar.side_effect = (
            RuntimeError("Error de búsqueda")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.buscarEjercicio()

        mock_error.assert_called_once_with(
            "Error al buscar: Error de búsqueda"
        )

    def test_limpiar_formulario(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        campos_entry = (
            widgets_formulario["nombre"],
            widgets_formulario["descripcion"],
            widgets_formulario["duracion"],
            widgets_formulario["calorias"],
        )

        for entry in campos_entry:
            entry.valor = "dato"

        widgets_formulario["tipo"].valor = "LISS"
        widgets_formulario["intensidad"].valor = "MEDIA"

        interfaz._limpiar_formulario()

        for entry in campos_entry:
            assert entry.valor == ""

        assert widgets_formulario["tipo"].valor == ""
        assert (
            widgets_formulario["intensidad"].valor
            == ""
        )