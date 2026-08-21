from abc import ABC, abstractmethod
from datetime import date

from src.servicios.gestor_seguridad import GestorSeguridad


class Usuario(ABC):
    def __init__(
        self,
        nombre,
        apellido,
        correo_electronico,
        contrasenia_hash,
        edad,
        tipo_usuario="cliente",
        id_usuario=None,
        fecha_registro=None,
    ):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.correo_electronico = correo_electronico
        self.contrasenia_hash = contrasenia_hash
        self.edad = edad
        self.tipo_usuario = tipo_usuario
        self.fecha_registro = fecha_registro or date.today()

    @property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, valor):
        self._id_usuario = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def apellido(self):
        return self._apellido

    @apellido.setter
    def apellido(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El apellido no puede estar vacío.")
        self._apellido = valor.strip()

    @property
    def correo_electronico(self):
        return self._correo_electronico

    @correo_electronico.setter
    def correo_electronico(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                "El correo electrónico no puede estar vacío."
            )
        self._correo_electronico = valor.strip()

    @property
    def contrasenia_hash(self):
        return self._contrasenia_hash

    @contrasenia_hash.setter
    def contrasenia_hash(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                "El hash de la contraseña no puede estar vacío."
            )
        self._contrasenia_hash = valor

    @property
    def edad(self):
        return self._edad

    @edad.setter
    def edad(self, valor):
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("La edad debe ser un entero mayor que cero.")
        self._edad = valor

    @property
    def tipo_usuario(self):
        return self._tipo_usuario

    @tipo_usuario.setter
    def tipo_usuario(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                "El tipo de usuario no puede estar vacío."
            )
        self._tipo_usuario = valor.strip().lower()

    @property
    def fecha_registro(self):
        return self._fecha_registro

    @fecha_registro.setter
    def fecha_registro(self, valor):
        self._fecha_registro = valor

    @abstractmethod
    def obtener_tipo_usuario(self):
        """Devuelve el tipo de usuario concreto."""
        pass

    def cambiar_contrasenia(self, contrasenia_actual, nueva_contrasenia):
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

    def obtener_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"tipo='{self.tipo_usuario}')"
        )