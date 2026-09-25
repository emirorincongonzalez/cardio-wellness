from unittest.mock import MagicMock, patch
import tkinter as tk

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
        self.configuraciones = []

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

        if len(args) >= 2 and args[0] == 0:
            self.valor = str(args[1])

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
        if not hasattr(self, "configuraciones"):
            self.configuraciones = []

        self.configuraciones.append((args, kwargs))

    def bind(self, *args, **kwargs):
        self.bind_args = args
        self.bind_kwargs = kwargs

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

    def test_constructor_inicializa_interfaz(
        self,
        control_ejercicios,
    ):
        """
        Verifica el constructor real sin abrir Tkinter.
        """
        master = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "InterfazBase.__init__",
            return_value=None,
        ) as mock_base_init, patch.object(
            InterfazGestionEjercicios,
            "pack",
        ) as mock_pack, patch.object(
            InterfazGestionEjercicios,
            "mostrarFormularioEjercicio",
        ) as mock_formulario, patch.object(
            InterfazGestionEjercicios,
            "mostrarEjercicios",
        ) as mock_mostrar:
            interfaz = InterfazGestionEjercicios(
                master,
                control_ejercicios,
            )

        mock_base_init.assert_called_once_with(
            master,
            controlador=control_ejercicios,
            padding=10,
        )

        mock_pack.assert_called_once_with(
            fill="both",
            expand=True,
        )

        mock_formulario.assert_called_once_with()
        mock_mostrar.assert_called_once_with()

        assert interfaz.control_ejercicios is control_ejercicios
        assert interfaz._id_ejercicio_editando is None
        assert interfaz._descripciones_ejercicios == {}
        assert interfaz._ejercicios_por_id == {}


    def test_mostrar_ejercicios_crea_treeview_si_no_existe(
        self,
        interfaz,
        control_ejercicios,
        ejercicio,
    ):
        """
        Verifica creación y configuración de la tabla.
        """
        tree = TreeviewFalso()

        control_ejercicios.listar.return_value = [
            ejercicio,
        ]

        with patch(
            "src.interfaz.interfaz_gestion_ejercicios."
            "ttk.Treeview",
            return_value=tree,
        ) as mock_treeview:
            interfaz.mostrarEjercicios()

        columnas = (
            "ID",
            "Nombre",
            "Tipo",
            "Descripcion",
            "Duracion",
            "Intensidad",
            "Calorias",
        )

        mock_treeview.assert_called_once_with(
            interfaz,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=10,
        )

        assert interfaz._tree is tree

        assert len(tree.insertados) == 1

        assert tree.bind_args[0] == "<<TreeviewSelect>>"
        assert tree.bind_args[1] == (
            interfaz._cargar_ejercicio_seleccionado
        )


    def test_insertar_ejercicio_inicializa_diccionarios_si_faltan(
        self,
        interfaz,
        ejercicio,
    ):
        """
        Verifica compatibilidad cuando no existen diccionarios internos.
        """
        interfaz._tree = TreeviewFalso()

        del interfaz._descripciones_ejercicios
        del interfaz._ejercicios_por_id

        interfaz._insertar_ejercicio(ejercicio)

        assert interfaz._descripciones_ejercicios == {
            1: "Actividad suave",
        }

        assert interfaz._ejercicios_por_id == {
            1: ejercicio,
        }

        assert len(interfaz._tree.insertados) == 1


    @pytest.mark.parametrize(
        ("campo", "valor", "mensaje"),
        [
            (
                "nombre",
                "",
                "Ingrese el nombre del ejercicio.",
            ),
            (
                "tipo",
                "",
                "Seleccione el tipo.",
            ),
            (
                "descripcion",
                "",
                "Ingrese la descripción.",
            ),
            (
                "duracion",
                "",
                "Ingrese la duración.",
            ),
            (
                "intensidad",
                "",
                "Seleccione la intensidad.",
            ),
            (
                "calorias",
                "",
                "Ingrese las calorías estimadas.",
            ),
        ],
    )
    def test_leer_datos_formulario_valida_campos_obligatorios(
        self,
        interfaz,
        widgets_formulario,
        campo,
        valor,
        mensaje,
    ):
        """
        Verifica cada campo obligatorio del formulario.
        """
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

        widgets_formulario[campo].valor = valor

        with pytest.raises(ValueError) as error:
            interfaz._leer_datos_formulario()

        assert str(error.value) == mensaje


    @pytest.mark.parametrize(
        ("duracion", "calorias", "mensaje"),
        [
            (
                "treinta",
                "250",
                "La duración debe ser un entero.",
            ),
            (
                "30",
                "muchas",
                "Las calorías deben ser numéricas.",
            ),
            (
                "0",
                "250",
                "La duración debe ser mayor que cero.",
            ),
            (
                "-5",
                "250",
                "La duración debe ser mayor que cero.",
            ),
            (
                "30",
                "0",
                "Las calorías deben ser mayores que cero.",
            ),
            (
                "30",
                "-10",
                "Las calorías deben ser mayores que cero.",
            ),
        ],
    )
    def test_leer_datos_formulario_valida_numeros(
        self,
        interfaz,
        widgets_formulario,
        duracion,
        calorias,
        mensaje,
    ):
        """
        Verifica validaciones numéricas del formulario.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Caminata"
        widgets_formulario["tipo"].valor = "LISS"
        widgets_formulario["descripcion"].valor = (
            "Actividad suave"
        )
        widgets_formulario["duracion"].valor = duracion
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = calorias

        with pytest.raises(ValueError) as error:
            interfaz._leer_datos_formulario()

        assert str(error.value) == mensaje


    def test_cargar_ejercicio_seleccionado_carga_formulario(
        self,
        interfaz,
        ejercicio,
        widgets_formulario,
    ):
        """
        Verifica que una selección cargue datos para edición.
        """
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
                ),
            },
        }

        interfaz._ejercicios_por_id = {
            1: ejercicio,
        }

        interfaz._lbl_modo = WidgetFalso()

        interfaz._cargar_ejercicio_seleccionado()

        assert interfaz._id_ejercicio_editando == 1

        assert widgets_formulario["nombre"].valor == "Caminata"

        assert widgets_formulario["descripcion"].valor == (
            "Actividad suave"
        )

        assert widgets_formulario["tipo"].valor == "LISS"
        assert widgets_formulario["duracion"].valor == "30"
        assert widgets_formulario["intensidad"].valor == "MEDIA"
        assert widgets_formulario["calorias"].valor == "250.0"

        assert interfaz._lbl_modo.configuraciones == [
            (
                (),
                {
                    "text": "Modo: editando ejercicio #1",
                    "foreground": "#174ea6",
                },
            ),
        ]


    def test_cargar_ejercicio_sin_seleccion_no_hace_nada(
        self,
        interfaz,
    ):
        """
        Verifica retorno temprano sin selección.
        """
        interfaz._tree = TreeviewFalso()

        interfaz._cargar_ejercicio_seleccionado()

        assert not hasattr(
            interfaz,
            "_id_ejercicio_editando",
        )


    def test_cargar_ejercicio_con_item_sin_valores_no_hace_nada(
        self,
        interfaz,
    ):
        """
        Verifica retorno temprano si el item no contiene valores.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (),
            },
        }

        interfaz._cargar_ejercicio_seleccionado()

        assert not hasattr(
            interfaz,
            "_id_ejercicio_editando",
        )


    def test_cargar_ejercicio_con_id_invalido_muestra_error(
        self,
        interfaz,
    ):
        """
        Verifica el manejo de un ID no convertible a entero.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    "no-es-id",
                ),
            },
        }

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._cargar_ejercicio_seleccionado()

        mock_error.assert_called_once_with(
            "El ID del ejercicio no es válido."
        )


    def test_cargar_ejercicio_no_encontrado_muestra_error(
        self,
        interfaz,
    ):
        """
        Verifica el manejo de una selección no registrada.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    99,
                ),
            },
        }

        interfaz._ejercicios_por_id = {}

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._cargar_ejercicio_seleccionado()

        mock_error.assert_called_once_with(
            "No se encontró el ejercicio seleccionado."
        )


    def test_editar_ejercicio_item_sin_valores(
        self,
        interfaz,
    ):
        """
        Verifica error cuando el item seleccionado no tiene valores.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (),
            },
        }

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarEjercicio()

        mock_error.assert_called_once_with(
            "No se pudo obtener el ejercicio seleccionado."
        )


    def test_editar_ejercicio_con_id_invalido(
        self,
        interfaz,
    ):
        """
        Verifica error al editar con un ID inválido.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    "abc",
                ),
            },
        }

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarEjercicio()

        mock_error.assert_called_once_with(
            "El ID del ejercicio no es válido."
        )


    def test_editar_ejercicio_no_encontrado(
        self,
        interfaz,
    ):
        """
        Verifica error si el ejercicio no existe en el diccionario.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    55,
                ),
            },
        }

        interfaz._ejercicios_por_id = {}

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarEjercicio()

        mock_error.assert_called_once_with(
            "No se encontró el ejercicio seleccionado."
        )


    def test_editar_ejercicio_maneja_value_error_formulario(
        self,
        interfaz,
        ejercicio,
        widgets_formulario,
    ):
        """
        Verifica ValueError al leer los datos de edición.
        """
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
                ),
            },
        }

        interfaz._ejercicios_por_id = {
            1: ejercicio,
        }

        widgets_formulario["nombre"].valor = ""

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarEjercicio()

        mock_error.assert_called_once_with(
            "Ingrese el nombre del ejercicio."
        )


    def test_editar_ejercicio_maneja_error_inesperado(
        self,
        interfaz,
        ejercicio,
        widgets_formulario,
        control_ejercicios,
    ):
        """
        Verifica error inesperado durante actualización.
        """
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
                ),
            },
        }

        interfaz._ejercicios_por_id = {
            1: ejercicio,
        }

        widgets_formulario["nombre"].valor = "Caminata"
        widgets_formulario["tipo"].valor = "LISS"
        widgets_formulario["descripcion"].valor = (
            "Actividad suave"
        )
        widgets_formulario["duracion"].valor = "30"
        widgets_formulario["intensidad"].valor = "MEDIA"
        widgets_formulario["calorias"].valor = "250"

        control_ejercicios.actualizar_ejercicio.side_effect = (
            RuntimeError("No se pudo actualizar")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarEjercicio()

        mock_error.assert_called_once_with(
            "Error al editar ejercicio: No se pudo actualizar"
        )


    def test_eliminar_ejercicio_item_sin_valores(
        self,
        interfaz,
    ):
        """
        Verifica error al eliminar si el item no tiene valores.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (),
            },
        }

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarEjercicio()

        mock_error.assert_called_once_with(
            "El ID del ejercicio no es válido."
        )


    def test_eliminar_ejercicio_con_id_invalido(
        self,
        interfaz,
    ):
        """
        Verifica error al eliminar con ID inválido.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    "invalido",
                ),
            },
        }

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarEjercicio()

        mock_error.assert_called_once_with(
            "El ID del ejercicio no es válido."
        )


    def test_eliminar_ejercicio_limpia_formulario_completo(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        """
        Verifica limpieza después de eliminar un ejercicio.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                ),
            },
        }

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ), patch.object(
            interfaz,
            "mostrarEjercicios",
        ) as mock_mostrar:
            interfaz.eliminarEjercicio()

        control_ejercicios.eliminar_ejercicio.assert_called_once_with(
            5
        )

        mock_mostrar.assert_called_once_with()

        assert widgets_formulario["nombre"].valor == ""
        assert widgets_formulario["descripcion"].valor == ""
        assert widgets_formulario["duracion"].valor == ""
        assert widgets_formulario["calorias"].valor == ""
        assert widgets_formulario["tipo"].valor == ""
        assert widgets_formulario["intensidad"].valor == ""


    def test_cancelar_edicion_limpia_formulario(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica que cancelar edición reutilice la limpieza.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        with patch.object(
            interfaz,
            "_limpiar_formulario",
        ) as mock_limpiar:
            interfaz._cancelar_edicion()

        mock_limpiar.assert_called_once_with()


    def test_limpiar_formulario_reinicia_modo_edicion(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica reinicio del ID y etiqueta de modo.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._id_ejercicio_editando = 8
        interfaz._lbl_modo = WidgetFalso()

        interfaz._limpiar_formulario()

        assert interfaz._id_ejercicio_editando is None

    def test_buscar_ejercicio_elimina_resultados_anteriores(
        self,
        interfaz,
        control_ejercicios,
        widgets_formulario,
    ):
        """
        Verifica que la búsqueda limpie resultados anteriores
        antes de insertar los nuevos.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()

        interfaz._tree.items = {
            "item_anterior_1": {
                "values": (
                    1,
                    "Ejercicio anterior",
                ),
            },
            "item_anterior_2": {
                "values": (
                    2,
                    "Otro ejercicio",
                ),
            },
        }

        widgets_formulario["buscar"].valor = "cami"

        control_ejercicios.listar.return_value = []

        interfaz.buscarEjercicio()

        assert interfaz._tree.eliminaciones == [
            (
                ("item_anterior_1",),
                {},
            ),
            (
                ("item_anterior_2",),
                {},
            ),
        ]

        control_ejercicios.listar.assert_called_once_with()