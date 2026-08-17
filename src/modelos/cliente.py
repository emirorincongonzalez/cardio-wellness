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
        tipo_usuario="cliente",
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
            tipo_usuario=tipo_usuario,
            id_usuario=id_usuario,
            fecha_registro=fecha_registro,
        )

        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.fecha_ingreso = fecha_ingreso

    def __repr__(self):
        return (
            f"Cliente(id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"peso={self.peso}, "
            f"altura={self.altura}, "
            f"objetivo='{self.objetivo}')"
        )