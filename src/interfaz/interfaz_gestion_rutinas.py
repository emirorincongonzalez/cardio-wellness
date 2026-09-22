from typing import List
import tkinter as tk
from tkinter import simpledialog, ttk

from src.controladores.control_rutinas import (
    ControlRutinas,
)
from src.modelos.rutina import Rutina
from src.interfaz.interfaz_base import InterfazBase


class InterfazGestionRutinas(InterfazBase):
    """
    Pestaña de gestión de rutinas.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_rutinas: ControlRutinas,
    ) -> None:
        super().__init__(
            master,
            controlador=control_rutinas,
            padding=10,
        )

        self.pack(
            fill="both",
            expand=True,
        )

        self._control_rutinas = control_rutinas

        self.mostrarFormularioRutina()
        self.mostrarRutinas()

    @property
    def control_rutinas(self) -> ControlRutinas:
        return self._control_rutinas

    def mostrarFormularioRutina(self) -> None:
        """
        Construye el formulario para crear una rutina.
        """
        form = ttk.LabelFrame(
            self,
            text="Registrar Nueva Rutina",
            padding=10,
        )

        form.pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            form,
            text="Nombre:",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_nombre = ttk.Entry(
            form,
            width=20,
        )

        self._ent_nombre.grid(
            row=0,
            column=1,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Nivel:",
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._cb_nivel = ttk.Combobox(
            form,
            values=(
                "BASICO",
                "INTERMEDIO",
                "AVANZADO",
            ),
            state="readonly",
            width=18,
        )

        self._cb_nivel.grid(
            row=0,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Descripcion:",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_descripcion = ttk.Entry(
            form,
            width=20,
        )

        self._ent_descripcion.grid(
            row=1,
            column=1,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Objetivo:",
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_objetivo = ttk.Entry(
            form,
            width=20,
        )

        self._ent_objetivo.grid(
            row=1,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Duracion (semanas):",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_duracion = ttk.Entry(
            form,
            width=20,
        )

        self._ent_duracion.grid(
            row=2,
            column=1,
            padx=5,
            pady=3,
        )

        frame_btns = ttk.Frame(form)

        frame_btns.grid(
            row=3,
            column=3,
            sticky="e",
            pady=10,
        )

        ttk.Button(
            frame_btns,
            text="Crear",
            command=self.crearRutina,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Editar",
            command=self.editarRutina,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Eliminar",
            command=self.eliminarRutina,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Asignar",
            command=self.asignarRutina,
        ).pack(
            side="left",
            padx=3,
        )

    def mostrarRutinas(self) -> None:
        """
        Carga las rutinas en la tabla.
        """
        if hasattr(self, "_tree"):
            for item in self._tree.get_children():
                self._tree.delete(item)

        else:
            columnas = (
                "ID",
                "Nombre",
                "Objetivo",
                "Nivel",
                "Duracion",
            )

            self._tree = ttk.Treeview(
                self,
                columns=columnas,
                show="headings",
                height=12,
            )

            for columna in columnas:
                self._tree.heading(
                    columna,
                    text=columna,
                )

                self._tree.column(
                    columna,
                    width=140,
                    anchor="center",
                )

            self._tree.pack(
                fill="both",
                expand=True,
                pady=10,
            )

        try:
            rutinas: List[Rutina] = (
                self._control_rutinas.listar()
            )

            for rutina in rutinas:
                nivel = getattr(
                    rutina.nivel,
                    "value",
                    str(rutina.nivel),
                )

                self._tree.insert(
                    "",
                    "end",
                    values=(
                        rutina.id_rutina,
                        rutina.nombre,
                        rutina.objetivo,
                        nivel,
                        (
                            f"{rutina.duracion_semanas}"
                            " sem"
                        ),
                    ),
                )

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar rutinas: {error}"
            )

    def crearRutina(self) -> None:
        """
        Crea una rutina nueva.
        """
        try:
            nombre = self._ent_nombre.get().strip()
            descripcion = (
                self._ent_descripcion.get().strip()
            )
            objetivo = (
                self._ent_objetivo.get().strip()
            )
            nivel = self._cb_nivel.get().strip()
            duracion_texto = (
                self._ent_duracion.get().strip()
            )

            if not nivel:
                self.mostrar_error(
                    "Seleccione un nivel."
                )
                return

            duracion = int(duracion_texto)

            administrador_id = (
                self._obtener_id_administrador()
            )

            self._control_rutinas.crear_rutina(
                nombre=nombre,
                descripcion=descripcion,
                nivel_dificultad=nivel,
                duracion_estimada=duracion,
                creado_por=administrador_id,
                objetivo=objetivo or "cardio",
            )

            self.mostrar_mensaje(
                "Rutina creada exitosamente."
            )

            self._limpiar_formulario()
            self.mostrarRutinas()

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                f"Error inesperado: {error}"
            )

    def editarRutina(self) -> None:
        """
        Edita la rutina seleccionada.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione una rutina para editar."
            )
            return

        self.mostrar_mensaje(
            "Funcionalidad de edición pendiente."
        )

    def eliminarRutina(self) -> None:
        """
        Elimina la rutina seleccionada.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione una rutina para eliminar."
            )
            return

        id_rutina = self._tree.item(
            seleccion[0]
        )["values"][0]

        if not self.confirmar_accion(
            f"¿Eliminar la rutina con ID {id_rutina}?"
        ):
            return

        try:
            administrador_id = (
                self._obtener_id_administrador()
            )

            self._control_rutinas.eliminar_rutina(
                int(id_rutina),
                administrador_id,
            )

            self.mostrar_mensaje(
                "Rutina eliminada correctamente."
            )

            self.mostrarRutinas()

        except Exception as error:
            self.mostrar_error(
                f"Error al eliminar: {error}"
            )

    def asignarRutina(self) -> None:
        """
        Asigna la rutina seleccionada a un cliente.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione una rutina para asignar."
            )
            return

        id_rutina = int(
            self._tree.item(
                seleccion[0]
            )["values"][0]
        )

        id_cliente = simpledialog.askinteger(
            "Asignar Rutina",
            "Ingrese el ID del cliente:",
            parent=self,
            minvalue=1,
        )

        if id_cliente is None:
            return

        observaciones = simpledialog.askstring(
            "Asignar Rutina",
            "Observaciones opcionales:",
            parent=self,
        )

        try:
            administrador_id = (
                self._obtener_id_administrador()
            )

            self._control_rutinas.asignar_rutina(
                cliente=id_cliente,
                rutina=id_rutina,
                asignado_por=administrador_id,
                observaciones=(
                    observaciones or ""
                ),
            )

            self.mostrar_mensaje(
                f"Rutina {id_rutina} asignada "
                f"al cliente {id_cliente}."
            )

        except Exception as error:
            self.mostrar_error(
                f"Error al asignar rutina: {error}"
            )

    def _obtener_id_administrador(self) -> int:
        """
        Obtiene el ID del administrador autenticado.
        """
        controlador_auth = getattr(
            self,
            "controlador",
            None,
        )

        if controlador_auth is not None:
            usuario_actual = getattr(
                controlador_auth,
                "usuario_actual",
                None,
            )

            if usuario_actual is not None:
                id_usuario = getattr(
                    usuario_actual,
                    "id_usuario",
                    None,
                )

                if id_usuario is not None:
                    return int(id_usuario)

        controladores = getattr(
            self.master,
            "_controladores",
            None,
        )

        if isinstance(controladores, dict):
            control_auth = controladores.get(
                "control_auth"
            )

            if control_auth is not None:
                usuario_actual = getattr(
                    control_auth,
                    "usuario_actual",
                    None,
                )

                if usuario_actual is not None:
                    id_usuario = getattr(
                        usuario_actual,
                        "id_usuario",
                        None,
                    )

                    if id_usuario is not None:
                        return int(id_usuario)

        return 1

    def _limpiar_formulario(self) -> None:
        """
        Limpia el formulario.
        """
        for entry in (
            self._ent_nombre,
            self._ent_descripcion,
            self._ent_objetivo,
            self._ent_duracion,
        ):
            entry.delete(
                0,
                tk.END,
            )

        self._cb_nivel.set("")