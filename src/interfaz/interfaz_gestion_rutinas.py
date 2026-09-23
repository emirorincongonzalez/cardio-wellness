from typing import List, Optional

import tkinter as tk
from tkinter import simpledialog, ttk

from src.controladores.control_rutinas import (
    ControlRutinas,
)
from src.controladores.control_ejercicios import (
    ControlEjercicios,
)
from src.interfaz.interfaz_base import InterfazBase
from src.modelos.rutina import Rutina


class InterfazGestionRutinas(InterfazBase):
    """
    Pestaña de gestión de rutinas.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_rutinas: ControlRutinas,
        control_autenticacion=None,
        control_ejercicios: Optional[
            ControlEjercicios
        ] = None,
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

        self._control_rutinas = (
            control_rutinas
        )

        self._control_autenticacion = (
            control_autenticacion
        )

        self._control_ejercicios = (
            control_ejercicios
        )

        self._rutinas_disponibles: List[
            Rutina
        ] = []

        self._ejercicios_disponibles = []

        self._id_rutina_editando: Optional[
            int
        ] = None

        self._id_rutina_vista_previa: Optional[
            int
        ] = None

        self._id_ejercicio_seleccionado: Optional[
            int
        ] = None

        self.mostrarFormularioRutina()
        self.mostrarRutinas()
        self.mostrarEjerciciosRutina()
        self._cargar_datos_ejercicios()

    @property
    def control_rutinas(self) -> ControlRutinas:
        return self._control_rutinas

    def mostrarFormularioRutina(self) -> None:
        """
        Construye el formulario de rutinas.
        """
        form = ttk.LabelFrame(
            self,
            text="Registrar nueva rutina",
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
            width=25,
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
            text="Descripción:",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_descripcion = ttk.Entry(
            form,
            width=25,
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
            width=25,
        )

        self._ent_objetivo.grid(
            row=1,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Duración (semanas):",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_duracion = ttk.Entry(
            form,
            width=25,
        )

        self._ent_duracion.grid(
            row=2,
            column=1,
            padx=5,
            pady=3,
        )

        self._lbl_modo = ttk.Label(
            form,
            text="Modo: crear rutina",
            foreground="#555555",
        )

        self._lbl_modo.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            padx=5,
            pady=5,
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
            text="Cancelar",
            command=self._cancelar_edicion_rutina,
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
        Carga las rutinas en la tabla principal.
        """
        if hasattr(self, "_tree_frame"):
            self._tree_frame.destroy()

        self._tree_frame = ttk.Frame(self)

        self._tree_frame.pack(
            fill="x",
            expand=False,
            pady=10,
        )

        columnas = (
            "ID",
            "Nombre",
            "Descripción",
            "Objetivo",
            "Nivel",
            "Duración",
        )

        self._tree = ttk.Treeview(
            self._tree_frame,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=8,
        )

        for columna in columnas:
            self._tree.heading(
                columna,
                text=columna,
            )

        self._tree.column(
            "ID",
            width=70,
            minwidth=60,
            anchor="center",
        )

        self._tree.column(
            "Nombre",
            width=180,
            minwidth=120,
            anchor="w",
        )

        self._tree.column(
            "Descripción",
            width=300,
            minwidth=180,
            anchor="w",
        )

        self._tree.column(
            "Objetivo",
            width=180,
            minwidth=120,
            anchor="w",
        )

        self._tree.column(
            "Nivel",
            width=120,
            minwidth=100,
            anchor="center",
        )

        self._tree.column(
            "Duración",
            width=100,
            minwidth=90,
            anchor="center",
        )

        scrollbar_y = ttk.Scrollbar(
            self._tree_frame,
            orient="vertical",
            command=self._tree.yview,
        )

        scrollbar_x = ttk.Scrollbar(
            self._tree_frame,
            orient="horizontal",
            command=self._tree.xview,
        )

        self._tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        self._tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scrollbar_y.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        scrollbar_x.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self._tree_frame.rowconfigure(
            0,
            weight=1,
        )

        self._tree_frame.columnconfigure(
            0,
            weight=1,
        )

        self._tree.bind(
            "<<TreeviewSelect>>",
            self._al_seleccionar_rutina,
        )

        self._tree.bind(
            "<Double-1>",
            self._editar_con_doble_click,
        )

        try:
            rutinas = (
                self._control_rutinas.listar()
            )

            self._rutinas_disponibles = list(
                rutinas
            )

            for rutina in self._rutinas_disponibles:
                nivel = getattr(
                    rutina.nivel,
                    "value",
                    str(rutina.nivel),
                )

                descripcion = getattr(
                    rutina,
                    "descripcion",
                    "",
                )

                objetivo = getattr(
                    rutina,
                    "objetivo",
                    "",
                )

                duracion = getattr(
                    rutina,
                    "duracion_semanas",
                    "",
                )

                self._tree.insert(
                    "",
                    "end",
                    values=(
                        rutina.id_rutina,
                        rutina.nombre,
                        descripcion,
                        objetivo,
                        nivel,
                        f"{duracion} sem",
                    ),
                )

            if hasattr(
                self,
                "_cb_rutina_ejercicios",
            ):
                self._cargar_rutinas_en_combo()

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar rutinas: {error}"
            )

    def mostrarEjerciciosRutina(self) -> None:
        """
        Construye la sección de ejercicios.
        """
        frame = ttk.LabelFrame(
            self,
            text="Ejercicios de la rutina",
            padding=10,
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=5,
        )

        ttk.Label(
            frame,
            text="Rutina:",
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="w",
        )

        self._cb_rutina_ejercicios = ttk.Combobox(
            frame,
            state="readonly",
            width=35,
        )

        self._cb_rutina_ejercicios.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        self._cb_rutina_ejercicios.bind(
            "<<ComboboxSelected>>",
            self._cargar_ejercicios_asociados,
        )

        ttk.Label(
            frame,
            text="Ejercicio:",
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="w",
        )

        self._cb_ejercicio_rutina = ttk.Combobox(
            frame,
            state="readonly",
            width=35,
        )

        self._cb_ejercicio_rutina.grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        ttk.Button(
            frame,
            text="Cargar datos",
            command=self._cargar_datos_ejercicios,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Button(
            frame,
            text="Agregar ejercicio",
            command=self._agregar_ejercicio_a_rutina,
        ).grid(
            row=1,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Button(
            frame,
            text="Quitar ejercicio",
            command=self._quitar_ejercicio_de_rutina,
        ).grid(
            row=1,
            column=3,
            padx=5,
            pady=5,
        )

        ttk.Label(
            frame,
            text="Ejercicios contenidos en la rutina:",
        ).grid(
            row=2,
            column=0,
            columnspan=4,
            padx=5,
            pady=(10, 2),
            sticky="w",
        )

        columnas = (
            "ID",
            "Nombre",
            "Orden",
        )

        self._tree_ejercicios_rutina = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=7,
        )

        for columna in columnas:
            self._tree_ejercicios_rutina.heading(
                columna,
                text=columna,
            )

        self._tree_ejercicios_rutina.column(
            "ID",
            width=80,
            anchor="center",
        )

        self._tree_ejercicios_rutina.column(
            "Nombre",
            width=260,
            anchor="w",
        )

        self._tree_ejercicios_rutina.column(
            "Orden",
            width=80,
            anchor="center",
        )

        self._tree_ejercicios_rutina.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=5,
            pady=5,
            sticky="nsew",
        )

        self._tree_ejercicios_rutina.bind(
            "<ButtonRelease-1>",
            self._seleccionar_ejercicio_por_clic,
        )

        frame.columnconfigure(
            1,
            weight=1,
        )

        frame.rowconfigure(
            3,
            weight=1,
        )

    def _cargar_datos_ejercicios(self) -> None:
        """
        Carga rutinas y ejercicios.
        """
        if self._control_ejercicios is None:
            self.mostrar_error(
                (
                    "No se recibió el controlador "
                    "de ejercicios."
                )
            )
            return

        try:
            self._rutinas_disponibles = list(
                self._control_rutinas.listar()
            )

            self._ejercicios_disponibles = list(
                self._control_ejercicios.listar()
            )

            self._cargar_rutinas_en_combo()

            self._cb_ejercicio_rutina[
                "values"
            ] = [
                (
                    f"{ejercicio.id_ejercicio} - "
                    f"{ejercicio.nombre}"
                )
                for ejercicio in (
                    self._ejercicios_disponibles
                )
            ]

            if (
                self._id_rutina_vista_previa
                is not None
            ):
                self._seleccionar_rutina_en_combo(
                    self._id_rutina_vista_previa
                )

                self._mostrar_ejercicios_asociados(
                    self._id_rutina_vista_previa
                )

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar datos: {error}"
            )

    def _cargar_rutinas_en_combo(self) -> None:
        """
        Carga rutinas en el Combobox.
        """
        self._cb_rutina_ejercicios[
            "values"
        ] = [
            (
                f"{rutina.id_rutina} - "
                f"{rutina.nombre}"
            )
            for rutina in self._rutinas_disponibles
        ]

    def _obtener_id_desde_combo(
        self,
        combo: ttk.Combobox,
        nombre: str,
    ) -> int:
        """
        Obtiene un ID desde un Combobox.
        """
        valor = combo.get().strip()

        if not valor:
            raise ValueError(
                f"Seleccione {nombre}."
            )

        parte_id = valor.split(
            "-",
            1,
        )[0].strip()

        try:
            id_objeto = int(parte_id)

        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                f"El ID de {nombre} no es válido."
            ) from error

        if id_objeto <= 0:
            raise ValueError(
                f"El ID de {nombre} no es válido."
            )

        return id_objeto

    def _seleccionar_rutina_en_combo(
        self,
        id_rutina: int,
    ) -> None:
        """
        Selecciona una rutina por ID.
        """
        for indice, rutina in enumerate(
            self._rutinas_disponibles
        ):
            if int(rutina.id_rutina) == int(
                id_rutina
            ):
                self._cb_rutina_ejercicios.current(
                    indice
                )
                return

        self._cb_rutina_ejercicios.set("")

    def _seleccionar_rutina_en_tabla(
        self,
        id_rutina: int,
    ) -> None:
        """
        Selecciona una rutina en la tabla.
        """
        for item in self._tree.get_children():
            valores = self._tree.item(
                item,
                "values",
            )

            if not valores:
                continue

            try:
                id_tabla = int(valores[0])

            except (
                TypeError,
                ValueError,
            ):
                continue

            if id_tabla == int(id_rutina):
                self._tree.selection_set(item)
                self._tree.focus(item)
                self._tree.see(item)
                return

    def _obtener_rutina_seleccionada(
        self,
    ) -> int:
        """
        Obtiene el ID de la rutina seleccionada.
        """
        if (
            self._id_rutina_vista_previa
            is not None
        ):
            return int(
                self._id_rutina_vista_previa
            )

        seleccion = self._tree.selection()

        if seleccion:
            valores = self._tree.item(
                seleccion[0],
                "values",
            )

            if valores:
                return int(
                    str(valores[0]).strip()
                )

        return self._obtener_id_desde_combo(
            self._cb_rutina_ejercicios,
            "una rutina",
        )

    def _al_seleccionar_rutina(
        self,
        _evento=None,
    ) -> None:
        """
        Carga una rutina desde la tabla.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            return

        valores = self._tree.item(
            seleccion[0],
            "values",
        )

        if not valores:
            return

        try:
            id_rutina = int(
                str(valores[0]).strip()
            )

        except (
            TypeError,
            ValueError,
        ):
            self.mostrar_error(
                "El ID de la rutina no es válido."
            )
            return

        try:
            rutina = (
                self._control_rutinas
                .buscar_por_id(id_rutina)
            )

            if rutina is None:
                raise ValueError(
                    "No se encontró la rutina."
                )

            self._id_rutina_editando = id_rutina
            self._id_rutina_vista_previa = id_rutina
            self._id_ejercicio_seleccionado = None

            self._ent_nombre.delete(
                0,
                tk.END,
            )

            self._ent_nombre.insert(
                0,
                rutina.nombre,
            )

            self._ent_descripcion.delete(
                0,
                tk.END,
            )

            self._ent_descripcion.insert(
                0,
                rutina.descripcion,
            )

            self._ent_objetivo.delete(
                0,
                tk.END,
            )

            self._ent_objetivo.insert(
                0,
                rutina.objetivo,
            )

            nivel = getattr(
                rutina.nivel,
                "value",
                str(rutina.nivel),
            )

            self._cb_nivel.set(nivel)

            self._ent_duracion.delete(
                0,
                tk.END,
            )

            self._ent_duracion.insert(
                0,
                str(rutina.duracion_semanas),
            )

            self._lbl_modo.config(
                text=(
                    "Modo: editando rutina "
                    f"#{id_rutina}"
                ),
                foreground="#174ea6",
            )

            self._seleccionar_rutina_en_combo(
                id_rutina
            )

            self._mostrar_ejercicios_asociados(
                id_rutina
            )

        except Exception as error:
            self.mostrar_error(
                (
                    f"No se pudo cargar la rutina "
                    f"{id_rutina}: {error}"
                )
            )

    def _cargar_ejercicios_asociados(
        self,
        _evento=None,
    ) -> None:
        """
        Carga los ejercicios de una rutina.
        """
        try:
            id_rutina = (
                self._obtener_id_desde_combo(
                    self._cb_rutina_ejercicios,
                    "una rutina",
                )
            )

            self._id_rutina_editando = id_rutina
            self._id_rutina_vista_previa = id_rutina
            self._id_ejercicio_seleccionado = None

            self._mostrar_ejercicios_asociados(
                id_rutina
            )

            self._seleccionar_rutina_en_tabla(
                id_rutina
            )

        except ValueError as error:
            self.mostrar_error(str(error))

    def _seleccionar_ejercicio_por_clic(
        self,
        evento,
    ) -> None:
        """
        Guarda el ID de la fila pulsada.
        """
        item_id = (
            self._tree_ejercicios_rutina
            .identify_row(evento.y)
        )

        if not item_id:
            self._id_ejercicio_seleccionado = None
            return

        self._tree_ejercicios_rutina.selection_set(
            item_id
        )

        self._tree_ejercicios_rutina.focus(
            item_id
        )

        valores = (
            self._tree_ejercicios_rutina.item(
                item_id,
                "values",
            )
        )

        if not valores:
            self._id_ejercicio_seleccionado = None
            return

        try:
            texto_id = str(
                valores[0]
            ).strip()

            if not texto_id:
                self._id_ejercicio_seleccionado = None
                return

            id_ejercicio = int(texto_id)

            if id_ejercicio <= 0:
                self._id_ejercicio_seleccionado = None
                return

            self._id_ejercicio_seleccionado = (
                id_ejercicio
            )

        except (
            TypeError,
            ValueError,
        ):
            self._id_ejercicio_seleccionado = None

    def _agregar_ejercicio_a_rutina(self) -> None:
        """
        Agrega un ejercicio a la rutina.
        """
        try:
            id_rutina = (
                self._id_rutina_vista_previa
            )

            if id_rutina is None:
                raise ValueError(
                    "Seleccione una rutina."
                )

            valor_ejercicio = (
                self._cb_ejercicio_rutina
                .get()
                .strip()
            )

            if not valor_ejercicio:
                raise ValueError(
                    "Seleccione un ejercicio."
                )

            parte_id = valor_ejercicio.split(
                "-",
                1,
            )[0].strip()

            id_ejercicio = int(parte_id)

            if id_ejercicio <= 0:
                raise ValueError(
                    (
                        "El ID del ejercicio no "
                        "es válido."
                    )
                )

            ejercicios_actuales = (
                self._control_rutinas
                .listar_ejercicios_de_rutina(
                    id_rutina
                )
            )

            ids_actuales = {
                int(item.id_ejercicio)
                for item in ejercicios_actuales
                if item.id_ejercicio is not None
            }

            if id_ejercicio in ids_actuales:
                raise ValueError(
                    (
                        "El ejercicio ya está asociado "
                        "a esta rutina."
                    )
                )

            administrador_id = (
                self._obtener_id_administrador()
            )

            resultado = (
                self._control_rutinas
                .agregar_ejercicio_a_rutina(
                    id_rutina=id_rutina,
                    id_ejercicio=id_ejercicio,
                    orden=len(
                        ejercicios_actuales
                    ) + 1,
                    usuario_accion=(
                        administrador_id
                    ),
                )
            )

            if not resultado:
                raise ValueError(
                    "No se pudo agregar el ejercicio."
                )

            self.mostrar_mensaje(
                "Ejercicio agregado correctamente."
            )

            self._mostrar_ejercicios_asociados(
                id_rutina
            )

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                (
                    "Error al agregar ejercicio: "
                    f"{error}"
                )
            )

    def _quitar_ejercicio_de_rutina(self) -> None:
        """
        Quita el ejercicio seleccionado.
        """
        try:
            id_rutina = (
                self._id_rutina_vista_previa
            )

            if id_rutina is None:
                raise ValueError(
                    "Seleccione primero una rutina."
                )

            id_ejercicio = (
                self._id_ejercicio_seleccionado
            )

            if id_ejercicio is None:
                raise ValueError(
                    (
                        "Haga clic sobre el ejercicio "
                        "que desea quitar."
                    )
                )

            if not self.confirmar_accion(
                (
                    "¿Quitar el ejercicio "
                    f"{id_ejercicio} de la rutina "
                    f"{id_rutina}?"
                )
            ):
                return

            administrador_id = (
                self._obtener_id_administrador()
            )

            eliminado = (
                self._control_rutinas
                .eliminar_ejercicio_de_rutina(
                    id_rutina=int(id_rutina),
                    id_ejercicio=int(id_ejercicio),
                    usuario_accion=(
                        administrador_id
                    ),
                )
            )

            if eliminado is not True:
                raise ValueError(
                    (
                        "No se eliminó la asociación "
                        f"rutina={id_rutina}, "
                        f"ejercicio={id_ejercicio}."
                    )
                )

            self._id_ejercicio_seleccionado = None

            self.mostrar_mensaje(
                "Ejercicio retirado correctamente."
            )

            self._mostrar_ejercicios_asociados(
                int(id_rutina)
            )

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                (
                    "Error al quitar ejercicio: "
                    f"{error}"
                )
            )

    def _mostrar_ejercicios_asociados(
        self,
        id_rutina: int,
    ) -> None:
        """
        Muestra los ejercicios asociados.
        """
        try:
            id_rutina = int(id_rutina)

        except (
            TypeError,
            ValueError,
        ):
            self.mostrar_error(
                "El ID de la rutina no es válido."
            )
            return

        self._id_rutina_vista_previa = id_rutina
        self._id_ejercicio_seleccionado = None

        for item in (
            self._tree_ejercicios_rutina
            .get_children()
        ):
            self._tree_ejercicios_rutina.delete(
                item
            )

        try:
            ejercicios = (
                self._control_rutinas
                .listar_ejercicios_de_rutina(
                    id_rutina
                )
            )

            if not ejercicios:
                self._tree_ejercicios_rutina.insert(
                    "",
                    "end",
                    values=(
                        "",
                        "La rutina no tiene ejercicios.",
                        "",
                    ),
                )
                return

            for orden, ejercicio in enumerate(
                ejercicios,
                start=1,
            ):
                self._tree_ejercicios_rutina.insert(
                    "",
                    "end",
                    values=(
                        int(ejercicio.id_ejercicio),
                        str(ejercicio.nombre),
                        orden,
                    ),
                )

        except Exception as error:
            self.mostrar_error(
                (
                    "No se pudieron cargar los "
                    "ejercicios de la rutina "
                    f"{id_rutina}: {error}"
                )
            )

    def _editar_con_doble_click(
        self,
        _evento=None,
    ) -> None:
        """
        Edita una rutina con doble clic.
        """
        self.editarRutina()

    def crearRutina(self) -> None:
        """
        Crea una nueva rutina.
        """
        try:
            datos = (
                self._leer_datos_formulario()
            )

            administrador_id = (
                self._obtener_id_administrador()
            )

            self._control_rutinas.crear_rutina(
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                nivel_dificultad=datos["nivel"],
                duracion_estimada=(
                    datos["duracion"]
                ),
                creado_por=administrador_id,
                objetivo=datos["objetivo"],
            )

            self.mostrar_mensaje(
                "Rutina creada exitosamente."
            )

            self._id_rutina_editando = None
            self._id_rutina_vista_previa = None
            self._id_ejercicio_seleccionado = None

            self._limpiar_formulario()
            self.mostrarRutinas()
            self._cargar_datos_ejercicios()
            self._limpiar_vista_previa()

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                (
                    "Error inesperado: "
                    f"{error}"
                )
            )

    def editarRutina(self) -> None:
        """
        Edita la rutina seleccionada.
        """
        if self._id_rutina_editando is None:
            seleccion = self._tree.selection()

            if not seleccion:
                self.mostrar_error(
                    "Seleccione una rutina para editar."
                )
                return

            valores = self._tree.item(
                seleccion[0],
                "values",
            )

            self._id_rutina_editando = int(
                valores[0]
            )

        try:
            datos = (
                self._leer_datos_formulario()
            )

            rutina_original = (
                self._control_rutinas
                .buscar_por_id(
                    self._id_rutina_editando
                )
            )

            if rutina_original is None:
                raise ValueError(
                    "No se encontró la rutina."
                )

            rutina = self._crear_rutina(
                datos,
                rutina_original,
            )

            administrador_id = (
                self._obtener_id_administrador()
            )

            resultado = (
                self._control_rutinas
                .actualizar_rutina(
                    rutina,
                    administrador_id,
                )
            )

            if resultado is None:
                raise ValueError(
                    "No se pudo actualizar la rutina."
                )

            id_rutina = (
                self._id_rutina_editando
            )

            self.mostrar_mensaje(
                "Rutina actualizada correctamente."
            )

            self.mostrarRutinas()
            self._cargar_datos_ejercicios()

            self._id_rutina_editando = id_rutina
            self._id_rutina_vista_previa = id_rutina

            self._seleccionar_rutina_en_combo(
                id_rutina
            )

            self._mostrar_ejercicios_asociados(
                id_rutina
            )

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                (
                    "Error al editar rutina: "
                    f"{error}"
                )
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

        valores = self._tree.item(
            seleccion[0],
            "values",
        )

        id_rutina = int(valores[0])

        if not self.confirmar_accion(
            (
                "¿Eliminar la rutina con ID "
                f"{id_rutina}?"
            )
        ):
            return

        try:
            administrador_id = (
                self._obtener_id_administrador()
            )

            self._control_rutinas.eliminar_rutina(
                id_rutina,
                administrador_id,
            )

            self.mostrar_mensaje(
                "Rutina eliminada correctamente."
            )

            self._id_rutina_editando = None
            self._id_rutina_vista_previa = None
            self._id_ejercicio_seleccionado = None

            self._limpiar_formulario()
            self.mostrarRutinas()
            self._cargar_datos_ejercicios()
            self._limpiar_vista_previa()

        except Exception as error:
            self.mostrar_error(
                f"Error al eliminar: {error}"
            )

    def asignarRutina(self) -> None:
        """
        Asigna una rutina a un cliente.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione una rutina para asignar."
            )
            return

        valores = self._tree.item(
            seleccion[0],
            "values",
        )

        id_rutina = int(valores[0])

        id_cliente = simpledialog.askinteger(
            "Asignar rutina",
            "Ingrese el ID del cliente:",
            parent=self,
            minvalue=1,
        )

        if id_cliente is None:
            return

        observaciones = simpledialog.askstring(
            "Asignar rutina",
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
                (
                    f"Rutina {id_rutina} asignada "
                    f"al cliente {id_cliente}."
                )
            )

        except Exception as error:
            self.mostrar_error(
                (
                    "Error al asignar rutina: "
                    f"{error}"
                )
            )

    def _leer_datos_formulario(self) -> dict:
        """
        Lee y valida el formulario.
        """
        nombre = (
            self._ent_nombre
            .get()
            .strip()
        )

        descripcion = (
            self._ent_descripcion
            .get()
            .strip()
        )

        objetivo = (
            self._ent_objetivo
            .get()
            .strip()
        )

        nivel = (
            self._cb_nivel
            .get()
            .strip()
        )

        duracion_texto = (
            self._ent_duracion
            .get()
            .strip()
        )

        if not nombre:
            raise ValueError(
                "Ingrese el nombre de la rutina."
            )

        if not descripcion:
            raise ValueError(
                "Ingrese la descripción."
            )

        if not objetivo:
            raise ValueError(
                "Ingrese el objetivo."
            )

        if not nivel:
            raise ValueError(
                "Seleccione un nivel."
            )

        if not duracion_texto:
            raise ValueError(
                "Ingrese la duración."
            )

        try:
            duracion = int(
                duracion_texto
            )

        except ValueError as error:
            raise ValueError(
                "La duración debe ser un entero."
            ) from error

        if duracion <= 0:
            raise ValueError(
                (
                    "La duración debe ser "
                    "mayor que cero."
                )
            )

        return {
            "nombre": nombre,
            "descripcion": descripcion,
            "objetivo": objetivo,
            "nivel": nivel,
            "duracion": duracion,
        }

    def _crear_rutina(
        self,
        datos: dict,
        rutina_original: Rutina,
    ) -> Rutina:
        """
        Construye una rutina conservando sus datos.
        """
        return Rutina(
            id_rutina=(
                self._id_rutina_editando
            ),
            nombre=datos["nombre"],
            descripcion=datos["descripcion"],
            objetivo=datos["objetivo"],
            nivel=datos["nivel"],
            duracion_semanas=(
                datos["duracion"]
            ),
            creado_por=(
                rutina_original.creado_por
            ),
            fecha_creacion=(
                rutina_original.fecha_creacion
            ),
            ejercicios=list(
                rutina_original.ejercicios
            ),
        )

    def _cancelar_edicion_rutina(self) -> None:
        """
        Cancela la edición.
        """
        self._id_rutina_editando = None
        self._id_rutina_vista_previa = None
        self._id_ejercicio_seleccionado = None

        self._limpiar_formulario()
        self._limpiar_vista_previa()

        self._cb_rutina_ejercicios.set("")

        seleccion = self._tree.selection()

        if seleccion:
            self._tree.selection_remove(
                seleccion
            )

    def _limpiar_vista_previa(self) -> None:
        """
        Limpia la tabla de ejercicios.
        """
        self._id_ejercicio_seleccionado = None

        if not hasattr(
            self,
            "_tree_ejercicios_rutina",
        ):
            return

        for item in (
            self._tree_ejercicios_rutina
            .get_children()
        ):
            self._tree_ejercicios_rutina.delete(
                item
            )

    def _obtener_id_administrador(self) -> int:
        """
        Obtiene el ID del administrador.
        """
        if self._control_autenticacion is not None:
            usuario_actual = getattr(
                self._control_autenticacion,
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

        ventana = self.winfo_toplevel()

        administrador_actual = getattr(
            ventana,
            "_administrador_actual",
            None,
        )

        if administrador_actual is not None:
            id_usuario = getattr(
                administrador_actual,
                "id_usuario",
                None,
            )

            if id_usuario is not None:
                return int(id_usuario)

        raise ValueError(
            (
                "No se pudo obtener el ID "
                "del administrador."
            )
        )

    def _limpiar_formulario(self) -> None:
        """
        Limpia el formulario.
        """
        self._ent_nombre.delete(
            0,
            tk.END,
        )

        self._ent_descripcion.delete(
            0,
            tk.END,
        )

        self._ent_objetivo.delete(
            0,
            tk.END,
        )

        self._ent_duracion.delete(
            0,
            tk.END,
        )

        self._cb_nivel.set("")

        self._lbl_modo.config(
            text="Modo: crear rutina",
            foreground="#555555",
        )