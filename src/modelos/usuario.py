from datetime import date


class Usuario:
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

    def __repr__(self):
        return (
            f"Usuario(id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"tipo='{self.tipo_usuario}')"
        )