from decimal import Decimal
from datetime import date
from typing import Optional

from src.modelos.usuario import Usuario


class Cliente(Usuario):

    def __init__(
        self,
        nombre: str,
        apellido: str,
        correo_electronico: str,
        contrasenia_hash: str,
        edad: int,
        peso: float,
        altura: float,
        objetivo: str,
        id_usuario: Optional[int] = None,
        fecha_registro: Optional[date] = None,
        fecha_ingreso: Optional[date] = None,
    ) -> None:
        super().__init__(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo_electronico,
            contrasenia_hash=contrasenia_hash,
            edad=edad,
            tipo_usuario="cliente", #forzar el tipo de usuario a cliente
            id_usuario=id_usuario,
            fecha_registro=fecha_registro,
        )

        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.fecha_ingreso = fecha_ingreso

#==Propiedades==
    @property
    def peso(self) -> Decimal:
        return self._peso

    @peso.setter
    def peso(self, valor: float) -> None:
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError("El peso debe ser mayor que cero.")

        self._peso = Decimal(str(valor))

    @property
    def altura(self) -> Decimal:
        return self._altura

    @altura.setter
    def altura(self, valor: float) -> None:
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError("La altura debe ser mayor que cero.")

        self._altura = Decimal(str(valor))

    @property
    def objetivo(self) -> str:
        return self._objetivo

    @objetivo.setter
    def objetivo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El objetivo no puede estar vacío.")

        self._objetivo = valor.strip()

    @property
    def fecha_ingreso(self) -> date:
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor: Optional[date]) -> None:
        self._fecha_ingreso = valor if valor is not None else date.today()

#==Metodos de DCD==
    def actualizar_peso(self, nuevo_peso: float) -> None:
        self.peso = nuevo_peso

    def actualizar_objetivo(self, nuevo_objetivo: str) -> None:
        self.objetivo = nuevo_objetivo

#==Implementacion de metodo abstracto==
    def obtener_tipo_usuario(self) -> str:
        return "cliente"

#==Representacion==
    def __repr__(self) -> str:
        return (
            f"Cliente(id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"peso={self.peso}, "
            f"altura={self.altura}, "
            f"objetivo='{self.objetivo}', "
            f"fecha_ingreso={self.fecha_ingreso}"
            f")"
        )