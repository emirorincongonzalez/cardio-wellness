from typing import List

import tkinter as tk
from tkinter import ttk

from src.controladores.control_ejercicios import ControlEjercicios
from src.interfaz.interfaz_base import InterfazBase
from src.modelos.ejercicio_cardio import EjercicioCardio


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

        self._control_ejercicios = control_ejercicios
        self._id_ejercicio_editando = None
        self._descripciones_ejercicios = {}
        self._ejercicios_por_id = {}

        self.mostrarFormularioEjercicio()
        self.mostrarEjercicios()

    @property
    def control_ejercicios(
        self,
    ) -> ControlEjercicios:
        return self._control_ejercicios

    def mostrarFormularioEjercicio(self) -> None:
        """
        Construye el formulario de ejercicios.
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

        etiquetas = (
            ("Nombre:", 0, 0),
            ("Tipo:", 0, 2),
            ("Descripcion:", 1, 0),
            ("Duracion (min):", 1, 2),
            ("Intensidad:", 2, 0),
            ("Calorias estimadas:", 2, 2),
        )

        for texto, fila, columna in etiquetas:
            ttk.Label(
                form,
                text=texto,
            ).grid(
                row=fila,
                column=columna,
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

        botones = ttk.Frame(form)
        botones.grid(
            row=3,
            column=3,
            sticky="e",
            pady=10,
        )

        ttk.Button(
            botones,
            text="Crear",
            command=self.crearEjercicio,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            botones,
            text="Editar",
            command=self.editarEjercicio,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            botones,
            text="Cancelar",
            command=self._cancelar_edicion,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            botones,
            text="Eliminar",
            command=self.eliminarEjercicio,
        ).pack(
            side="left",
            padx=3,
        )

        buscar = ttk.Frame(
            self,
            padding=5,
        )
        buscar.pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            buscar,
            text="Buscar por nombre:",
        ).pack(
            side="left",
            padx=5,
        )

        self._ent_buscar = ttk.Entry(
            buscar,
            width=25,
        )
        self._ent_buscar.pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buscar,
            text="Buscar",
            command=self.buscarEjercicio,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buscar,
            text="Mostrar todos",
            command=self.mostrarEjercicios,
        ).pack(
            side="left",
            padx=5,
        )

    def _insertar_ejercicio(
        self,
        ejercicio: EjercicioCardio,
    ) -> None:
        """
        Inserta un ejercicio en la tabla y conserva
        su objeto completo para mostrar y editar datos.
        """
        intensidad = getattr(
            ejercicio.intensidad,
            "value",
            str(ejercicio.intensidad),
        )

        descripcion = str(
            getattr(
                ejercicio,
                "descripcion",
                "",
            )
        )

        if "_descripciones_ejercicios" not in self.__dict__:
            self._descripciones_ejercicios = {}

        if "_ejercicios_por_id" not in self.__dict__:
            self._ejercicios_por_id = {}

        self._descripciones_ejercicios[
            ejercicio.id_ejercicio
        ] = descripcion

        self._ejercicios_por_id[
            ejercicio.id_ejercicio
        ] = ejercicio

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

    def mostrarEjercicios(self) -> None:
        """
        Carga ejercicios en la tabla.
        """
        if "_tree" in self.__dict__:
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
                "Descripcion": 280,
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
                    anchor=(
                        "w"
                        if columna == "Descripcion"
                        else "center"
                    ),
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

        try:
            ejercicios: List[EjercicioCardio] = (
                self._control_ejercicios.listar()
            )

            self._descripciones_ejercicios = {}
            self._ejercicios_por_id = {}

            for ejercicio in ejercicios:
                self._insertar_ejercicio(ejercicio)

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar ejercicios: {error}"
            )

    def crearEjercicio(self) -> None:
        """
        Crea un ejercicio.
        """
        try:
            datos = self._leer_datos_formulario()

            self._control_ejercicios.crear_ejercicio(
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                tipo=datos["tipo"],
                duracion_minutos=datos[
                    "duracion_minutos"
                ],
                intensidad=datos["intensidad"],
                calorias_estimadas=datos[
                    "calorias_estimadas"
                ],
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
        Actualiza el ejercicio seleccionado.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione un ejercicio para editar."
            )
            return

        datos_item = self._tree.item(
            seleccion[0]
        )

        valores = datos_item.get(
            "values",
            (),
        )

        if not valores:
            self.mostrar_error(
                "No se pudo obtener el ejercicio seleccionado."
            )
            return

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

        ejercicio = self._ejercicios_por_id.get(
            id_ejercicio
        )

        if ejercicio is None:
            self.mostrar_error(
                "No se encontró el ejercicio seleccionado."
            )
            return

        try:
            datos = self._leer_datos_formulario()

            ejercicio.nombre = datos["nombre"]
            ejercicio.descripcion = datos["descripcion"]
            ejercicio.tipo = datos["tipo"]
            ejercicio.duracion_minutos = (
                datos["duracion_minutos"]
            )
            ejercicio.intensidad = datos["intensidad"]
            ejercicio.calorias_estimadas = (
                datos["calorias_estimadas"]
            )

            self._control_ejercicios.actualizar_ejercicio(
                ejercicio
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
            seleccion[0]
        ).get(
            "values",
            (),
        )

        if not valores:
            self.mostrar_error(
                "El ID del ejercicio no es válido."
            )
            return

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
            f"Eliminar el ejercicio con ID {id_ejercicio}?"
        ):
            return

        try:
            self._control_ejercicios.eliminar_ejercicio(
                id_ejercicio
            )

            self.mostrar_mensaje(
                "Ejercicio eliminado correctamente."
            )

            self.mostrarEjercicios()

            campos = {
                "_ent_nombre",
                "_ent_descripcion",
                "_ent_duracion",
                "_ent_calorias",
                "_cb_tipo",
                "_cb_intensidad",
            }

            if campos.issubset(self.__dict__):
                self._limpiar_formulario()

        except Exception as error:
            self.mostrar_error(
                f"Error al eliminar: {error}"
            )

    def buscarEjercicio(self) -> None:
        """
        Busca ejercicios por nombre.
        """
        texto = self._ent_buscar.get().strip().lower()

        if not texto:
            self.mostrarEjercicios()
            return

        for item in self._tree.get_children():
            self._tree.delete(item)

        try:
            ejercicios = self._control_ejercicios.listar()

            self._descripciones_ejercicios = {}
            self._ejercicios_por_id = {}

            for ejercicio in ejercicios:
                if texto in ejercicio.nombre.lower():
                    self._insertar_ejercicio(ejercicio)

        except Exception as error:
            self.mostrar_error(
                f"Error al buscar: {error}"
            )

    def _cargar_ejercicio_seleccionado(
        self,
        _evento=None,
    ) -> None:
        """
        Carga el ejercicio seleccionado en el formulario.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            return

        valores = self._tree.item(
            seleccion[0]
        ).get(
            "values",
            (),
        )

        if not valores:
            return

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

        ejercicio = self._ejercicios_por_id.get(
            id_ejercicio
        )

        if ejercicio is None:
            self.mostrar_error(
                "No se encontró el ejercicio seleccionado."
            )
            return

        self._id_ejercicio_editando = id_ejercicio

        self._ent_nombre.delete(0, tk.END)
        self._ent_nombre.insert(0, ejercicio.nombre)

        self._ent_descripcion.delete(0, tk.END)
        self._ent_descripcion.insert(
            0,
            ejercicio.descripcion,
        )

        self._cb_tipo.set(ejercicio.tipo)

        self._ent_duracion.delete(0, tk.END)
        self._ent_duracion.insert(
            0,
            str(ejercicio.duracion_minutos),
        )

        intensidad = getattr(
            ejercicio.intensidad,
            "value",
            str(ejercicio.intensidad),
        )
        self._cb_intensidad.set(intensidad)

        self._ent_calorias.delete(0, tk.END)
        self._ent_calorias.insert(
            0,
            str(ejercicio.calorias_estimadas),
        )

        if "_lbl_modo" in self.__dict__:
            self._lbl_modo.config(
                text=(
                    "Modo: editando ejercicio "
                    f"#{id_ejercicio}"
                ),
                foreground="#174ea6",
            )

    def _leer_datos_formulario(self) -> dict:
        """
        Lee y valida los campos del formulario.
        """
        nombre = self._ent_nombre.get().strip()
        tipo = self._cb_tipo.get().strip()
        descripcion = self._ent_descripcion.get().strip()
        duracion_texto = self._ent_duracion.get().strip()
        intensidad = self._cb_intensidad.get().strip()
        calorias_texto = self._ent_calorias.get().strip()

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
            duracion = int(duracion_texto)

        except ValueError as error:
            raise ValueError(
                "La duración debe ser un entero."
            ) from error

        try:
            calorias = float(calorias_texto)

        except ValueError as error:
            raise ValueError(
                "Las calorías deben ser numéricas."
            ) from error

        if duracion <= 0:
            raise ValueError(
                "La duración debe ser mayor que cero."
            )

        if calorias <= 0:
            raise ValueError(
                "Las calorías deben ser mayores que cero."
            )

        return {
            "nombre": nombre,
            "tipo": tipo,
            "descripcion": descripcion,
            "duracion_minutos": duracion,
            "intensidad": intensidad,
            "calorias_estimadas": calorias,
        }

    def _cancelar_edicion(self) -> None:
        """
        Cancela la edición actual.
        """
        self._limpiar_formulario()

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
            entry.delete(0, tk.END)

        self._cb_tipo.set("")
        self._cb_intensidad.set("")
        self._id_ejercicio_editando = None

        if "_lbl_modo" in self.__dict__:
            self._lbl_modo.config(
                text="Modo: crear ejercicio",
                foreground="#555555",
            )