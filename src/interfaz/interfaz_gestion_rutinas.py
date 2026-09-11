from typing import List
import tkinter as tk
from tkinter import ttk

from src.controladores.control_rutinas import ControlRutinas
from src.modelos.rutina import Rutina
from src.interfaz.interfaz_base import InterfazBase


class InterfazGestionRutinas(InterfazBase):
    """
    Pestania de gestion de rutinas.

    Atributos (segun DCD):
        -controlRutinas : ControlRutinas → Controlador de rutinas.

    Métodos (según DCD):
        +mostrarRutinas(): void             -> Carga la lista de rutinas.
        +mostrarFormularioRutina(): void    -> Construye el formulario.
        +crearRutina(): void                -> Crea una nueva rutina.
        +editarRutina(): void               -> Edita la rutina seleccionada.
        +eliminarRutina(): void             -> Elimina la rutina seleccionada.
        +asignarRutina(): void              -> Asigna la rutina a un cliente.
    """

    def __init__(self, master: tk.Misc, control_rutinas: ControlRutinas) -> None:
        super().__init__(master, controlador=control_rutinas, padding=10)
        self.pack(fill="both", expand=True)

        self._control_rutinas: ControlRutinas = control_rutinas

        self.mostrarFormularioRutina()
        self.mostrarRutinas()

    @property
    def control_rutinas(self) -> ControlRutinas:
        return self._control_rutinas

    # ==========================================================
    # METODOS DEL DCD
    # ==========================================================
    def mostrarFormularioRutina(self) -> None:
        """Construye el formulario para crear una rutina."""
        form = ttk.LabelFrame(self, text="Registrar Nueva Rutina", padding=10)
        form.pack(fill="x", pady=5)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self._ent_nombre = ttk.Entry(form, width=20)
        self._ent_nombre.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(form, text="Nivel:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self._cb_nivel = ttk.Combobox(form, values=["BASICO", "INTERMEDIO", "AVANZADO"], state="readonly", width=18)
        self._cb_nivel.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(form, text="Descripcion:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self._ent_descripcion = ttk.Entry(form, width=20)
        self._ent_descripcion.grid(row=1, column=1, padx=5, pady=3)

        ttk.Label(form, text="Objetivo:").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self._ent_objetivo = ttk.Entry(form, width=20)
        self._ent_objetivo.grid(row=1, column=3, padx=5, pady=3)

        ttk.Label(form, text="Duracion (semanas):").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self._ent_duracion = ttk.Entry(form, width=20)
        self._ent_duracion.grid(row=2, column=1, padx=5, pady=3)

        frame_btns = ttk.Frame(form)
        frame_btns.grid(row=3, column=3, sticky="e", pady=10)

        ttk.Button(frame_btns, text="Crear", command=self.crearRutina).pack(side="left", padx=3)
        ttk.Button(frame_btns, text="Editar", command=self.editarRutina).pack(side="left", padx=3)
        ttk.Button(frame_btns, text="Eliminar", command=self.eliminarRutina).pack(side="left", padx=3)
        ttk.Button(frame_btns, text="Asignar", command=self.asignarRutina).pack(side="left", padx=3)

    def mostrarRutinas(self) -> None:
        """Carga la lista de rutinas en la tabla."""
        if hasattr(self, "_tree"):
            for item in self._tree.get_children():
                self._tree.delete(item)
        else:
            cols = ("ID", "Nombre", "Objetivo", "Nivel", "Duracion")
            self._tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
            for col in cols:
                self._tree.heading(col, text=col)
                self._tree.column(col, width=140)
            self._tree.pack(fill="both", expand=True, pady=10)

        try:
            rutinas: List[Rutina] = self._control_rutinas.listar()
            for r in rutinas:
                self._tree.insert("", "end", values=(
                    r.id_rutina, r.nombre, r.objetivo, r.nivel.value,
                    f"{r.duracion_semanas} sem",
                ))
        except Exception as e:
            self.mostrar_error(f"Error al cargar rutinas: {e}")

    def crearRutina(self) -> None:
        """Crea una nueva rutina con los datos del formulario."""
        try:
            self._control_rutinas.crear_rutina(
                nombre=self._ent_nombre.get().strip(),
                descripcion=self._ent_descripcion.get().strip(),
                objetivo=self._ent_objetivo.get().strip(),
                nivel=self._cb_nivel.get().strip(),
                duracion_semanas=int(self._ent_duracion.get().strip()),
            )
            self.mostrar_mensaje("Rutina creada exitosamente.")
            self._limpiar_formulario()
            self.mostrarRutinas()
        except ValueError as e:
            self.mostrar_error(str(e))
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {e}")

    def editarRutina(self) -> None:
        """Edita la rutina seleccionada."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione una rutina para editar.")
            return
        self.mostrar_mensaje("Funcionalidad de edición pendiente de implementar.")

    def eliminarRutina(self) -> None:
        """Elimina la rutina seleccionada."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione una rutina para eliminar.")
            return

        id_rutina = self._tree.item(seleccion[0])["values"][0]
        if not self.confirmar_accion(f"¿Eliminar la rutina con ID {id_rutina}?"):
            return

        try:
            self._control_rutinas.eliminar_rutina(int(id_rutina))
            self.mostrar_mensaje("Rutina eliminada correctamente.")
            self.mostrarRutinas()
        except Exception as e:
            self.mostrar_error(f"Error al eliminar: {e}")

    def asignarRutina(self) -> None:
        """Asigna la rutina seleccionada a un cliente por ID."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione una rutina para asignar.")
            return

        id_rutina = int(self._tree.item(seleccion[0])["values"][0])

        # Pedir ID del cliente mediante un diálogo simple
        from tkinter import simpledialog
        id_cliente = simpledialog.askinteger(
            "Asignar Rutina",
            "Ingrese el ID del cliente:",
            parent=self,
        )
        if id_cliente is None:
            return

        try:
            self._control_rutinas.asignar_rutina(
                id_cliente=id_cliente,
                id_rutina=id_rutina,
            )
            self.mostrar_mensaje(f"Rutina {id_rutina} asignada al cliente {id_cliente}.")
        except Exception as e:
            self.mostrar_error(f"Error al asignar rutina: {e}")

    def _limpiar_formulario(self) -> None:
        for entry in (self._ent_nombre, self._ent_descripcion, self._ent_objetivo, self._ent_duracion):
            entry.delete(0, tk.END)
        self._cb_nivel.set("")
