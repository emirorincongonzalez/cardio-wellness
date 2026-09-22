from typing import Any, Optional

import tkinter as tk
from tkinter import ttk


from src.controladores.control_progreso import (
    ControlProgreso,
)
from src.controladores.control_rutinas import (
    ControlRutinas,
)
from src.controladores.control_sesiones import (
    ControlSesiones,
)
from src.interfaz.interfaz_progreso import (
    InterfazProgreso,
)
from src.interfaz.interfaz_registro_sesion import (
    InterfazRegistroSesion,
)
from src.modelos.cliente import Cliente


class InterfazCliente(tk.Tk):
    """
    Ventana principal del cliente de Cardio-Wellness.
    """

    def __init__(
        self,
        cliente_actual: Cliente,
        control_rutinas: Optional[ControlRutinas] = None,
        control_sesiones: Optional[ControlSesiones] = None,
        control_progreso: Optional[ControlProgreso] = None,
        control_autenticacion: Optional[Any] = None,
        controladores: Optional[dict] = None,
    ) -> None:
        """
        Inicializa la ventana del cliente.
        """
        super().__init__()

        if controladores is not None:
            control_rutinas = controladores.get(
                "control_rutinas",
                control_rutinas,
            )

            control_sesiones = controladores.get(
                "control_sesiones",
                control_sesiones,
            )

            control_progreso = controladores.get(
                "control_progreso",
                control_progreso,
            )

            control_autenticacion = controladores.get(
                "control_auth",
                control_autenticacion,
            )

        if control_rutinas is None:
            raise ValueError(
                "InterfazCliente requiere un "
                "ControlRutinas inicializado."
            )

        if control_sesiones is None:
            raise ValueError(
                "InterfazCliente requiere un "
                "ControlSesiones inicializado."
            )

        if control_progreso is None:
            raise ValueError(
                "InterfazCliente requiere un "
                "ControlProgreso inicializado."
            )

        if control_autenticacion is None:
            raise ValueError(
                "InterfazCliente requiere un "
                "ControlAutenticacion inicializado."
            )

        self._cliente_actual = cliente_actual
        self._control_rutinas = control_rutinas
        self._control_sesiones = control_sesiones
        self._control_progreso = control_progreso
        self._control_autenticacion = control_autenticacion

        self._controladores = controladores or {
            "control_auth": control_autenticacion,
            "control_rutinas": control_rutinas,
            "control_sesiones": control_sesiones,
            "control_progreso": control_progreso,
        }

        self.title(
            "Cardio Wellness - Cliente: "
            f"{cliente_actual.nombre}"
        )

        self.geometry("900x700")
        self.resizable(True, True)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cerrarSesion,
        )

        self.mostrarInicio()

    @property
    def cliente_actual(self) -> Cliente:
        """
        Devuelve el cliente actual.
        """
        return self._cliente_actual

    @property
    def control_rutinas(self) -> ControlRutinas:
        """
        Devuelve el controlador de rutinas.
        """
        return self._control_rutinas

    @property
    def control_sesiones(self) -> ControlSesiones:
        """
        Devuelve el controlador de sesiones.
        """
        return self._control_sesiones

    @property
    def control_progreso(self) -> ControlProgreso:
        """
        Devuelve el controlador de progreso.
        """
        return self._control_progreso

    def mostrarInicio(self) -> None:
        """
        Construye la pantalla principal del cliente.
        """
        frame_top = ttk.Frame(
            self,
            padding=10,
        )

        frame_top.pack(
            fill="x",
        )

        nombre_cliente = (
            self._cliente_actual.obtener_nombre_completo()
        )

        ttk.Label(
            frame_top,
            text=f"Bienvenido, {nombre_cliente}",
            font=("Helvetica", 12, "bold"),
        ).pack(
            side="left",
        )

        ttk.Button(
            frame_top,
            text="Cerrar Sesion",
            command=self.cerrarSesion,
        ).pack(
            side="right",
        )

        self._notebook = ttk.Notebook(self)

        self._notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.consultarRutinaActiva()
        self.registrarSesion()
        self.consultarProgreso()

    def consultarRutinaActiva(self) -> None:
        """
        Muestra la rutina activa del cliente.
        """
        pestania_rutina = ttk.Frame(
            self._notebook,
            padding=10,
        )

        self._notebook.add(
            pestania_rutina,
            text="Mi Rutina",
        )

        ttk.Label(
            pestania_rutina,
            text="Rutina Activa",
            font=("Helvetica", 12, "bold"),
        ).pack(
            anchor="w",
        )

        self._lbl_rutina_nombre = ttk.Label(
            pestania_rutina,
            text="Cargando...",
        )

        self._lbl_rutina_nombre.pack(
            anchor="w",
            pady=5,
        )

        columnas = (
            "Ejercicio",
            "Tipo",
            "Duracion",
            "Intensidad",
        )

        self._tree_ejercicios = ttk.Treeview(
            pestania_rutina,
            columns=columnas,
            show="headings",
            height=10,
        )

        for columna in columnas:
            self._tree_ejercicios.heading(
                columna,
                text=columna,
            )

            self._tree_ejercicios.column(
                columna,
                width=160,
                anchor="center",
            )

        self._tree_ejercicios.pack(
            fill="both",
            expand=True,
            pady=10,
        )

        self._cargar_datos_rutina()

    def consultarProgreso(self) -> None:
        """
        Muestra la pestaña de progreso.
        """
        pestania_progreso = InterfazProgreso(
            self._notebook,
            self._control_progreso,
            self._cliente_actual,
        )

        self._notebook.add(
            pestania_progreso,
            text="Mi Progreso",
        )

    def registrarSesion(self) -> None:
        """
        Muestra el formulario para registrar una sesión.

        El formulario solo se habilita cuando el cliente
        tiene una rutina activa.
        """
        try:
            asignacion = (
                self._control_rutinas
                .asignacion_dao
                .buscar_activa(
                    self._cliente_actual.id_usuario
                )
            )

            if asignacion is None:
                self._mostrar_sin_rutina_activa()
                return

            id_rutina = self._obtener_id_rutina(
                asignacion
            )

            if id_rutina is None or id_rutina <= 0:
                self._mostrar_error_rutina()
                return

            pestania_sesion = InterfazRegistroSesion(
                self._notebook,
                self._control_sesiones,
                self._cliente_actual.id_usuario,
                id_rutina,
            )

            self._notebook.add(
                pestania_sesion,
                text="Registrar Sesion",
            )

        except Exception as error:
            pestania_sesion = ttk.Frame(
                self._notebook,
                padding=10,
            )

            ttk.Label(
                pestania_sesion,
                text=(
                    "No se pudo cargar el formulario "
                    f"de sesiones: {error}"
                ),
                foreground="red",
                wraplength=600,
            ).pack(
                pady=30,
            )

            self._notebook.add(
                pestania_sesion,
                text="Registrar Sesion",
            )

    def cerrarSesion(self) -> None:
        """
        Cierra la sesión y vuelve al login.
        """
        try:
            self._control_sesiones._registrar_log(
                self._cliente_actual.correo_electronico,
                "LOGOUT",
            )
        except Exception:
            pass

        self.destroy()

        from src.interfaz.interfaz_login import (
            InterfazLogin,
        )

        app = InterfazLogin(
            control_autenticacion=(
                self._control_autenticacion
            ),
            controladores=self._controladores,
        )

        app.mainloop()

    def _cargar_datos_rutina(self) -> None:
        """
        Carga y muestra la rutina activa.
        """
        try:
            asignacion = (
                self._control_rutinas
                .asignacion_dao
                .buscar_activa(
                    self._cliente_actual.id_usuario
                )
            )

            if asignacion is None:
                self._lbl_rutina_nombre.config(
                    text=(
                        "No tienes una rutina asignada "
                        "actualmente."
                    )
                )
                return

            id_rutina = self._obtener_id_rutina(
                asignacion
            )

            if id_rutina is None:
                self._lbl_rutina_nombre.config(
                    text=(
                        "La asignacion no contiene "
                        "una rutina valida."
                    )
                )
                return

            rutina = (
                self._control_rutinas.buscar_por_id(
                    id_rutina
                )
            )

            if rutina is None:
                self._lbl_rutina_nombre.config(
                    text=(
                        "No se encontro la rutina activa."
                    )
                )
                return

            nombre = getattr(
                rutina,
                "nombre",
                "Sin nombre",
            )

            nivel = getattr(
                rutina,
                "nivel",
                "",
            )

            nivel_texto = getattr(
                nivel,
                "value",
                str(nivel),
            )

            self._lbl_rutina_nombre.config(
                text=(
                    f"Rutina: {nombre} "
                    f"({nivel_texto})"
                )
            )

            ejercicios = getattr(
                rutina,
                "ejercicios",
                [],
            ) or []

            if not ejercicios:
                self._tree_ejercicios.insert(
                    "",
                    "end",
                    values=(
                        "Sin ejercicios",
                        "",
                        "",
                        "",
                    ),
                )
                return

            for ejercicio in ejercicios:
                nombre_ejercicio = getattr(
                    ejercicio,
                    "nombre",
                    "",
                )

                tipo = getattr(
                    ejercicio,
                    "tipo",
                    "",
                )

                duracion = getattr(
                    ejercicio,
                    "duracion_minutos",
                    getattr(
                        ejercicio,
                        "duracion",
                        "",
                    ),
                )

                intensidad = getattr(
                    ejercicio,
                    "intensidad",
                    "",
                )

                intensidad_texto = getattr(
                    intensidad,
                    "value",
                    str(intensidad),
                )

                self._tree_ejercicios.insert(
                    "",
                    "end",
                    values=(
                        nombre_ejercicio,
                        tipo,
                        f"{duracion} min",
                        intensidad_texto,
                    ),
                )

        except Exception as error:
            self._lbl_rutina_nombre.config(
                text=(
                    "Error al cargar la rutina: "
                    f"{error}"
                )
            )

    def _mostrar_sin_rutina_activa(self) -> None:
        """
        Muestra un mensaje cuando no existe rutina activa.
        """
        pestania_sesion = ttk.Frame(
            self._notebook,
            padding=10,
        )

        ttk.Label(
            pestania_sesion,
            text=(
                "No puedes registrar una sesion "
                "porque no tienes una rutina activa "
                "asignada."
            ),
            foreground="red",
            wraplength=600,
            justify="center",
        ).pack(
            pady=30,
        )

        self._notebook.add(
            pestania_sesion,
            text="Registrar Sesion",
        )

    def _mostrar_error_rutina(self) -> None:
        """
        Muestra un mensaje cuando la asignación no contiene
        un ID de rutina válido.
        """
        pestania_sesion = ttk.Frame(
            self._notebook,
            padding=10,
        )

        ttk.Label(
            pestania_sesion,
            text=(
                "La asignacion activa no contiene "
                "una rutina valida."
            ),
            foreground="red",
            wraplength=600,
            justify="center",
        ).pack(
            pady=30,
        )

        self._notebook.add(
            pestania_sesion,
            text="Registrar Sesion",
        )

    @staticmethod
    def _obtener_id_rutina(
        asignacion: Any,
    ) -> Optional[int]:
        """
        Obtiene id_rutina desde un objeto o diccionario.
        """
        if isinstance(asignacion, dict):
            valor = asignacion.get(
                "id_rutina"
            )
        else:
            valor = getattr(
                asignacion,
                "id_rutina",
                None,
            )

        if valor is None:
            return None

        try:
            return int(valor)
        except (
            TypeError,
            ValueError,
        ):
            return None