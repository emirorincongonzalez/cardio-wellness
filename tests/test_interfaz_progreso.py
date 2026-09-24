from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.interfaz.interfaz_base import InterfazBase
from src.interfaz.interfaz_progreso import (
    InterfazProgreso,
)
from src.modelos.enums import Intensidad


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
        self.valor = ""

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

    def configure(self, *args, **kwargs):
        self.configuraciones.append((args, kwargs))

    def insert(self, *args, **kwargs):
        self.insertados.append((args, kwargs))
        item_id = f"item_{len(self.insertados)}"
        self.items[item_id] = kwargs.get("values", ())
        return item_id

    def get_children(self):
        return list(self.items.keys())

    def delete(self, item_id, *args):
        self.items.pop(item_id, None)

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor

    def bind(self, *args, **kwargs):
        pass

    def yview(self, *args, **kwargs):
        pass

    def xview(self, *args, **kwargs):
        pass

    def rowconfigure(self, *args, **kwargs):
        pass

    def columnconfigure(self, *args, **kwargs):
        pass

    def pack_forget(self, *args, **kwargs):
        pass

    def place(self, *args, **kwargs):
        pass

    def winfo_children(self):
        return []

    def __setitem__(self, clave, valor):
        setattr(
            self,
            clave,
            valor,
        )

    def __getitem__(self, clave):
        return getattr(
            self,
            clave,
            None,
        )

class EntryFalso(WidgetFalso):
    """
    Entry falso con soporte para delete.
    """

    def delete(self, *args, **kwargs):
        self.valor = ""


class TestInterfazProgreso:
    @pytest.fixture
    def cliente(self):
        """
        Crea un cliente simulado.
        """
        cliente = MagicMock()

        cliente.id_usuario = 10
        cliente.id_cliente = None
        cliente.nombre = "Laura"
        cliente.apellido = "Martínez"
        cliente.peso = 70
        cliente.peso_objetivo = 65
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
        Crea la interfaz sin ejecutar el constructor real de Tk.
        """
        interfaz = object.__new__(InterfazProgreso)

        interfaz._controlador = control_progreso
        interfaz._cliente = cliente
        interfaz._tree = WidgetFalso()
        interfaz._tree_progreso = interfaz._tree
        interfaz._tree_sesiones = WidgetFalso()
        interfaz._ent_nuevo_peso = EntryFalso()

        interfaz._lbl_sesiones = MagicMock()
        interfaz._lbl_minutos = MagicMock()
        interfaz._lbl_calorias = MagicMock()
        interfaz._lbl_meta = MagicMock()
        interfaz._lbl_planificadas = MagicMock()
        interfaz._lbl_realizadas = MagicMock()
        interfaz._lbl_cumplimiento = MagicMock()
        interfaz._lbl_peso_actual = MagicMock()
        interfaz._lbl_objetivo = MagicMock()
        interfaz._lbl_peso_objetivo = MagicMock()
        interfaz._lbl_rango_meta = MagicMock()
        interfaz._lbl_diferencia_meta = MagicMock()

        interfaz.mostrar_error = MagicMock()
        interfaz.mostrar_mensaje = MagicMock()
        interfaz.cargarDatos = MagicMock()

        return interfaz


    def test_constructor_crea_interfaz_completa_sin_tk(
        self,
        cliente,
        control_progreso,
    ):
        """
        Verifica que el constructor cree los componentes visuales sin
        abrir una ventana real de Tkinter.

        Cubre barra superior, botones, resumen, meta, actualización de
        peso, tablas, Treeviews y scrollbars.
        """

        def inicializar_interfaz_base(
            instancia,
            *args,
            **kwargs,
        ):
            """
            Reemplaza temporalmente el constructor real de ttk.Frame.
            """
            if len(args) >= 2:
                instancia._controlador = args[1]
            else:
                instancia._controlador = kwargs.get(
                    "controlador",
                    control_progreso,
                )

        with patch.object(
            InterfazBase,
            "__init__",
            inicializar_interfaz_base,
        ), patch.object(
            InterfazProgreso,
            "pack",
        ), patch.object(
            InterfazProgreso,
            "cargarDatos",
        ) as mock_cargar_datos, patch(
            "src.interfaz.interfaz_progreso.ttk.Frame",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.LabelFrame",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Label",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Entry",
            side_effect=EntryFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Button",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Treeview",
            side_effect=WidgetFalso,
        ), patch(
            "src.interfaz.interfaz_progreso.ttk.Scrollbar",
            side_effect=WidgetFalso,
        ):
            interfaz_creada = InterfazProgreso(
                MagicMock(),
                control_progreso,
                cliente,
            )

        assert interfaz_creada.cliente is cliente

        assert hasattr(
            interfaz_creada,
            "_lbl_sesiones",
        )

        assert hasattr(
            interfaz_creada,
            "_lbl_minutos",
        )

        assert hasattr(
            interfaz_creada,
            "_lbl_calorias",
        )

        assert hasattr(
            interfaz_creada,
            "_lbl_meta",
        )

        assert hasattr(
            interfaz_creada,
            "_ent_nuevo_peso",
        )

        assert hasattr(
            interfaz_creada,
            "_tree_sesiones",
        )

        assert hasattr(
            interfaz_creada,
            "_tree_progreso",
        )

        assert hasattr(
            interfaz_creada,
            "_tree",
        )

        assert (
            interfaz_creada._tree
            is interfaz_creada._tree_progreso
        )

        mock_cargar_datos.assert_called_once_with()


    
    def test_propiedad_cliente(
        self,
        interfaz,
        cliente,
    ):
        """
        Verifica la propiedad cliente.
        """
        assert interfaz.cliente is cliente

    @pytest.mark.parametrize(
        "valor,predeterminado,esperado",
        [
            (10, 0.0, 10.0),
            (15.5, 0.0, 15.5),
            ("18.4", 0.0, 18.4),
            ("no_numero", 7.0, 7.0),
            (None, 4.0, 4.0),
            (True, 9.0, 9.0),
            (False, 6.0, 6.0),
        ],
    )
    def test_obtener_numero(
        self,
        valor,
        predeterminado,
        esperado,
    ):
        """
        Prueba conversión segura de valores numéricos.
        """
        resultado = InterfazProgreso._obtener_numero(
            valor,
            predeterminado,
        )

        assert resultado == esperado

    def test_valor_sesion_con_diccionario(self):
        """
        Prueba lectura de datos cuando la sesión es dict.
        """
        sesion = {
            "duracion_real": 45,
            "nombre_ejercicio": "Caminata",
        }

        assert (
            InterfazProgreso._valor_sesion(
                sesion,
                "duracion_real",
            )
            == 45
        )

        assert (
            InterfazProgreso._valor_sesion(
                sesion,
                "inexistente",
                "predeterminado",
            )
            == "predeterminado"
        )

    def test_valor_sesion_con_objeto(self):
        """
        Prueba lectura de atributos de un objeto.
        """
        sesion = MagicMock()
        sesion.calorias_quemadas = 350

        assert (
            InterfazProgreso._valor_sesion(
                sesion,
                "calorias_quemadas",
            )
            == 350
        )

    @pytest.mark.parametrize(
        "valor,esperado",
        [
            (Intensidad.ALTA, "ALTA"),
            (None, ""),
            ("MEDIA", "MEDIA"),
        ],
    )
    def test_formatear_intensidad(
        self,
        valor,
        esperado,
    ):
        """
        Prueba formato de intensidad.
        """
        assert (
            InterfazProgreso._formatear_intensidad(valor)
            == esperado
        )

    @pytest.mark.parametrize(
        "valor,esperado",
        [
            (None, ""),
            (datetime(2026, 1, 15), "2026-01-15"),
            (date(2026, 2, 20), "2026-02-20"),
            ("texto", "texto"),
        ],
    )
    def test_formatear_fecha(
        self,
        valor,
        esperado,
    ):
        """
        Prueba formato de fechas.
        """
        assert (
            InterfazProgreso._formatear_fecha(valor)
            == esperado
        )

    @pytest.mark.parametrize(
        "valor,esperado",
        [
            (None, ""),
            (datetime(2026, 1, 15), "January 2026"),
            (date(2026, 2, 1), "February 2026"),
            ("Marzo 2026", "Marzo 2026"),
        ],
    )
    def test_formatear_mes(
        self,
        valor,
        esperado,
    ):
        """
        Prueba formato de mes.
        """
        assert (
            InterfazProgreso._formatear_mes(valor)
            == esperado
        )

    @pytest.mark.parametrize(
        "planificadas,realizadas,esperado",
        [
            (10, 5, 50.0),
            (10, 10, 100.0),
            (10, 15, 100.0),
            (0, 5, 0.0),
            (-1, 5, 0.0),
            ("invalido", 5, 0.0),
            (None, 5, 0.0),
        ],
    )
    def test_calcular_porcentaje(
        self,
        planificadas,
        realizadas,
        esperado,
    ):
        """
        Prueba cálculo seguro de porcentaje.
        """
        resultado = InterfazProgreso._calcular_porcentaje(
            planificadas,
            realizadas,
        )

        assert resultado == esperado

    def test_calcular_cumplimiento(
        self,
    ):
        """
        Prueba alias de cálculo de cumplimiento.
        """
        resultado = InterfazProgreso._calcular_cumplimiento(
            8,
            6,
        )

        assert resultado == 75.0

    @pytest.mark.parametrize(
        "valor,esperado",
        [
            (50, "50.00%"),
            (66.666, "66.67%"),
            ("80", "80.00%"),
            (None, "0.00%"),
            ("texto", "0.00%"),
        ],
    )
    def test_formatear_porcentaje(
        self,
        valor,
        esperado,
    ):
        """
        Prueba formato de porcentaje.
        """
        assert (
            InterfazProgreso._formatear_porcentaje(valor)
            == esperado
        )

    def test_obtener_porcentaje_sesion_con_metodo(
        self,
    ):
        """
        Prueba porcentaje mediante método del objeto sesión.
        """
        sesion = MagicMock()
        sesion.porcentaje_cumplimiento = MagicMock(
            return_value=83.5
        )

        resultado = InterfazProgreso._obtener_porcentaje_sesion(
            sesion,
            10,
            2,
        )

        assert resultado == 83.5

    def test_obtener_porcentaje_sesion_con_atributo(
        self,
    ):
        """
        Prueba porcentaje mediante atributo numérico.
        """
        sesion = MagicMock()
        sesion.porcentaje_cumplimiento = 72.4

        resultado = InterfazProgreso._obtener_porcentaje_sesion(
            sesion,
            10,
            2,
        )

        assert resultado == 72.4

    def test_obtener_porcentaje_sesion_calcula_por_defecto(
        self,
    ):
        """
        Prueba cálculo cuando la sesión no tiene porcentaje válido.
        """
        sesion = MagicMock()
        sesion.porcentaje_cumplimiento = "invalido"

        resultado = InterfazProgreso._obtener_porcentaje_sesion(
            sesion,
            8,
            6,
        )

        assert resultado == 75.0

    def test_obtener_estado_sesion_con_metodo(
        self,
    ):
        """
        Prueba estado mediante método especializado.
        """
        sesion = MagicMock()
        sesion.obtener_estado_cumplimiento.return_value = (
            "COMPLETADA"
        )

        resultado = InterfazProgreso._obtener_estado_sesion(
            sesion,
            10,
            3,
        )

        assert resultado == "COMPLETADA"

    def test_obtener_estado_sesion_con_valores(
        self,
    ):
        """
        Prueba estados calculados usando valores realizados.
        """
        sesion = MagicMock()
        sesion.obtener_estado_cumplimiento.side_effect = (
            RuntimeError("Sin estado")
        )

        completada = InterfazProgreso._obtener_estado_sesion(
            sesion,
            5,
            5,
        )

        pendiente = InterfazProgreso._obtener_estado_sesion(
            sesion,
            5,
            3,
        )

        assert completada == "COMPLETADA"
        assert pendiente == "PENDIENTE"

    def test_obtener_estado_sesion_con_valores_invalidos(
        self,
    ):
        """
        Prueba estado pendiente ante valores no convertibles.
        """
        sesion = MagicMock()
        sesion.obtener_estado_cumplimiento.side_effect = (
            RuntimeError("Sin estado")
        )

        resultado = InterfazProgreso._obtener_estado_sesion(
            sesion,
            "invalido",
            "dato",
        )

        assert resultado == "PENDIENTE"

    def test_obtener_id_cliente_desde_id_usuario(
        self,
        interfaz,
    ):
        """
        Prueba preferencia por id_usuario.
        """
        interfaz._cliente.id_usuario = 25
        interfaz._cliente.id_cliente = 99

        assert interfaz._obtener_id_cliente() == 25

    def test_obtener_id_cliente_desde_id_cliente(
        self,
        interfaz,
    ):
        """
        Prueba uso de id_cliente si no hay id_usuario válido.
        """
        interfaz._cliente.id_usuario = None
        interfaz._cliente.id_cliente = 35

        assert interfaz._obtener_id_cliente() == 35

    def test_obtener_id_cliente_convierte_texto(
        self,
        interfaz,
    ):
        """
        Prueba conversión de ID textual válido.
        """
        interfaz._cliente.id_usuario = "48"
        interfaz._cliente.id_cliente = None

        assert interfaz._obtener_id_cliente() == 48

    def test_obtener_id_cliente_rechaza_invalido(
        self,
        interfaz,
    ):
        """
        Prueba error si no existe un ID válido.
        """
        interfaz._cliente.id_usuario = None
        interfaz._cliente.id_cliente = "invalido"

        with pytest.raises(
            ValueError,
            match="identificador válido",
        ):
            interfaz._obtener_id_cliente()

    def test_mostrar_resumen_correctamente(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba carga correcta del resumen.
        """
        resumen = {
            "total_sesiones": 12,
            "total_minutos": 360,
            "total_calorias": 2500,
        }

        control_progreso.calcular_resumen_cliente.return_value = (
            resumen
        )

        interfaz.mostrarResumen()

        control_progreso.calcular_resumen_cliente.assert_called_once_with(
            10
        )

        interfaz._lbl_sesiones.config.assert_called_once_with(
            text="Sesiones: 12"
        )

        interfaz._lbl_minutos.config.assert_called_once_with(
            text="Minutos: 360"
        )

        interfaz._lbl_calorias.config.assert_called_once_with(
            text="Calorias: 2500"
        )

    def test_mostrar_resumen_maneja_error(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba manejo de excepción al consultar resumen.
        """
        control_progreso.calcular_resumen_cliente.side_effect = (
            RuntimeError("Error de base de datos")
        )

        interfaz.mostrarResumen()

        interfaz.mostrar_error.assert_called_once_with(
            "Error al cargar resumen: Error de base de datos"
        )

    def test_mostrar_progreso_mensual_carga_historial(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba historial mensual con datos.
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

        interfaz.mostrarProgresoMensual()

        control_progreso.consultar_progreso.assert_called_once_with(
            10
        )

        assert len(interfaz._tree.insertados) == 1

        valores = interfaz._tree.insertados[0][1]["values"]

        assert valores == (
            "January 2026",
            "70.5 kg",
            8,
            12,
            "66.67%",
        )

    def test_mostrar_progreso_mensual_sin_datos(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba historial vacío.
        """
        control_progreso.consultar_progreso.return_value = []

        interfaz.mostrarProgresoMensual()

        assert interfaz._tree.insertados == []

    def test_mostrar_progreso_mensual_maneja_error(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba error al consultar historial mensual.
        """
        control_progreso.consultar_progreso.side_effect = (
            RuntimeError("Error de base de datos")
        )

        interfaz.mostrarProgresoMensual()

        interfaz.mostrar_error.assert_called_once_with(
            "Error al cargar historial: Error de base de datos"
        )

    def test_mostrar_historial_llama_progreso_mensual(
        self,
        interfaz,
    ):
        """
        Prueba alias mostrarHistorial.
        """
        interfaz.mostrarProgresoMensual = MagicMock()

        interfaz.mostrarHistorial()

        interfaz.mostrarProgresoMensual.assert_called_once_with()

    def test_mostrar_sesiones_carga_sesiones(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba carga de sesiones en Treeview.
        """
        control_progreso.obtener_sesiones_cliente.return_value = [
            {
                "fecha": date(2026, 1, 10),
                "nombre_ejercicio": "Caminata",
                "duracion_real": 30,
                "intensidad_real": Intensidad.MEDIA,
                "calorias_quemadas": 220,
                "veces_planificadas": 2,
                "veces_realizadas": 2,
                "observaciones": "Sesión completada",
            }
        ]

        interfaz.mostrarSesiones()

        assert len(interfaz._tree_sesiones.insertados) == 1

        valores = interfaz._tree_sesiones.insertados[0][1][
            "values"
        ]

        assert valores[0] == "2026-01-10"
        assert valores[1] == "Caminata"
        assert valores[2] == "30 min"
        assert valores[3] == "MEDIA"
        assert valores[4] == "220 kcal"
        assert valores[7] == "100.00%"
        assert valores[8] == "COMPLETADA"

    def test_generar_progreso_mensual_exitoso(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba creación exitosa del progreso mensual.
        """
        interfaz._cliente.peso = 72.5

        interfaz.generarProgresoMensual()

        control_progreso.generar_progreso_mensual.assert_called_once()

        argumentos = (
            control_progreso.generar_progreso_mensual.call_args
            .kwargs
        )

        assert argumentos["cliente"] is interfaz._cliente
        assert argumentos["peso_actual"] == 72.5

        interfaz.mostrar_mensaje.assert_called_once_with(
            "Progreso mensual generado correctamente."
        )

        interfaz.cargarDatos.assert_called_once_with()

    def test_generar_progreso_mensual_sin_peso(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba validación cuando el cliente no tiene peso.
        """
        interfaz._cliente.peso = None

        interfaz.generarProgresoMensual()

        control_progreso.generar_progreso_mensual.assert_not_called()

        interfaz.mostrar_error.assert_called_once_with(
            "El cliente no tiene peso registrado."
        )

    def test_generar_progreso_mensual_ya_existente(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba mensaje cuando el progreso mensual ya existe.
        """
        control_progreso.generar_progreso_mensual.side_effect = (
            ValueError("Ya existe un registro de progreso")
        )

        interfaz.generarProgresoMensual()

        interfaz.mostrar_mensaje.assert_called_once()

        assert (
            "ya fue generado"
            in interfaz.mostrar_mensaje.call_args.args[0]
        )

    def test_generar_progreso_mensual_error_validacion(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba error de validación diferente al progreso duplicado.
        """
        control_progreso.generar_progreso_mensual.side_effect = (
            ValueError("Peso inválido")
        )

        interfaz.generarProgresoMensual()

        interfaz.mostrar_error.assert_called_once_with(
            "Peso inválido"
        )

    def test_registrar_peso_mensual_exitoso(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba registro correcto de peso mensual.
        """
        interfaz._ent_nuevo_peso.valor = "68.5"

        interfaz.registrarPesoMensual()

        control_progreso.generar_progreso_mensual.assert_called_once()

        argumentos = (
            control_progreso.generar_progreso_mensual.call_args
            .kwargs
        )

        assert argumentos["peso_actual"] == 68.5

        interfaz._cliente.actualizar_peso.assert_called_once_with(
            68.5
        )

        interfaz.mostrar_mensaje.assert_called_once_with(
            "Peso mensual registrado correctamente."
        )

        interfaz.cargarDatos.assert_called_once_with()

    @pytest.mark.parametrize(
        "valor,mensaje",
        [
            ("", "Ingrese el nuevo peso."),
            ("texto", "El peso debe ser un número válido."),
            ("0", "El peso debe ser mayor que cero."),
            ("-10", "El peso debe ser mayor que cero."),
        ],
    )
    def test_registrar_peso_mensual_rechaza_valor_invalido(
        self,
        interfaz,
        control_progreso,
        valor,
        mensaje,
    ):
        """
        Prueba validaciones de peso mensual.
        """
        interfaz._ent_nuevo_peso.valor = valor

        interfaz.registrarPesoMensual()

        control_progreso.generar_progreso_mensual.assert_not_called()

        interfaz.mostrar_error.assert_called_once_with(
            mensaje
        )

    def test_generar_reporte_pdf_exitoso(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba generación y apertura automática del PDF.
        """
        control_progreso.calcular_resumen_cliente.return_value = {
            "total_sesiones": 5,
            "total_minutos": 180,
            "total_calorias": 1100,
        }

        control_progreso.consultar_progreso.return_value = []

        generador_pdf = MagicMock()
        generador_pdf.generar_reporte_progreso_cliente.return_value = (
            "reportes/reporte_prueba.pdf"
        )

        with patch(
            "src.interfaz.interfaz_progreso.GeneradorReportesPDF",
            return_value=generador_pdf,
        ), patch(
            "src.interfaz.interfaz_progreso.os.startfile",
        ) as mock_abrir_archivo:
            interfaz.generarReportePDF()

        generador_pdf.generar_reporte_progreso_cliente.assert_called_once()

        mock_abrir_archivo.assert_called_once_with(
            "reportes/reporte_prueba.pdf"
        )

        interfaz.mostrar_mensaje.assert_called_once()

        mensaje = interfaz.mostrar_mensaje.call_args.args[0]

        assert "Reporte PDF generado correctamente" in mensaje
        assert "reporte_prueba.pdf" in mensaje

    def test_generar_reporte_pdf_maneja_error(
        self,
        interfaz,
        control_progreso,
    ):
        """
        Prueba manejo de error durante generación del PDF.
        """
        control_progreso.calcular_resumen_cliente.side_effect = (
            RuntimeError("Error de base de datos")
        )

        with patch(
            "src.interfaz.interfaz_progreso.traceback.print_exc",
        ):
            interfaz.generarReportePDF()

        interfaz.mostrar_error.assert_called_once()

        mensaje = interfaz.mostrar_error.call_args.args[0]

        assert "No se pudo generar el reporte PDF" in mensaje
        assert "RuntimeError" in mensaje

    def test_evaluar_meta_sesiones_alcanzada(
        self,
        interfaz,
    ):
        """
        Prueba una meta alcanzada por cantidad de sesiones.
        """
        interfaz._cliente.objetivo = "Mejorar resistencia"

        interfaz._evaluar_meta(
            {
                "total_sesiones": 12,
            }
        )

        interfaz._lbl_meta.config.assert_called_once_with(
            text="META ALCANZADA! Sigue asi!",
            foreground="green",
        )

    def test_evaluar_meta_sesiones_no_alcanzada(
        self,
        interfaz,
    ):
        """
        Prueba una meta no alcanzada por cantidad de sesiones.
        """
        interfaz._cliente.objetivo = "Mejorar resistencia"

        interfaz._evaluar_meta(
            {
                "total_sesiones": 5,
            }
        )

        interfaz._lbl_meta.config.assert_called_once_with(
            text="Progreso: 5/12 sesiones",
            foreground="red",
        )

    def test_evaluar_meta_bajar_peso_alcanzada(
        self,
        interfaz,
    ):
        """
        Prueba meta alcanzada de reducción de peso.
        """
        interfaz._cliente.objetivo = "Bajar de peso"
        interfaz._cliente.peso = 70

        interfaz._evaluar_meta(
            {
                "total_sesiones": 2,
            }
        )

        interfaz._lbl_meta.config.assert_called_once_with(
            text="META ALCANZADA! Peso: 70.0 kg",
            foreground="green",
        )

    def test_evaluar_meta_bajar_peso_no_alcanzada(
        self,
        interfaz,
    ):
        """
        Prueba meta no alcanzada de reducción de peso.
        """
        interfaz._cliente.objetivo = "Perder peso"
        interfaz._cliente.peso = 80
        interfaz._cliente.peso_objetivo = 75

        interfaz._evaluar_meta(
            {
                "total_sesiones": 2,
            }
        )

        interfaz._lbl_meta.config.assert_called_once_with(
            text=(
                "Meta no alcanzada. Peso: 80.0 kg "
                "(Meta: 75 kg)"
            ),
            foreground="red",
        )