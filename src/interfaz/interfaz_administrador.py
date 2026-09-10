from typing import Optional
import tkinter as tk
from tkinter import ttk

from src.controladores.control_clientes import ControlClientes
from src.controladores.control_ejercicios import ControlEjercicios
from src.controladores.control_rutinas import ControlRutinas
from src.modelos.administrador import Administrador
from src.interfaz.interfaz_gestion_clientes import InterfazGestionClientes
from src.interfaz.interfaz_gestion_ejercicios import InterfazGestionEjercicios
from src.interfaz.interfaz_gestion_rutinas import InterfazGestionRutinas


class InterfazAdministrador(tk.Tk):
    """
    Ventana principal del Administrador del sistema Cardio-Wellness.

    Atributos (segun DCD):
        -administradorActual : Administrador -> Administrador logueado.
        -controlClientes     : ControlClientes -> Controlador de clientes.
        -controlRutinas      : ControlRutinas -> Controlador de rutinas.
        -controlEjercicios   : ControlEjercicios -> Controlador de ejercicios.

    Métodos (segun DCD):
        +mostrarMenuPrincipal(): void    -> Construye y muestra el menu.
        +abrirGestionClientes(): void    -> Abre la pestaña de gestion de clientes.
        +abrirGestionRutinas(): void     -> Abre la pestaña de gestion de rutinas.
        +abrirGestionEjercicios(): void  -> Abre la pestaña de gestion de ejercicios.
        +cerrarSesion(): void            -> Cierra la sesion y vuelve al login.
    """

    def __init__(
        self,
        administrador_actual: Administrador,
        control_clientes: Optional[ControlClientes] = None,
        control_rutinas: Optional[ControlRutinas] = None,
        control_ejercicios: Optional[ControlEjercicios] = None,
    ) -> None:
        """
        Inicializa la ventana del administrador.

        Args:
            administrador_actual: Administrador logueado.
            control_clientes: Controlador de clientes (inyectable).
            control_rutinas: Controlador de rutinas (inyectable).
            control_ejercicios: Controlador de ejercicios (inyectable).
        """
        super().__init__()

        # Atributos del DCD
        self._administrador_actual: Administrador = administrador_actual
        self._control_clientes: ControlClientes = control_clientes or ControlClientes()
        self._control_rutinas: ControlRutinas = control_rutinas or ControlRutinas()
        self._control_ejercicios: ControlEjercicios = control_ejercicios or ControlEjercicios()

        # Configuracion de la ventana
        self.title(f"Cardio Wellness - Administrador: {administrador_actual.nombre}")
        self.geometry("900x600")
        self.resizable(True, True)

        # Construir el menu principal
        self.mostrarMenuPrincipal()

    # ==========================================================
    # PROPIEDADES (encapsulamiento de los atributos del DCD)
    # ==========================================================
    @property
    def administrador_actual(self) -> Administrador:
        return self._administrador_actual

    @property
    def control_clientes(self) -> ControlClientes:
        return self._control_clientes

    @property
    def control_rutinas(self) -> ControlRutinas:
        return self._control_rutinas

    @property
    def control_ejercicios(self) -> ControlEjercicios:
        return self._control_ejercicios

    # ==========================================================
    # MÉTODOS DEL DCD
    # ==========================================================
    def mostrarMenuPrincipal(self) -> None:
        """
        Construye y muestra el menu principal del administrador.
        Incluye la barra superior y el notebook con pestañas.
        """
        # Barra superior con bienvenida y boton de cerrar sesion
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill="x")

        ttk.Label(
            frame_top,
            text=f"Bienvenido, {self._administrador_actual.obtener_nombre_completo()}",
            font=("Helvetica", 12, "bold"),
        ).pack(side="left")

        ttk.Button(
            frame_top,
            text="Cerrar Sesión",
            command=self.cerrarSesion,
        ).pack(side="right")

        # Notebook con pestañas
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Abrir cada pestaña usando los metodos del DCD
        self.abrirGestionClientes()
        self.abrirGestionRutinas()
        self.abrirGestionEjercicios()

    def abrirGestionClientes(self) -> None:
        pestaña_clientes = InterfazGestionClientes(
            self._notebook,
            self._control_clientes,
        )
        self._notebook.add(pestaña_clientes, text="Clientes")

    def abrirGestionRutinas(self) -> None:
        pestaña_rutinas = InterfazGestionRutinas(
            self._notebook,
            self._control_rutinas,
        )
        self._notebook.add(pestaña_rutinas, text="📋 Rutinas")

    def abrirGestionEjercicios(self) -> None:
        pestaña_ejercicios = InterfazGestionEjercicios(
            self._notebook,
            self._control_ejercicios,
        )
        self._notebook.add(pestaña_ejercicios, text="Ejercicios")

    def cerrarSesion(self) -> None:
        # Registrar el cierre de sesión en el LOG (opcional)
        try:
            self._control_clientes._registrar_log(
                self._administrador_actual.correo_electronico,
                "LOGOUT",
            )
        except Exception:
            pass  # No interrumpir si falla el LOG

        # Cerrar la ventana actual
        self.destroy()

        # Volver al login
        from src.controladores.control_autenticacion import ControlAutenticacion
        from src.interfaz.interfaz_login import InterfazLogin

        app = InterfazLogin(ControlAutenticacion())
        app.mainloop()
