import tkinter as tk
import unittest
from unittest.mock import patch

from src.interfaz.interfaz_base import InterfazBase


class ControladorPrueba:
    pass


class TestInterfazBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Crea una única ventana raíz para todas las pruebas.
        """
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        """
        Destruye la ventana raíz al terminar todas las pruebas.
        """
        cls.root.destroy()

    def setUp(self):
        """
        Se ejecuta antes de cada prueba.
        """
        self.controlador = ControladorPrueba()

        self.interfaz = InterfazBase(
            self.root,
            controlador=self.controlador
        )

    def tearDown(self):
        """
        Destruye el Frame después de cada prueba.
        """
        self.interfaz.destroy()

    def test_guardar_y_obtener_controlador(self):
        """
        Verifica que el controlador se guarde y se obtenga correctamente.
        """
        self.assertIs(
            self.interfaz.controlador,
            self.controlador
        )

    @patch("src.interfaz.interfaz_base.messagebox.showinfo")
    def test_mostrar_mensaje(self, mock_showinfo):
        """
        Verifica que mostrar_mensaje llame a showinfo.
        """
        mensaje = "Operación realizada correctamente."

        self.interfaz.mostrar_mensaje(mensaje)

        mock_showinfo.assert_called_once_with(
            "Informacion",
            mensaje
        )

    @patch("src.interfaz.interfaz_base.messagebox.showerror")
    def test_mostrar_error(self, mock_showerror):
        """
        Verifica que mostrar_error llame a showerror.
        """
        mensaje = "Ocurrió un error."

        self.interfaz.mostrar_error(mensaje)

        mock_showerror.assert_called_once_with(
            "Error",
            mensaje
        )

    @patch("src.interfaz.interfaz_base.messagebox.askyesno")
    def test_confirmar_accion_aceptada(self, mock_askyesno):
        """
        Verifica que confirmar_accion devuelva True
        cuando el usuario acepta.
        """
        mock_askyesno.return_value = True
        mensaje = "¿Desea continuar?"

        resultado = self.interfaz.confirmar_accion(mensaje)

        self.assertTrue(resultado)

        mock_askyesno.assert_called_once_with(
            "Confirmar",
            mensaje
        )

    @patch("src.interfaz.interfaz_base.messagebox.askyesno")
    def test_confirmar_accion_rechazada(self, mock_askyesno):
        """
        Verifica que confirmar_accion devuelva False
        cuando el usuario rechaza.
        """
        mock_askyesno.return_value = False
        mensaje = "¿Desea eliminar el registro?"

        resultado = self.interfaz.confirmar_accion(mensaje)

        self.assertFalse(resultado)

        mock_askyesno.assert_called_once_with(
            "Confirmar",
            mensaje
        )


if __name__ == "__main__":
    unittest.main()