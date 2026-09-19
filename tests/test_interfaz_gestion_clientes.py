from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_gestion_clientes import (
    InterfazGestionClientes,
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


class TreeviewFalso(WidgetFalso):
    pass


class TestInterfazGestionClientes:

    @pytest.fixture
    def control_clientes(self):
        """
        Crea un controlador de clientes simulado.
        """
        controlador = MagicMock()
        controlador.listar.return_value = []

        return controlador

    @pytest.fixture
    def cliente(self):
        """
        Crea un cliente simulado.
        """
        cliente = MagicMock()

        cliente.id_usuario = 1
        cliente.peso = 70.5
        cliente.objetivo = "Mejorar resistencia"
        cliente.correo_electronico = "ana@example.com"

        cliente.obtener_nombre_completo.return_value = "Ana Pérez"

        return cliente

    @pytest.fixture
    def interfaz(self, control_clientes):
        """
        Crea la interfaz sin ejecutar el constructor real.
        """
        interfaz = object.__new__(InterfazGestionClientes)

        interfaz._controlador = control_clientes
        interfaz._control_clientes = control_clientes

        return interfaz

    @pytest.fixture
    def widgets_formulario(self):
        """
        Crea los widgets falsos del formulario.
        """
        return {
            "nombre": EntryFalso(),
            "apellido": EntryFalso(),
            "correo": EntryFalso(),
            "contrasenia": EntryFalso(),
            "edad": EntryFalso(),
            "peso": EntryFalso(),
            "altura": EntryFalso(),
            "objetivo": EntryFalso(),
            "buscar": EntryFalso(),
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
        interfaz._ent_apellido = widgets["apellido"]
        interfaz._ent_correo = widgets["correo"]
        interfaz._ent_contrasenia = widgets["contrasenia"]
        interfaz._ent_edad = widgets["edad"]
        interfaz._ent_peso = widgets["peso"]
        interfaz._ent_altura = widgets["altura"]
        interfaz._ent_objetivo = widgets["objetivo"]
        interfaz._ent_buscar = widgets["buscar"]

    def test_control_clientes_devuelve_el_controlador(
        self,
        interfaz,
        control_clientes,
    ):
        """
        Verifica la propiedad control_clientes.
        """
        assert interfaz.control_clientes is control_clientes

    def test_mostrar_formulario_cliente_crea_widgets(
        self,
        interfaz,
    ):
        """
        Verifica que se creen los widgets del formulario.
        """
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

        assert hasattr(interfaz, "_ent_nombre")
        assert hasattr(interfaz, "_ent_apellido")
        assert hasattr(interfaz, "_ent_correo")
        assert hasattr(interfaz, "_ent_contrasenia")
        assert hasattr(interfaz, "_ent_edad")
        assert hasattr(interfaz, "_ent_peso")
        assert hasattr(interfaz, "_ent_altura")
        assert hasattr(interfaz, "_ent_objetivo")
        assert hasattr(interfaz, "_ent_buscar")

        assert isinstance(interfaz._ent_nombre, EntryFalso)
        assert isinstance(interfaz._ent_apellido, EntryFalso)
        assert isinstance(interfaz._ent_correo, EntryFalso)
        assert isinstance(interfaz._ent_contrasenia, EntryFalso)
        assert isinstance(interfaz._ent_edad, EntryFalso)
        assert isinstance(interfaz._ent_peso, EntryFalso)
        assert isinstance(interfaz._ent_altura, EntryFalso)
        assert isinstance(interfaz._ent_objetivo, EntryFalso)
        assert isinstance(interfaz._ent_buscar, EntryFalso)

    def test_mostrar_clientes_carga_clientes(
        self,
        interfaz,
        control_clientes,
        cliente,
    ):
        """
        Verifica que los clientes se carguen en la tabla.
        """
        interfaz._tree = TreeviewFalso()
        control_clientes.listar.return_value = [cliente]

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarClientes()

        control_clientes.listar.assert_called_once_with()

        assert interfaz._tree.insertados == [
            (
                ("", "end"),
                {
                    "values": (
                        1,
                        "Ana Pérez",
                        "ana@example.com",
                        70.5,
                        "Mejorar resistencia",
                    )
                },
            )
        ]

        mock_error.assert_not_called()

    def test_mostrar_clientes_elimina_datos_anteriores(
        self,
        interfaz,
        control_clientes,
        cliente,
    ):
        """
        Verifica que se eliminen los datos anteriores
        antes de cargar la lista nuevamente.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.items = {
            "item1": {
                "values": (
                    1,
                    "Cliente anterior",
                )
            }
        }

        control_clientes.listar.return_value = [cliente]

        interfaz.mostrarClientes()

        assert len(interfaz._tree.eliminaciones) == 1
        assert interfaz._tree.eliminaciones[0][0] == ("item1",)

    def test_mostrar_clientes_maneja_error(
        self,
        interfaz,
        control_clientes,
    ):
        """
        Verifica el manejo de errores al listar clientes.
        """
        interfaz._tree = TreeviewFalso()

        control_clientes.listar.side_effect = RuntimeError(
            "Error de base de datos"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.mostrarClientes()

        mock_error.assert_called_once_with(
            "Error al cargar clientes: Error de base de datos"
        )

    def test_registrar_cliente_correctamente(
        self,
        interfaz,
        control_clientes,
        widgets_formulario,
        cliente,
    ):
        """
        Verifica el registro correcto de un cliente.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = " Ana "
        widgets_formulario["apellido"].valor = " Pérez "
        widgets_formulario["correo"].valor = " ana@example.com "
        widgets_formulario["contrasenia"].valor = "123456"
        widgets_formulario["edad"].valor = "30"
        widgets_formulario["peso"].valor = "70.5"
        widgets_formulario["altura"].valor = "1.70"
        widgets_formulario["objetivo"].valor = "Mejorar resistencia"

        control_clientes.registrar_cliente.return_value = cliente

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje, patch.object(
            interfaz,
            "mostrarClientes",
        ) as mock_mostrar_clientes:

            interfaz.registrarCliente()

        control_clientes.registrar_cliente.assert_called_once_with(
            nombre="Ana",
            apellido="Pérez",
            correo_electronico="ana@example.com",
            contrasenia_plana="123456",
            edad=30,
            peso=70.5,
            altura=1.70,
            objetivo="Mejorar resistencia",
        )

        mock_mensaje.assert_called_once_with(
            "Cliente Ana Pérez registrado."
        )

        mock_mostrar_clientes.assert_called_once_with()

        for nombre, entry in widgets_formulario.items():
            if nombre != "buscar":
                assert entry.valor == ""

    def test_registrar_cliente_maneja_value_error(
        self,
        interfaz,
        control_clientes,
        widgets_formulario,
    ):
        """
        Verifica el manejo de errores de validación.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Ana"
        widgets_formulario["apellido"].valor = "Pérez"
        widgets_formulario["correo"].valor = "ana@example.com"
        widgets_formulario["contrasenia"].valor = "123456"
        widgets_formulario["edad"].valor = "edad inválida"
        widgets_formulario["peso"].valor = "70"
        widgets_formulario["altura"].valor = "1.70"
        widgets_formulario["objetivo"].valor = "Salud"

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarCliente()

        control_clientes.registrar_cliente.assert_not_called()
        mock_error.assert_called_once()

    def test_registrar_cliente_maneja_error_del_controlador(
        self,
        interfaz,
        control_clientes,
        widgets_formulario,
    ):
        """
        Verifica el manejo de errores inesperados.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["nombre"].valor = "Ana"
        widgets_formulario["apellido"].valor = "Pérez"
        widgets_formulario["correo"].valor = "ana@example.com"
        widgets_formulario["contrasenia"].valor = "123456"
        widgets_formulario["edad"].valor = "30"
        widgets_formulario["peso"].valor = "70"
        widgets_formulario["altura"].valor = "1.70"
        widgets_formulario["objetivo"].valor = "Salud"

        control_clientes.registrar_cliente.side_effect = RuntimeError(
            "Error inesperado"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.registrarCliente()

        mock_error.assert_called_once_with(
            "Error inesperado: Error inesperado"
        )

    def test_editar_cliente_sin_seleccion(
        self,
        interfaz,
    ):
        """
        Verifica el error cuando no se selecciona
        ningún cliente para editar.
        """
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.editarCliente()

        mock_error.assert_called_once_with(
            "Seleccione un cliente para editar."
        )

    def test_editar_cliente_con_seleccion(
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
            interfaz.editarCliente()

        mock_mensaje.assert_called_once_with(
            "Funcionalidad de edicion pendiente de implementar."
        )

    def test_eliminar_cliente_sin_seleccion(
        self,
        interfaz,
    ):
        """
        Verifica el error cuando no se selecciona
        ningún cliente para eliminar.
        """
        interfaz._tree = TreeviewFalso()

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.eliminarCliente()

        mock_error.assert_called_once_with(
            "Seleccione un cliente para eliminar."
        )

    def test_eliminar_cliente_usuario_cancela(
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
                    "Ana Pérez",
                )
            }
        }

        with patch.object(
            interfaz,
            "confirmar_accion",
            return_value=False,
        ) as mock_confirmar:
            interfaz.eliminarCliente()

        mock_confirmar.assert_called_once_with(
            "Eliminar al cliente con ID 5?"
        )

    def test_eliminar_cliente_correctamente(
        self,
        interfaz,
        control_clientes,
    ):
        """
        Verifica la eliminación correcta de un cliente.
        """
        interfaz._tree = TreeviewFalso()
        interfaz._tree.seleccion_actual = ["item1"]
        interfaz._tree.items = {
            "item1": {
                "values": (
                    5,
                    "Ana Pérez",
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
            "mostrarClientes",
        ) as mock_mostrar_clientes:

            interfaz.eliminarCliente()

        control_clientes.eliminar_cliente.assert_called_once_with(5)

        mock_mensaje.assert_called_once_with(
            "Cliente eliminado correctamente."
        )

        mock_mostrar_clientes.assert_called_once_with()

    def test_eliminar_cliente_maneja_error(
        self,
        interfaz,
        control_clientes,
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
                    "Ana Pérez",
                )
            }
        }

        control_clientes.eliminar_cliente.side_effect = RuntimeError(
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

            interfaz.eliminarCliente()

        mock_error.assert_called_once_with(
            "Error al eliminar: No se pudo eliminar"
        )

    def test_buscar_cliente_sin_correo(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica el error cuando el correo está vacío.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["buscar"].valor = "   "

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.buscarCliente()

        mock_error.assert_called_once_with(
            "Ingrese un correo para buscar."
        )

        interfaz.control_clientes.buscar_por_correo.assert_not_called()

    def test_buscar_cliente_no_encontrado(
        self,
        interfaz,
        control_clientes,
        widgets_formulario,
    ):
        """
        Verifica el mensaje cuando no se encuentra un cliente.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["buscar"].valor = "ana@example.com"
        control_clientes.buscar_por_correo.return_value = None

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.buscarCliente()

        control_clientes.buscar_por_correo.assert_called_once_with(
            "ana@example.com"
        )

        mock_mensaje.assert_called_once_with(
            "No se encontro ningun cliente con ese correo."
        )

    def test_buscar_cliente_encontrado(
        self,
        interfaz,
        control_clientes,
        widgets_formulario,
        cliente,
    ):
        """
        Verifica el mensaje cuando se encuentra un cliente.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["buscar"].valor = "ana@example.com"
        control_clientes.buscar_por_correo.return_value = cliente

        with patch.object(
            interfaz,
            "mostrar_mensaje",
        ) as mock_mensaje:
            interfaz.buscarCliente()

        control_clientes.buscar_por_correo.assert_called_once_with(
            "ana@example.com"
        )

        mock_mensaje.assert_called_once_with(
            "Encontrado: Ana Pérez - ana@example.com"
        )

    def test_buscar_cliente_maneja_error(
        self,
        interfaz,
        control_clientes,
        widgets_formulario,
    ):
        """
        Verifica el manejo de errores al buscar.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        widgets_formulario["buscar"].valor = "ana@example.com"

        control_clientes.buscar_por_correo.side_effect = RuntimeError(
            "Error de búsqueda"
        )

        with patch.object(
            interfaz,
            "mostrar_error",
        ) as mock_error:
            interfaz.buscarCliente()

        mock_error.assert_called_once_with(
            "Error al buscar: Error de búsqueda"
        )

    def test_limpiar_formulario(
        self,
        interfaz,
        widgets_formulario,
    ):
        """
        Verifica que se limpien únicamente los campos
        del formulario de registro.
        """
        self.asignar_widgets_formulario(
            interfaz,
            widgets_formulario,
        )

        campos_formulario = (
            widgets_formulario["nombre"],
            widgets_formulario["apellido"],
            widgets_formulario["correo"],
            widgets_formulario["contrasenia"],
            widgets_formulario["edad"],
            widgets_formulario["peso"],
            widgets_formulario["altura"],
            widgets_formulario["objetivo"],
        )

        for entry in campos_formulario:
            entry.valor = "dato"

        widgets_formulario["buscar"].valor = "correo para conservar"

        interfaz._limpiar_formulario()

        for entry in campos_formulario:
            assert entry.valor == ""

        assert widgets_formulario["buscar"].valor == (
            "correo para conservar"
        )