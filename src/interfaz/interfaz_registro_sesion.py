from datetime import date
import tkinter as tk
from tkinter import ttk

from src.controladores.control_sesiones import ControlSesiones
from src.interfaz.interfaz_base import InterfazBase


class InterfazRegistroSesion(InterfazBase):
    """
    Pestania para registrar una nueva sesion de entrenamiento.

    Atributos (segun DCD):
        -idCliente : int -> ID del cliente que registra la sesion.

    Metodos (segun DCD):
        +mostrarFormularioSesion(): void  -> Construye el formulario.
        +registrarSesion(): void          -> Registra la sesion.
        +cancelarRegistro(): void         -> Limpia el formulario.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_sesiones: ControlSesiones,
        id_cliente: int,
    ) -> None:
        super().__init__(master, controlador=control_sesiones, padding=10)
        self.pack(fill="both", expand=True)

        self._id_cliente: int = id_cliente
        self.mostrarFormularioSesion()

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    def mostrarFormularioSesion(self) -> None:
        form = ttk.LabelFrame(self, text="Detalle del Entrenamiento", padding=15)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Duracion Real (min):").grid(row=0, column=0, sticky="w", pady=8, padx=5)
        self._ent_duracion = ttk.Entry(form, width=25)
        self._ent_duracion.grid(row=0, column=1, pady=8, padx=5)

        ttk.Label(form, text="Intensidad Real:").grid(row=1, column=0, sticky="w", pady=8, padx=5)
        self._cb_intensidad = ttk.Combobox(form, values=["BAJA", "MEDIA", "ALTA"], state="readonly", width=22)
        self._cb_intensidad.grid(row=1, column=1, pady=8, padx=5)

        ttk.Label(form, text="Calorias Quemadas:").grid(row=2, column=0, sticky="w", pady=8, padx=5)
        self._ent_calorias = ttk.Entry(form, width=25)
        self._ent_calorias.grid(row=2, column=1, pady=8, padx=5)

        ttk.Label(form, text="Observaciones:").grid(row=3, column=0, sticky="w", pady=8, padx=5)
        self._ent_observaciones = ttk.Entry(form, width=25)
        self._ent_observaciones.grid(row=3, column=1, pady=8, padx=5)

        frame_btns = ttk.Frame(form)
        frame_btns.grid(row=4, column=1, sticky="e", pady=15)

        ttk.Button(frame_btns, text="Guardar Sesion", command=self.registrarSesion).pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Cancelar", command=self.cancelarRegistro).pack(side="left", padx=5)

    def registrarSesion(self) -> None:
        duracion_str = self._ent_duracion.get().strip()
        intensidad = self._cb_intensidad.get().strip()
        calorias_str = self._ent_calorias.get().strip()
        observaciones = self._ent_observaciones.get().strip()

        if not duracion_str or not intensidad or not calorias_str:
            self.mostrar_error("Los campos Duracion, Intensidad y Calorias son obligatorios.")
            return

        try:
            duracion = int(duracion_str)
            calorias = float(calorias_str)
        except ValueError:
            self.mostrar_error("Duracion debe ser entero y Calorias decimal.")
            return

        try:
            self.controlador.registrar_sesion(
                id_cliente=self._id_cliente,
                duracion_real=duracion,
                intensidad_real=intensidad,
                calorias_quemadas=calorias,
                observaciones=observaciones,
                fecha=date.today(),
            )
            self.mostrar_mensaje("Sesion registrada exitosamente.")
            self.cancelarRegistro()
        except ValueError as e:
            self.mostrar_error(str(e))
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {e}")

    def cancelarRegistro(self) -> None:
        self._ent_duracion.delete(0, tk.END)
        self._cb_intensidad.set("")
        self._ent_calorias.delete(0, tk.END)
        self._ent_observaciones.delete(0, tk.END)
