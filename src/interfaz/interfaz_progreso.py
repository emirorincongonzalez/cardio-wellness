from datetime import date, datetime
from typing import Any, Optional
import traceback

import tkinter as tk
from tkinter import ttk

from src.controladores.control_progreso import (
    ControlProgreso,
)
from src.interfaz.interfaz_base import InterfazBase
from src.modelos.cliente import Cliente
from src.modelos.enums import Intensidad


class InterfazProgreso(InterfazBase):
    """
    Pestaña de progreso del cliente.

    Muestra:

    - Resumen de actividad.
    - Estado de la meta.
    - Sesiones registradas.
    - Historial mensual.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_progreso: ControlProgreso,
        cliente: Cliente,
    ) -> None:
        super().__init__(
            master,
            controlador=control_progreso,
            padding=10,
        )

        self.pack(
            fill="both",
            expand=True,
        )

        self._cliente = cliente

        self._crear_interfaz()
        self.cargarDatos()

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    def _crear_interfaz(self) -> None:
        self._crear_barra_acciones()
        self._crear_resumen()
        self._crear_sesiones()
        self._crear_historial()

    def _crear_barra_acciones(self) -> None:
        frame = ttk.Frame(self)

        frame.pack(
            fill="x",
            pady=(0, 8),
        )

        ttk.Button(
            frame,
            text="Actualizar",
            command=self.cargarDatos,
        ).pack(
            side="right",
            padx=5,
        )

        ttk.Button(
            frame,
            text="Generar Progreso Mensual",
            command=self.generarProgresoMensual,
        ).pack(
            side="right",
            padx=5,
        )

    def _crear_resumen(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Resumen de Actividad",
            padding=10,
        )

        frame.pack(
            fill="x",
            pady=5,
        )

        self._lbl_sesiones = ttk.Label(
            frame,
            text="Sesiones: -",
        )

        self._lbl_sesiones.grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
        )

        self._lbl_minutos = ttk.Label(
            frame,
            text="Minutos: -",
        )

        self._lbl_minutos.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
        )

        self._lbl_calorias = ttk.Label(
            frame,
            text="Calorias: -",
        )

        self._lbl_calorias.grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
        )

        frame_meta = ttk.LabelFrame(
            self,
            text="Mi Meta (Objetivo)",
            padding=10,
        )

        frame_meta.pack(
            fill="x",
            pady=8,
        )

        self._lbl_meta = ttk.Label(
            frame_meta,
            text="Calculando...",
            font=("Helvetica", 12, "bold"),
        )

        self._lbl_meta.pack(
            pady=8,
        )

    def _crear_sesiones(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Sesiones Registradas",
            padding=8,
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=5,
        )

        columnas = (
            "Fecha",
            "Ejercicio",
            "Duracion",
            "Intensidad",
            "Calorias",
            "Observaciones",
        )

        self._tree_sesiones = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            height=7,
        )

        anchos = {
            "Fecha": 110,
            "Ejercicio": 180,
            "Duracion": 100,
            "Intensidad": 110,
            "Calorias": 110,
            "Observaciones": 260,
        }

        for columna in columnas:
            self._tree_sesiones.heading(
                columna,
                text=columna,
            )

            self._tree_sesiones.column(
                columna,
                width=anchos[columna],
                minwidth=80,
                anchor="center",
            )

        scrollbar_y = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self._tree_sesiones.yview,
        )

        scrollbar_x = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self._tree_sesiones.xview,
        )

        self._tree_sesiones.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        self._tree_sesiones.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scrollbar_y.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        scrollbar_x.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        frame.rowconfigure(
            0,
            weight=1,
        )

        frame.columnconfigure(
            0,
            weight=1,
        )

    def _crear_historial(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Historial de Progreso Mensual",
            padding=8,
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=(5, 10),
        )

        columnas = (
            "Mes",
            "Peso",
            "Sesiones Completadas",
            "Sesiones Planificadas",
            "Cumplimiento",
        )

        self._tree_progreso = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            height=7,
        )

        anchos = {
            "Mes": 120,
            "Peso": 100,
            "Sesiones Completadas": 170,
            "Sesiones Planificadas": 170,
            "Cumplimiento": 130,
        }

        for columna in columnas:
            self._tree_progreso.heading(
                columna,
                text=columna,
            )

            self._tree_progreso.column(
                columna,
                width=anchos[columna],
                minwidth=100,
                anchor="center",
            )

        scrollbar_y = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self._tree_progreso.yview,
        )

        scrollbar_x = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self._tree_progreso.xview,
        )

        self._tree_progreso.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        self._tree_progreso.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scrollbar_y.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        scrollbar_x.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        frame.rowconfigure(
            0,
            weight=1,
        )

        frame.columnconfigure(
            0,
            weight=1,
        )

    def cargarDatos(self) -> None:
        """
        Recarga todos los datos de la pestaña.
        """
        self._limpiar_tablas()

        resumen = self._cargar_resumen()

        self._cargar_sesiones()
        self._cargar_historial_progreso()

        if resumen is not None:
            self._evaluar_meta(resumen)

    def _limpiar_tablas(self) -> None:
        for item in self._tree_sesiones.get_children():
            self._tree_sesiones.delete(item)

        for item in self._tree_progreso.get_children():
            self._tree_progreso.delete(item)

    def _cargar_resumen(self) -> Optional[dict]:
        """
        Carga únicamente el resumen.
        """
        try:
            resumen = (
                self.controlador.calcular_resumen_cliente(
                    self._obtener_id_cliente()
                )
            )

            resumen = resumen or {}

            self._lbl_sesiones.config(
                text=(
                    "Sesiones: "
                    f"{resumen.get('total_sesiones', 0)}"
                )
            )

            self._lbl_minutos.config(
                text=(
                    "Minutos: "
                    f"{resumen.get('total_minutos', 0)}"
                )
            )

            self._lbl_calorias.config(
                text=(
                    "Calorias: "
                    f"{resumen.get('total_calorias', 0)}"
                )
            )

            return resumen

        except Exception as error:
            traceback.print_exc()

            self._lbl_sesiones.config(
                text="Sesiones: 0",
            )

            self._lbl_minutos.config(
                text="Minutos: 0",
            )

            self._lbl_calorias.config(
                text="Calorias: 0",
            )

            self._lbl_meta.config(
                text=(
                    "No se pudo cargar el resumen: "
                    f"{type(error).__name__}"
                ),
                foreground="red",
            )

            return None

    def _cargar_sesiones(self) -> None:
        """
        Carga las sesiones del cliente.
        """
        try:
            id_cliente = self._obtener_id_cliente()

            sesiones = (
                self.controlador.obtener_sesiones_cliente(
                    id_cliente
                )
            )

            sesiones = sesiones or []

            if not sesiones:
                self._insertar_mensaje_sesiones(
                    "Todavia no hay sesiones registradas."
                )
                return

            for sesion in sesiones:
                fecha = self._valor_sesion(
                    sesion,
                    "fecha",
                    default="",
                )

                nombre_ejercicio = self._valor_sesion(
                    sesion,
                    "nombre_ejercicio",
                    default="Sin ejercicio",
                )

                duracion = self._valor_sesion(
                    sesion,
                    "duracion_real",
                    default=0,
                )

                intensidad = self._valor_sesion(
                    sesion,
                    "intensidad_real",
                    default="",
                )

                calorias = self._valor_sesion(
                    sesion,
                    "calorias_quemadas",
                    default=0,
                )

                observaciones = self._valor_sesion(
                    sesion,
                    "observaciones",
                    default="",
                )

                self._tree_sesiones.insert(
                    "",
                    "end",
                    values=(
                        self._formatear_fecha(fecha),
                        str(
                            nombre_ejercicio
                            or "Sin ejercicio"
                        ),
                        f"{duracion} min",
                        self._formatear_intensidad(
                            intensidad
                        ),
                        f"{calorias} kcal",
                        str(observaciones or ""),
                    ),
                )

        except Exception as error:
            traceback.print_exc()

            self._insertar_mensaje_sesiones(
                "Error al cargar sesiones: "
                f"{type(error).__name__}: {error}"
            )

    def _cargar_historial_progreso(self) -> None:
        """
        Carga el historial de progreso mensual.
        """
        try:
            historial = (
                self.controlador.consultar_progreso(
                    self._obtener_id_cliente()
                )
            )

            historial = historial or []

            if not historial:
                self._insertar_mensaje_progreso(
                    "Todavia no hay registros mensuales."
                )
                return

            for progreso in historial:
                mes = self._valor_sesion(
                    progreso,
                    "mes",
                    default="",
                )

                peso = self._valor_sesion(
                    progreso,
                    "peso",
                    default=0,
                )

                completadas = self._valor_sesion(
                    progreso,
                    "sesiones_completadas",
                    default=0,
                )

                planificadas = self._valor_sesion(
                    progreso,
                    "sesiones_planificadas",
                    default=12,
                )

                cumplimiento = self._valor_sesion(
                    progreso,
                    "porcentaje_cumplimiento",
                    default=None,
                )

                if cumplimiento is None:
                    cumplimiento = (
                        self._calcular_cumplimiento(
                            completadas,
                            planificadas,
                        )
                    )

                self._tree_progreso.insert(
                    "",
                    "end",
                    values=(
                        self._formatear_mes(mes),
                        f"{peso} kg",
                        completadas,
                        planificadas,
                        f"{cumplimiento}%",
                    ),
                )

        except Exception as error:
            traceback.print_exc()

            self._insertar_mensaje_progreso(
                "Error al cargar historial: "
                f"{type(error).__name__}: {error}"
            )

    def generarProgresoMensual(self) -> None:
        """
        Genera o actualiza el progreso mensual.
        """
        peso = self._valor_sesion(
            self._cliente,
            "peso",
            default=None,
        )

        if peso is None:
            self.mostrar_error(
                "El cliente no tiene peso registrado."
            )
            return

        try:
            self.controlador.generar_progreso_mensual(
                cliente=self._cliente,
                mes=date.today(),
                peso_actual=peso,
            )

            self.mostrar_mensaje(
                "Progreso mensual generado correctamente."
            )

            self.cargarDatos()

        except Exception as error:
            traceback.print_exc()

            self.mostrar_error(
                "No se pudo generar el progreso mensual: "
                f"{type(error).__name__}: {error}"
            )

    def mostrarResumen(self) -> None:
        self._cargar_resumen()

    def mostrarSesiones(self) -> None:
        self._cargar_sesiones()

    def mostrarProgresoMensual(self) -> None:
        self._cargar_historial_progreso()

    def mostrarHistorial(self) -> None:
        self._cargar_historial_progreso()

    def _evaluar_meta(
        self,
        resumen: dict,
    ) -> None:
        """
        Evalúa la meta del cliente.
        """
        objetivo = str(
            getattr(
                self._cliente,
                "objetivo",
                "",
            ) or ""
        ).lower()

        peso_actual = self._valor_sesion(
            self._cliente,
            "peso",
            default=None,
        )

        objetivo_peso = (
            "bajar" in objetivo
            or "perder" in objetivo
            or "adelgazar" in objetivo
            or "peso" in objetivo
        )

        if objetivo_peso:
            try:
                peso = float(peso_actual)
            except (
                TypeError,
                ValueError,
            ):
                peso = None

            if peso is not None and peso <= 75:
                self._lbl_meta.config(
                    text=(
                        "META ALCANZADA! "
                        f"Peso: {peso:g} kg"
                    ),
                    foreground="green",
                )
                return

            if peso is not None:
                self._lbl_meta.config(
                    text=(
                        "Meta no alcanzada. "
                        f"Peso: {peso:g} kg "
                        "(Meta: 75 kg)"
                    ),
                    foreground="red",
                )
                return

        sesiones = self._convertir_entero(
            resumen.get(
                "total_sesiones",
                0,
            )
        )

        if sesiones >= 12:
            self._lbl_meta.config(
                text="META ALCANZADA! Sigue asi!",
                foreground="green",
            )
        else:
            self._lbl_meta.config(
                text=(
                    f"Progreso: {sesiones}/12 "
                    "sesiones"
                ),
                foreground="red",
            )

    def _insertar_mensaje_sesiones(
        self,
        mensaje: str,
    ) -> None:
        self._tree_sesiones.insert(
            "",
            "end",
            values=(
                mensaje,
                "",
                "",
                "",
                "",
                "",
            ),
        )

    def _insertar_mensaje_progreso(
        self,
        mensaje: str,
    ) -> None:
        self._tree_progreso.insert(
            "",
            "end",
            values=(
                mensaje,
                "",
                "",
                "",
                "",
            ),
        )

    def _obtener_id_cliente(self) -> int:
        """
        Obtiene el identificador correcto del cliente.
        """
        id_cliente = getattr(
            self._cliente,
            "id_cliente",
            None,
        )

        if id_cliente is None:
            id_cliente = getattr(
                self._cliente,
                "id_usuario",
                None,
            )

        if id_cliente is None:
            raise ValueError(
                "El cliente no tiene un identificador válido."
            )

        try:
            id_cliente = int(id_cliente)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "El identificador del cliente no es válido."
            ) from error

        if id_cliente <= 0:
            raise ValueError(
                "El identificador del cliente debe ser positivo."
            )

        return id_cliente

    @staticmethod
    def _valor_sesion(
        objeto: Any,
        nombre: str,
        default: Any = None,
    ) -> Any:
        """
        Obtiene un atributo o una clave.
        """
        if isinstance(objeto, dict):
            return objeto.get(
                nombre,
                default,
            )

        try:
            return getattr(
                objeto,
                nombre,
            )
        except AttributeError:
            return default

    @staticmethod
    def _formatear_intensidad(
        valor: Any,
    ) -> str:
        """
        Convierte intensidad o texto a texto.
        """
        if isinstance(valor, Intensidad):
            return valor.value

        if valor is None:
            return ""

        return str(
            getattr(
                valor,
                "value",
                valor,
            )
        )

    @staticmethod
    def _formatear_fecha(
        valor: Any,
    ) -> str:
        """
        Formatea una fecha.
        """
        if valor is None:
            return ""

        if isinstance(valor, datetime):
            return valor.strftime("%Y-%m-%d")

        if isinstance(valor, date):
            return valor.strftime("%Y-%m-%d")

        return str(valor)

    @staticmethod
    def _formatear_mes(
        valor: Any,
    ) -> str:
        """
        Formatea el mes.
        """
        if valor is None:
            return ""

        if isinstance(valor, datetime):
            return valor.strftime("%B %Y")

        if isinstance(valor, date):
            return valor.strftime("%B %Y")

        return str(valor)

    @staticmethod
    def _convertir_entero(
        valor: Any,
    ) -> int:
        try:
            return int(valor)
        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _calcular_cumplimiento(
        completadas: Any,
        planificadas: Any,
    ) -> str:
        try:
            completadas_num = float(completadas)
            planificadas_num = float(planificadas)

            if planificadas_num <= 0:
                return "0.00"

            porcentaje = (
                completadas_num
                / planificadas_num
                * 100
            )

            return f"{min(porcentaje, 100):.2f}"

        except (
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            return "0.00"