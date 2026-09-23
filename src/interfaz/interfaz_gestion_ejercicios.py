from typing import List

import tkinter as tk
from tkinter import ttk

from src.controladores.control_ejercicios import (
    ControlEjercicios,
)
from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
)
from src.interfaz.interfaz_base import InterfazBase


class InterfazGestionEjercicios(InterfazBase):
    """
    Pestaña de gestión de ejercicios.
    """

    def __init__(
        self,
        master: tk.Misc,
        control_ejercicios: ControlEjercicios,
    ) -> None:
        super().__init__(
            master,
            controlador=control_ejercicios,
            padding=10,
        )

        self.pack(
            fill="both",
            expand=True,
        )

        self._control_ejercicios = (
            control_ejercicios
        )

        self._id_ejercicio_editando = None

        self.mostrarFormularioEjercicio()
        self.mostrarEjercicios()

    @property
    def control_ejercicios(
        self,
    ) -> ControlEjercicios:
        return self._control_ejercicios

    def mostrarFormularioEjercicio(self) -> None:
        """
        Construye el formulario.
        """
        form = ttk.LabelFrame(
            self,
            text="Registrar Nuevo Ejercicio",
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
            text="Tipo:",
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._cb_tipo = ttk.Combobox(
            form,
            values=(
                "LISS",
                "HIIT",
                "Cardio funcional",
            ),
            width=18,
        )

        self._cb_tipo.grid(
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
            text="Duracion (min):",
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_duracion = ttk.Entry(
            form,
            width=20,
        )

        self._ent_duracion.grid(
            row=1,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Intensidad:",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._cb_intensidad = ttk.Combobox(
            form,
            values=(
                "BAJA",
                "MEDIA",
                "ALTA",
            ),
            state="readonly",
            width=18,
        )

        self._cb_intensidad.grid(
            row=2,
            column=1,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Calorias estimadas:",
        ).grid(
            row=2,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_calorias = ttk.Entry(
            form,
            width=20,
        )

        self._ent_calorias.grid(
            row=2,
            column=3,
            padx=5,
            pady=3,
        )

        self._lbl_modo = ttk.Label(
            form,
            text="Modo: crear ejercicio",
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
            command=self.crearEjercicio,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Editar",
            command=self.editarEjercicio,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Cancelar",
            command=self._cancelar_edicion,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Eliminar",
            command=self.eliminarEjercicio,
        ).pack(
            side="left",
            padx=3,
        )

        frame_buscar = ttk.Frame(
            self,
            padding=5,
        )

        frame_buscar.pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            frame_buscar,
            text="Buscar por nombre:",
        ).pack(
            side="left",
            padx=5,
        )

        self._ent_buscar = ttk.Entry(
            frame_buscar,
            width=25,
        )

        self._ent_buscar.pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            frame_buscar,
            text="Buscar",
            command=self.buscarEjercicio,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            frame_buscar,
            text="Mostrar todos",
            command=self.mostrarEjercicios,
        ).pack(
            side="left",
            padx=5,
        )

    def mostrarEjercicios(self) -> None:
        """
        Carga los ejercicios en la tabla.
        """
        if hasattr(self, "_tree"):
            for item in self._tree.get_children():
                self._tree.delete(item)

        else:
            columnas = (
                "ID",
                "Nombre",
                "Tipo",
                "Descripcion",
                "Duracion",
                "Intensidad",
                "Calorias",
            )

            self._tree = ttk.Treeview(
                self,
                columns=columnas,
                show="headings",
                selectmode="browse",
                height=10,
            )

            anchos = {
                "ID": 60,
                "Nombre": 150,
                "Tipo": 130,
                "Descripcion": 180,
                "Duracion": 100,
                "Intensidad": 110,
                "Calorias": 110,
            }

            for columna in columnas:
                self._tree.heading(
                    columna,
                    text=columna,
                )

                self._tree.column(
                    columna,
                    width=anchos[columna],
                    anchor="center",
                )

            self._tree.pack(
                fill="both",
                expand=True,
                pady=10,
            )

            self._tree.bind(
                "<<TreeviewSelect>>",
                self._cargar_ejercicio_seleccionado,
            )

            self._tree.bind(
                "<Double-1>",
                self._editar_con_doble_click,
            )

        try:
            ejercicios: List[
                EjercicioCardio
            ] = self._control_ejercicios.listar()

            for ejercicio in ejercicios:
                intensidad = getattr(
                    ejercicio.intensidad,
                    "value",
                    str(ejercicio.intensidad),
                )

                descripcion = getattr(
                    ejercicio,
                    "descripcion",
                    "",
                )

                self._tree.insert(
                    "",
                    "end",
                    values=(
                        ejercicio.id_ejercicio,
                        ejercicio.nombre,
                        ejercicio.tipo,
                        descripcion,
                        ejercicio.duracion_minutos,
                        intensidad,
                        ejercicio.calorias_estimadas,
                    ),
                )

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar ejercicios: {error}"
            )

    def _cargar_ejercicio_seleccionado(
        self,
        _evento=None,
    ) -> None:
        """
        Carga los datos del ejercicio seleccionado.
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
            self._id_ejercicio_editando = int(
                valores[0]
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            self.mostrar_error(
                "El ID del ejercicio no es válido."
            )
            return

        self._ent_nombre.delete(
            0,
            tk.END,
        )

        self._ent_nombre.insert(
            0,
            valores[1],
        )

        self._cb_tipo.set(
            valores[2],
        )

        self._ent_descripcion.delete(
            0,
            tk.END,
        )

        self._ent_descripcion.insert(
            0,
            valores[3],
        )

        self._ent_duracion.delete(
            0,
            tk.END,
        )

        self._ent_duracion.insert(
            0,
            valores[4],
        )

        self._cb_intensidad.set(
            valores[5],
        )

        self._ent_calorias.delete(
            0,
            tk.END,
        )

        self._ent_calorias.insert(
            0,
            valores[6],
        )

        self._lbl_modo.config(
            text=(
                "Modo: editando ejercicio "
                f"#{self._id_ejercicio_editando}"
            ),
            foreground="#174ea6",
        )

    def _editar_con_doble_click(
        self,
        _evento=None,
    ) -> None:
        """
        Permite editar haciendo doble clic.
        """
        self.editarEjercicio()

    def crearEjercicio(self) -> None:
        """
        Crea un ejercicio nuevo.
        """
        try:
            datos = self._leer_datos_formulario()

            self._control_ejercicios.crear_ejercicio(
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                duracion_minutos=(
                    datos["duracion_minutos"]
                ),
                calorias_estimadas=(
                    datos["calorias_estimadas"]
                ),
                tipo=datos["tipo"],
                intensidad=datos["intensidad"],
            )

            self.mostrar_mensaje(
                "Ejercicio creado exitosamente."
            )

            self._limpiar_formulario()
            self.mostrarEjercicios()

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                f"Error inesperado: {error}"
            )

    def editarEjercicio(self) -> None:
        """
        Edita el ejercicio seleccionado.
        """
        if self._id_ejercicio_editando is None:
            seleccion = self._tree.selection()

            if not seleccion:
                self.mostrar_error(
                    "Seleccione un ejercicio para editar."
                )
                return

            valores = self._tree.item(
                seleccion[0],
                "values",
            )

            try:
                self._id_ejercicio_editando = int(
                    valores[0]
                )

            except (
                TypeError,
                ValueError,
            ):
                self.mostrar_error(
                    "El ID del ejercicio no es válido."
                )
                return

        try:
            datos = self._leer_datos_formulario()

            ejercicio = self._crear_ejercicio(
                datos
            )

            resultado = (
                self._control_ejercicios
                .actualizar_ejercicio(
                    ejercicio
                )
            )

            if resultado is False:
                raise ValueError(
                    "No se pudo actualizar el ejercicio."
                )

            self.mostrar_mensaje(
                "Ejercicio actualizado correctamente."
            )

            self._limpiar_formulario()
            self.mostrarEjercicios()

        except ValueError as error:
            self.mostrar_error(str(error))

        except Exception as error:
            self.mostrar_error(
                f"Error al editar ejercicio: {error}"
            )

    def eliminarEjercicio(self) -> None:
        """
        Elimina el ejercicio seleccionado.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione un ejercicio para eliminar."
            )
            return

        valores = self._tree.item(
            seleccion[0],
            "values",
        )

        try:
            id_ejercicio = int(valores[0])

        except (
            TypeError,
            ValueError,
        ):
            self.mostrar_error(
                "El ID del ejercicio no es válido."
            )
            return

        if not self.confirmar_accion(
            "¿Eliminar el ejercicio con "
            f"ID {id_ejercicio}?"
        ):
            return

        try:
            self._control_ejercicios.eliminar_ejercicio(
                id_ejercicio
            )

            self.mostrar_mensaje(
                "Ejercicio eliminado correctamente."
            )

            self._limpiar_formulario()
            self.mostrarEjercicios()

        except Exception as error:
            self.mostrar_error(
                f"Error al eliminar: {error}"
            )

    def buscarEjercicio(self) -> None:
        """
        Busca ejercicios por nombre.
        """
        texto = (
            self._ent_buscar
            .get()
            .strip()
            .lower()
        )

        if not texto:
            self.mostrarEjercicios()
            return

        for item in self._tree.get_children():
            self._tree.delete(item)

        try:
            ejercicios = (
                self._control_ejercicios.listar()
            )

            for ejercicio in ejercicios:
                if texto in (
                    ejercicio.nombre.lower()
                ):
                    intensidad = getattr(
                        ejercicio.intensidad,
                        "value",
                        str(ejercicio.intensidad),
                    )

                    descripcion = getattr(
                        ejercicio,
                        "descripcion",
                        "",
                    )

                    self._tree.insert(
                        "",
                        "end",
                        values=(
                            ejercicio.id_ejercicio,
                            ejercicio.nombre,
                            ejercicio.tipo,
                            descripcion,
                            ejercicio.duracion_minutos,
                            intensidad,
                            ejercicio.calorias_estimadas,
                        ),
                    )

        except Exception as error:
            self.mostrar_error(
                f"Error al buscar: {error}"
            )

    def _leer_datos_formulario(self) -> dict:
        """
        Lee y valida los datos del formulario.
        """
        nombre = (
            self._ent_nombre
            .get()
            .strip()
        )

        tipo = (
            self._cb_tipo
            .get()
            .strip()
        )

        descripcion = (
            self._ent_descripcion
            .get()
            .strip()
        )

        duracion_texto = (
            self._ent_duracion
            .get()
            .strip()
        )

        intensidad = (
            self._cb_intensidad
            .get()
            .strip()
        )

        calorias_texto = (
            self._ent_calorias
            .get()
            .strip()
        )

        if not nombre:
            raise ValueError(
                "Ingrese el nombre del ejercicio."
            )

        if not tipo:
            raise ValueError(
                "Seleccione el tipo."
            )

        if not descripcion:
            raise ValueError(
                "Ingrese la descripción."
            )

        if not duracion_texto:
            raise ValueError(
                "Ingrese la duración."
            )

        if not intensidad:
            raise ValueError(
                "Seleccione la intensidad."
            )

        if not calorias_texto:
            raise ValueError(
                "Ingrese las calorías estimadas."
            )

        try:
            duracion = int(
                duracion_texto
            )

        except ValueError as error:
            raise ValueError(
                "La duración debe ser un entero."
            ) from error

        try:
            calorias = float(
                calorias_texto
            )

        except ValueError as error:
            raise ValueError(
                "Las calorías deben ser numéricas."
            ) from error

        if duracion <= 0:
            raise ValueError(
                "La duración debe ser mayor "
                "que cero."
            )

        if calorias <= 0:
            raise ValueError(
                "Las calorías deben ser mayores "
                "que cero."
            )

        return {
            "nombre": nombre,
            "tipo": tipo,
            "descripcion": descripcion,
            "duracion_minutos": duracion,
            "intensidad": intensidad,
            "calorias_estimadas": calorias,
        }

    def _crear_ejercicio(
        self,
        datos: dict,
    ) -> EjercicioCardio:
        """
        Crea el objeto para actualizar.
        """
        ejercicio = EjercicioCardio(
            nombre=datos["nombre"],
            descripcion=datos["descripcion"],
            tipo=datos["tipo"],
            duracion_minutos=(
                datos["duracion_minutos"]
            ),
            intensidad=datos["intensidad"],
            calorias_estimadas=(
                datos["calorias_estimadas"]
            ),
        )

        ejercicio.id_ejercicio = (
            self._id_ejercicio_editando
        )

        return ejercicio

    def _cancelar_edicion(self) -> None:
        """
        Cancela la edición actual.
        """
        self._limpiar_formulario()

        self._tree.selection_remove(
            self._tree.selection()
        )

    def _limpiar_formulario(self) -> None:
        """
        Limpia el formulario.
        """
        for entry in (
            self._ent_nombre,
            self._ent_descripcion,
            self._ent_duracion,
            self._ent_calorias,
        ):
            entry.delete(
                0,
                tk.END,
            )

        self._cb_tipo.set("")
        self._cb_intensidad.set("")

        self._id_ejercicio_editando = None

        self._lbl_modo.config(
            text="Modo: crear ejercicio",
            foreground="#555555",
        )