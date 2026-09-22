from typing import Optional

import tkinter as tk
from tkinter import ttk


from src.controladores.control_clientes import ControlClientes
from src.controladores.control_ejercicios import ControlEjercicios
from src.controladores.control_rutinas import ControlRutinas
from src.modelos.administrador import Administrador
from src.interfaz.interfaz_gestion_clientes import (
    InterfazGestionClientes,
)
from src.interfaz.interfaz_gestion_ejercicios import (
    InterfazGestionEjercicios,
)
from src.interfaz.interfaz_gestion_rutinas import (
    InterfazGestionRutinas,
)


class InterfazAdministrador(tk.Tk):
    """
    Ventana principal del administrador del sistema
    Cardio-Wellness.
    """

    def __init__(
        self,
        administrador_actual: Administrador,
        control_clientes: Optional[ControlClientes] = None,
        control_rutinas: Optional[ControlRutinas] = None,
        control_ejercicios: Optional[ControlEjercicios] = None,
        control_autenticacion: Optional[object] = None,
        controladores: Optional[dict] = None,
    ) -> None:
        """
        Inicializa la ventana del administrador.

        Los controladores deben ser creados en main.py e
        inyectados a esta interfaz.
        """
        super().__init__()

        if controladores is not None:
            control_clientes = controladores.get(
                "control_clientes",
                control_clientes,
            )

            control_rutinas = controladores.get(
                "control_rutinas",
                control_rutinas,
            )

            control_ejercicios = controladores.get(
                "control_ejercicios",
                control_ejercicios,
            )

            control_autenticacion = controladores.get(
                "control_auth",
                control_autenticacion,
            )

        if control_clientes is None:
            raise ValueError(
                "InterfazAdministrador requiere un "
                "ControlClientes inicializado."
            )

        if control_rutinas is None:
            raise ValueError(
                "InterfazAdministrador requiere un "
                "ControlRutinas inicializado."
            )

        if control_ejercicios is None:
            raise ValueError(
                "InterfazAdministrador requiere un "
                "ControlEjercicios inicializado."
            )

        if control_autenticacion is None:
            raise ValueError(
                "InterfazAdministrador requiere un "
                "ControlAutenticacion inicializado."
            )

        self._administrador_actual: Administrador = (
            administrador_actual
        )

        self._control_clientes: ControlClientes = (
            control_clientes
        )

        self._control_rutinas: ControlRutinas = (
            control_rutinas
        )

        self._control_ejercicios: ControlEjercicios = (
            control_ejercicios
        )

        self._control_autenticacion = control_autenticacion

        self._controladores = controladores or {
            "control_auth": control_autenticacion,
            "control_clientes": control_clientes,
            "control_rutinas": control_rutinas,
            "control_ejercicios": control_ejercicios,
        }

        self.title(
            "Cardio Wellness - Administrador: "
            f"{administrador_actual.nombre}"
        )

        self.geometry("900x600")
        self.resizable(True, True)

        self.mostrarMenuPrincipal()

    @property
    def administrador_actual(self) -> Administrador:
        """Devuelve el administrador actual."""
        return self._administrador_actual

    @property
    def control_clientes(self) -> ControlClientes:
        """Devuelve el controlador de clientes."""
        return self._control_clientes

    @property
    def control_rutinas(self) -> ControlRutinas:
        """Devuelve el controlador de rutinas."""
        return self._control_rutinas

    @property
    def control_ejercicios(self) -> ControlEjercicios:
        """Devuelve el controlador de ejercicios."""
        return self._control_ejercicios

    def mostrarMenuPrincipal(self) -> None:
        """
        Construye el menú principal del administrador.
        """
        frame_top = ttk.Frame(
            self,
            padding=10,
        )
        frame_top.pack(fill="x")

        ttk.Label(
            frame_top,
            text=(
                "Bienvenido, "
                f"{self._administrador_actual.obtener_nombre_completo()}"
            ),
            font=("Helvetica", 12, "bold"),
        ).pack(side="left")

        ttk.Button(
            frame_top,
            text="Cerrar Sesion",
            command=self.cerrarSesion,
        ).pack(side="right")

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.abrirGestionClientes()
        self.abrirGestionRutinas()
        self.abrirGestionEjercicios()

    def abrirGestionClientes(self) -> None:
        """
        Abre la pestaña de gestión de clientes.
        """
        pestania_clientes = InterfazGestionClientes(
            self._notebook,
            self._control_clientes,
        )

        self._notebook.add(
            pestania_clientes,
            text="Clientes",
        )

    def abrirGestionRutinas(self) -> None:
        """
        Abre la pestaña de gestión de rutinas.
        """
        pestania_rutinas = InterfazGestionRutinas(
            self._notebook,
            self._control_rutinas,
        )

        self._notebook.add(
            pestania_rutinas,
            text="Rutinas",
        )

    def abrirGestionEjercicios(self) -> None:
        """
        Abre la pestaña de gestión de ejercicios.
        """
        pestania_ejercicios = InterfazGestionEjercicios(
            self._notebook,
            self._control_ejercicios,
        )

        self._notebook.add(
            pestania_ejercicios,
            text="Ejercicios",
        )

    def cerrarSesion(self) -> None:
        """
        Cierra la sesión del administrador y vuelve al login.
        """
        try:
            self._control_clientes._registrar_log(
                self._administrador_actual.correo_electronico,
                "LOGOUT",
            )
        except Exception:
            pass

        self.destroy()

        from src.interfaz.interfaz_login import (
            InterfazLogin,
        )

        app = InterfazLogin(
            control_autenticacion=self._control_autenticacion,
            controladores=self._controladores,
        )

        app.mainloop()