from typing import Optional
from datetime import date

from src.modelos.usuario import Usuario


class Administrador(Usuario):

    def __init__(
        self,
        nombre: str,
        apellido: str,
        correo_electronico: str,
        contrasenia_hash: str,
        edad: int,
        id_usuario: Optional[int] = None,
        fecha_registro: Optional[date] = None,
    ) -> None:
        super().__init__(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo_electronico,
            contrasenia_hash=contrasenia_hash,
            edad=edad,
            tipo_usuario="administrador",
            id_usuario=id_usuario,
            fecha_registro=fecha_registro,
        )

    #==Forzar tipo de usuario==
    def obtener_tipo_usuario(self) -> str:
        return "administrador"

    #==Representacion==
    def __repr__(self) -> str:
        return (
            f"Administrador(id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}')"
        )