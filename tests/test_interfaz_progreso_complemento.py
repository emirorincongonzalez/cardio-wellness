from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.interfaz.interfaz_progreso import InterfazProgreso


class WidgetFalso:
    def __init__(self):
        self.items = {}
        self.valor = ""
        self.configuraciones = []

    def get_children(self):
        return list(self.items.keys())

    def delete(self, item, *args):
        self.items.pop(item, None)

    def insert(self, *args, **kwargs):
        item = f"item_{len(self.items)}"
        self.items[item] = kwargs.get("values", ())
        return item

    def get(self):
        return self.valor

    def delete_texto(self, *args):
        self.valor = ""

    def config(self, **kwargs):
        self.configuraciones.append(kwargs)

    def configure(self, **kwargs):
        self.configuraciones.append(kwargs)


def crear_interfaz():
    interfaz = object.__new__(InterfazProgreso)

    interfaz._cliente = SimpleNamespace(
        id_usuario=10,
        id_cliente=None,
        peso=80,
        peso_objetivo=75,
        objetivo="Perder peso",
    )

    interfaz._controlador = MagicMock()

    interfaz._tree_sesiones = WidgetFalso()
    interfaz._tree_progreso = WidgetFalso()
    interfaz._tree = interfaz._tree_progreso

    interfaz._lbl_sesiones = MagicMock()
    interfaz._lbl_minutos = MagicMock()
    interfaz._lbl_calorias = MagicMock()
    interfaz._lbl_planificadas = MagicMock()
    interfaz._lbl_realizadas = MagicMock()
    interfaz._lbl_cumplimiento = MagicMock()
    interfaz._lbl_meta = MagicMock()
    interfaz._lbl_peso_actual = MagicMock()
    interfaz._lbl_objetivo = MagicMock()
    interfaz._lbl_peso_objetivo = MagicMock()
    interfaz._lbl_rango_meta = MagicMock()
    interfaz._lbl_diferencia_meta = MagicMock()

    interfaz._ent_nuevo_peso = MagicMock()
    interfaz._ent_nuevo_peso.get.return_value = "70"
    interfaz._ent_nuevo_peso.delete = MagicMock()

    interfaz.mostrar_error = MagicMock()
    interfaz.mostrar_mensaje = MagicMock()
    interfaz.cargarDatos = MagicMock()

    return interfaz


def test_asegurar_labels_y_tree_sin_atributos(monkeypatch):
    interfaz = crear_interfaz()

    del interfaz._lbl_sesiones
    del interfaz._tree
    del interfaz._tree_progreso

    monkeypatch.setattr(
        "src.interfaz.interfaz_progreso.ttk.LabelFrame",
        MagicMock(),
    )

    monkeypatch.setattr(
        "src.interfaz.interfaz_progreso.ttk.Label",
        MagicMock(),
    )

    tree = MagicMock()

    monkeypatch.setattr(
        "src.interfaz.interfaz_progreso.ttk.Treeview",
        MagicMock(return_value=tree),
    )

    interfaz._asegurar_labels_resumen()
    interfaz._asegurar_tree_progreso()

    assert hasattr(interfaz, "_lbl_sesiones")
    assert interfaz._tree is tree
    assert interfaz._tree_progreso is tree


def test_cargar_datos_actualiza_y_limpia():
    interfaz = crear_interfaz()

    interfaz._limpiar_tablas = MagicMock()
    interfaz._actualizar_datos_cliente = MagicMock()
    interfaz._cargar_resumen = MagicMock(
        return_value={"total_sesiones": 3}
    )
    interfaz._cargar_sesiones = MagicMock()
    interfaz._cargar_historial_progreso = MagicMock()
    interfaz._actualizar_meta = MagicMock()
    interfaz._evaluar_meta = MagicMock()

    del interfaz.cargarDatos

    interfaz.cargarDatos()

    interfaz._limpiar_tablas.assert_called_once()
    interfaz._actualizar_datos_cliente.assert_called_once()
    interfaz._cargar_sesiones.assert_called_once()
    interfaz._cargar_historial_progreso.assert_called_once()
    interfaz._actualizar_meta.assert_called_once()
    interfaz._evaluar_meta.assert_called_once_with(
        {"total_sesiones": 3}
    )


def test_actualizar_cliente_y_limpiar_tablas():
    interfaz = crear_interfaz()

    cliente_actualizado = SimpleNamespace(
        id_usuario=10,
        peso=70,
    )

    with patch(
        "src.interfaz.interfaz_progreso.Cliente",
        SimpleNamespace,
    ):
        interfaz._controlador.buscar_cliente.return_value = (
            cliente_actualizado
        )

        interfaz._actualizar_datos_cliente()

    assert interfaz._cliente is cliente_actualizado

    interfaz._tree_sesiones.items = {
        "sesion": (1,)
    }

    interfaz._tree_progreso.items = {
        "progreso": (1,)
    }

    interfaz._limpiar_tablas()

    assert interfaz._tree_sesiones.items == {}
    assert interfaz._tree_progreso.items == {}


def test_cargar_resumen_y_meta_completa():
    interfaz = crear_interfaz()

    interfaz._controlador.calcular_resumen_cliente.return_value = {
        "total_sesiones": 4,
        "total_minutos": 120,
        "total_calorias": 900,
        "total_veces_planificadas": 10,
        "total_veces_realizadas": 7,
    }

    resumen = interfaz._cargar_resumen()

    assert resumen["total_sesiones"] == 4

    interfaz._lbl_planificadas.config.assert_called_once()
    interfaz._lbl_realizadas.config.assert_called_once()
    interfaz._lbl_cumplimiento.config.assert_called_once()

    interfaz._cliente.objetivo = "Bajar de peso"
    interfaz._cliente.peso = 80

    interfaz._evaluar_meta(
        {"total_sesiones": 1}
    )

    interfaz._lbl_meta.config.assert_called()

    interfaz._cliente.objetivo = "Perder peso"
    interfaz._cliente.peso = 70

    interfaz._evaluar_meta(
        {"total_sesiones": 1}
    )


def test_historial_sin_porcentaje_y_sesiones_rutas_faltantes():
    interfaz = crear_interfaz()

    interfaz._controlador.consultar_progreso.return_value = [
        {
            "mes": "Enero",
            "peso": 70,
            "sesiones_completadas": 2,
            "sesiones_planificadas": 4,
            "porcentaje_cumplimiento": None,
        }
    ]

    interfaz.mostrarProgresoMensual()

    assert len(interfaz._tree.items) == 1

    interfaz._tree.items = {
        "anterior": (1,)
    }

    interfaz.mostrarProgresoMensual = MagicMock()

    interfaz._cargar_historial_progreso()

    interfaz.mostrarProgresoMensual.assert_called_once()

    del interfaz._tree_sesiones

    interfaz._cargar_sesiones()


def test_errores_de_peso_progreso_pdf_y_porcentaje(monkeypatch):
    interfaz = crear_interfaz()

    interfaz._ent_nuevo_peso.get.return_value = "70"

    interfaz._controlador.generar_progreso_mensual.side_effect = (
        RuntimeError("Fallo peso")
    )

    monkeypatch.setattr(
        "src.interfaz.interfaz_progreso.traceback.print_exc",
        MagicMock(),
    )

    interfaz.registrarPesoMensual()

    assert interfaz.mostrar_error.called

    interfaz.mostrar_error.reset_mock()

    interfaz._controlador.generar_progreso_mensual.side_effect = (
        RuntimeError("Fallo progreso")
    )

    interfaz.generarProgresoMensual()

    assert interfaz.mostrar_error.called

    interfaz.mostrar_error.reset_mock()

    interfaz._controlador.calcular_resumen_cliente.side_effect = (
        ValueError("Error PDF")
    )

    interfaz.generarReportePDF()

    interfaz.mostrar_error.assert_called_once_with("Error PDF")

    def porcentaje_invalido():
        raise RuntimeError("Sin porcentaje")

    sesion = SimpleNamespace(
        porcentaje_cumplimiento=porcentaje_invalido
    )

    resultado = InterfazProgreso._obtener_porcentaje_sesion(
        sesion,
        10,
        5,
    )

    assert resultado == 50.0

def test_asegurar_tree_progreso_reutiliza_tree_existente():
    interfaz = crear_interfaz()

    del interfaz._tree_progreso

    tree_existente = WidgetFalso()
    interfaz._tree = tree_existente

    interfaz._asegurar_tree_progreso()

    assert interfaz._tree_progreso is tree_existente
    assert interfaz._tree is tree_existente


def test_actualizar_datos_cliente_ignora_error():
    interfaz = crear_interfaz()

    interfaz._controlador.buscar_cliente.side_effect = RuntimeError(
        "Fallo al buscar cliente"
    )

    interfaz._actualizar_datos_cliente()

    assert interfaz._cliente.id_usuario == 10


def test_cargar_resumen_devuelve_diccionario_vacio_si_falla():
    interfaz = crear_interfaz()

    interfaz._controlador.calcular_resumen_cliente.side_effect = (
        RuntimeError("Fallo de resumen")
    )

    resultado = interfaz._cargar_resumen()

    assert resultado == {}


def test_evaluar_meta_crea_labels_si_no_existen(monkeypatch):
    interfaz = crear_interfaz()

    del interfaz._lbl_meta

    monkeypatch.setattr(
        "src.interfaz.interfaz_progreso.ttk.LabelFrame",
        MagicMock(),
    )

    monkeypatch.setattr(
        "src.interfaz.interfaz_progreso.ttk.Label",
        MagicMock(),
    )

    interfaz._cliente.objetivo = "Objetivo diferente"

    interfaz._actualizar_meta = MagicMock()

    interfaz._evaluar_meta(
        {"total_sesiones": 1}
    )

    interfaz._actualizar_meta.assert_called_once_with()


def test_evaluar_meta_llama_actualizar_meta_para_otro_objetivo():
    interfaz = crear_interfaz()

    interfaz._cliente.objetivo = "Mantener salud"

    interfaz._actualizar_meta = MagicMock()

    interfaz._evaluar_meta(
        {"total_sesiones": 3}
    )

    interfaz._actualizar_meta.assert_called_once_with()


def test_actualizar_meta_cubre_estado_alcanzado_y_progreso():
    interfaz = crear_interfaz()

    interfaz._cliente.peso = 70
    interfaz._cliente.peso_objetivo = 65
    interfaz._cliente.objetivo = "Bajar de peso"

    interfaz._cliente.obtener_estado_meta = MagicMock(
        return_value="META ALCANZADA"
    )

    interfaz._cliente.obtener_diferencia_meta = MagicMock(
        return_value=0
    )

    interfaz._cliente.obtener_descripcion_meta = MagicMock(
        return_value="Peso objetivo alcanzado"
    )

    interfaz._actualizar_meta()

    interfaz._lbl_peso_actual.config.assert_called()
    interfaz._lbl_objetivo.config.assert_called()
    interfaz._lbl_peso_objetivo.config.assert_called()
    interfaz._lbl_rango_meta.config.assert_called_with(
        text="Peso objetivo alcanzado"
    )

    interfaz._lbl_meta.config.assert_called_with(
        text="META ALCANZADA",
        foreground="green",
    )

    interfaz._lbl_diferencia_meta.config.assert_called_with(
        text="Diferencia: 0 kg",
        foreground="green",
    )

    interfaz._lbl_meta.reset_mock()
    interfaz._lbl_diferencia_meta.reset_mock()

    interfaz._cliente.obtener_estado_meta = MagicMock(
        return_value="EN PROGRESO"
    )

    interfaz._cliente.obtener_diferencia_meta = MagicMock(
        return_value=4.5
    )

    interfaz._cliente.obtener_descripcion_meta = MagicMock(
        return_value="Continua trabajando"
    )

    interfaz._actualizar_meta()

    interfaz._lbl_diferencia_meta.config.assert_called_with(
        text="Diferencia restante: 4.5 kg",
        foreground="red",
    )


def test_actualizar_meta_ignora_errores_de_metodos_cliente():
    interfaz = crear_interfaz()

    interfaz._cliente.peso = 80
    interfaz._cliente.peso_objetivo = 75

    def falla_estado():
        raise RuntimeError("Estado no disponible")

    def falla_diferencia():
        raise RuntimeError("Diferencia no disponible")

    def falla_descripcion():
        raise RuntimeError("Descripcion no disponible")

    interfaz._cliente.obtener_estado_meta = falla_estado
    interfaz._cliente.obtener_diferencia_meta = falla_diferencia
    interfaz._cliente.obtener_descripcion_meta = falla_descripcion

    interfaz._actualizar_meta()

    interfaz._lbl_rango_meta.config.assert_called_with(text="")

    interfaz._lbl_diferencia_meta.config.assert_called_with(
        text="Diferencia restante: 5.0 kg",
        foreground="red",
    )


def test_cargar_sesiones_ignora_error_controlador():
    interfaz = crear_interfaz()

    interfaz._controlador.obtener_sesiones_cliente.side_effect = (
        RuntimeError("Fallo de sesiones")
    )

    interfaz._cargar_sesiones()

    assert interfaz._tree_sesiones.items == {}


def test_registrar_peso_mensual_muestra_value_error():
    interfaz = crear_interfaz()

    interfaz._ent_nuevo_peso.get.return_value = "70"

    interfaz._controlador.generar_progreso_mensual.side_effect = (
        ValueError("El progreso ya existe")
    )

    interfaz.registrarPesoMensual()

    interfaz.mostrar_error.assert_called_once_with(
        "El progreso ya existe"
    )

def test_actualizar_meta_sin_labels_sale_sin_error():
    interfaz = crear_interfaz()

    del interfaz._lbl_peso_actual

    interfaz._actualizar_meta()