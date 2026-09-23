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
    Ventana principal del cliente de Cardio Wellness.
    """

    def __init__(
        self,
        cliente_actual: Cliente,
        control_rutinas: Optional[
            ControlRutinas
        ] = None,
        control_sesiones: Optional[
            ControlSesiones
        ] = None,
        control_progreso: Optional[
            ControlProgreso
        ] = None,
        control_autenticacion: Optional[Any] = None,
        controladores: Optional[dict] = None,
    ) -> None:
        """
        Inicializa la ventana del cliente.
        """
        super().__init__()

        if cliente_actual is None:
            raise ValueError(
                "Debe existir un cliente autenticado."
            )

        if not isinstance(
            cliente_actual,
            Cliente,
        ):
            raise TypeError(
                "El usuario autenticado debe ser Cliente."
            )

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

            control_autenticacion = (
                controladores.get(
                    "control_auth",
                    controladores.get(
                        "control_autenticacion",
                        control_autenticacion,
                    ),
                )
            )

        if control_rutinas is None:
            raise ValueError(
                (
                    "InterfazCliente requiere un "
                    "ControlRutinas inicializado."
                )
            )

        if control_sesiones is None:
            raise ValueError(
                (
                    "InterfazCliente requiere un "
                    "ControlSesiones inicializado."
                )
            )

        if control_progreso is None:
            raise ValueError(
                (
                    "InterfazCliente requiere un "
                    "ControlProgreso inicializado."
                )
            )

        if control_autenticacion is None:
            raise ValueError(
                (
                    "InterfazCliente requiere un "
                    "ControlAutenticacion inicializado."
                )
            )

        self._cliente_actual = cliente_actual
        self._control_rutinas = control_rutinas
        self._control_sesiones = control_sesiones
        self._control_progreso = control_progreso
        self._control_autenticacion = (
            control_autenticacion
        )

        self._controladores = (
            controladores
            if controladores is not None
            else {
                "control_auth": (
                    control_autenticacion
                ),
                "control_autenticacion": (
                    control_autenticacion
                ),
                "control_rutinas": control_rutinas,
                "control_sesiones": control_sesiones,
                "control_progreso": control_progreso,
            }
        )

        self.title(
            "Cardio Wellness - Cliente: "
            f"{cliente_actual.nombre}"
        )

        self.geometry("1050x780")
        self.minsize(900, 650)
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
        Construye la pantalla principal.
        """
        frame_top = ttk.Frame(
            self,
            padding=10,
        )

        frame_top.pack(
            fill="x",
        )

        nombre_cliente = (
            self._cliente_actual
            .obtener_nombre_completo()
        )

        ttk.Label(
            frame_top,
            text=(
                f"Bienvenido, {nombre_cliente}"
            ),
            font=("Helvetica", 12, "bold"),
        ).pack(
            side="left",
        )

        ttk.Button(
            frame_top,
            text="Cerrar sesión",
            command=self.cerrarSesion,
        ).pack(
            side="right",
        )

        self._crear_datos_personales()

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

    def _crear_datos_personales(self) -> None:
        """
        Muestra los datos personales del cliente.

        No incluye descripción.
        """
        frame = ttk.LabelFrame(
            self,
            text="Datos personales",
            padding=10,
        )

        frame.pack(
            fill="x",
            padx=10,
            pady=(0, 5),
        )

        cliente = self._cliente_actual

        nombre = (
            cliente.obtener_nombre_completo()
        )

        correo = getattr(
            cliente,
            "correo_electronico",
            "",
        )

        edad = getattr(
            cliente,
            "edad",
            "",
        )

        altura = getattr(
            cliente,
            "altura",
            "",
        )

        genero = getattr(
            cliente,
            "genero",
            "PREFIERO NO DECIRLO",
        )

        peso = getattr(
            cliente,
            "peso",
            "",
        )

        peso_objetivo = getattr(
            cliente,
            "peso_objetivo",
            "",
        )

        objetivo = getattr(
            cliente,
            "objetivo",
            "",
        )

        datos = (
            (
                "Nombre:",
                str(nombre),
            ),
            (
                "Correo:",
                str(correo),
            ),
            (
                "Edad:",
                f"{edad} años",
            ),
            (
                "Altura:",
                f"{self._formatear_decimal(altura)} m",
            ),
            (
                "Género:",
                str(genero),
            ),
            (
                "Peso actual:",
                f"{self._formatear_decimal(peso)} kg",
            ),
            (
                "Peso objetivo:",
                (
                    f"{self._formatear_decimal(
                        peso_objetivo
                    )} kg"
                ),
            ),
            (
                "Objetivo:",
                str(objetivo),
            ),
        )

        for columna in range(4):
            frame.columnconfigure(
                columna,
                weight=1,
            )

        for indice, (etiqueta, valor) in enumerate(
            datos
        ):
            fila = indice // 4
            columna = (indice % 4) * 2

            ttk.Label(
                frame,
                text=etiqueta,
                font=("Helvetica", 9, "bold"),
            ).grid(
                row=fila,
                column=columna,
                sticky="w",
                padx=(5, 2),
                pady=4,
            )

            ttk.Label(
                frame,
                text=valor,
            ).grid(
                row=fila,
                column=columna + 1,
                sticky="w",
                padx=(2, 12),
                pady=4,
            )

    @staticmethod
    def _formatear_decimal(
        valor: Any,
    ) -> str:
        """
        Formatea valores numéricos.
        """
        if valor is None or valor == "":
            return "-"

        try:
            return f"{float(valor):.2f}"

        except (
            TypeError,
            ValueError,
        ):
            return str(valor)

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
            text="Mi rutina",
        )

        ttk.Label(
            pestania_rutina,
            text="Rutina activa",
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
            "Duración",
            "Intensidad",
        )

        self._tree_ejercicios = ttk.Treeview(
            pestania_rutina,
            columns=columnas,
            show="headings",
            height=10,
        )

        anchos = {
            "Ejercicio": 240,
            "Tipo": 180,
            "Duración": 140,
            "Intensidad": 160,
        }

        for columna in columnas:
            self._tree_ejercicios.heading(
                columna,
                text=columna,
            )

            self._tree_ejercicios.column(
                columna,
                width=anchos[columna],
                minwidth=100,
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
        Muestra el progreso del cliente.
        """
        pestania_progreso = InterfazProgreso(
            master=self._notebook,
            control_progreso=(
                self._control_progreso
            ),
            cliente=self._cliente_actual,
        )

        self._notebook.add(
            pestania_progreso,
            text="Mi progreso",
        )

    def registrarSesion(self) -> None:
        """
        Muestra el formulario para registrar sesión.
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

            pestania_sesion = (
                InterfazRegistroSesion(
                    self._notebook,
                    self._control_sesiones,
                    self._cliente_actual.id_usuario,
                    id_rutina,
                )
            )

            self._notebook.add(
                pestania_sesion,
                text="Registrar sesión",
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
                text="Registrar sesión",
            )

    def cerrarSesion(self) -> None:
        """
        Cierra la sesión y vuelve al login.
        """
        try:
            self._control_sesiones._registrar_log(
                self._cliente_actual
                .correo_electronico,
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
                        "No tienes una rutina "
                        "asignada actualmente."
                    )
                )
                return

            id_rutina = self._obtener_id_rutina(
                asignacion
            )

            if id_rutina is None:
                self._lbl_rutina_nombre.config(
                    text=(
                        "La asignación no contiene "
                        "una rutina válida."
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
                        "No se encontró la rutina activa."
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
        Muestra un mensaje sin rutina activa.
        """
        pestania_sesion = ttk.Frame(
            self._notebook,
            padding=10,
        )

        ttk.Label(
            pestania_sesion,
            text=(
                "No puedes registrar una sesión "
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
            text="Registrar sesión",
        )

    def _mostrar_error_rutina(self) -> None:
        """
        Muestra un error de rutina inválida.
        """
        pestania_sesion = ttk.Frame(
            self._notebook,
            padding=10,
        )

        ttk.Label(
            pestania_sesion,
            text=(
                "La asignación activa no contiene "
                "una rutina válida."
            ),
            foreground="red",
            wraplength=600,
            justify="center",
        ).pack(
            pady=30,
        )

        self._notebook.add(
            pestania_sesion,
            text="Registrar sesión",
        )

    @staticmethod
    def _obtener_id_rutina(
        asignacion: Any,
    ) -> Optional[int]:
        """
        Obtiene id_rutina desde objeto o diccionario.
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