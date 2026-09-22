from typing import Optional

import tkinter as tk
from tkinter import messagebox, ttk

from src.controladores.control_autenticacion import (
    ControlAutenticacion,
)
from src.modelos.usuario import Usuario


class InterfazLogin(tk.Tk):
    """
    Ventana de inicio de sesión de Cardio-Wellness.
    """

    def __init__(
        self,
        control_autenticacion: ControlAutenticacion,
        controladores: Optional[dict] = None,
    ) -> None:
        super().__init__()

        self._correo = ""
        self._contrasenia = ""
        self._control = control_autenticacion

        self._controladores = (
            controladores
            if controladores is not None
            else {
                "control_auth": control_autenticacion,
            }
        )

        self.title(
            "Cardio Wellness - Iniciar Sesion"
        )
        self.geometry("400x350")
        self.resizable(False, False)

        self.mostrarFormulario()

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def contrasenia(self) -> str:
        return self._contrasenia

    @property
    def control(self) -> ControlAutenticacion:
        return self._control

    def mostrarFormulario(self) -> None:
        """
        Construye el formulario de login.
        """
        ttk.Label(
            self,
            text="Sistema Cardio-Wellness",
            font=("Helvetica", 16, "bold"),
        ).pack(pady=25)

        frame = ttk.Frame(
            self,
            padding="20",
        )

        frame.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            frame,
            text="Correo Electronico:",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=5,
        )

        self._ent_correo = ttk.Entry(
            frame,
            width=32,
        )

        self._ent_correo.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 12),
        )

        ttk.Label(
            frame,
            text="Contrasenia:",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5,
        )

        self._ent_contrasenia = ttk.Entry(
            frame,
            width=32,
            show="*",
        )

        self._ent_contrasenia.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 20),
        )

        ttk.Button(
            frame,
            text="Iniciar Sesion",
            command=self.iniciarSesion,
        ).grid(
            row=4,
            column=0,
            sticky="ew",
            pady=5,
        )

        ttk.Button(
            frame,
            text="Salir",
            command=self.destroy,
        ).grid(
            row=5,
            column=0,
            sticky="ew",
            pady=5,
        )

    def capturarCredenciales(self) -> bool:
        """
        Captura y valida las credenciales.
        """
        self._correo = (
            self._ent_correo.get().strip()
        )

        self._contrasenia = (
            self._ent_contrasenia.get().strip()
        )

        if not self._correo or not self._contrasenia:
            messagebox.showwarning(
                "Campos Vacios",
                "Por favor complete todos los campos.",
            )
            return False

        return True

    def iniciarSesion(self) -> None:
        """
        Ejecuta la autenticación.
        """
        if not self.capturarCredenciales():
            return

        try:
            usuario = (
                self._control.iniciar_sesion(
                    self._correo,
                    self._contrasenia,
                )
            )

            if usuario is None:
                messagebox.showerror(
                    "Error",
                    "Credenciales incorrectas.",
                )
                return

            self.destroy()

            self._abrir_interfaz_por_rol(
                usuario
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Error al iniciar sesion: {error}",
            )

    def _abrir_interfaz_por_rol(
        self,
        usuario: Usuario,
    ) -> None:
        """
        Abre la interfaz según el tipo de usuario.
        """
        tipo_usuario = str(
            getattr(
                usuario,
                "tipo_usuario",
                "",
            )
        ).strip().lower()

        if tipo_usuario in {
            "administrador",
            "admin",
        }:
            from src.interfaz.interfaz_administrador import (
                InterfazAdministrador,
            )

            app = InterfazAdministrador(
                administrador_actual=usuario,
                controladores=self._controladores,
            )

        else:
            from src.interfaz.interfaz_cliente import (
                InterfazCliente,
            )

            app = InterfazCliente(
                cliente_actual=usuario,
                controladores=self._controladores,
            )

        app.mainloop()