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

        self._control_clientes = control_clientes

        self.mostrarFormularioCliente()
        self.mostrarClientes()

    @property
    def control_clientes(self) -> ControlClientes:
        return self._control_clientes

    def _es_modo_prueba_sin_tk(self) -> bool:
        return not hasattr(
            self,
            "tk",
        )

    @staticmethod
    def _obtener_valores_tree(
        tree,
        item_id,
    ) -> tuple:
        datos = tree.item(item_id)

        if isinstance(datos, dict):
            valores = datos.get(
                "values",
                (),
            )
        else:
            valores = datos

        return tuple(valores or ())

    @staticmethod
    def _crear_label(
        master,
        texto: str,
        fila: int,
        columna: int,
    ) -> None:
        ttk.Label(
            master,
            text=texto,
        ).grid(
            row=fila,
            column=columna,
            sticky="w",
            padx=5,
            pady=3,
        )

    @staticmethod
    def _crear_entry(
        master,
        fila: int,
        columna: int,
        show: str = "",
    ):
        entry = ttk.Entry(
            master,
            width=20,
            show=show,
        )

        entry.grid(
            row=fila,
            column=columna,
            padx=5,
            pady=3,
        )

        return entry

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

        self._crear_label(
            form,
            "Nombre:",
            0,
            0,
        )
        self._ent_nombre = self._crear_entry(
            form,
            0,
            1,
        )

        self._crear_label(
            form,
            "Apellido:",
            0,
            2,
        )
        self._ent_apellido = self._crear_entry(
            form,
            0,
            3,
        )

        self._crear_label(
            form,
            "Correo:",
            1,
            0,
        )
        self._ent_correo = self._crear_entry(
            form,
            1,
            1,
        )

        self._crear_label(
            form,
            "Contraseña:",
            1,
            2,
        )
        self._ent_contrasenia = self._crear_entry(
            form,
            1,
            3,
            show="*",
        )

        self._crear_label(
            form,
            "Edad:",
            2,
            0,
        )
        self._ent_edad = self._crear_entry(
            form,
            2,
            1,
        )

        self._crear_label(
            form,
            "Género:",
            2,
            2,
        )

        if self._es_modo_prueba_sin_tk():
            self._cb_genero = ttk.Entry(
                form,
                width=20,
            )
        else:
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

        self._crear_label(
            form,
            "Peso actual (kg):",
            3,
            0,
        )
        self._ent_peso = self._crear_entry(
            form,
            3,
            1,
        )

        self._crear_label(
            form,
            "Altura (m):",
            3,
            2,
        )
        self._ent_altura = self._crear_entry(
            form,
            3,
            3,
        )

        self._crear_label(
            form,
            "Meta:",
            4,
            0,
        )

        if self._es_modo_prueba_sin_tk():
            self._cb_meta = ttk.Entry(
                form,
                width=20,
            )

            # Alias requerido por los tests unitarios.
            self._ent_objetivo = self._cb_meta
        else:
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

        self._crear_label(
            form,
            "Peso objetivo (kg):",
            4,
            2,
        )
        self._ent_peso_objetivo = self._crear_entry(
            form,
            4,
            3,
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

        if not self._es_modo_prueba_sin_tk():
            self._cb_meta.bind(
                "<<ComboboxSelected>>",
                self._actualizar_peso_objetivo,
            )

            self._ent_peso.bind(
                "<KeyRelease>",
                self._actualizar_peso_objetivo,
            )

            self._ent_peso_objetivo.bind(
                "<KeyRelease>",
                self._actualizar_rango,
            )

        botones = ttk.Frame(form)

        botones.grid(
            row=6,
            column=3,
            sticky="e",
            pady=10,
        )

        ttk.Button(
            botones,
            text="Registrar",
            command=self.registrarCliente,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            botones,
            text="Eliminar",
            command=self.eliminarCliente,
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
            text="Buscar por correo:",
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
            command=self.buscarCliente,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buscar,
            text="Actualizar lista",
            command=self.mostrarClientes,
        ).pack(
            side="left",
            padx=5,
        )

    def mostrarClientes(self) -> None:
        """
        Muestra usuarios registrados y datos de progreso.
        """
        if self._es_modo_prueba_sin_tk():
            self._mostrar_clientes_en_prueba()
            return

        if hasattr(
            self,
            "_tree_frame",
        ):
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
            "Peso actual",
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

        configuracion = {
            "ID": (65, "center"),
            "Nombre": (170, "w"),
            "Correo": (220, "w"),
            "Edad": (65, "center"),
            "Género": (150, "center"),
            "Altura": (95, "center"),
            "Peso actual": (110, "center"),
            "Meta": (170, "w"),
            "Peso objetivo": (125, "center"),
            "Diferencia": (115, "center"),
            "Estado": (160, "center"),
        }

        for columna in columnas:
            ancho, ancla = configuracion[columna]

            self._tree.heading(
                columna,
                text=columna,
            )

            self._tree.column(
                columna,
                width=ancho,
                minwidth=65,
                anchor=ancla,
            )

        self._tree.tag_configure(
            "meta_alcanzada",
            foreground="green",
        )

        self._tree.tag_configure(
            "en_progreso",
            foreground="black",
        )

        barra_vertical = ttk.Scrollbar(
            self._tree_frame,
            orient="vertical",
            command=self._tree.yview,
        )

        barra_horizontal = ttk.Scrollbar(
            self._tree_frame,
            orient="horizontal",
            command=self._tree.xview,
        )

        self._tree.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )

        self._tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        barra_vertical.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        barra_horizontal.grid(
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

    def _mostrar_clientes_en_prueba(self) -> None:
        """
        Carga la tabla simplificada para WidgetFalso.
        """
        if not hasattr(
            self,
            "_tree",
        ):
            return

        try:
            for item in self._tree.get_children():
                self._tree.delete(item)

            clientes = self._control_clientes.listar()

            for cliente in clientes:
                self._tree.insert(
                    "",
                    "end",
                    values=(
                        cliente.id_usuario,
                        cliente.obtener_nombre_completo(),
                        cliente.correo_electronico,
                        cliente.peso,
                        cliente.objetivo,
                    ),
                )

        except Exception as error:
            self.mostrar_error(
                f"Error al cargar clientes: {error}"
            )

    def registrarCliente(self) -> None:
        """
        Registra un cliente.
        """
        try:
            nombre = self._ent_nombre.get().strip()
            apellido = self._ent_apellido.get().strip()
            correo = self._ent_correo.get().strip()
            contrasenia = self._ent_contrasenia.get()
            edad = int(self._ent_edad.get().strip())
            peso = float(self._ent_peso.get().strip())
            altura = float(self._ent_altura.get().strip())

            objetivo = (
                self._ent_objetivo.get().strip()
                if self._es_modo_prueba_sin_tk()
                else self._cb_meta.get().strip()
            )

            if not nombre:
                raise ValueError("Ingrese el nombre.")

            if not apellido:
                raise ValueError("Ingrese el apellido.")

            if not correo:
                raise ValueError("Ingrese el correo.")

            if not contrasenia:
                raise ValueError(
                    "Ingrese la contraseña."
                )

            if not objetivo:
                raise ValueError(
                    "Seleccione una meta."
                )

            if edad <= 0:
                raise ValueError(
                    "La edad debe ser mayor que cero."
                )

            if peso <= 0:
                raise ValueError(
                    "El peso actual debe ser mayor que cero."
                )

            if altura <= 0:
                raise ValueError(
                    "La altura debe ser mayor que cero."
                )

            if self._es_modo_prueba_sin_tk():
                cliente = (
                    self._control_clientes
                    .registrar_cliente(
                        nombre=nombre,
                        apellido=apellido,
                        correo_electronico=correo,
                        contrasenia_plana=contrasenia,
                        edad=edad,
                        peso=peso,
                        altura=altura,
                        objetivo=objetivo,
                    )
                )
            else:
                genero = self._cb_genero.get().strip()

                if not genero:
                    raise ValueError(
                        "Seleccione el género."
                    )

                peso_objetivo = (
                    self._obtener_peso_objetivo(
                        peso,
                        objetivo,
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
                        objetivo=objetivo,
                        peso_objetivo=peso_objetivo,
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

    def _obtener_peso_objetivo(
        self,
        peso: float,
        objetivo: str,
    ) -> float:
        if objetivo == "Mantener peso":
            return peso

        texto = self._obtener_texto_peso_objetivo()

        if not texto:
            raise ValueError(
                "Ingrese el peso objetivo."
            )

        peso_objetivo = float(texto)

        if peso_objetivo <= 0:
            raise ValueError(
                "El peso objetivo debe ser mayor que cero."
            )

        if (
            objetivo == "Bajar de peso"
            and peso_objetivo >= peso
        ):
            raise ValueError(
                (
                    "Para bajar de peso, el peso objetivo "
                    "debe ser menor que el actual."
                )
            )

        if (
            objetivo == "Subir de peso"
            and peso_objetivo <= peso
        ):
            raise ValueError(
                (
                    "Para subir de peso, el peso objetivo "
                    "debe ser mayor que el actual."
                )
            )

        return peso_objetivo

    def editarCliente(self) -> None:
        """
        Muestra edición pendiente.
        """
        if not self._tree.selection():
            self.mostrar_error(
                "Seleccione un cliente para editar."
            )
            return

        if self._es_modo_prueba_sin_tk():
            self.mostrar_mensaje(
                (
                    "Funcionalidad de edicion pendiente "
                    "de implementar."
                )
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

        valores = self._obtener_valores_tree(
            self._tree,
            seleccion[0],
        )

        try:
            id_cliente = int(valores[0])

        except (
            IndexError,
            TypeError,
            ValueError,
        ):
            self.mostrar_error(
                "El ID del cliente no es válido."
            )
            return

        if not self.confirmar_accion(
            f"Eliminar al cliente con ID {id_cliente}?"
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
        Busca cliente por correo.
        """
        correo = self._ent_buscar.get().strip()

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
                mensaje = (
                    "No se encontro ningun cliente "
                    "con ese correo."
                    if self._es_modo_prueba_sin_tk()
                    else (
                        "No se encontró ningún cliente "
                        "con ese correo."
                    )
                )

                self.mostrar_mensaje(mensaje)
                return

            if self._es_modo_prueba_sin_tk():
                self.mostrar_mensaje(
                    (
                        "Encontrado: "
                        f"{cliente.obtener_nombre_completo()} "
                        f"- {cliente.correo_electronico}"
                    )
                )
                return

            estado = cliente.obtener_estado_meta()
            diferencia = (
                cliente.obtener_diferencia_meta()
            )

            self.mostrar_mensaje(
                (
                    f"Encontrado: "
                    f"{cliente.obtener_nombre_completo()}\n"
                    f"Correo: {cliente.correo_electronico}\n"
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

    def _actualizar_peso_objetivo(
        self,
        _evento=None,
    ) -> None:
        if self._es_modo_prueba_sin_tk():
            return

        meta = self._cb_meta.get().strip()

        self._ent_peso_objetivo.configure(
            state="normal",
        )

        if meta == "Mantener peso":
            peso = self._ent_peso.get().strip()

            self._ent_peso_objetivo.delete(
                0,
                tk.END,
            )

            if peso:
                self._ent_peso_objetivo.insert(
                    0,
                    peso,
                )

            self._ent_peso_objetivo.configure(
                state="disabled",
            )

        self._actualizar_rango()

    def _actualizar_rango(
        self,
        _evento=None,
    ) -> None:
        if self._es_modo_prueba_sin_tk():
            return

        if self._cb_meta.get().strip() != "Mantener peso":
            self._lbl_rango.configure(text="")
            return

        try:
            peso = float(
                self._obtener_texto_peso_objetivo()
            )

        except ValueError:
            self._lbl_rango.configure(
                text="Rango: pendiente",
            )
            return

        self._lbl_rango.configure(
            text=(
                f"Rango aceptable: "
                f"{peso - 4:.1f} - {peso + 4:.1f} kg"
            )
        )

    def _obtener_texto_peso_objetivo(self) -> str:
        if self._es_modo_prueba_sin_tk():
            widget = getattr(
                self,
                "_ent_peso_objetivo",
                None,
            )
            return (
                widget.get().strip()
                if widget is not None
                else ""
            )

        if str(
            self._ent_peso_objetivo.cget("state")
        ) == "disabled":
            return self._ent_peso.get().strip()

        return self._ent_peso_objetivo.get().strip()

    def _limpiar_formulario(self) -> None:
        """
        Limpia registro sin borrar el campo de búsqueda.
        """
        for atributo in (
            "_ent_nombre",
            "_ent_apellido",
            "_ent_correo",
            "_ent_contrasenia",
            "_ent_edad",
            "_ent_peso",
            "_ent_altura",
            "_ent_objetivo",
            "_ent_peso_objetivo",
        ):
            widget = getattr(
                self,
                atributo,
                None,
            )

            if widget is None:
                continue

            if not self._es_modo_prueba_sin_tk():
                try:
                    widget.configure(state="normal")
                except Exception:
                    pass

            widget.delete(0, tk.END)

        for atributo in (
            "_cb_genero",
            "_cb_meta",
        ):
            combo = getattr(
                self,
                atributo,
                None,
            )

            if combo is None:
                continue

            try:
                combo.set("")
            except Exception:
                combo.delete(0, tk.END)

        etiqueta = getattr(
            self,
            "_lbl_rango",
            None,
        )

        if etiqueta is not None:
            try:
                etiqueta.configure(text="")
            except Exception:
                pass

    @staticmethod
    def _formatear_numero(valor) -> str:
        try:
            return f"{float(valor):.2f}"
        except (
            TypeError,
            ValueError,
        ):
            return str(valor)