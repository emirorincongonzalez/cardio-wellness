from datetime import date
import tkinter as tk
from tkinter import ttk

from src.controladores.control_sesiones import (
    ControlSesiones,
)
from src.interfaz.interfaz_base import InterfazBase


class InterfazRegistroSesion(InterfazBase):
    """
    Pestaña para registrar una sesión diaria.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_sesiones: ControlSesiones,
        id_cliente: int,
        id_rutina: int,
    ) -> None:
        super().__init__(
            master,
            controlador=control_sesiones,
            padding=10,
        )

        self.pack(
            fill="both",
            expand=True,
        )

        self._id_cliente = id_cliente
        self._id_rutina = id_rutina

        self.mostrarFormularioSesion()

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    @property
    def id_rutina(self) -> int:
        return self._id_rutina

    def mostrarFormularioSesion(self) -> None:
        """
        Construye el formulario de registro.
        """
        form = ttk.LabelFrame(
            self,
            text="Detalle del entrenamiento",
            padding=15,
        )

        form.pack(
            fill="x",
            pady=10,
        )

        ttk.Label(
            form,
            text=(
                f"Rutina asignada: "
                f"{self._id_rutina}"
            ),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 12),
            padx=5,
        )

        ttk.Label(
            form,
            text="Nombre del ejercicio:",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._ent_nombre_ejercicio = ttk.Entry(
            form,
            width=25,
        )

        self._ent_nombre_ejercicio.grid(
            row=1,
            column=1,
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text="Duración real (min):",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._ent_duracion = ttk.Entry(
            form,
            width=25,
        )

        self._ent_duracion.grid(
            row=2,
            column=1,
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text="Intensidad real:",
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._cb_intensidad = ttk.Combobox(
            form,
            values=(
                "BAJA",
                "MEDIA",
                "ALTA",
            ),
            state="readonly",
            width=22,
        )

        self._cb_intensidad.grid(
            row=3,
            column=1,
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text="Calorías quemadas:",
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._ent_calorias = ttk.Entry(
            form,
            width=25,
        )

        self._ent_calorias.grid(
            row=4,
            column=1,
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text="Veces planificadas:",
        ).grid(
            row=5,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._ent_veces_planificadas = (
            ttk.Entry(
                form,
                width=25,
            )
        )

        self._ent_veces_planificadas.grid(
            row=5,
            column=1,
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text="Veces realizadas:",
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._ent_veces_realizadas = ttk.Entry(
            form,
            width=25,
        )

        self._ent_veces_realizadas.grid(
            row=6,
            column=1,
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text=(
                "La sesión se completará automáticamente "
                "si las veces realizadas alcanzan "
                "las planificadas."
            ),
            foreground="#555555",
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="w",
            pady=8,
            padx=5,
        )

        ttk.Label(
            form,
            text="Observaciones:",
        ).grid(
            row=8,
            column=0,
            sticky="w",
            pady=8,
            padx=5,
        )

        self._ent_observaciones = ttk.Entry(
            form,
            width=25,
        )

        self._ent_observaciones.grid(
            row=8,
            column=1,
            pady=8,
            padx=5,
        )

        frame_botones = ttk.Frame(form)

        frame_botones.grid(
            row=9,
            column=1,
            sticky="e",
            pady=15,
        )

        ttk.Button(
            frame_botones,
            text="Guardar sesión",
            command=self.registrarSesion,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            frame_botones,
            text="Limpiar",
            command=self.cancelarRegistro,
        ).pack(
            side="left",
            padx=5,
        )

    def registrarSesion(self) -> None:
        """
        Valida y registra la sesión.
        """
        nombre_ejercicio = (
            self._ent_nombre_ejercicio
            .get()
            .strip()
        )

        duracion_texto = (
            self._ent_duracion
            .get()
            .strip()
        )

        intensidad = (
            self._cb_intensidad
            .get()
            .strip()
        )

        calorias_texto = (
            self._ent_calorias
            .get()
            .strip()
        )

        planificadas_texto = (
            self._ent_veces_planificadas
            .get()
            .strip()
        )

        realizadas_texto = (
            self._ent_veces_realizadas
            .get()
            .strip()
        )

        observaciones = (
            self._ent_observaciones
            .get()
            .strip()
        )

        if not nombre_ejercicio:
            self.mostrar_error(
                "El nombre del ejercicio "
                "es obligatorio."
            )
            return

        if len(nombre_ejercicio) > 100:
            self.mostrar_error(
                (
                    "El nombre del ejercicio no puede "
                    "superar 100 caracteres."
                )
            )
            return

        if (
            not duracion_texto
            or not intensidad
            or not calorias_texto
            or not planificadas_texto
            or not realizadas_texto
        ):
            self.mostrar_error(
                (
                    "Complete duración, intensidad, "
                    "calorías, veces planificadas "
                    "y veces realizadas."
                )
            )
            return

        try:
            duracion = int(
                duracion_texto
            )

            calorias = float(
                calorias_texto
            )

            veces_planificadas = int(
                planificadas_texto
            )

            veces_realizadas = int(
                realizadas_texto
            )

        except ValueError:
            self.mostrar_error(
                (
                    "Duración, veces planificadas "
                    "y veces realizadas deben ser "
                    "enteros. Calorías debe ser numérica."
                )
            )
            return

        if duracion <= 0:
            self.mostrar_error(
                "La duración debe ser mayor que cero."
            )
            return

        if calorias < 0:
            self.mostrar_error(
                "Las calorías no pueden ser negativas."
            )
            return

        if veces_planificadas <= 0:
            self.mostrar_error(
                (
                    "Las veces planificadas deben "
                    "ser mayores que cero."
                )
            )
            return

        if veces_realizadas < 0:
            self.mostrar_error(
                (
                    "Las veces realizadas no pueden "
                    "ser negativas."
                )
            )
            return

        if (
            veces_realizadas
            > veces_planificadas
        ):
            self.mostrar_error(
                (
                    "Las veces realizadas no pueden "
                    "superar las planificadas."
                )
            )
            return

        try:
            sesion = (
                self.controlador
                .registrar_sesion(
                    cliente=self._id_cliente,
                    rutina=self._id_rutina,
                    fecha=date.today(),
                    nombre_ejercicio=(
                        nombre_ejercicio
                    ),
                    duracion_real=duracion,
                    intensidad_real=intensidad,
                    calorias_quemadas=calorias,
                    observaciones=(
                        observaciones
                    ),
                    veces_planificadas=(
                        veces_planificadas
                    ),
                    veces_realizadas=(
                        veces_realizadas
                    ),
                )
            )

            estado = (
                "completada"
                if sesion.completada
                else "pendiente"
            )

            self.mostrar_mensaje(
                (
                    "Sesión registrada correctamente.\n"
                    f"Estado: {estado}\n"
                    f"Cumplimiento: "
                    f"{sesion.veces_realizadas}/"
                    f"{sesion.veces_planificadas}"
                )
            )

            self.cancelarRegistro()

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                f"Error inesperado: {error}"
            )

    def cancelarRegistro(self) -> None:
        """
        Limpia el formulario.
        """
        self._ent_nombre_ejercicio.delete(
            0,
            tk.END,
        )

        self._ent_duracion.delete(
            0,
            tk.END,
        )

        self._cb_intensidad.set("")

        self._ent_calorias.delete(
            0,
            tk.END,
        )

        self._ent_veces_planificadas.delete(
            0,
            tk.END,
        )

        self._ent_veces_realizadas.delete(
            0,
            tk.END,
        )

        self._ent_observaciones.delete(
            0,
            tk.END,
        )