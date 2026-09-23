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
        self._crear_actualizacion_peso()
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
            text="Generar progreso mensual",
            command=self.generarProgresoMensual,
        ).pack(
            side="right",
            padx=5,
        )

    def _crear_resumen(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Resumen de actividad",
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
            text="Calorías: -",
        )

        self._lbl_calorias.grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
        )

        self._lbl_planificadas = ttk.Label(
            frame,
            text="Veces planificadas: -",
        )

        self._lbl_planificadas.grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
        )

        self._lbl_realizadas = ttk.Label(
            frame,
            text="Veces realizadas: -",
        )

        self._lbl_realizadas.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
        )

        self._lbl_cumplimiento = ttk.Label(
            frame,
            text="Cumplimiento: -",
        )

        self._lbl_cumplimiento.grid(
            row=1,
            column=2,
            padx=10,
            pady=5,
        )

        frame_meta = ttk.LabelFrame(
            self,
            text="Mi meta de peso",
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
            pady=5,
        )

        self._lbl_peso_actual = ttk.Label(
            frame_meta,
            text="Peso actual: -",
        )

        self._lbl_peso_actual.pack(
            pady=2,
        )

        self._lbl_objetivo = ttk.Label(
            frame_meta,
            text="Objetivo: -",
        )

        self._lbl_objetivo.pack(
            pady=2,
        )

        self._lbl_peso_objetivo = ttk.Label(
            frame_meta,
            text="Peso objetivo: -",
        )

        self._lbl_peso_objetivo.pack(
            pady=2,
        )

        self._lbl_rango_meta = ttk.Label(
            frame_meta,
            text="",
        )

        self._lbl_rango_meta.pack(
            pady=2,
        )

        self._lbl_diferencia_meta = ttk.Label(
            frame_meta,
            text="Diferencia: -",
        )

        self._lbl_diferencia_meta.pack(
            pady=2,
        )

    def _crear_actualizacion_peso(self) -> None:
        """
        Crea el formulario para registrar el peso mensual.
        """
        frame = ttk.LabelFrame(
            self,
            text="Actualizar peso mensual",
            padding=10,
        )

        frame.pack(
            fill="x",
            pady=8,
        )

        ttk.Label(
            frame,
            text="Nuevo peso (kg):",
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="w",
        )

        self._ent_nuevo_peso = ttk.Entry(
            frame,
            width=15,
        )

        self._ent_nuevo_peso.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
        )

        ttk.Button(
            frame,
            text="Registrar peso",
            command=self.registrarPesoMensual,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
        )

        self._lbl_actualizacion_peso = ttk.Label(
            frame,
            text=(
                "El peso se guardará para el mes actual "
                "y no cambiará el peso objetivo."
            ),
            foreground="#555555",
        )

        self._lbl_actualizacion_peso.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=5,
            pady=5,
            sticky="w",
        )

    def _crear_sesiones(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Sesiones registradas",
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
            "Duración",
            "Intensidad",
            "Calorías",
            "Planificadas",
            "Realizadas",
            "Cumplimiento",
            "Estado",
            "Observaciones",
        )

        self._tree_sesiones = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            height=7,
        )

        anchos = {
            "Fecha": 100,
            "Ejercicio": 160,
            "Duración": 90,
            "Intensidad": 100,
            "Calorías": 100,
            "Planificadas": 100,
            "Realizadas": 100,
            "Cumplimiento": 110,
            "Estado": 110,
            "Observaciones": 240,
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
            text="Historial de progreso mensual",
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
            "Sesiones completadas",
            "Sesiones planificadas",
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
            "Sesiones completadas": 170,
            "Sesiones planificadas": 170,
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
        self._actualizar_datos_cliente()

        resumen = self._cargar_resumen()

        self._cargar_sesiones()
        self._cargar_historial_progreso()

        self._actualizar_meta()

        if resumen is not None:
            self._evaluar_meta(resumen)

    def _actualizar_datos_cliente(self) -> None:
        """
        Actualiza el objeto cliente si el controlador
        dispone de un método compatible.
        """
        try:
            metodo = getattr(
                self.controlador,
                "buscar_cliente",
                None,
            )

            if callable(metodo):
                cliente_actualizado = metodo(
                    self._obtener_id_cliente()
                )

                if isinstance(
                    cliente_actualizado,
                    Cliente,
                ):
                    self._cliente = (
                        cliente_actualizado
                    )

        except Exception:
            pass

    def _limpiar_tablas(self) -> None:
        for item in (
            self._tree_sesiones.get_children()
        ):
            self._tree_sesiones.delete(item)

        for item in (
            self._tree_progreso.get_children()
        ):
            self._tree_progreso.delete(item)

    def _actualizar_meta(self) -> None:
        """
        Actualiza visualmente el progreso de la meta.
        """
        cliente = self._cliente

        peso_actual = cliente.peso
        peso_objetivo = cliente.peso_objetivo
        objetivo = cliente.objetivo
        estado = cliente.obtener_estado_meta()
        diferencia = (
            cliente.obtener_diferencia_meta()
        )
        descripcion = (
            cliente.obtener_descripcion_meta()
        )

        self._lbl_peso_actual.config(
            text=(
                f"Peso actual: "
                f"{peso_actual:.1f} kg"
            )
        )

        self._lbl_objetivo.config(
            text=f"Objetivo: {objetivo}",
        )

        self._lbl_peso_objetivo.config(
            text=(
                f"Peso objetivo: "
                f"{peso_objetivo:.1f} kg"
            )
        )

        self._lbl_rango_meta.config(
            text=descripcion,
        )

        if estado == "META ALCANZADA":
            self._lbl_meta.config(
                text="META ALCANZADA",
                foreground="green",
            )

            self._lbl_diferencia_meta.config(
                text="Diferencia: 0 kg",
                foreground="green",
            )

        else:
            self._lbl_meta.config(
                text="EN PROGRESO",
                foreground="red",
            )

            self._lbl_diferencia_meta.config(
                text=(
                    "Diferencia restante: "
                    f"{diferencia:.1f} kg"
                ),
                foreground="red",
            )

    def registrarPesoMensual(self) -> None:
        """
        Registra el peso del cliente para el mes actual.
        """
        texto = (
            self._ent_nuevo_peso
            .get()
            .strip()
        )

        if not texto:
            self.mostrar_error(
                "Ingrese el nuevo peso."
            )
            return

        try:
            nuevo_peso = float(texto)

        except ValueError:
            self.mostrar_error(
                "El peso debe ser un número válido."
            )
            return

        if nuevo_peso <= 0:
            self.mostrar_error(
                "El peso debe ser mayor que cero."
            )
            return

        try:
            self.controlador.generar_progreso_mensual(
                cliente=self._cliente,
                mes=date.today(),
                peso_actual=nuevo_peso,
            )

            self._cliente.actualizar_peso(
                nuevo_peso
            )

            self._ent_nuevo_peso.delete(
                0,
                tk.END,
            )

            self.mostrar_mensaje(
                "Peso mensual registrado correctamente."
            )

            self.cargarDatos()

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            traceback.print_exc()

            self.mostrar_error(
                (
                    "No se pudo registrar el peso mensual: "
                    f"{type(error).__name__}: {error}"
                )
            )

    def _cargar_resumen(self) -> Optional[dict]:
        """
        Carga el resumen de actividad.
        """
        try:
            resumen = (
                self.controlador
                .calcular_resumen_cliente(
                    self._obtener_id_cliente()
                )
            )

            resumen = resumen or {}

            total_sesiones = resumen.get(
                "total_sesiones",
                0,
            )

            total_minutos = resumen.get(
                "total_minutos",
                0,
            )

            total_calorias = resumen.get(
                "total_calorias",
                0,
            )

            total_planificadas = (
                resumen.get(
                    "total_veces_planificadas",
                    resumen.get(
                        "veces_planificadas",
                        0,
                    ),
                )
            )

            total_realizadas = (
                resumen.get(
                    "total_veces_realizadas",
                    resumen.get(
                        "veces_realizadas",
                        0,
                    ),
                )
            )

            cumplimiento = (
                resumen.get(
                    "porcentaje_cumplimiento",
                    None,
                )
            )

            if cumplimiento is None:
                cumplimiento = (
                    self._calcular_cumplimiento(
                        total_planificadas,
                        total_realizadas,
                    )
                )

            self._lbl_sesiones.config(
                text=(
                    "Sesiones: "
                    f"{total_sesiones}"
                )
            )

            self._lbl_minutos.config(
                text=(
                    "Minutos: "
                    f"{total_minutos}"
                )
            )

            self._lbl_calorias.config(
                text=(
                    "Calorías: "
                    f"{total_calorias}"
                )
            )

            self._lbl_planificadas.config(
                text=(
                    "Veces planificadas: "
                    f"{total_planificadas}"
                )
            )

            self._lbl_realizadas.config(
                text=(
                    "Veces realizadas: "
                    f"{total_realizadas}"
                )
            )

            self._lbl_cumplimiento.config(
                text=(
                    "Cumplimiento: "
                    f"{self._formatear_porcentaje(cumplimiento)}"
                )
            )

            return resumen

        except Exception:
            traceback.print_exc()

            self._lbl_sesiones.config(
                text="Sesiones: 0",
            )

            self._lbl_minutos.config(
                text="Minutos: 0",
            )

            self._lbl_calorias.config(
                text="Calorías: 0",
            )

            self._lbl_planificadas.config(
                text="Veces planificadas: 0",
            )

            self._lbl_realizadas.config(
                text="Veces realizadas: 0",
            )

            self._lbl_cumplimiento.config(
                text="Cumplimiento: 0.00%",
            )

            return {}

    def _cargar_sesiones(self) -> None:
        """
        Carga las sesiones y muestra sus cantidades.
        """
        try:
            sesiones = (
                self.controlador
                .obtener_sesiones_cliente(
                    self._obtener_id_cliente()
                )
            )

            sesiones = sesiones or []

            if not sesiones:
                self._insertar_mensaje_sesiones(
                    "Todavía no hay sesiones registradas."
                )
                return

            for sesion in sesiones:
                fecha = self._valor_sesion(
                    sesion,
                    "fecha",
                    default="",
                )

                nombre_ejercicio = (
                    self._valor_sesion(
                        sesion,
                        "nombre_ejercicio",
                        default="Sin ejercicio",
                    )
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

                planificadas = self._valor_sesion(
                    sesion,
                    "veces_planificadas",
                    default=1,
                )

                realizadas = self._valor_sesion(
                    sesion,
                    "veces_realizadas",
                    default=0,
                )

                porcentaje = (
                    self._obtener_porcentaje_sesion(
                        sesion,
                        planificadas,
                        realizadas,
                    )
                )

                estado = (
                    self._obtener_estado_sesion(
                        sesion,
                        planificadas,
                        realizadas,
                    )
                )

                observaciones = (
                    self._valor_sesion(
                        sesion,
                        "observaciones",
                        default="",
                    )
                )

                self._tree_sesiones.insert(
                    "",
                    "end",
                    values=(
                        self._formatear_fecha(
                            fecha
                        ),
                        str(
                            nombre_ejercicio
                            or "Sin ejercicio"
                        ),
                        f"{duracion} min",
                        self._formatear_intensidad(
                            intensidad
                        ),
                        f"{calorias} kcal",
                        planificadas,
                        realizadas,
                        f"{porcentaje:.2f}%",
                        estado,
                        str(
                            observaciones or ""
                        ),
                    ),
                )

        except Exception as error:
            traceback.print_exc()

            self._insertar_mensaje_sesiones(
                (
                    "Error al cargar sesiones: "
                    f"{type(error).__name__}: {error}"
                )
            )

    def _cargar_historial_progreso(self) -> None:
        """
        Carga el historial mensual.
        """
        try:
            historial = (
                self.controlador
                .consultar_progreso(
                    self._obtener_id_cliente()
                )
            )

            historial = historial or []

            if not historial:
                self._insertar_mensaje_progreso(
                    "Todavía no hay registros mensuales."
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
                    default=0,
                )

                cumplimiento = self._valor_sesion(
                    progreso,
                    "porcentaje_cumplimiento",
                    default=None,
                )

                if cumplimiento is None:
                    cumplimiento = (
                        self._calcular_cumplimiento(
                            planificadas,
                            completadas,
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
                        (
                            f"{self._formatear_porcentaje(
                                cumplimiento
                            )}"
                        ),
                    ),
                )

        except Exception as error:
            traceback.print_exc()

            self._insertar_mensaje_progreso(
                (
                    "Error al cargar historial: "
                    f"{type(error).__name__}: {error}"
                )
            )

    def generarProgresoMensual(self) -> None:
        """
        Genera el progreso mensual.
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
                (
                    "No se pudo generar el progreso mensual: "
                    f"{type(error).__name__}: {error}"
                )
            )

    def mostrarResumen(self) -> None:
        self._cargar_resumen()
        self._actualizar_meta()

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
        self._actualizar_meta()

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
        Obtiene el identificador del cliente.
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
                (
                    "El identificador del cliente "
                    "debe ser positivo."
                )
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

        return getattr(
            objeto,
            nombre,
            default,
        )

    @staticmethod
    def _formatear_intensidad(
        valor: Any,
    ) -> str:
        """
        Convierte intensidad a texto.
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
    def _obtener_porcentaje_sesion(
        sesion: Any,
        planificadas: Any,
        realizadas: Any,
    ) -> float:
        """
        Obtiene el porcentaje de una sesión.
        """
        porcentaje = getattr(
            sesion,
            "porcentaje_cumplimiento",
            None,
        )

        if callable(porcentaje):
            try:
                return float(porcentaje())
            except Exception:
                pass

        if porcentaje is not None:
            try:
                return float(porcentaje)
            except (
                TypeError,
                ValueError,
            ):
                pass

        return InterfazProgreso._calcular_porcentaje(
            planificadas,
            realizadas,
        )

    @staticmethod
    def _obtener_estado_sesion(
        sesion: Any,
        planificadas: Any,
        realizadas: Any,
    ) -> str:
        """
        Obtiene el estado calculado.
        """
        metodo = getattr(
            sesion,
            "obtener_estado_cumplimiento",
            None,
        )

        if callable(metodo):
            try:
                return str(metodo())
            except Exception:
                pass

        try:
            planificadas_num = int(
                planificadas
            )

            realizadas_num = int(
                realizadas
            )

            if (
                realizadas_num
                >= planificadas_num
            ):
                return "COMPLETADA"

        except (
            TypeError,
            ValueError,
        ):
            pass

        return "PENDIENTE"

    @staticmethod
    def _calcular_porcentaje(
        planificadas: Any,
        realizadas: Any,
    ) -> float:
        try:
            planificadas_num = float(
                planificadas
            )

            realizadas_num = float(
                realizadas
            )

            if planificadas_num <= 0:
                return 0.0

            return min(
                realizadas_num
                / planificadas_num
                * 100,
                100.0,
            )

        except (
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            return 0.0

    @staticmethod
    def _calcular_cumplimiento(
        planificadas: Any,
        realizadas: Any,
    ) -> float:
        return InterfazProgreso._calcular_porcentaje(
            planificadas,
            realizadas,
        )

    @staticmethod
    def _formatear_porcentaje(
        valor: Any,
    ) -> str:
        try:
            return f"{float(valor):.2f}%"
        except (
            TypeError,
            ValueError,
        ):
            return "0.00%"