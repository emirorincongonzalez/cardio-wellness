from typing import List, Optional
import tkinter as tk
from tkinter import ttk

from src.controladores.control_clientes import ControlClientes
from src.modelos.cliente import Cliente
from src.interfaz.interfaz_base import InterfazBase


class InterfazGestionClientes(InterfazBase):
    """
    Pestania de gestion de clientes.

    Atributos (segun DCD):
        -controlClientes : ControlClientes → Controlador de clientes.

    Metodos (segun DCD):
        +mostrarClientes(): void              -> Carga la lista de clientes.
        +mostrarFormularioCliente(): void     -> Construye el formulario.
        +registrarCliente(): void             -> Registra un nuevo cliente.
        +editarCliente(): void                -> Edita el cliente seleccionado.
        +eliminarCliente(): void              -> Elimina el cliente seleccionado.
        +buscarCliente(): void                -> Busca por nombre o correo.
    """

    def __init__(self, master: tk.Misc, control_clientes: ControlClientes) -> None:
        super().__init__(master, controlador=control_clientes, padding=10)
        self.pack(fill="both", expand=True)

        # Atributos
        self._control_clientes: ControlClientes = control_clientes

        # Construir la vista
        self.mostrarFormularioCliente()
        self.mostrarClientes()

    @property
    def control_clientes(self) -> ControlClientes:
        return self._control_clientes

    # ==========================================================
    # METODOS DEL DCD
    # ==========================================================
    def mostrarFormularioCliente(self) -> None:
        """Construye el formulario para registrar un cliente."""
        form = ttk.LabelFrame(self, text="Registrar Nuevo Cliente", padding=10)
        form.pack(fill="x", pady=5)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self._ent_nombre = ttk.Entry(form, width=20)
        self._ent_nombre.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(form, text="Apellido:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self._ent_apellido = ttk.Entry(form, width=20)
        self._ent_apellido.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(form, text="Correo:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self._ent_correo = ttk.Entry(form, width=20)
        self._ent_correo.grid(row=1, column=1, padx=5, pady=3)

        ttk.Label(form, text="Contrasenia:").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self._ent_contrasenia = ttk.Entry(form, width=20, show="*")
        self._ent_contrasenia.grid(row=1, column=3, padx=5, pady=3)

        ttk.Label(form, text="Edad:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self._ent_edad = ttk.Entry(form, width=20)
        self._ent_edad.grid(row=2, column=1, padx=5, pady=3)

        ttk.Label(form, text="Peso (kg):").grid(row=2, column=2, sticky="w", padx=5, pady=3)
        self._ent_peso = ttk.Entry(form, width=20)
        self._ent_peso.grid(row=2, column=3, padx=5, pady=3)

        ttk.Label(form, text="Altura (m):").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        self._ent_altura = ttk.Entry(form, width=20)
        self._ent_altura.grid(row=3, column=1, padx=5, pady=3)

        ttk.Label(form, text="Objetivo (META):").grid(row=3, column=2, sticky="w", padx=5, pady=3)
        self._ent_objetivo = ttk.Entry(form, width=20)
        self._ent_objetivo.grid(row=3, column=3, padx=5, pady=3)

        frame_btns = ttk.Frame(form)
        frame_btns.grid(row=4, column=3, sticky="e", pady=10)

        ttk.Button(frame_btns, text="Registrar", command=self.registrarCliente).pack(side="left", padx=3)
        ttk.Button(frame_btns, text="Eliminar", command=self.eliminarCliente).pack(side="left", padx=3)

        # Busqueda
        frame_buscar = ttk.Frame(self, padding=5)
        frame_buscar.pack(fill="x", pady=5)

        ttk.Label(frame_buscar, text="Buscar por correo:").pack(side="left", padx=5)
        self._ent_buscar = ttk.Entry(frame_buscar, width=25)
        self._ent_buscar.pack(side="left", padx=5)
        ttk.Button(frame_buscar, text="Buscar", command=self.buscarCliente).pack(side="left", padx=5)

    def mostrarClientes(self) -> None:
        """Carga la lista de clientes en la tabla."""
        if hasattr(self, "_tree"):
            for item in self._tree.get_children():
                self._tree.delete(item)
        else:
            cols = ("ID", "Nombre", "Correo", "Peso", "Objetivo")
            self._tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
            for col in cols:
                self._tree.heading(col, text=col)
                self._tree.column(col, width=140)
            self._tree.pack(fill="both", expand=True, pady=10)

        try:
            clientes: List[Cliente] = self._control_clientes.listar()
            for c in clientes:
                self._tree.insert("", "end", values=(
                    c.id_usuario, c.obtener_nombre_completo(),
                    c.correo_electronico, c.peso, c.objetivo,
                ))
        except Exception as e:
            self.mostrar_error(f"Error al cargar clientes: {e}")

    def registrarCliente(self) -> None:
        """Registra un nuevo cliente con los datos del formulario."""
        try:
            cliente = self._control_clientes.registrar_cliente(
                nombre=self._ent_nombre.get().strip(),
                apellido=self._ent_apellido.get().strip(),
                correo_electronico=self._ent_correo.get().strip(),
                contrasenia_plana=self._ent_contrasenia.get(),
                edad=int(self._ent_edad.get().strip()),
                peso=float(self._ent_peso.get().strip()),
                altura=float(self._ent_altura.get().strip()),
                objetivo=self._ent_objetivo.get().strip(),
            )
            self.mostrar_mensaje(f"Cliente {cliente.obtener_nombre_completo()} registrado.")
            self._limpiar_formulario()
            self.mostrarClientes()
        except ValueError as e:
            self.mostrar_error(str(e))
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {e}")

    def editarCliente(self) -> None:
        """Edita el cliente seleccionado en la tabla."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione un cliente para editar.")
            return
        # Aqui iría la logica de edicion (abrir formulario modal, etc.)
        self.mostrar_mensaje("Funcionalidad de edición pendiente de implementar.")

    def eliminarCliente(self) -> None:
        """Elimina el cliente seleccionado en la tabla."""
        seleccion = self._tree.selection()
        if not seleccion:
            self.mostrar_error("Seleccione un cliente para eliminar.")
            return

        id_cliente = self._tree.item(seleccion[0])["values"][0]
        if not self.confirmar_accion(f"¿Eliminar al cliente con ID {id_cliente}?"):
            return

        try:
            self._control_clientes.eliminar_cliente(int(id_cliente))
            self.mostrar_mensaje("Cliente eliminado correctamente.")
            self.mostrarClientes()
        except Exception as e:
            self.mostrar_error(f"Error al eliminar: {e}")

    def buscarCliente(self) -> None:
        """Busca un cliente por correo."""
        correo = self._ent_buscar.get().strip()
        if not correo:
            self.mostrar_error("Ingrese un correo para buscar.")
            return
        try:
            cliente = self._control_clientes.buscar_por_correo(correo)
            if cliente is None:
                self.mostrar_mensaje("No se encontró ningún cliente con ese correo.")
                return
            self.mostrar_mensaje(
                f"Encontrado: {cliente.obtener_nombre_completo()} - {cliente.correo_electronico}"
            )
        except Exception as e:
            self.mostrar_error(f"Error al buscar: {e}")

    # ==========================================================
    # METODOS AUXILIARES
    # ==========================================================
    def _limpiar_formulario(self) -> None:
        for entry in (
            self._ent_nombre, self._ent_apellido, self._ent_correo,
            self._ent_contrasenia, self._ent_edad, self._ent_peso,
            self._ent_altura, self._ent_objetivo,
        ):
            entry.delete(0, tk.END)
