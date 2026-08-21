from datetime import date
from decimal import Decimal

from src.modelos.usuario import Usuario


class Cliente(Usuario):

    def __init__(
        self,
        nombre,
        apellido,
        correo_electronico,
        contrasenia_hash,
        edad,
        peso,
        altura,
        objetivo,
        id_usuario=None,
        fecha_registro=None,
        fecha_ingreso=None,
    ):
        super().__init__(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo_electronico,
            contrasenia_hash=contrasenia_hash,
            edad=edad,
            tipo_usuario="cliente",
            id_usuario=id_usuario,
            fecha_registro=fecha_registro,
        )

        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.fecha_ingreso = fecha_ingreso

    @property
    def peso(self):
        return self._peso

    @peso.setter
    def peso(self, valor):
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError("El peso debe ser mayor que cero.")

        self._peso = valor

    @property
    def altura(self):
        return self._altura

    @altura.setter
    def altura(self, valor):
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError("La altura debe ser mayor que cero.")

        self._altura = valor

    @property
    def objetivo(self):
        return self._objetivo

    @objetivo.setter
    def objetivo(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El objetivo no puede estar vacío.")

        self._objetivo = valor.strip()

    @property
    def fecha_ingreso(self):
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        self._fecha_ingreso = valor or date.today()

    def obtener_tipo_usuario(self):
        return "cliente"

    def __repr__(self):
        return (
            f"Cliente(id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"peso={self.peso}, "
            f"altura={self.altura}, "
            f"objetivo='{self.objetivo}')"
        )