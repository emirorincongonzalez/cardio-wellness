from typing import List
import tkinter as tk
from tkinter import ttk

from src.controladores.control_ejercicios import ControlEjercicios
from src.modelos.ejercicio_cardio import EjercicioCardio
from src.interfaz.interfaz_base import InterfazBase


class InterfazGestionEjercicios(InterfazBase):
    """
    Pestania de gestion de ejercicios.

    Atributos (segun DCD):
        -controlEjercicios : ControlEjercicios -> Controlador de ejercicios.

    Metodos (segun DCD):
        +mostrarEjercicios(): void              -> Carga la lista de ejercicios.
        +mostrarFormularioEjercicio(): void     -> Construye el formulario.
        +crearEjercicio(): void                 -> Crea un nuevo ejercicio.
        +editarEjercicio(): void                -> Edita el ejercicio seleccionado.
        +eliminarEjercicio(): void              -> Elimina el ejercicio seleccionado.
        +buscarEjercicio(): void                -> Busca un ejercicio por nombre.
    """

    def __init__(self, master: tk.Misc, control_ejercicios: ControlEjercicios) -> None:
        super().__init__(master, controlador=control_ejercicios, padding=10)
        self.pack(fill="both", expand=True)

        self._control_ejercicios: ControlEjercicios = control_ejercicios

        self.mostrarFormularioEjercicio()
        self.mostrarEjercicios()

    @property
    def control_ejercicios(self) -> ControlEjercicios:
        return self._control_ejercicios

    # ==========================================================
    # METODOS DEL DCD
    # ==========================================================
    def mostrarFormularioEjercicio(self) -> None:
        """Construye el formulario para crear un ejercicio."""
        form = ttk.LabelFrame(self, text="Registrar Nuevo Ejercicio", padding=10)
        form.pack(fill="x", pady=5)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self._ent_nombre = ttk.Entry(form, width=20)
        self._ent_nombre.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(form, text="Tipo:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self._cb_tipo = ttk.Combobox(form, values=["LISS", "HIIT", "Cardio funcional"], width=18)
        self._cb_tipo.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(form, text="Descripcion:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self._ent_descripcion = ttk.Entry(form, width=20)
        self._ent_descripcion.grid(row=1, column=1, padx=5, pady=3)

        ttk.Label(form, text="Duracion (min):").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self._ent_duracion = ttk.Entry(form, width=20)
        self._ent_duracion.grid(row=1, column=3, padx=5, pady=3)

        ttk.Label(form, text="Intensidad:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self._cb_intensidad = ttk.Combobox(form, values=["BAJA", "MEDIA", "ALTA"], state="readonly", width=18)
        self._cb_intensidad.grid(row=2, column=1, padx=5, pady=3)

        ttk.Label(form, text="Calorias estimadas:").grid(row=2, column=2, sticky="w", padx=5, pady=3)
        self._ent_calorias = ttk.Entry(form, width=20)
        self._ent_calorias.grid(row=2, column=3, padx=5, pady=3)

        frame_btns = ttk.Frame(form)
        frame_btns.grid(row=3, column=3, sticky="e", pady=10)

        ttk.Button(frame_btns, text="Crear", command=self.crearEjercicio).pack(side="left", padx=3)
        ttk.Button(frame_btns, text="Editar", command=self.editarEjercicio).pack(side="left", padx=3)
        ttk.Button(frame_btns, text="Eliminar", command=self.eliminarEjercicio).pack(side="left", padx=3)

        # Busqueda
        frame_buscar = ttk.Frame(self, padding=5)
        frame_buscar.pack(fill="x", pady=5)
        ttk.Label(frame_buscar, text="Buscar por nombre:").pack(side="left", padx=5)
        self._ent_buscar = ttk.Entry(frame_buscar, width=25)
        self._ent_buscar.pack(side="left", padx=5)
        ttk.Button(frame_buscar, text="Buscar", command=self.buscarEjercicio).pack(side="left", padx=5)

    def mostrarEjercicios(self) -> None:
        """Carga la lista de ejercicios en la tabla."""
        if hasattr(self, "_tree"):
            for item in self._tree.get_children():
                self._tree.delete(item)
        else:
            cols = ("ID", "Nombre", "Tipo", "Duracion", "Intensidad", "Calorias")
            self._tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
            for col in cols:
                self._tree.heading(col, text=col)
                self._tree.column(col, width=120)
            self._tree.pack(fill="both", expand=True, pady=10)

        try:
            ejercicios: List[EjercicioCardio] = self._control_ejercicios.listar()
            for e in ejercicios:
                self._tree.insert("", "end", values=(
                    e.id_ejercicio, e.nombre, e.tipo,
                    e.duracion_minutos, e.intensidad.value, e.calorias_estimadas,
                ))
        except Exception as e:
            self.mostrar_error(f"Error al cargar ejercicios: {e}")

    def crearEjercicio(self) -> None:
        """Crea un nuevo ejercicio con los datos del formulario."""
        try:
            self._control_ejercicios.crear_ejercicio(
                nombre=self._ent_nombre.get().strip(),
                descripcion=self._ent_descripcion.get().strip(),
                tipo=self._cb_tipo.get().strip(),
                duracion_minutos=int(self._ent_duracion.get().strip()),
                intensidad=self._cb_intensidad.get().strip(),
                calorias_estimadas=float(self._ent_calorias.get().strip()),
            )
            self.mostrar_mensaje("Ejercicio creado exitosamente.")
            self._limpiar_formulario()
            self.mostrarEjercicios()
        except ValueError as e:
            self.mostrar_error(str(e))
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {e}")

    def editarEjercicio(self) -> None:
        """Edita el ejercicio seleccionado."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione un ejercicio para editar.")
            return
        self.mostrar_mensaje("Funcionalidad de edicion pendiente de implementar.")

    def eliminarEjercicio(self) -> None:
        """Elimina el ejercicio seleccionado."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione un ejercicio para eliminar.")
            return

        id_ejercicio = self._tree.item(seleccion[0])["values"][0]
        if not self.confirmar_accion(f"Eliminar el ejercicio con ID {id_ejercicio}?"):
            return

        try:
            self._control_ejercicios.eliminar_ejercicio(int(id_ejercicio))
            self.mostrar_mensaje("Ejercicio eliminado correctamente.")
            self.mostrarEjercicios()
        except Exception as e:
            self.mostrar_error(f"Error al eliminar: {e}")

    def buscarEjercicio(self) -> None:
        """Busca un ejercicio por nombre (busqueda simple en la tabla)."""
        texto = self._ent_buscar.get().strip().lower()
        if not texto:
            self.mostrarEjercicios()
            return

        for item in self._tree.get_children():
            self._tree.delete(item)

        try:
            ejercicios = self._control_ejercicios.listar()
            for e in ejercicios:
                if texto in e.nombre.lower():
                    self._tree.insert("", "end", values=(
                        e.id_ejercicio, e.nombre, e.tipo,
                        e.duracion_minutos, e.intensidad.value, e.calorias_estimadas,
                    ))
        except Exception as e:
            self.mostrar_error(f"Error al buscar: {e}")

    def _limpiar_formulario(self) -> None:
        for entry in (self._ent_nombre, self._ent_descripcion, self._ent_duracion, self._ent_calorias):
            entry.delete(0, tk.END)
        self._cb_tipo.set("")
        self._cb_intensidad.set("")
