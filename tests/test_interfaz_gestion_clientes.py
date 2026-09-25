from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_gestion_clientes import (
    InterfazGestionClientes,
)


class WidgetFalso:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.valor = ""
        self.items = {}
        self.insertados = []
        self.eliminaciones = []
        self.seleccion_actual = []
        self.configuracion = {}
        self.destruido = False

    def pack(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        pass

    def destroy(self):
        self.destruido = True

    def delete(self, *args, **kwargs):
        self.eliminaciones.append((args, kwargs))
        self.valor = ""

    def insert(self, *args, **kwargs):
        self.insertados.append((args, kwargs))

        if len(args) >= 2 and "values" not in kwargs:
            self.valor = args[1]

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor

    def item(self, item_id):
        return self.items.get(
            item_id,
            {"values": ()},
        )

    def get_children(self):
        return list(self.items.keys())

    def selection(self):
        return self.seleccion_actual

    def selection_remove(self, *args):
        self.seleccion_actual = []

    def heading(self, *args, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def tag_configure(self, *args, **kwargs):
        pass

    def rowconfigure(self, *args, **kwargs):
        pass

    def columnconfigure(self, *args, **kwargs):
        pass

    def yview(self, *args, **kwargs):
        pass

    def xview(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        self.configuracion.update(kwargs)

    def config(self, *args, **kwargs):
        self.configuracion.update(kwargs)

    def cget(self, clave):
        return self.configuracion.get(clave, "")

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


class ScrollbarFalso(WidgetFalso):
    def set(self, *args, **kwargs):
        pass


class TestInterfazGestionClientes:
    @pytest.fixture
    def control_clientes(self):
        controlador = MagicMock()
        controlador.listar.return_value = []
        return controlador

    @pytest.fixture
    def cliente(self):
        cliente = SimpleNamespace(
            id_usuario=1,
            correo_electronico="ana@example.com",
            edad=30,
            genero="MUJER",
            altura=1.70,
            peso=70.5,
            objetivo="Bajar de peso",
            peso_objetivo=65.0,
        )

        cliente.obtener_nombre_completo = MagicMock(
            return_value="Ana Perez"
        )

        cliente.obtener_estado_meta = MagicMock(
            return_value="EN PROGRESO"
        )

        cliente.obtener_diferencia_meta = MagicMock(
            return_value=5.5
        )

        return cliente

    @pytest.fixture
    def interfaz(self, control_clientes):
        instancia = object.__new__(
            InterfazGestionClientes
        )

        instancia._controlador = control_clientes
        instancia._control_clientes = control_clientes

        return instancia

    @pytest.fixture
    def widgets(self):
        return {
            "nombre": EntryFalso(),
            "apellido": EntryFalso(),
            "correo": EntryFalso(),
            "contrasenia": EntryFalso(),
            "edad": EntryFalso(),
            "peso": EntryFalso(),
            "altura": EntryFalso(),
            "objetivo": EntryFalso(),
            "peso_objetivo": EntryFalso(),
            "buscar": EntryFalso(),
            "genero": ComboboxFalso(),
            "meta": ComboboxFalso(),
            "rango": LabelFalso(),
        }

    def asignar_widgets(
        self,
        interfaz,
        widgets,
    ):
        interfaz._ent_nombre = widgets["nombre"]
        interfaz._ent_apellido = widgets["apellido"]
        interfaz._ent_correo = widgets["correo"]
        interfaz._ent_contrasenia = widgets["contrasenia"]
        interfaz._ent_edad = widgets["edad"]
        interfaz._ent_peso = widgets["peso"]
        interfaz._ent_altura = widgets["altura"]
        interfaz._ent_objetivo = widgets["objetivo"]
        interfaz._ent_peso_objetivo = widgets["peso_objetivo"]
        interfaz._ent_buscar = widgets["buscar"]
        interfaz._cb_genero = widgets["genero"]
        interfaz._cb_meta = widgets["meta"]
        interfaz._lbl_rango = widgets["rango"]

    def cargar_datos_validos(
        self,
        widgets,
    ):
        widgets["nombre"].valor = "Ana"
        widgets["apellido"].valor = "Perez"
        widgets["correo"].valor = "ana@example.com"
        widgets["contrasenia"].valor = "123456"
        widgets["edad"].valor = "30"
        widgets["peso"].valor = "70.5"
        widgets["altura"].valor = "1.70"
        widgets["objetivo"].valor = "Bajar de peso"
        widgets["peso_objetivo"].valor = "65"
        widgets["genero"].valor = "MUJER"
        widgets["meta"].valor = "Bajar de peso"

    def preparar_tree(
        self,
        interfaz,
        valores=(1, "Ana Perez"),
    ):
        interfaz._tree = TreeviewFalso()

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        interfaz._tree.items = {
            "fila-1": {
                "values": valores
            }
        }

    def test_constructor_inicializa_interfaz(
        self,
        control_clientes,
    ):
        master = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_clientes."
            "InterfazBase.__init__",
            return_value=None,
        ) as mock_base, patch.object(
            InterfazGestionClientes,
            "pack",
        ) as mock_pack, patch.object(
            InterfazGestionClientes,
            "mostrarFormularioCliente",
        ) as mock_formulario, patch.object(
            InterfazGestionClientes,
            "mostrarClientes",
        ) as mock_clientes:

            interfaz = InterfazGestionClientes(
                master,
                control_clientes,
            )

        mock_base.assert_called_once_with(
            master,
            controlador=control_clientes,
            padding=10,
        )

        mock_pack.assert_called_once_with(
            fill="both",
            expand=True,
        )

        mock_formulario.assert_called_once_with()
        mock_clientes.assert_called_once_with()

        assert interfaz.control_clientes is control_clientes

    def test_obtener_valores_tree_directos_y_vacios(self):
        tree = MagicMock()

        tree.item.return_value = (
            1,
            "Ana",
        )

        assert (
            InterfazGestionClientes._obtener_valores_tree(
                tree,
                "fila",
            )
            == (1, "Ana")
        )

        tree.item.return_value = None

        assert (
            InterfazGestionClientes._obtener_valores_tree(
                tree,
                "fila",
            )
            == ()
        )

    def test_formatear_numero(self):
        assert (
            InterfazGestionClientes._formatear_numero(
                70
            )
            == "70.00"
        )

        assert (
            InterfazGestionClientes._formatear_numero(
                "invalido"
            )
            == "invalido"
        )

    def test_mostrar_formulario_en_modo_prueba(
        self,
        interfaz,
    ):
        with patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Button",
            side_effect=ButtonFalso,
        ):
            interfaz.mostrarFormularioCliente()

        assert isinstance(
            interfaz._cb_genero,
            EntryFalso,
        )

        assert isinstance(
            interfaz._cb_meta,
            EntryFalso,
        )

        assert interfaz._ent_objetivo is interfaz._cb_meta

    def test_mostrar_formulario_en_produccion(
        self,
        interfaz,
    ):
        interfaz.tk = MagicMock()

        with patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.LabelFrame",
            side_effect=LabelFrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Label",
            side_effect=LabelFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Combobox",
            side_effect=ComboboxFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Button",
            side_effect=ButtonFalso,
        ):
            interfaz.mostrarFormularioCliente()

        assert isinstance(
            interfaz._cb_genero,
            ComboboxFalso,
        )

        assert isinstance(
            interfaz._cb_meta,
            ComboboxFalso,
        )

    def test_mostrar_clientes_en_prueba(
        self,
        interfaz,
        control_clientes,
        cliente,
    ):
        interfaz._tree = TreeviewFalso()

        control_clientes.listar.return_value = [
            cliente
        ]

        interfaz.mostrarClientes()

        assert len(interfaz._tree.insertados) == 1

    def test_mostrar_clientes_en_prueba_sin_tree(
        self,
        interfaz,
        control_clientes,
    ):
        interfaz._mostrar_clientes_en_prueba()

        control_clientes.listar.assert_not_called()

    def test_mostrar_clientes_produccion(
        self,
        interfaz,
        control_clientes,
        cliente,
    ):
        interfaz.tk = MagicMock()

        control_clientes.listar.return_value = [
            cliente
        ]

        with patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Scrollbar",
            side_effect=ScrollbarFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:

            interfaz.mostrarClientes()

        assert len(interfaz._tree.insertados) == 1

        mock_error.assert_not_called()

    def test_mostrar_clientes_produccion_con_meta_alcanzada(
        self,
        interfaz,
        control_clientes,
        cliente,
    ):
        interfaz.tk = MagicMock()

        cliente.obtener_estado_meta.return_value = (
            "META ALCANZADA"
        )

        control_clientes.listar.return_value = [
            cliente
        ]

        with patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Scrollbar",
            side_effect=ScrollbarFalso,
        ):
            interfaz.mostrarClientes()

        assert len(interfaz._tree.insertados) == 1

    def test_mostrar_clientes_muestra_error(
        self,
        interfaz,
        control_clientes,
    ):
        interfaz._tree = TreeviewFalso()

        control_clientes.listar.side_effect = RuntimeError(
            "Fallo de base"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarClientes()

        mock_error.assert_called_once_with(
            "Error al cargar clientes: Fallo de base"
        )

    def test_registrar_cliente_modo_prueba(
        self,
        interfaz,
        control_clientes,
        widgets,
        cliente,
    ):
        self.asignar_widgets(interfaz, widgets)
        self.cargar_datos_validos(widgets)

        control_clientes.registrar_cliente.return_value = (
            cliente
        )

        interfaz.mostrarClientes = MagicMock()

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.registrarCliente()

        control_clientes.registrar_cliente.assert_called_once_with(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_plana="123456",
            edad=30,
            peso=70.5,
            altura=1.70,
            objetivo="Bajar de peso",
        )

        mock_mensaje.assert_called_once()

        interfaz.mostrarClientes.assert_called_once_with()

    def test_registrar_cliente_produccion(
        self,
        interfaz,
        control_clientes,
        widgets,
        cliente,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)
        self.cargar_datos_validos(widgets)

        control_clientes.registrar_cliente.return_value = (
            cliente
        )

        interfaz._obtener_peso_objetivo = MagicMock(
            return_value=65.0
        )

        interfaz._limpiar_formulario = MagicMock()
        interfaz.mostrarClientes = MagicMock()

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.registrarCliente()

        control_clientes.registrar_cliente.assert_called_once_with(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_plana="123456",
            edad=30,
            genero="MUJER",
            peso=70.5,
            altura=1.70,
            objetivo="Bajar de peso",
            peso_objetivo=65.0,
        )

        mock_mensaje.assert_called_once()

    def test_registrar_cliente_valida_genero(
        self,
        interfaz,
        control_clientes,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)
        self.cargar_datos_validos(widgets)

        widgets["genero"].valor = ""

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarCliente()

        control_clientes.registrar_cliente.assert_not_called()

        mock_error.assert_called_once_with(
            "Seleccione el género."
        )

    def test_registrar_cliente_valida_conversion(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)
        self.cargar_datos_validos(widgets)

        widgets["edad"].valor = "invalida"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarCliente()

        mock_error.assert_called_once()

    def test_registrar_cliente_muestra_type_error(
        self,
        interfaz,
        control_clientes,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)
        self.cargar_datos_validos(widgets)

        control_clientes.registrar_cliente.side_effect = TypeError(
            "argumento invalido"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarCliente()

        mock_error.assert_called_once()

    def test_obtener_peso_objetivo(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        widgets["peso_objetivo"].valor = "65"

        assert (
            interfaz._obtener_peso_objetivo(
                70,
                "Bajar de peso",
            )
            == 65.0
        )

        assert (
            interfaz._obtener_peso_objetivo(
                70,
                "Mantener peso",
            )
            == 70
        )

    def test_obtener_peso_objetivo_valida_valores(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        widgets["peso_objetivo"].valor = ""

        with pytest.raises(ValueError):
            interfaz._obtener_peso_objetivo(
                70,
                "Bajar de peso",
            )

        widgets["peso_objetivo"].valor = "0"

        with pytest.raises(ValueError):
            interfaz._obtener_peso_objetivo(
                70,
                "Bajar de peso",
            )

        widgets["peso_objetivo"].valor = "80"

        with pytest.raises(ValueError):
            interfaz._obtener_peso_objetivo(
                70,
                "Bajar de peso",
            )

        widgets["peso_objetivo"].valor = "60"

        with pytest.raises(ValueError):
            interfaz._obtener_peso_objetivo(
                70,
                "Subir de peso",
            )

    def test_editar_cliente_modos(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarCliente()

        mock_error.assert_called_once_with(
            "Seleccione un cliente para editar."
        )

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.editarCliente()

        mock_mensaje.assert_called_once()

    def test_editar_cliente_produccion(
        self,
        interfaz,
    ):
        interfaz.tk = MagicMock()

        interfaz._tree = TreeviewFalso()

        interfaz._tree.seleccion_actual = [
            "fila-1"
        ]

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.editarCliente()

        mock_mensaje.assert_called_once_with(
            "Funcionalidad de edición pendiente."
        )

    def test_eliminar_cliente(
        self,
        interfaz,
        control_clientes,
    ):
        self.preparar_tree(interfaz)

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=True,
        ), patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarClientes",
        ) as mock_clientes:
            interfaz.eliminarCliente()

        control_clientes.eliminar_cliente.assert_called_once_with(
            1
        )

        mock_mensaje.assert_called_once_with(
            "Cliente eliminado correctamente."
        )

        mock_clientes.assert_called_once_with()

    def test_eliminar_cliente_valida_id_y_cancelacion(
        self,
        interfaz,
        control_clientes,
    ):
        self.preparar_tree(
            interfaz,
            valores=(),
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarCliente()

        mock_error.assert_called_once_with(
            "El ID del cliente no es válido."
        )

        self.preparar_tree(interfaz)

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=False,
        ):
            interfaz.eliminarCliente()

        control_clientes.eliminar_cliente.assert_not_called()

    def test_eliminar_cliente_muestra_error(
        self,
        interfaz,
        control_clientes,
    ):
        self.preparar_tree(interfaz)

        control_clientes.eliminar_cliente.side_effect = RuntimeError(
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
            interfaz.eliminarCliente()

        mock_error.assert_called_once_with(
            "Error al eliminar: Fallo al eliminar"
        )

    def test_buscar_cliente_modos(
        self,
        interfaz,
        control_clientes,
        widgets,
        cliente,
    ):
        self.asignar_widgets(interfaz, widgets)

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.buscarCliente()

        mock_error.assert_called_once_with(
            "Ingrese un correo para buscar."
        )

        widgets["buscar"].valor = "ana@example.com"

        control_clientes.buscar_por_correo.return_value = None

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.buscarCliente()

        mock_mensaje.assert_called_once_with(
            "No se encontro ningun cliente con ese correo."
        )

        control_clientes.buscar_por_correo.return_value = cliente

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.buscarCliente()

        mock_mensaje.assert_called_once()

    def test_buscar_cliente_produccion(
        self,
        interfaz,
        control_clientes,
        widgets,
        cliente,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        widgets["buscar"].valor = "ana@example.com"

        control_clientes.buscar_por_correo.return_value = cliente

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.buscarCliente()

        mock_mensaje.assert_called_once()

        mensaje = mock_mensaje.call_args.args[0]

        assert "Estado: EN PROGRESO" in mensaje

    def test_buscar_cliente_produccion_no_encontrado(
        self,
        interfaz,
        control_clientes,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        widgets["buscar"].valor = "nadie@example.com"

        control_clientes.buscar_por_correo.return_value = None

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.buscarCliente()

        mock_mensaje.assert_called_once_with(
            "No se encontró ningún cliente con ese correo."
        )

    def test_buscar_cliente_muestra_error(
        self,
        interfaz,
        control_clientes,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        widgets["buscar"].valor = "ana@example.com"

        control_clientes.buscar_por_correo.side_effect = RuntimeError(
            "Fallo de busqueda"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.buscarCliente()

        mock_error.assert_called_once_with(
            "Error al buscar: Fallo de busqueda"
        )

    def test_actualizar_peso_objetivo(
        self,
        interfaz,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        widgets["meta"].valor = "Mantener peso"
        widgets["peso"].valor = "70"

        interfaz._actualizar_peso_objetivo()

        assert widgets["peso_objetivo"].valor == "70"

        assert (
            widgets["peso_objetivo"].configuracion["state"]
            == "disabled"
        )

    def test_actualizar_rango(
        self,
        interfaz,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        widgets["meta"].valor = "Bajar de peso"

        interfaz._actualizar_rango()

        assert widgets["rango"].configuracion["text"] == ""

        widgets["meta"].valor = "Mantener peso"
        widgets["peso_objetivo"].valor = "invalido"

        interfaz._actualizar_rango()

        assert (
            widgets["rango"].configuracion["text"]
            == "Rango: pendiente"
        )

        widgets["peso_objetivo"].valor = "70"

        interfaz._actualizar_rango()

        assert (
            widgets["rango"].configuracion["text"]
            == "Rango aceptable: 66.0 - 74.0 kg"
        )

    def test_obtener_texto_peso_objetivo(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        widgets["peso_objetivo"].valor = "65"

        assert (
            interfaz._obtener_texto_peso_objetivo()
            == "65"
        )

        interfaz.tk = MagicMock()

        widgets["peso_objetivo"].configuracion[
            "state"
        ] = "disabled"

        widgets["peso"].valor = "70"

        assert (
            interfaz._obtener_texto_peso_objetivo()
            == "70"
        )

        widgets["peso_objetivo"].configuracion[
            "state"
        ] = "normal"

        widgets["peso_objetivo"].valor = "66"

        assert (
            interfaz._obtener_texto_peso_objetivo()
            == "66"
        )

    def test_limpiar_formulario(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        self.cargar_datos_validos(widgets)

        interfaz._limpiar_formulario()

        assert widgets["nombre"].valor == ""
        assert widgets["apellido"].valor == ""
        assert widgets["correo"].valor == ""
        assert widgets["contrasenia"].valor == ""
        assert widgets["edad"].valor == ""
        assert widgets["peso"].valor == ""
        assert widgets["altura"].valor == ""
        assert widgets["objetivo"].valor == ""
        assert widgets["peso_objetivo"].valor == ""

    def test_limpiar_formulario_produccion(
        self,
        interfaz,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        self.cargar_datos_validos(widgets)

        interfaz._limpiar_formulario()

        assert widgets["genero"].valor == ""
        assert widgets["meta"].valor == ""

        assert widgets["rango"].configuracion["text"] == ""

    def test_mostrar_clientes_destruye_frame_anterior(
        self,
        interfaz,
        control_clientes,
    ):
        interfaz.tk = MagicMock()

        frame_anterior = FrameFalso()
        interfaz._tree_frame = frame_anterior

        control_clientes.listar.return_value = []

        with patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Scrollbar",
            side_effect=ScrollbarFalso,
        ):
            interfaz.mostrarClientes()

        assert frame_anterior.destruido is True

    def test_mostrar_clientes_produccion_error(
        self,
        interfaz,
        control_clientes,
    ):
        interfaz.tk = MagicMock()

        control_clientes.listar.side_effect = RuntimeError(
            "Fallo de consulta"
        )

        with patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Frame",
            side_effect=FrameFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Treeview",
            side_effect=TreeviewFalso,
        ), patch(
            "src.interfaz.interfaz_gestion_clientes.ttk.Scrollbar",
            side_effect=ScrollbarFalso,
        ), patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarClientes()

        mock_error.assert_called_once_with(
            "Error al cargar clientes: Fallo de consulta"
        )

    def test_mostrar_clientes_prueba_elimina_fila_anterior(
        self,
        interfaz,
        control_clientes,
    ):
        interfaz._tree = TreeviewFalso()

        interfaz._tree.items = {
            "fila-anterior": {
                "values": (
                    1,
                    "Cliente anterior",
                )
            }
        }

        control_clientes.listar.return_value = []

        interfaz._mostrar_clientes_en_prueba()

        assert interfaz._tree.eliminaciones[0][0] == (
            "fila-anterior",
        )

    def test_registrar_cliente_valida_campos_obligatorios(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        casos = (
            (
                "nombre",
                "Ingrese el nombre.",
            ),
            (
                "apellido",
                "Ingrese el apellido.",
            ),
            (
                "correo",
                "Ingrese el correo.",
            ),
            (
                "contrasenia",
                "Ingrese la contraseña.",
            ),
            (
                "objetivo",
                "Seleccione una meta.",
            ),
        )

        for campo, mensaje in casos:
            self.cargar_datos_validos(widgets)

            widgets[campo].valor = ""

            with patch.object(
                interfaz,
                "mostrar_error",
            ) as mock_error:
                interfaz.registrarCliente()

            mock_error.assert_called_once_with(mensaje)

    def test_registrar_cliente_valida_numeros_positivos(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        casos = (
            (
                "edad",
                "0",
                "La edad debe ser mayor que cero.",
            ),
            (
                "peso",
                "0",
                "El peso actual debe ser mayor que cero.",
            ),
            (
                "altura",
                "0",
                "La altura debe ser mayor que cero.",
            ),
        )

        for campo, valor, mensaje in casos:
            self.cargar_datos_validos(widgets)

            widgets[campo].valor = valor

            with patch.object(
                interfaz,
                "mostrar_error",
            ) as mock_error:
                interfaz.registrarCliente()

            mock_error.assert_called_once_with(mensaje)

    def test_registrar_cliente_error_inesperado(
        self,
        interfaz,
        control_clientes,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        self.cargar_datos_validos(widgets)

        control_clientes.registrar_cliente.side_effect = RuntimeError(
            "Fallo inesperado"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarCliente()

        mock_error.assert_called_once_with(
            "Error inesperado: Fallo inesperado"
        )

    def test_eliminar_cliente_sin_seleccion(
        self,
        interfaz,
    ):
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarCliente()

        mock_error.assert_called_once_with(
            "Seleccione un cliente para eliminar."
        )

    def test_actualizar_peso_objetivo_modo_prueba(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        widgets["meta"].valor = "Mantener peso"
        widgets["peso"].valor = "70"

        interfaz._actualizar_peso_objetivo()

        assert widgets["peso_objetivo"].valor == ""

    def test_actualizar_rango_modo_prueba(
        self,
        interfaz,
        widgets,
    ):
        self.asignar_widgets(interfaz, widgets)

        widgets["meta"].valor = "Mantener peso"
        widgets["peso_objetivo"].valor = "70"

        interfaz._actualizar_rango()

        assert widgets["rango"].configuracion == {}

    def test_actualizar_peso_objetivo_sin_peso(
        self,
        interfaz,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        widgets["meta"].valor = "Mantener peso"
        widgets["peso"].valor = ""

        interfaz._actualizar_rango = MagicMock()

        interfaz._actualizar_peso_objetivo()

        assert widgets["peso_objetivo"].valor == ""

        assert (
            widgets["peso_objetivo"].configuracion["state"]
            == "disabled"
        )

    def test_limpiar_formulario_cubre_rutas_excepcionales(
        self,
        interfaz,
        widgets,
    ):
        interfaz.tk = MagicMock()

        self.asignar_widgets(interfaz, widgets)

        widgets["nombre"].configure = MagicMock(
            side_effect=RuntimeError("No configurable")
        )

        widgets["nombre"].valor = "Ana"

        combo_genero = MagicMock()
        combo_genero.set.side_effect = RuntimeError(
            "No se puede usar set"
        )

        combo_meta = MagicMock()
        combo_meta.set.side_effect = RuntimeError(
            "No se puede usar set"
        )

        etiqueta = MagicMock()
        etiqueta.configure.side_effect = RuntimeError(
            "Etiqueta no disponible"
        )

        interfaz._cb_genero = combo_genero
        interfaz._cb_meta = combo_meta
        interfaz._lbl_rango = etiqueta

        interfaz._limpiar_formulario()

        assert widgets["nombre"].valor == ""

        combo_genero.delete.assert_called_once()
        combo_meta.delete.assert_called_once()

    def test_limpiar_formulario_widgets_y_combos_ausentes(
        self,
        interfaz,
    ):
        interfaz._ent_nombre = EntryFalso()

        interfaz._limpiar_formulario()

        assert interfaz._ent_nombre.valor == ""