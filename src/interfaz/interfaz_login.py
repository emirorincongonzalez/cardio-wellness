from typing import Optional
import tkinter as tk
from tkinter import ttk, messagebox

from src.controladores.control_autenticacion import ControlAutenticacion
from src.modelos.usuario import Usuario


class InterfazLogin(tk.Tk):
    """
    Ventana de inicio de sesion del sistema Cardio-Wellness.

    Atributos (segun DCD):
        -correo : String       -> Correo ingresado por el usuario.
        -contrasenia : String   -> Contraseniaa ingresada por el usuario.
        -control : ControlAutenticacion -> Controlador de autenticacion.

    Metodos (segun DCD):
        +mostrarFormulario(): void       -> Construye y muestra la ventana.
        +capturarCredenciales(): void    -> Captura los datos de los campos.
        +iniciarSesion(): void           -> Ejecuta el proceso de autenticacion.
    """

    def __init__(self, control_autenticacion: ControlAutenticacion) -> None:
        """
        Inicializa la ventana de login.

        Args:
            control_autenticacion: Controlador de autenticacion inyectado.
        """
        super().__init__()

        # Atributos
        self._correo: str = ""
        self._contrasenia: str = ""
        self._control: ControlAutenticacion = control_autenticacion

        #  Configuracion de la ventana
        self.title("Cardio Wellness - Iniciar Sesión")
        self.geometry("400x350")
        self.resizable(False, False)

        # Construir el formulario
        self.mostrarFormulario()

    # ==========================================================
    # PROPIEDADES (encapsulamiento de los atributos del DCD)
    # ==========================================================
    @property
    def correo(self) -> str:
        return self._correo

    @property
    def contrasenia(self) -> str:
        return self._contrasenia

    @property
    def control(self) -> ControlAutenticacion:
        return self._control

    # ==========================================================
    # METODOS DEL DCD
    # ==========================================================
    def mostrarFormulario(self) -> None:
        """
        Construye y muestra el formulario de inicio de sesion.
        """
        title = ttk.Label(
            self,
            text="Sistema Cardio-Wellness",
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=25)

        frame = ttk.Frame(self, padding="20")
        frame.pack(fill="both", expand=True)

        # Campo: Correo
        ttk.Label(frame, text="Correo Electrónico:").grid(row=0, column=0, sticky="w", pady=5)
        self._ent_correo = ttk.Entry(frame, width=32)
        self._ent_correo.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Campo: Contraseña
        ttk.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
        self._ent_password = ttk.Entry(frame, width=32, show="*")
        self._ent_password.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        # Botones
        ttk.Button(frame, text="Iniciar Sesión", command=self.iniciarSesion).grid(
            row=4, column=0, sticky="ew", pady=5
        )
        ttk.Button(frame, text="Salir", command=self.destroy).grid(
            row=5, column=0, sticky="ew", pady=5
        )

    def capturarCredenciales(self) -> bool:
        """
        Captura los datos ingresados por el usuario en los campos del formulario.

        Returns:
            bool: True si los datos son válidos (no vacíos), False en caso contrario.
        """
        self._correo = self._ent_correo.get().strip()
        self._contrasenia = self._ent_password.get().strip()

        if not self._correo or not self._contrasenia:
            messagebox.showwarning("Campos Vacíos", "Por favor complete todos los campos.")
            return False
        return True

    def iniciarSesion(self) -> None:
        """
        Ejecuta el proceso de autenticacion.
        Delega en ControlAutenticacion.iniciar_sesion().
        """
        # 1. Capturar credenciales
        if not self.capturarCredenciales():
            return

        # 2. Autenticar usando el controlador
        try:
            usuario: Optional[Usuario] = self._control.iniciar_sesion(
                self._correo, self._contraseña
            )

            if usuario is None:
                messagebox.showerror("Error", "Credenciales incorrectas.")
                return

            # 3. Redirigir según el rol del usuario
            self.destroy()
            self._abrir_interfaz_por_rol(usuario)

        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {e}")

    # ==========================================================
    # METODOS AUXILIARES
    # ==========================================================
    def _abrir_interfaz_por_rol(self, usuario: Usuario) -> None:
        """
        Abre la interfaz correspondiente segun el tipo de usuario.
        Este metodo es un detalle de implementacion, no del DCD.
        """
        if usuario.tipo_usuario == "administrador":
            from src.interfaz.interfaz_administrador import InterfazAdministrador
            app = InterfazAdministrador(usuario)
        else:
            from src.interfaz.interfaz_cliente import InterfazCliente
            app = InterfazCliente(usuario)
        app.mainloop()
