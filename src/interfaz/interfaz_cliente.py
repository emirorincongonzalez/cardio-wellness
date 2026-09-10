from typing import Optional
import tkinter as tk
from tkinter import ttk, messagebox

from src.controladores.control_progreso import ControlProgreso
from src.controladores.control_rutinas import ControlRutinas
from src.controladores.control_sesiones import ControlSesiones
from src.modelos.cliente import Cliente
from src.interfaz.interfaz_progreso import InterfazProgreso
from src.interfaz.interfaz_registro_sesion import InterfazRegistroSesion


class InterfazCliente(tk.Tk):
    """
    Ventana principal del Cliente del sistema Cardio-Wellness.

    Atributos (segun DCD):
        -clienteActual    : Cliente            -> Cliente logueado.
        -controlRutinas   : ControlRutinas     -> Controlador de rutinas.
        -controlSesiones  : ControlSesiones    -> Controlador de sesiones.
        -controlProgreso  : ControlProgreso    -> Controlador de progreso.

    Metodos (segun DCD):
        +mostrarInicio(): void          -> Construye y muestra la ventana.
        +consultarRutinaActiva(): void  -> Muestra la rutina activa del cliente.
        +consultarProgreso(): void      -> Muestra el progreso del cliente.
        +registrarSesion(): void        -> Abre el formulario de registro de sesión.
        +cerrarSesion(): void           -> Cierra la sesión y vuelve al login.
    """

    def __init__(
        self,
        cliente_actual: Cliente,
        control_rutinas: Optional[ControlRutinas] = None,
        control_sesiones: Optional[ControlSesiones] = None,
        control_progreso: Optional[ControlProgreso] = None,
    ) -> None:
        """
        Inicializa la ventana del cliente.

        Args:
            cliente_actual: Cliente logueado.
            control_rutinas: Controlador de rutinas (inyectable).
            control_sesiones: Controlador de sesiones (inyectable).
            control_progreso: Controlador de progreso (inyectable).
        """
        super().__init__()

        # Atributos del DCD
        self._cliente_actual: Cliente = cliente_actual
        self._control_rutinas: ControlRutinas = control_rutinas or ControlRutinas()
        self._control_sesiones: ControlSesiones = control_sesiones or ControlSesiones()
        self._control_progreso: ControlProgreso = control_progreso or ControlProgreso()

        # Configuracion de la ventana
        self.title(f"Cardio Wellness - Cliente: {cliente_actual.nombre}")
        self.geometry("750x550")
        self.resizable(True, True)

        # Construir la ventana
        self.mostrarInicio()

    # ==========================================================
    # PROPIEDADES (encapsulamiento de los atributos del DCD)
    # ==========================================================
    @property
    def cliente_actual(self) -> Cliente:
        return self._cliente_actual

    @property
    def control_rutinas(self) -> ControlRutinas:
        return self._control_rutinas

    @property
    def control_sesiones(self) -> ControlSesiones:
        return self._control_sesiones

    @property
    def control_progreso(self) -> ControlProgreso:
        return self._control_progreso

    # ==========================================================
    # METODOS DEL DCD
    # ==========================================================
    def mostrarInicio(self) -> None:
        """
        Construye y muestra la pantalla principal del cliente.
        Incluye la barra superior y el notebook con pestañas.
        """
        # Barra superior con bienvenida y botón de cerrar sesión
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill="x")

        ttk.Label(
            frame_top,
            text=f"Bienvenido, {self._cliente_actual.obtener_nombre_completo()}",
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

        # Abrir cada pestaña usando los métodos del DCD
        self.consultarRutinaActiva()
        self.registrarSesion()
        self.consultarProgreso()

    def consultarRutinaActiva(self) -> None:
        """
        Muestra la pestaña con la rutina activa del cliente.
        """
        pestania_rutina = ttk.Frame(self._notebook, padding=10)
        self._notebook.add(pestania_rutina, text="Mi Rutina")

        ttk.Label(
            pestania_rutina,
            text="Rutina Activa",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor="w")

        self._lbl_rutina_nombre = ttk.Label(pestania_rutina, text="Cargando...")
        self._lbl_rutina_nombre.pack(anchor="w", pady=5)

        # Tabla de ejercicios
        cols = ("Ejercicio", "Tipo", "Duración", "Intensidad")
        self._tree_ejercicios = ttk.Treeview(
            pestania_rutina,
            columns=cols,
            show="headings",
            height=10,
        )
        for c in cols:
            self._tree_ejercicios.heading(c, text=c)
            self._tree_ejercicios.column(c, width=140)
        self._tree_ejercicios.pack(fill="both", expand=True, pady=10)

        # Cargar los datos de la rutina
        self._cargar_datos_rutina()

    def consultarProgreso(self) -> None:
        """
        Muestra la pestaña con el progreso del cliente.
        """
        pestania_progreso = InterfazProgreso(
            self._notebook,
            self._control_progreso,
            self._cliente_actual,
        )
        self._notebook.add(pestania_progreso, text="Mi Progreso")

    def registrarSesion(self) -> None:
        """
        Muestra la pestaña para registrar una nueva sesion de entrenamiento.
        Equivale al método +registrarSesion() del DCD.
        """
        pestania_sesion = InterfazRegistroSesion(
            self._notebook,
            self._control_sesiones,
            self._cliente_actual.id_usuario,
        )
        self._notebook.add(pestania_sesion, text="Registrar Sesión")

    def cerrarSesion(self) -> None:
        """
        Cierra la sesión del cliente y vuelve a la ventana de login.
        """
        # Registrar el cierre de sesión en el LOG
        try:
            self._control_sesiones._registrar_log(
                self._cliente_actual.correo_electronico,
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

    # ==========================================================
    # METODOS AUXILIARES
    # ==========================================================
    def _cargar_datos_rutina(self) -> None:
        """
        Carga la rutina activa del cliente desde el controlador.
        """
        try:
            # Buscar la asignacion activa del cliente
            asignacion = self._control_rutinas.asignacion_dao.buscar_activa(
                self._cliente_actual.id_usuario
            )

            if asignacion is None:
                self._lbl_rutina_nombre.config(
                    text="No tienes una rutina asignada actualmente."
                )
                return

            # Obtener la rutina asociada
            rutina = self._control_rutinas.buscar_por_id(asignacion.id_rutina)

            if rutina is None:
                self._lbl_rutina_nombre.config(text="No se encontró la rutina activa.")
                return

            # Mostrar el nombre de la rutina
            self._lbl_rutina_nombre.config(
                text=f"Rutina: {rutina.nombre} ({rutina.nivel.value})"
            )

            # Cargar los ejercicios
            for ejercicio in rutina.ejercicios:
                self._tree_ejercicios.insert(
                    "",
                    "end",
                    values=(
                        ejercicio.nombre,
                        ejercicio.tipo,
                        f"{ejercicio.duracion_minutos} min",
                        ejercicio.intensidad.value,
                    ),
                )

        except Exception as e:
            self._lbl_rutina_nombre.config(text=f"Error al cargar la rutina: {e}")
