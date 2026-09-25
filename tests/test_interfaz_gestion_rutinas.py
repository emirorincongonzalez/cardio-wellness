from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_gestion_rutinas import (
    InterfazGestionRutinas,
)


class WidgetFalso:
    """Widget falso generico para simular widgets ttk."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.valor = ""
        self.eliminaciones = []
        self.insertados = []
        self.seleccion_actual = []
        self.items = {}
        self.configuracion = {}
        self.pack_ocultado = False
        self.fila_identificada = ""
        self.destruido = False

    def pack(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass

    def destroy(self):
        self.destruido = True

    def bind(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        self.eliminaciones.append((args, kwargs))
        self.valor = ""

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor

    def insert(self, *args, **kwargs):
        self.insertados.append((args, kwargs))

        if len(args) >= 2 and "values" not in kwargs:
            self.valor = args[1]

    def selection(self):
        return self.seleccion_actual

    def selection_remove(self, *items):
        self.seleccion_actual = []

    def item(self, item_id):
        return self.items.get(
            item_id,
            {"values": []},
        )

    def get_children(self):
        return list(self.items.keys())

    def identify_row(self, _y):
        return self.fila_identificada

    def heading(self, *args, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def columnconfigure(self, *args, **kwargs):
        pass

    def config(self, *args, **kwargs):
        self.configuracion.update(kwargs)

    def pack_forget(self):
        self.pack_ocultado = True

    def __setitem__(self, clave, valor):
        self.configuracion[clave] = valor

    def __getitem__(self, clave):
        return self.configuracion.get(clave)


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
        controlador = MagicMock()
        controlador.listar.return_value = []
        return controlador

    @pytest.fixture
    def interfaz(self, control_rutinas):
        interfaz = object.__new__(InterfazGestionRutinas)

        interfaz._controlador = control_rutinas
        interfaz._control_rutinas = control_rutinas
        interfaz._control_ejercicios = MagicMock()
        interfaz._control_autenticacion = None

        interfaz._rutinas_disponibles = []
        interfaz._ejercicios_disponibles = []

        interfaz._id_rutina_editando = None
        interfaz._id_rutina_vista_previa = None
        interfaz._id_ejercicio_seleccionado = None

        return interfaz

    @pytest.fixture
    def widgets_formulario(self):
        return {
            "nombre": EntryFalso(),
            "nivel": ComboboxFalso(),
            "descripcion": EntryFalso(),
            "objetivo": EntryFalso(),
            "duracion": EntryFalso(),
        }

    @pytest.fixture
    def rutina(self):
        return SimpleNamespace(
            id_rutina=1,
            nombre="Rutina inicial",
            descripcion="Rutina de inicio",
            objetivo="Mejorar resistencia",
            nivel=SimpleNamespace(value="BASICO"),
            duracion_semanas=8,
            creado_por=10,
            fecha_creacion="2026-01-01",
            ejercicios=[],
        )

    def asignar_widgets_formulario(
        self,
        interfaz,
        widgets,
    ):
        interfaz._ent_nombre = widgets["nombre"]
        interfaz._cb_nivel = widgets["nivel"]
        interfaz._ent_descripcion = widgets["descripcion"]
        interfaz._ent_objetivo = widgets["objetivo"]
        interfaz._ent_duracion = widgets["duracion"]

    def cargar_datos_validos(
        self,
        widgets,
    ):
        widgets["nombre"].valor = "Rutina cardio"
        widgets["nivel"].valor = "BASICO"
        widgets["descripcion"].valor = "Rutina de inicio"
        widgets["objetivo"].valor = "Mejorar resistencia"
        widgets["duracion"].valor = "8"

    def test_control_rutinas_devuelve_el_controlador(
        self,
        interfaz,
        control_rutinas,
    ):
        assert interfaz.control_rutinas is control_rutinas

    def test_modo_prueba_sin_tk_es_verdadero(
        self,
        interfaz,
    ):
        assert interfaz._es_modo_prueba_sin_tk() is True

    def test_mostrar_formulario_rutina_crea_widgets(
        self,
        interfaz,
    ):
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
        interfaz._tree = TreeviewFalso()
        control_rutinas.listar.return_value = [rutina]

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarRutinas()

        control_rutinas.listar.assert_called_once_with()

        assert len(interfaz._tree.insertados) == 1
        assert interfaz._tree.insertados[0][1]["values"] == (
            1,
            "Rutina inicial",
            "Mejorar resistencia",
            "BASICO",
            "8 sem",
        )

        mock_error.assert_not_called()

    def test_mostrar_rutinas_elimina_datos_anteriores(
        self,
        interfaz,
        control_rutinas,
        rutina,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.items = {
            "item-1": {
                "values": (
                    1,
                    "Rutina anterior",
                )
            }
        }

        control_rutinas.listar.return_value = [rutina]

        interfaz.mostrarRutinas()

        assert interfaz._tree.eliminaciones[0][0] == ("item-1",)

    def test_mostrar_rutinas_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
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

    def test_leer_datos_formulario_devuelve_datos_limpios(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "  Rutina cardio  "
        widgets_formulario["descripcion"].valor = (
            "  Mejorar resistencia  "
        )
        widgets_formulario["objetivo"].valor = (
            "  Condicion fisica  "
        )
        widgets_formulario["nivel"].valor = "  INTERMEDIO  "
        widgets_formulario["duracion"].valor = " 12 "

        datos = interfaz._leer_datos_formulario()

        assert datos == {
            "nombre": "Rutina cardio",
            "descripcion": "Mejorar resistencia",
            "objetivo": "Condicion fisica",
            "nivel": "INTERMEDIO",
            "duracion": 12,
        }

    def test_leer_datos_formulario_valida_nombre(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["nombre"].valor = ""

        with pytest.raises(
            ValueError,
            match="Ingrese el nombre de la rutina.",
        ):
            interfaz._leer_datos_formulario()

    def test_leer_datos_formulario_valida_descripcion(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["descripcion"].valor = ""

        with pytest.raises(
            ValueError,
            match="Ingrese la descripci",
        ):
            interfaz._leer_datos_formulario()

    def test_leer_datos_formulario_valida_objetivo(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["objetivo"].valor = ""

        with pytest.raises(
            ValueError,
            match="Ingrese el objetivo.",
        ):
            interfaz._leer_datos_formulario()

    def test_leer_datos_formulario_valida_nivel(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["nivel"].valor = ""

        with pytest.raises(
            ValueError,
            match="Seleccione un nivel.",
        ):
            interfaz._leer_datos_formulario()

    def test_leer_datos_formulario_valida_duracion_vacia(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["duracion"].valor = ""

        with pytest.raises(
            ValueError,
            match="Ingrese la duraci",
        ):
            interfaz._leer_datos_formulario()

    def test_leer_datos_formulario_valida_duracion_texto(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["duracion"].valor = "texto"

        with pytest.raises(
            ValueError,
            match="La duraci",
        ):
            interfaz._leer_datos_formulario()

    def test_leer_datos_formulario_valida_duracion_cero(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)
        widgets_formulario["duracion"].valor = "0"

        with pytest.raises(
            ValueError,
            match="La duraci",
        ):
            interfaz._leer_datos_formulario()

    def test_crear_rutina_correctamente(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarRutinas",
        ) as mock_mostrar_rutinas:
            interfaz.crearRutina()

        control_rutinas.crear_rutina.assert_called_once_with(
            nombre="Rutina cardio",
            descripcion="Rutina de inicio",
            objetivo="Mejorar resistencia",
            nivel="BASICO",
            duracion_semanas=8,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina creada exitosamente."
        )

        mock_mostrar_rutinas.assert_called_once_with()

    def test_crear_rutina_maneja_error_validacion(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = ""

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.crearRutina()

        control_rutinas.crear_rutina.assert_not_called()

        mock_error.assert_called_once_with(
            "Ingrese el nombre de la rutina."
        )

    def test_crear_rutina_maneja_error_controlador(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)

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

    def test_obtener_id_rutina_tabla_sin_seleccion(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        assert interfaz._obtener_id_rutina_tabla() is None

    def test_obtener_id_rutina_tabla_valido(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    "15",
                    "Rutina cardio",
                )
            }
        }

        assert interfaz._obtener_id_rutina_tabla() == 15

    def test_obtener_id_rutina_tabla_invalido(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    "no-es-numero",
                    "Rutina cardio",
                )
            }
        }

        assert interfaz._obtener_id_rutina_tabla() is None

    def test_editar_rutina_sin_seleccion(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarRutina()

        mock_error.assert_called_once_with(
            "Seleccione una rutina para editar."
        )

    def test_editar_rutina_con_id_muestra_mensaje(
        self,
        interfaz,
    ):
        interfaz._id_rutina_editando = 5

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
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarRutina()

        mock_error.assert_called_once_with(
            "Seleccione una rutina para eliminar."
        )

    def test_eliminar_rutina_cancelada(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
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
        ):
            interfaz.eliminarRutina()

        control_rutinas.eliminar_rutina.assert_not_called()

    def test_eliminar_rutina_correctamente(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
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

    def test_asignar_rutina_sin_seleccion(
        self,
        interfaz,
    ):
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
        control_rutinas,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        with patch(
            "src.interfaz.interfaz_gestion_rutinas"
            ".simpledialog.askinteger",
            return_value=None,
        ):
            interfaz.asignarRutina()

        control_rutinas.asignar_rutina.assert_not_called()

    def test_asignar_rutina_correctamente(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        with patch(
            "src.interfaz.interfaz_gestion_rutinas"
            ".simpledialog.askinteger",
            return_value=10,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.asignarRutina()

        control_rutinas.asignar_rutina.assert_called_once_with(
            id_cliente=10,
            id_rutina=5,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina 5 asignada al cliente 10."
        )

    def test_al_seleccionar_rutina_actualiza_ids(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    7,
                    "Rutina cardio",
                )
            }
        }

        interfaz._al_seleccionar_rutina()

        assert interfaz._id_rutina_editando == 7
        assert interfaz._id_rutina_vista_previa == 7

    def test_cancelar_edicion_rutina_limpia_estado(
        self,
        interfaz,
        widgets_formulario,
    ):
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]

        interfaz._lbl_modo = LabelFalso()
        interfaz._cb_rutina_ejercicios = ComboboxFalso()
        interfaz._cb_ejercicio_rutina = ComboboxFalso()
        interfaz._frame_ejercicios_rutina = FrameFalso()
        interfaz._tree_ejercicios_rutina = TreeviewFalso()

        interfaz._id_rutina_editando = 5
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = 8

        with patch.object(
            interfaz,
            "mostrarRutinas",
        ) as mock_mostrar:
            interfaz._cancelar_edicion_rutina()

        assert interfaz._id_rutina_editando is None
        assert interfaz._id_rutina_vista_previa is None
        assert interfaz._id_ejercicio_seleccionado is None

        assert interfaz._frame_ejercicios_rutina.pack_ocultado is True

        mock_mostrar.assert_called_once_with()

    def test_cargar_datos_ejercicios(
        self,
        interfaz,
        control_rutinas,
        rutina,
    ):
        ejercicio = SimpleNamespace(
            id_ejercicio=6,
            nombre="Caminata",
        )

        control_rutinas.listar.return_value = [rutina]
        interfaz._control_ejercicios.listar.return_value = [
            ejercicio
        ]

        interfaz._cb_rutina_ejercicios = ComboboxFalso()
        interfaz._cb_ejercicio_rutina = ComboboxFalso()

        interfaz._cargar_datos_ejercicios()

        assert interfaz._cb_rutina_ejercicios["values"] == [
            "1 - Rutina inicial"
        ]

        assert interfaz._cb_ejercicio_rutina["values"] == [
            "6 - Caminata"
        ]

    def test_cargar_ejercicios_asociados(
        self,
        interfaz,
    ):
        interfaz._cb_rutina_ejercicios = ComboboxFalso()
        interfaz._cb_rutina_ejercicios.valor = (
            "5 - Rutina cardio"
        )

        with patch.object(
            interfaz,
            "_mostrar_ejercicios_asociados",
        ) as mock_mostrar:
            interfaz._cargar_ejercicios_asociados()

        assert interfaz._id_rutina_vista_previa == 5

        mock_mostrar.assert_called_once_with(5)

    def test_mostrar_ejercicios_asociados(
        self,
        interfaz,
        control_rutinas,
    ):
        ejercicio_1 = SimpleNamespace(
            id_ejercicio=1,
            nombre="Caminata",
        )

        ejercicio_2 = SimpleNamespace(
            id_ejercicio=2,
            nombre="Bicicleta",
        )

        interfaz._tree_ejercicios_rutina = TreeviewFalso()
        interfaz._tree_ejercicios_rutina.items = {
            "fila-anterior": {
                "values": (
                    99,
                    "Anterior",
                    1,
                )
            }
        }

        control_rutinas.listar_ejercicios_de_rutina.return_value = [
            ejercicio_1,
            ejercicio_2,
        ]

        interfaz._mostrar_ejercicios_asociados(5)

        assert len(
            interfaz._tree_ejercicios_rutina.eliminaciones
        ) == 1

        assert len(
            interfaz._tree_ejercicios_rutina.insertados
        ) == 2

    def test_seleccionar_ejercicio_por_clic(
        self,
        interfaz,
    ):
        interfaz._tree_ejercicios_rutina = TreeviewFalso()
        interfaz._tree_ejercicios_rutina.fila_identificada = (
            "fila-1"
        )

        interfaz._tree_ejercicios_rutina.items = {
            "fila-1": {
                "values": (
                    "8",
                    "Caminata",
                    1,
                )
            }
        }

        evento = SimpleNamespace(y=10)

        interfaz._seleccionar_ejercicio_por_clic(evento)

        assert interfaz._id_ejercicio_seleccionado == 8

    def test_agregar_ejercicio_a_rutina(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._id_rutina_vista_previa = 5
        interfaz._cb_ejercicio_rutina = ComboboxFalso()
        interfaz._cb_ejercicio_rutina.valor = "9 - Bicicleta"

        control_rutinas.listar_ejercicios_de_rutina.return_value = [
            SimpleNamespace(
                id_ejercicio=1,
                nombre="Caminata",
            )
        ]

        interfaz._obtener_id_administrador = MagicMock(
            return_value=10
        )

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "_mostrar_ejercicios_asociados",
        ) as mock_mostrar:
            interfaz._agregar_ejercicio_a_rutina()

        (
            control_rutinas
            .agregar_ejercicio_a_rutina
            .assert_called_once_with(
                id_rutina=5,
                id_ejercicio=9,
                orden=2,
                usuario_accion=10,
            )
        )

        mock_mensaje.assert_called_once_with(
            "Ejercicio agregado correctamente."
        )

        mock_mostrar.assert_called_once_with(5)

    def test_quitar_ejercicio_de_rutina(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = 9

        interfaz._obtener_id_administrador = MagicMock(
            return_value=10
        )

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "_mostrar_ejercicios_asociados",
        ) as mock_mostrar:
            interfaz._quitar_ejercicio_de_rutina()

        (
            control_rutinas
            .eliminar_ejercicio_de_rutina
            .assert_called_once_with(
                id_rutina=5,
                id_ejercicio=9,
                usuario_accion=10,
            )
        )

        assert interfaz._id_ejercicio_seleccionado is None

        mock_mensaje.assert_called_once_with(
            "Ejercicio retirado correctamente."
        )

        mock_mostrar.assert_called_once_with(5)

    def test_limpiar_vista_previa(
        self,
        interfaz,
    ):
        interfaz._id_ejercicio_seleccionado = 8

        interfaz._tree_ejercicios_rutina = TreeviewFalso()
        interfaz._tree_ejercicios_rutina.items = {
            "fila-1": {
                "values": (
                    1,
                    "Caminata",
                    1,
                )
            },
            "fila-2": {
                "values": (
                    2,
                    "Bicicleta",
                    2,
                )
            },
        }

        interfaz._limpiar_vista_previa()

        assert interfaz._id_ejercicio_seleccionado is None

        assert len(
            interfaz._tree_ejercicios_rutina.eliminaciones
        ) == 2

    def test_obtener_id_administrador_desde_usuario_actual(
        self,
        interfaz,
    ):
        interfaz._control_autenticacion = SimpleNamespace(
            usuario_actual=SimpleNamespace(
                id_usuario="25"
            )
        )

        assert interfaz._obtener_id_administrador() == 25

    def test_constructor_inicializa_atributos_y_carga_datos(
        self,
        control_rutinas,
    ):
        master = MagicMock()
        control_autenticacion = MagicMock()
        control_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_rutinas."
            "InterfazBase.__init__",
            return_value=None,
        ) as mock_base_init, patch.object(
            InterfazGestionRutinas,
            "pack",
        ) as mock_pack, patch.object(
            InterfazGestionRutinas,
            "mostrarFormularioRutina",
        ) as mock_formulario, patch.object(
            InterfazGestionRutinas,
            "mostrarRutinas",
        ) as mock_rutinas, patch.object(
            InterfazGestionRutinas,
            "mostrarEjerciciosRutina",
        ) as mock_ejercicios, patch.object(
            InterfazGestionRutinas,
            "_cargar_datos_ejercicios",
        ) as mock_cargar_datos:

            interfaz = InterfazGestionRutinas(
                master=master,
                control_rutinas=control_rutinas,
                control_autenticacion=control_autenticacion,
                control_ejercicios=control_ejercicios,
            )

        mock_base_init.assert_called_once_with(
            master,
            controlador=control_rutinas,
            padding=10,
        )

        mock_pack.assert_called_once_with(
            fill="both",
            expand=True,
        )

        mock_formulario.assert_called_once_with()
        mock_rutinas.assert_called_once_with()
        mock_ejercicios.assert_called_once_with()
        mock_cargar_datos.assert_called_once_with()

        assert interfaz._control_rutinas is control_rutinas

        assert (
            interfaz._control_autenticacion
            is control_autenticacion
        )

        assert (
            interfaz._control_ejercicios
            is control_ejercicios
        )

        assert interfaz._rutinas_disponibles == []
        assert interfaz._ejercicios_disponibles == []

        assert interfaz._id_rutina_editando is None
        assert interfaz._id_rutina_vista_previa is None
        assert interfaz._id_ejercicio_seleccionado is None

    def test_constructor_sin_control_ejercicios_no_carga_datos(
        self,
        control_rutinas,
    ):
        master = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_rutinas."
            "InterfazBase.__init__",
            return_value=None,
        ), patch.object(
            InterfazGestionRutinas,
            "pack",
        ), patch.object(
            InterfazGestionRutinas,
            "mostrarFormularioRutina",
        ), patch.object(
            InterfazGestionRutinas,
            "mostrarRutinas",
        ), patch.object(
            InterfazGestionRutinas,
            "mostrarEjerciciosRutina",
        ), patch.object(
            InterfazGestionRutinas,
            "_cargar_datos_ejercicios",
        ) as mock_cargar_datos:

            interfaz = InterfazGestionRutinas(
                master=master,
                control_rutinas=control_rutinas,
                control_autenticacion=None,
                control_ejercicios=None,
            )

        mock_cargar_datos.assert_not_called()

        assert interfaz._control_rutinas is control_rutinas
        assert interfaz._control_autenticacion is None
        assert interfaz._control_ejercicios is None

        assert interfaz._rutinas_disponibles == []
        assert interfaz._ejercicios_disponibles == []

        assert interfaz._id_rutina_editando is None
        assert interfaz._id_rutina_vista_previa is None
        assert interfaz._id_ejercicio_seleccionado is None

    def test_mostrar_rutinas_en_modo_produccion(
        self,
        interfaz,
        control_rutinas,
        rutina,
    ):
        interfaz.tk = MagicMock()

        control_rutinas.listar.return_value = [rutina]

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarRutinas()

        assert isinstance(
            interfaz._tree_frame,
            FrameFalso,
        )

        assert isinstance(
            interfaz._tree,
            TreeviewFalso,
        )

        control_rutinas.listar.assert_called_once_with()

        assert interfaz._rutinas_disponibles == [rutina]

        assert len(interfaz._tree.insertados) == 1

        assert interfaz._tree.insertados[0][1]["values"] == (
            1,
            "Rutina inicial",
            "Rutina de inicio",
            "Mejorar resistencia",
            "BASICO",
            "8 sem",
        )

        mock_error.assert_not_called()

    def test_mostrar_rutinas_en_modo_produccion_destruye_frame_anterior(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz.tk = MagicMock()

        frame_anterior = FrameFalso()
        interfaz._tree_frame = frame_anterior

        control_rutinas.listar.return_value = []

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarRutinas()

        mock_error.assert_not_called()

        assert frame_anterior.destruido is True

        assert isinstance(
            interfaz._tree_frame,
            FrameFalso,
        )

        assert interfaz._tree_frame is not frame_anterior

    def test_mostrar_rutinas_en_modo_produccion_maneja_error(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz.tk = MagicMock()

        control_rutinas.listar.side_effect = RuntimeError(
            "Error de consulta"
        )

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarRutinas()

        mock_error.assert_called_once_with(
            "Error al cargar rutinas: Error de consulta"
        )

    def test_obtener_valores_tree_con_valores_directos(self):
        tree = MagicMock()
        tree.item.return_value = (
            1,
            "Rutina cardio",
        )

        valores = InterfazGestionRutinas._obtener_valores_tree(
            tree,
            "fila-1",
        )

        assert valores == (
            1,
            "Rutina cardio",
        )

    def test_obtener_valores_tree_con_none_devuelve_tupla_vacia(
        self,
    ):
        tree = MagicMock()
        tree.item.return_value = None

        valores = InterfazGestionRutinas._obtener_valores_tree(
            tree,
            "fila-1",
        )

        assert valores == ()

    def test_mostrar_rutinas_en_prueba_sin_tree_no_hace_nada(
        self,
        interfaz,
        control_rutinas,
    ):
        if hasattr(interfaz, "_tree"):
            del interfaz._tree

        interfaz._mostrar_rutinas_en_prueba()

        control_rutinas.listar.assert_not_called()

    def test_mostrar_ejercicios_rutina_crea_widgets(
        self,
        interfaz,
    ):
        with patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Combobox",
            side_effect=ComboboxFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Button",
            side_effect=ButtonFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Treeview",
            side_effect=TreeviewFalso,
        ):
            interfaz.mostrarEjerciciosRutina()

        assert isinstance(
            interfaz._frame_ejercicios_rutina,
            LabelFrameFalso,
        )

        assert isinstance(
            interfaz._cb_rutina_ejercicios,
            ComboboxFalso,
        )

        assert isinstance(
            interfaz._cb_ejercicio_rutina,
            ComboboxFalso,
        )

        assert isinstance(
            interfaz._tree_ejercicios_rutina,
            TreeviewFalso,
        )

    def test_crear_rutina_en_produccion(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        interfaz._limpiar_formulario = MagicMock()
        interfaz.mostrarRutinas = MagicMock()
        interfaz._cargar_datos_ejercicios = MagicMock()
        interfaz._limpiar_vista_previa = MagicMock()

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.crearRutina()

        control_rutinas.crear_rutina.assert_called_once_with(
            nombre="Rutina cardio",
            descripcion="Rutina de inicio",
            nivel_dificultad="BASICO",
            duracion_estimada=8,
            creado_por=20,
            objetivo="Mejorar resistencia",
        )

        mock_mensaje.assert_called_once_with(
            "Rutina creada exitosamente."
        )

        interfaz._limpiar_formulario.assert_called_once_with()
        interfaz.mostrarRutinas.assert_called_once_with()

        interfaz._cargar_datos_ejercicios.assert_called_once_with()

        interfaz._limpiar_vista_previa.assert_called_once_with()

    def test_editar_rutina_en_produccion_correctamente(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
        rutina,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)

        interfaz._id_rutina_editando = 1

        control_rutinas.buscar_por_id.return_value = rutina

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        interfaz.mostrarRutinas = MagicMock()
        interfaz._cargar_datos_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.Rutina",
        ) as mock_rutina, patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.editarRutina()

        mock_rutina.assert_called_once_with(
            id_rutina=1,
            nombre="Rutina cardio",
            descripcion="Rutina de inicio",
            objetivo="Mejorar resistencia",
            nivel="BASICO",
            duracion_semanas=8,
            creado_por=10,
            fecha_creacion="2026-01-01",
            ejercicios=[],
        )

        control_rutinas.actualizar_rutina.assert_called_once_with(
            mock_rutina.return_value,
            20,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina actualizada correctamente."
        )

        interfaz.mostrarRutinas.assert_called_once_with()

        interfaz._cargar_datos_ejercicios.assert_called_once_with()

    def test_editar_rutina_en_produccion_sin_valores(
        self,
        interfaz,
    ):
        interfaz.tk = MagicMock()

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": ()
            }
        }

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarRutina()

        mock_error.assert_called_once_with(
            "Seleccione una rutina para editar."
        )

    def test_editar_rutina_muestra_error_si_no_existe(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)

        interfaz._id_rutina_editando = 5

        control_rutinas.buscar_por_id.return_value = None

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarRutina()

        mock_error.assert_called_once_with(
            "No se encontró la rutina."
        )

    def test_editar_rutina_muestra_error_inesperado(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
        rutina,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(widgets_formulario)

        interfaz._id_rutina_editando = 5

        control_rutinas.buscar_por_id.return_value = rutina

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        control_rutinas.actualizar_rutina.side_effect = RuntimeError(
            "Fallo al actualizar"
        )

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.Rutina",
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarRutina()

        mock_error.assert_called_once_with(
            "Error al editar rutina: Fallo al actualizar"
        )

    def test_eliminar_rutina_en_produccion(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        interfaz._cargar_datos_ejercicios = MagicMock()
        interfaz._limpiar_vista_previa = MagicMock()
        interfaz.mostrarRutinas = MagicMock()

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.eliminarRutina()

        control_rutinas.eliminar_rutina.assert_called_once_with(
            5,
            20,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina eliminada correctamente."
        )

        interfaz._cargar_datos_ejercicios.assert_called_once_with()

        interfaz._limpiar_vista_previa.assert_called_once_with()

    def test_asignar_rutina_en_produccion(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz.tk = MagicMock()

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        with patch(
            "src.interfaz.interfaz_gestion_rutinas"
            ".simpledialog.askinteger",
            return_value=10,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas"
            ".simpledialog.askstring",
            return_value="Cliente recomendado",
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.asignarRutina()

        control_rutinas.asignar_rutina.assert_called_once_with(
            cliente=10,
            rutina=5,
            asignado_por=20,
            observaciones="Cliente recomendado",
        )

        mock_mensaje.assert_called_once_with(
            "Rutina 5 asignada al cliente 10."
        )

    def test_asignar_rutina_produccion_muestra_error(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz.tk = MagicMock()

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        control_rutinas.asignar_rutina.side_effect = RuntimeError(
            "Fallo al asignar"
        )

        with patch(
            "src.interfaz.interfaz_gestion_rutinas"
            ".simpledialog.askinteger",
            return_value=10,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas"
            ".simpledialog.askstring",
            return_value=None,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.asignarRutina()

        mock_error.assert_called_once_with(
            "Error al asignar rutina: Fallo al asignar"
        )

    def test_al_seleccionar_rutina_en_produccion(
        self,
        interfaz,
        control_rutinas,
        rutina,
        widgets_formulario,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._lbl_modo = LabelFalso()
        interfaz._frame_ejercicios_rutina = FrameFalso()

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    1,
                    "Rutina inicial",
                )
            }
        }

        control_rutinas.buscar_por_id.return_value = rutina

        interfaz._mostrar_ejercicios_asociados = MagicMock()

        interfaz._al_seleccionar_rutina()

        assert interfaz._id_rutina_editando == 1

        assert interfaz._id_rutina_vista_previa == 1

        assert widgets_formulario["nombre"].valor == (
            "Rutina inicial"
        )

        assert widgets_formulario["descripcion"].valor == (
            "Rutina de inicio"
        )

        assert widgets_formulario["objetivo"].valor == (
            "Mejorar resistencia"
        )

        assert widgets_formulario["nivel"].valor == "BASICO"

        assert widgets_formulario["duracion"].valor == "8"

        assert interfaz._lbl_modo.configuracion["text"] == (
            "Modo: editando rutina #1"
        )

        interfaz._mostrar_ejercicios_asociados.assert_called_once_with(
            1
        )

    def test_al_seleccionar_rutina_muestra_error(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    1,
                    "Rutina inicial",
                )
            }
        }

        control_rutinas.buscar_por_id.return_value = None

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._al_seleccionar_rutina()

        mock_error.assert_called_once_with(
            "No se pudo cargar la rutina 1: "
            "No se encontró la rutina."
        )

    def test_editar_con_doble_click_llama_editar_rutina(
        self,
        interfaz,
    ):
        interfaz.editarRutina = MagicMock()

        interfaz._editar_con_doble_click()

        interfaz.editarRutina.assert_called_once_with()

    def test_cargar_datos_ejercicios_sin_control_no_hace_nada(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._control_ejercicios = None

        interfaz._cargar_datos_ejercicios()

        control_rutinas.listar.assert_not_called()

    def test_cargar_datos_ejercicios_muestra_error(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._cb_rutina_ejercicios = ComboboxFalso()
        interfaz._cb_ejercicio_rutina = ComboboxFalso()

        control_rutinas.listar.side_effect = RuntimeError(
            "Fallo de carga"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._cargar_datos_ejercicios()

        mock_error.assert_called_once_with(
            "Error al cargar datos: Fallo de carga"
        )

    def test_cargar_rutinas_en_combo_sin_combo(
        self,
        interfaz,
    ):
        if hasattr(
            interfaz,
            "_cb_rutina_ejercicios",
        ):
            del interfaz._cb_rutina_ejercicios

        interfaz._rutinas_disponibles = [
            SimpleNamespace(
                id_rutina=1,
                nombre="Rutina cardio",
            )
        ]

        interfaz._cargar_rutinas_en_combo()

    def test_cargar_ejercicios_asociados_sin_valor(
        self,
        interfaz,
    ):
        interfaz._cb_rutina_ejercicios = ComboboxFalso()

        interfaz._mostrar_ejercicios_asociados = MagicMock()

        interfaz._cargar_ejercicios_asociados()

        interfaz._mostrar_ejercicios_asociados.assert_not_called()

    def test_cargar_ejercicios_asociados_con_valor_invalido(
        self,
        interfaz,
    ):
        interfaz._cb_rutina_ejercicios = ComboboxFalso()
        interfaz._cb_rutina_ejercicios.valor = "sin identificador"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._cargar_ejercicios_asociados()

        mock_error.assert_called_once()

    def test_mostrar_ejercicios_asociados_sin_tree(
        self,
        interfaz,
        control_rutinas,
    ):
        if hasattr(
            interfaz,
            "_tree_ejercicios_rutina",
        ):
            del interfaz._tree_ejercicios_rutina

        interfaz._mostrar_ejercicios_asociados(5)

        control_rutinas.listar_ejercicios_de_rutina.assert_not_called()

    def test_mostrar_ejercicios_asociados_muestra_error(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._tree_ejercicios_rutina = TreeviewFalso()

        control_rutinas.listar_ejercicios_de_rutina.side_effect = (
            RuntimeError("Fallo de consulta")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._mostrar_ejercicios_asociados(5)

        mock_error.assert_called_once_with(
            "No se pudieron cargar los ejercicios de la rutina "
            "5: Fallo de consulta"
        )

    def test_seleccionar_ejercicio_sin_tree_no_hace_nada(
        self,
        interfaz,
    ):
        if hasattr(
            interfaz,
            "_tree_ejercicios_rutina",
        ):
            del interfaz._tree_ejercicios_rutina

        interfaz._id_ejercicio_seleccionado = 8

        interfaz._seleccionar_ejercicio_por_clic(
            SimpleNamespace(y=10)
        )

        assert interfaz._id_ejercicio_seleccionado == 8

    def test_seleccionar_ejercicio_sin_fila_limpia_id(
        self,
        interfaz,
    ):
        interfaz._tree_ejercicios_rutina = TreeviewFalso()

        interfaz._id_ejercicio_seleccionado = 8

        interfaz._seleccionar_ejercicio_por_clic(
            SimpleNamespace(y=10)
        )

        assert interfaz._id_ejercicio_seleccionado is None

    def test_seleccionar_ejercicio_invalido_limpia_id(
        self,
        interfaz,
    ):
        interfaz._tree_ejercicios_rutina = TreeviewFalso()

        interfaz._tree_ejercicios_rutina.fila_identificada = (
            "fila-1"
        )

        interfaz._tree_ejercicios_rutina.items = {
            "fila-1": {
                "values": (
                    "no-es-numero",
                    "Caminata",
                    1,
                )
            }
        }

        interfaz._seleccionar_ejercicio_por_clic(
            SimpleNamespace(y=10)
        )

        assert interfaz._id_ejercicio_seleccionado is None

    def test_agregar_ejercicio_sin_rutina_muestra_error(
        self,
        interfaz,
    ):
        interfaz._id_rutina_vista_previa = None

        interfaz._cb_ejercicio_rutina = ComboboxFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._agregar_ejercicio_a_rutina()

        mock_error.assert_called_once_with(
            "Error al agregar ejercicio: Seleccione una rutina."
        )

    def test_agregar_ejercicio_sin_ejercicio_muestra_error(
        self,
        interfaz,
    ):
        interfaz._id_rutina_vista_previa = 5

        interfaz._cb_ejercicio_rutina = ComboboxFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._agregar_ejercicio_a_rutina()

        mock_error.assert_called_once_with(
            "Error al agregar ejercicio: Seleccione un ejercicio."
        )

    def test_agregar_ejercicio_muestra_error_controlador(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._id_rutina_vista_previa = 5

        interfaz._cb_ejercicio_rutina = ComboboxFalso()
        interfaz._cb_ejercicio_rutina.valor = "8 - Caminata"

        control_rutinas.listar_ejercicios_de_rutina.side_effect = (
            RuntimeError("Fallo al listar")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._agregar_ejercicio_a_rutina()

        mock_error.assert_called_once_with(
            "Error al agregar ejercicio: Fallo al listar"
        )

    def test_quitar_ejercicio_sin_rutina_muestra_error(
        self,
        interfaz,
    ):
        interfaz._id_rutina_vista_previa = None
        interfaz._id_ejercicio_seleccionado = 8

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._quitar_ejercicio_de_rutina()

        mock_error.assert_called_once_with(
            "Error al quitar ejercicio: "
            "Seleccione primero una rutina."
        )

    def test_quitar_ejercicio_sin_ejercicio_muestra_error(
        self,
        interfaz,
    ):
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = None

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._quitar_ejercicio_de_rutina()

        mock_error.assert_called_once_with(
            "Error al quitar ejercicio: "
            "Haga clic sobre el ejercicio que desea quitar."
        )

    def test_quitar_ejercicio_cancelado_no_elimina(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = 8

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=False,
        ):
            interfaz._quitar_ejercicio_de_rutina()

        (
            control_rutinas
            .eliminar_ejercicio_de_rutina
            .assert_not_called()
        )

    def test_quitar_ejercicio_muestra_error_controlador(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = 8

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        control_rutinas.eliminar_ejercicio_de_rutina.side_effect = (
            RuntimeError("Fallo al quitar")
        )

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._quitar_ejercicio_de_rutina()

        mock_error.assert_called_once_with(
            "Error al quitar ejercicio: Fallo al quitar"
        )

    def test_limpiar_vista_previa_sin_tree(
        self,
        interfaz,
    ):
        if hasattr(
            interfaz,
            "_tree_ejercicios_rutina",
        ):
            del interfaz._tree_ejercicios_rutina

        interfaz._id_ejercicio_seleccionado = 8

        interfaz._limpiar_vista_previa()

        assert interfaz._id_ejercicio_seleccionado is None

    def test_obtener_id_administrador_desde_ventana(
        self,
        interfaz,
    ):
        interfaz._control_autenticacion = None

        interfaz.winfo_toplevel = MagicMock(
            return_value=SimpleNamespace(
                _administrador_actual=SimpleNamespace(
                    id_usuario="30"
                )
            )
        )

        assert interfaz._obtener_id_administrador() == 30

    def test_obtener_id_administrador_muestra_error_si_no_existe(
        self,
        interfaz,
    ):
        interfaz._control_autenticacion = None

        interfaz.winfo_toplevel = MagicMock(
            return_value=SimpleNamespace(
                _administrador_actual=None
            )
        )

        with pytest.raises(
            ValueError,
            match="No se pudo obtener el ID",
        ):
            interfaz._obtener_id_administrador()

    def test_mostrar_rutinas_produccion_carga_combo_ejercicios(
        self,
        interfaz,
        control_rutinas,
        rutina,
    ):
        interfaz.tk = MagicMock()

        interfaz._cb_rutina_ejercicios = ComboboxFalso()

        control_rutinas.listar.return_value = [rutina]

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_rutinas.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarRutinas()

        assert interfaz._cb_rutina_ejercicios["values"] == [
            "1 - Rutina inicial"
        ]

        mock_error.assert_not_called()

    def test_al_seleccionar_rutina_sin_seleccion_no_hace_nada(
        self,
        interfaz,
    ):
        interfaz.tk = MagicMock()
        interfaz._tree = TreeviewFalso()

        interfaz._id_rutina_editando = None
        interfaz._id_rutina_vista_previa = None

        interfaz._al_seleccionar_rutina()

        assert interfaz._id_rutina_editando is None
        assert interfaz._id_rutina_vista_previa is None

    def test_al_seleccionar_rutina_sin_frame_ejercicios(
        self,
        interfaz,
        control_rutinas,
        rutina,
        widgets_formulario,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        interfaz._lbl_modo = LabelFalso()

        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["fila-1"]
        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    1,
                    "Rutina inicial",
                )
            }
        }

        if hasattr(
            interfaz,
            "_frame_ejercicios_rutina",
        ):
            del interfaz._frame_ejercicios_rutina

        control_rutinas.buscar_por_id.return_value = rutina

        interfaz._mostrar_ejercicios_asociados = MagicMock()

        interfaz._al_seleccionar_rutina()

        assert interfaz._id_rutina_editando == 1
        assert interfaz._id_rutina_vista_previa == 1

        interfaz._mostrar_ejercicios_asociados.assert_called_once_with(
            1
        )

    def test_cancelar_edicion_sin_widgets_opcionales(
        self,
        interfaz,
    ):
        interfaz._limpiar_formulario = MagicMock()
        interfaz._limpiar_vista_previa = MagicMock()
        interfaz.mostrarRutinas = MagicMock()

        if hasattr(interfaz, "_tree"):
            del interfaz._tree

        if hasattr(
            interfaz,
            "_cb_rutina_ejercicios",
        ):
            del interfaz._cb_rutina_ejercicios

        if hasattr(
            interfaz,
            "_cb_ejercicio_rutina",
        ):
            del interfaz._cb_ejercicio_rutina

        if hasattr(
            interfaz,
            "_frame_ejercicios_rutina",
        ):
            del interfaz._frame_ejercicios_rutina

        interfaz._id_rutina_editando = 5
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = 8

        interfaz._cancelar_edicion_rutina()

        assert interfaz._id_rutina_editando is None
        assert interfaz._id_rutina_vista_previa is None
        assert interfaz._id_ejercicio_seleccionado is None

        interfaz._limpiar_formulario.assert_called_once_with()
        interfaz._limpiar_vista_previa.assert_called_once_with()
        interfaz.mostrarRutinas.assert_called_once_with()

    def test_limpiar_formulario_sin_widgets_no_falla(
        self,
        interfaz,
    ):
        for atributo in (
            "_ent_nombre",
            "_ent_descripcion",
            "_ent_objetivo",
            "_ent_duracion",
            "_cb_nivel",
            "_lbl_modo",
        ):
            if hasattr(interfaz, atributo):
                delattr(interfaz, atributo)

        interfaz._limpiar_formulario()

    def test_cargar_rutinas_en_combo_lista_vacia(
        self,
        interfaz,
    ):
        interfaz._cb_rutina_ejercicios = ComboboxFalso()
        interfaz._rutinas_disponibles = []

        interfaz._cargar_rutinas_en_combo()

        assert interfaz._cb_rutina_ejercicios["values"] == []

    def test_mostrar_ejercicios_asociados_lista_vacia(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._tree_ejercicios_rutina = TreeviewFalso()

        interfaz._tree_ejercicios_rutina.items = {
            "fila-anterior": {
                "values": (
                    1,
                    "Caminata",
                    1,
                )
            }
        }

        control_rutinas.listar_ejercicios_de_rutina.return_value = []

        interfaz._mostrar_ejercicios_asociados(5)

        assert len(
            interfaz._tree_ejercicios_rutina.eliminaciones
        ) == 1

        assert interfaz._tree_ejercicios_rutina.insertados == []

    def test_cargar_ejercicios_asociados_error_de_controlador(
        self,
        interfaz,
    ):
        interfaz._cb_rutina_ejercicios = ComboboxFalso()

        interfaz._cb_rutina_ejercicios.valor = (
            "5 - Rutina cardio"
        )

        interfaz._mostrar_ejercicios_asociados = MagicMock(
            side_effect=RuntimeError("Fallo de carga")
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._cargar_ejercicios_asociados()

        mock_error.assert_called_once_with("Fallo de carga")

    def test_agregar_ejercicio_formato_invalido_muestra_error(
        self,
        interfaz,
    ):
        interfaz._id_rutina_vista_previa = 5

        interfaz._cb_ejercicio_rutina = ComboboxFalso()

        interfaz._cb_ejercicio_rutina.valor = (
            "ejercicio invalido"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz._agregar_ejercicio_a_rutina()

        mock_error.assert_called_once()

    def test_quitar_ejercicio_limpia_seleccion_si_se_confirma(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz._id_rutina_vista_previa = 5
        interfaz._id_ejercicio_seleccionado = 8

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        interfaz._mostrar_ejercicios_asociados = MagicMock()

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ):
            interfaz._quitar_ejercicio_de_rutina()

        control_rutinas.eliminar_ejercicio_de_rutina.assert_called_once_with(
            id_rutina=5,
            id_ejercicio=8,
            usuario_accion=20,
        )

        assert interfaz._id_ejercicio_seleccionado is None

    def test_editar_rutina_con_seleccion_en_modo_prueba(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.editarRutina()

        mock_mensaje.assert_called_once_with(
            "Funcionalidad de edicion pendiente de implementar."
        )

    def test_editar_rutina_produccion_obtiene_id_desde_tree(
        self,
        interfaz,
        control_rutinas,
        widgets_formulario,
        rutina,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        self.cargar_datos_validos(
            widgets_formulario,
        )

        interfaz._tree = TreeviewFalso()

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    "5",
                    "Rutina inicial",
                )
            }
        }

        control_rutinas.buscar_por_id.return_value = rutina

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        interfaz.mostrarRutinas = MagicMock()

        interfaz._cargar_datos_ejercicios = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_rutinas.Rutina",
        ) as mock_rutina, patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:

            interfaz.editarRutina()

        assert interfaz._id_rutina_editando == 5

        mock_rutina.assert_called_once()

        control_rutinas.actualizar_rutina.assert_called_once_with(
            mock_rutina.return_value,
            20,
        )

        mock_mensaje.assert_called_once_with(
            "Rutina actualizada correctamente."
        )

        interfaz.mostrarRutinas.assert_called_once_with()

        interfaz._cargar_datos_ejercicios.assert_called_once_with()

    def test_eliminar_rutina_produccion_muestra_error(
        self,
        interfaz,
        control_rutinas,
    ):
        interfaz.tk = MagicMock()

        interfaz._tree = TreeviewFalso()

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        interfaz._tree.items = {
            "fila-1": {
                "values": (
                    5,
                    "Rutina inicial",
                )
            }
        }

        interfaz._obtener_id_administrador = MagicMock(
            return_value=20
        )

        control_rutinas.eliminar_rutina.side_effect = RuntimeError(
            "Fallo al eliminar"
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
            "Error al eliminar: Fallo al eliminar"
        )

    def test_obtener_id_rutina_tabla_sin_tree_devuelve_none(
        self,
    ):
        interfaz = object.__new__(
            InterfazGestionRutinas
        )

        resultado = interfaz._obtener_id_rutina_tabla()

        assert resultado is None

    def test_obtener_id_rutina_tabla_sin_valores_devuelve_none(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        interfaz._tree.items = {
            "fila-1": {
                "values": ()
            }
        }

        resultado = interfaz._obtener_id_rutina_tabla()

        assert resultado is None