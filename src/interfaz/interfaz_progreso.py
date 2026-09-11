from typing import List
import tkinter as tk
from tkinter import ttk

from src.controladores.control_progreso import ControlProgreso
from src.modelos.cliente import Cliente
from src.modelos.progreso_mensual import ProgresoMensual
from src.interfaz.interfaz_base import InterfazBase


class InterfazProgreso(InterfazBase):
    """
    Pestania de progreso del cliente (incluye parámetro META con colores).

    Atributos (segun DCD):
        -cliente : Cliente -> Cliente logueado.

    Métodos (segun DCD):
        +mostrarProgresoMensual(): void  -> Muestra el progreso del mes.
        +mostrarHistorial(): void        -> Muestra el historial completo.
        +mostrarResumen(): void          -> Muestra el resumen de actividad.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_progreso: ControlProgreso,
        cliente: Cliente,
    ) -> None:
        super().__init__(master, controlador=control_progreso, padding=10)
        self.pack(fill="both", expand=True)

        self._cliente: Cliente = cliente

        self.mostrarResumen()
        self.mostrarProgresoMensual()

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    # ==========================================================
    # METODOS DEL DCD
    # ==========================================================
    def mostrarResumen(self) -> None:
        """Muestra el resumen de actividad del cliente."""
        frame_resumen = ttk.LabelFrame(self, text="Resumen de Actividad", padding=10)
        frame_resumen.pack(fill="x", pady=5)

        self._lbl_sesiones = ttk.Label(frame_resumen, text="Sesiones: -")
        self._lbl_sesiones.grid(row=0, column=0, padx=10, pady=5)

        self._lbl_minutos = ttk.Label(frame_resumen, text="Minutos: -")
        self._lbl_minutos.grid(row=0, column=1, padx=10, pady=5)

        self._lbl_calorias = ttk.Label(frame_resumen, text="Calorias: -")
        self._lbl_calorias.grid(row=0, column=2, padx=10, pady=5)

        # Parametro META
        frame_meta = ttk.LabelFrame(self, text="Mi Meta (Objetivo)", padding=10)
        frame_meta.pack(fill="x", pady=10)

        self._lbl_meta = ttk.Label(frame_meta, text="Calculando...", font=("Helvetica", 12, "bold"))
        self._lbl_meta.pack(pady=10)

        try:
            resumen = self.controlador.calcular_resumen_cliente(self._cliente.id_usuario)
            self._lbl_sesiones.config(text=f"Sesiones: {resumen['total_sesiones']}")
            self._lbl_minutos.config(text=f"Minutos: {resumen['total_minutos']}")
            self._lbl_calorias.config(text=f"Calorias: {resumen['total_calorias']}")
            self._evaluar_meta(resumen)
        except Exception as e:
            self.mostrar_error(f"Error al cargar resumen: {e}")

    def mostrarProgresoMensual(self) -> None:
        """Muestra la tabla con el historial de progreso mensual."""
        cols = ("Mes", "Peso", "Sesiones Completadas", "Sesiones Planificadas", "Cumplimiento")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=130)
        self._tree.pack(fill="both", expand=True, pady=10)

        try:
            historial: List[ProgresoMensual] = self.controlador.consultar_progreso(self._cliente.id_usuario)
            for p in historial:
                self._tree.insert("", "end", values=(
                    p.mes.strftime("%B %Y"),
                    f"{p.peso} kg",
                    p.sesiones_completadas,
                    p.sesiones_planificadas,
                    f"{p.porcentaje_cumplimiento}%",
                ))
        except Exception as e:
            self.mostrar_error(f"Error al cargar historial: {e}")

    def mostrarHistorial(self) -> None:
        """Alias de mostrarProgresoMensual."""
        self.mostrarProgresoMensual()

    # ==========================================================
    # METODO AUXILIAR
    # ==========================================================
    def _evaluar_meta(self, resumen: dict) -> None:
        """Evalua si el cliente alcanzo su meta y muestra el resultado con colores."""
        objetivo = (self._cliente.objetivo or "").lower()

        if "bajar" in objetivo or "perder" in objetivo:
            peso_actual = float(self._cliente.peso)
            if peso_actual <= 75:
                self._lbl_meta.config(
                    text=f"META ALCANZADA! Peso: {peso_actual} kg",
                    foreground="green",
                )
            else:
                self._lbl_meta.config(
                    text=f"Meta no alcanzada. Peso: {peso_actual} kg (Meta: 75 kg)",
                    foreground="red",
                )
        else:
            if resumen["total_sesiones"] >= 12:
                self._lbl_meta.config(text="META ALCANZADA! Sigue asi!", foreground="green")
            else:
                self._lbl_meta.config(
                    text=f"Progreso: {resumen['total_sesiones']}/12 sesiones",
                    foreground="red",
                )
