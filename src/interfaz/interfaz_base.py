from typing import Optional
import tkinter as tk
from tkinter import messagebox, ttk


class InterfazBase(ttk.Frame):
    """
    Clase base abstracta para todas las interfaces del sistema.
    Proporciona metodos comunes para mostrar mensajes y errores.

    Esta clase NO debe instanciarse directamente; sirve como contrato
    comun para las subclases (InterfazGestionClientes, InterfazProgreso, etc.).
    """

    def __init__(
        self,
        master: tk.Misc,
        controlador: Optional[object] = None,
        **kwargs,
    ) -> None:
        """
        Inicializa la interfaz base.

        Args:
            master: Widget padre (ventana o frame contenedor).
            controlador: Controlador asociado (opcional).
            **kwargs: Argumentos adicionales para ttk.Frame.
        """
        super().__init__(master, **kwargs)
        self._controlador = controlador

    @property
    def controlador(self) -> Optional[object]:
        """Devuelve el controlador asociado a esta interfaz."""
        return self._controlador

    def mostrar_mensaje(self, mensaje: str) -> None:
        """Muestra un mensaje informativo al usuario."""
        messagebox.showinfo("Informacion", mensaje)

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un mensaje de error al usuario."""
        messagebox.showerror("Error", mensaje)

    def confirmar_accion(self, mensaje: str) -> bool:
        """Solicita confirmacion al usuario y devuelve True si acepta."""
        return messagebox.askyesno("Confirmar", mensaje)
