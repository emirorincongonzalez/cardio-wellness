from typing import List

import tkinter as tk
from tkinter import ttk

from src.controladores.control_clientes import (
    ControlClientes,
)
from src.interfaz.interfaz_base import InterfazBase
from src.modelos.cliente import Cliente


class InterfazGestionClientes(InterfazBase):
    """
    Pestaña de gestión de clientes.
    """

    GENEROS = (
        "HOMBRE",
        "MUJER",
        "OTRO",
        "PREFIERO NO DECIRLO",
    )

    METAS = (
        "Bajar de peso",
        "Subir de peso",
        "Mantener peso",
    )

    def __init__(
        self,
        master: tk.Misc,
        control_clientes: ControlClientes,
    ) -> None:
        super().__init__(
            master,
            controlador=control_clientes,
            padding=10,
        )

        self.pack(
            fill="both",
            expand=True,
        )

        self._control_clientes = (
            control_clientes
        )

        self.mostrarFormularioCliente()
        self.mostrarClientes()

    @property
    def control_clientes(self) -> ControlClientes:
        return self._control_clientes

    def mostrarFormularioCliente(self) -> None:
        """
        Construye el formulario de registro.
        """
        form = ttk.LabelFrame(
            self,
            text="Registrar nuevo cliente",
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
            text="Apellido:",
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_apellido = ttk.Entry(
            form,
            width=20,
        )

        self._ent_apellido.grid(
            row=0,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Correo:",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_correo = ttk.Entry(
            form,
            width=20,
        )

        self._ent_correo.grid(
            row=1,
            column=1,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Contraseña:",
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_contrasenia = ttk.Entry(
            form,
            width=20,
            show="*",
        )

        self._ent_contrasenia.grid(
            row=1,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Edad:",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_edad = ttk.Entry(
            form,
            width=20,
        )

        self._ent_edad.grid(
            row=2,
            column=1,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Género:",
        ).grid(
            row=2,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._cb_genero = ttk.Combobox(
            form,
            values=self.GENEROS,
            state="readonly",
            width=18,
        )

        self._cb_genero.grid(
            row=2,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Peso actual (kg):",
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_peso = ttk.Entry(
            form,
            width=20,
        )

        self._ent_peso.grid(
            row=3,
            column=1,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Altura (m):",
        ).grid(
            row=3,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_altura = ttk.Entry(
            form,
            width=20,
        )

        self._ent_altura.grid(
            row=3,
            column=3,
            padx=5,
            pady=3,
        )

        ttk.Label(
            form,
            text="Meta:",
        ).grid(
            row=4,
            column=0,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._cb_meta = ttk.Combobox(
            form,
            values=self.METAS,
            state="readonly",
            width=18,
        )

        self._cb_meta.grid(
            row=4,
            column=1,
            padx=5,
            pady=3,
        )

        self._cb_meta.bind(
            "<<ComboboxSelected>>",
            self._actualizar_peso_objetivo,
        )

        ttk.Label(
            form,
            text="Peso objetivo (kg):",
        ).grid(
            row=4,
            column=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_peso_objetivo = ttk.Entry(
            form,
            width=20,
        )

        self._ent_peso_objetivo.grid(
            row=4,
            column=3,
            padx=5,
            pady=3,
        )

        self._lbl_rango = ttk.Label(
            form,
            text="",
            foreground="#555555",
        )

        self._lbl_rango.grid(
            row=5,
            column=2,
            columnspan=2,
            sticky="w",
            padx=5,
            pady=3,
        )

        self._ent_peso.bind(
            "<KeyRelease>",
            self._actualizar_peso_objetivo,
        )

        self._ent_peso_objetivo.bind(
            "<KeyRelease>",
            self._actualizar_rango,
        )

        frame_btns = ttk.Frame(form)

        frame_btns.grid(
            row=6,
            column=3,
            sticky="e",
            pady=10,
        )

        ttk.Button(
            frame_btns,
            text="Registrar",
            command=self.registrarCliente,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            frame_btns,
            text="Eliminar",
            command=self.eliminarCliente,
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
            text="Buscar por correo:",
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
            command=self.buscarCliente,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            frame_buscar,
            text="Actualizar lista",
            command=self.mostrarClientes,
        ).pack(
            side="left",
            padx=5,
        )

    def _actualizar_peso_objetivo(
        self,
        _evento=None,
    ) -> None:
        """
        Actualiza el campo de peso objetivo.
        """
        meta = self._cb_meta.get().strip()

        if meta == "Mantener peso":
            peso_actual = (
                self._ent_peso
                .get()
                .strip()
            )

            self._ent_peso_objetivo.configure(
                state="normal",
            )

            self._ent_peso_objetivo.delete(
                0,
                tk.END,
            )

            if peso_actual:
                self._ent_peso_objetivo.insert(
                    0,
                    peso_actual,
                )

            self._ent_peso_objetivo.configure(
                state="disabled",
            )

        else:
            self._ent_peso_objetivo.configure(
                state="normal",
            )

        self._actualizar_rango()

    def _actualizar_rango(
        self,
        _evento=None,
    ) -> None:
        """
        Muestra el rango de mantenimiento.
        """
        meta = self._cb_meta.get().strip()

        if meta != "Mantener peso":
            self._lbl_rango.configure(
                text="",
            )
            return

        texto = (
            self._obtener_texto_peso_objetivo()
        )

        try:
            peso_objetivo = float(texto)

        except ValueError:
            self._lbl_rango.configure(
                text="Rango: pendiente",
            )
            return

        minimo = peso_objetivo - 4
        maximo = peso_objetivo + 4

        self._lbl_rango.configure(
            text=(
                f"Rango aceptable: "
                f"{minimo:.1f} - {maximo:.1f} kg"
            ),
        )

    def mostrarClientes(self) -> None:
        """
        Carga los clientes en la tabla.
        """
        if hasattr(self, "_tree_frame"):
            self._tree_frame.destroy()

        self._tree_frame = ttk.Frame(self)

        self._tree_frame.pack(
            fill="both",
            expand=True,
            pady=10,
        )

        columnas = (
            "ID",
            "Nombre",
            "Correo",
            "Edad",
            "Género",
            "Altura",
            "Peso",
            "Meta",
            "Peso objetivo",
            "Diferencia",
            "Estado",
        )

        self._tree = ttk.Treeview(
            self._tree_frame,
            columns=columnas,
            show="headings",
            height=10,
        )

        anchos = {
            "ID": 60,
            "Nombre": 170,
            "Correo": 220,
            "Edad": 70,
            "Género": 150,
            "Altura": 90,
            "Peso": 100,
            "Meta": 150,
            "Peso objetivo": 120,
            "Diferencia": 110,
            "Estado": 130,
        }

        for columna in columnas:
            self._tree.heading(
                columna,
                text=columna,
            )

            self._tree.column(
                columna,
                width=anchos[columna],
                minwidth=70,
                anchor="center",
            )

        self._tree.tag_configure(
            "meta_alcanzada",
            foreground="green",
        )

        self._tree.tag_configure(
            "en_progreso",
            foreground="black",
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

        try:
            clientes: List[Cliente] = (
                self._control_clientes.listar()
            )

            for cliente in clientes:
                estado = (
                    cliente.obtener_estado_meta()
                )

                diferencia = (
                    cliente.obtener_diferencia_meta()
                )

                etiqueta = (
                    "meta_alcanzada"
                    if estado == "META ALCANZADA"
                    else "en_progreso"
                )

                self._tree.insert(
                    "",
                    "end",
                    values=(
                        cliente.id_usuario,
                        cliente.obtener_nombre_completo(),
                        cliente.correo_electronico,
                        cliente.edad,
                        cliente.genero,
                        (
                            f"{self._formatear_numero(
                                cliente.altura
                            )} m"
                        ),
                        (
                            f"{self._formatear_numero(
                                cliente.peso
                            )} kg"
                        ),
                        cliente.objetivo,
                        (
                            f"{self._formatear_numero(
                                cliente.peso_objetivo
                            )} kg"
                        ),
                        (
                            f"{self._formatear_numero(
                                diferencia
                            )} kg"
                        ),
                        estado,
                    ),
                    tags=(etiqueta,),
                )

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar clientes: {error}"
            )

    def registrarCliente(self) -> None:
        """
        Registra un nuevo cliente.
        """
        try:
            nombre = (
                self._ent_nombre
                .get()
                .strip()
            )

            apellido = (
                self._ent_apellido
                .get()
                .strip()
            )

            correo = (
                self._ent_correo
                .get()
                .strip()
            )

            contrasenia = (
                self._ent_contrasenia
                .get()
            )

            edad_texto = (
                self._ent_edad
                .get()
                .strip()
            )

            genero = (
                self._cb_genero
                .get()
                .strip()
            )

            peso_texto = (
                self._ent_peso
                .get()
                .strip()
            )

            altura_texto = (
                self._ent_altura
                .get()
                .strip()
            )

            meta = (
                self._cb_meta
                .get()
                .strip()
            )

            peso_objetivo_texto = (
                self._obtener_texto_peso_objetivo()
            )

            if not nombre:
                raise ValueError(
                    "Ingrese el nombre."
                )

            if not apellido:
                raise ValueError(
                    "Ingrese el apellido."
                )

            if not correo:
                raise ValueError(
                    "Ingrese el correo."
                )

            if not contrasenia:
                raise ValueError(
                    "Ingrese la contraseña."
                )

            if not edad_texto:
                raise ValueError(
                    "Ingrese la edad."
                )

            if not genero:
                raise ValueError(
                    "Seleccione el género."
                )

            if not peso_texto:
                raise ValueError(
                    "Ingrese el peso actual."
                )

            if not altura_texto:
                raise ValueError(
                    "Ingrese la altura."
                )

            if not meta:
                raise ValueError(
                    "Seleccione una meta."
                )

            edad = int(edad_texto)
            peso = float(peso_texto)
            altura = float(altura_texto)

            if meta == "Mantener peso":
                peso_objetivo = peso

            else:
                if not peso_objetivo_texto:
                    raise ValueError(
                        "Ingrese el peso objetivo."
                    )

                peso_objetivo = float(
                    peso_objetivo_texto
                )

            if edad <= 0:
                raise ValueError(
                    (
                        "La edad debe ser mayor "
                        "que cero."
                    )
                )

            if peso <= 0:
                raise ValueError(
                    (
                        "El peso actual debe ser "
                        "mayor que cero."
                    )
                )

            if altura <= 0:
                raise ValueError(
                    (
                        "La altura debe ser mayor "
                        "que cero."
                    )
                )

            if peso_objetivo <= 0:
                raise ValueError(
                    (
                        "El peso objetivo debe ser "
                        "mayor que cero."
                    )
                )

            if meta == "Bajar de peso":
                if peso_objetivo >= peso:
                    raise ValueError(
                        (
                            "Para bajar de peso, el "
                            "peso objetivo debe ser "
                            "menor que el actual."
                        )
                    )

            elif meta == "Subir de peso":
                if peso_objetivo <= peso:
                    raise ValueError(
                        (
                            "Para subir de peso, el "
                            "peso objetivo debe ser "
                            "mayor que el actual."
                        )
                    )

            cliente = (
                self._control_clientes
                .registrar_cliente(
                    nombre=nombre,
                    apellido=apellido,
                    correo_electronico=correo,
                    contrasenia_plana=contrasenia,
                    edad=edad,
                    genero=genero,
                    peso=peso,
                    altura=altura,
                    objetivo=meta,
                    peso_objetivo=(
                        peso_objetivo
                    ),
                )
            )

            self.mostrar_mensaje(
                (
                    "Cliente "
                    f"{cliente.obtener_nombre_completo()} "
                    "registrado."
                )
            )

            self._limpiar_formulario()
            self.mostrarClientes()

        except ValueError as error:
            self.mostrar_error(str(error))

        except TypeError as error:
            self.mostrar_error(
                (
                    "El controlador no acepta uno de "
                    f"los parámetros enviados: {error}"
                )
            )

        except Exception as error:
            self.mostrar_error(
                f"Error inesperado: {error}"
            )

    def _obtener_texto_peso_objetivo(self) -> str:
        """
        Obtiene el texto del peso objetivo.
        """
        estado = str(
            self._ent_peso_objetivo.cget(
                "state"
            )
        )

        if estado == "disabled":
            return (
                self._ent_peso
                .get()
                .strip()
            )

        return (
            self._ent_peso_objetivo
            .get()
            .strip()
        )

    def editarCliente(self) -> None:
        """
        Edita el cliente seleccionado.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione un cliente para editar."
            )
            return

        self.mostrar_mensaje(
            "Funcionalidad de edición pendiente."
        )

    def eliminarCliente(self) -> None:
        """
        Elimina el cliente seleccionado.
        """
        seleccion = self._tree.selection()

        if not seleccion:
            self.mostrar_error(
                "Seleccione un cliente para eliminar."
            )
            return

        valores = self._tree.item(
            seleccion[0],
            "values",
        )

        id_cliente = int(valores[0])

        if not self.confirmar_accion(
            (
                "¿Eliminar al cliente con ID "
                f"{id_cliente}?"
            )
        ):
            return

        try:
            self._control_clientes.eliminar_cliente(
                id_cliente
            )

            self.mostrar_mensaje(
                "Cliente eliminado correctamente."
            )

            self.mostrarClientes()

        except Exception as error:
            self.mostrar_error(
                f"Error al eliminar: {error}"
            )

    def buscarCliente(self) -> None:
        """
        Busca un cliente por correo.
        """
        correo = (
            self._ent_buscar
            .get()
            .strip()
        )

        if not correo:
            self.mostrar_error(
                "Ingrese un correo para buscar."
            )
            return

        try:
            cliente = (
                self._control_clientes
                .buscar_por_correo(correo)
            )

            if cliente is None:
                self.mostrar_mensaje(
                    (
                        "No se encontró ningún cliente "
                        "con ese correo."
                    )
                )
                return

            estado = (
                cliente.obtener_estado_meta()
            )

            diferencia = (
                cliente.obtener_diferencia_meta()
            )

            self.mostrar_mensaje(
                (
                    "Encontrado: "
                    f"{cliente.obtener_nombre_completo()}\n"
                    f"Correo: "
                    f"{cliente.correo_electronico}\n"
                    f"Edad: {cliente.edad}\n"
                    f"Género: {cliente.genero}\n"
                    f"Altura: {cliente.altura} m\n"
                    f"Peso actual: {cliente.peso} kg\n"
                    f"Meta: {cliente.objetivo}\n"
                    f"Peso objetivo: "
                    f"{cliente.peso_objetivo} kg\n"
                    f"Diferencia: {diferencia} kg\n"
                    f"Estado: {estado}"
                )
            )

        except Exception as error:
            self.mostrar_error(
                f"Error al buscar: {error}"
            )

    def _limpiar_formulario(self) -> None:
        """
        Limpia el formulario.
        """
        for entry in (
            self._ent_nombre,
            self._ent_apellido,
            self._ent_correo,
            self._ent_contrasenia,
            self._ent_edad,
            self._ent_peso,
            self._ent_altura,
            self._ent_peso_objetivo,
        ):
            entry.configure(
                state="normal",
            )

            entry.delete(
                0,
                tk.END,
            )

        self._cb_genero.set("")
        self._cb_meta.set("")

        self._lbl_rango.configure(
            text="",
        )

    @staticmethod
    def _formatear_numero(
        valor,
    ) -> str:
        """
        Formatea números con dos decimales.
        """
        try:
            return f"{float(valor):.2f}"

        except (
            TypeError,
            ValueError,
        ):
            return str(valor)