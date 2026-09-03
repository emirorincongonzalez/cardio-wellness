from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from src.servicios.gestor_seguridad import GestorSeguridad


class Usuario(ABC):
    def __init__(
        self,
        nombre: str,
        apellido: str,
        correo_electronico: str,
        contrasenia_hash: str,
        edad: int,
        tipo_usuario: str = "cliente",
        id_usuario: Optional[int] = None,
        fecha_registro: Optional[date] = None,
    ) -> None:
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.correo_electronico = correo_electronico
        self.contrasenia_hash = contrasenia_hash
        self.edad = edad
        self.tipo_usuario = tipo_usuario
        self.fecha_registro = fecha_registro or date.today()

    @property
    def id_usuario(self) -> Optional[int]:
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, valor: Optional[int]) -> None:
        self._id_usuario = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El apellido no puede estar vacío.")
        self._apellido = valor.strip()

    @property
    def correo_electronico(self) -> str:
        return self._correo_electronico

    @correo_electronico.setter
    def correo_electronico(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                "El correo electrónico no puede estar vacío."
            )
        self._correo_electronico = valor.strip()

    @property
    def contrasenia_hash(self) -> str:
        return self._contrasenia_hash

    @contrasenia_hash.setter
    def contrasenia_hash(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                "El hash de la contraseña no puede estar vacío."
            )
        self._contrasenia_hash = valor

    @property
    def edad(self) -> int:
        return self._edad

    @edad.setter
    def edad(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("La edad debe ser un entero mayor que cero.")
        self._edad = valor

    @property
    def tipo_usuario(self) -> str:
        return self._tipo_usuario

    @tipo_usuario.setter
    def tipo_usuario(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                "El tipo de usuario no puede estar vacío."
            )
        self._tipo_usuario = valor.strip().lower()

    @property
    def fecha_registro(self) -> date:
        return self._fecha_registro

    @fecha_registro.setter
    def fecha_registro(self, valor: Optional[date]) -> None:
        self._fecha_registro = valor

#==Metodos abstractos==#
    @abstractmethod
    def obtener_tipo_usuario(self) -> str:
        pass

#==Metodos concretos==#
    def actualizar_datos_personales(
            self,
            nombre: str,
            apellido: str,
            correo: str,
            edad: int
    ) -> None:
        self.nombre = nombre
        self.apellido = apellido
        self.correo_electronico = correo
        self.edad = edad

    def cambiar_contrasenia(self, contrasenia_actual: str, nueva_contrasenia: str) -> bool:
        if not isinstance(nueva_contrasenia, str) or not nueva_contrasenia:
            raise ValueError(
                "La nueva contraseña no puede estar vacía."
            )

        contrasenia_correcta = GestorSeguridad.verificar_contrasenia(
            contrasenia_actual,
            self.contrasenia_hash,
        )

        if not contrasenia_correcta:
            return False

        self.contrasenia_hash = GestorSeguridad.generar_hash(
            nueva_contrasenia
        )

        return True

    def obtener_nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"tipo='{self.tipo_usuario}')"
        )
