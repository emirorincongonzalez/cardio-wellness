class EjercicioCardio:
    def __init__(
        self,
        nombre,
        descripcion,
        tipo,
        duracion_minutos,
        intensidad,
        calorias_estimadas,
        creado_por=None,
        id_ejercicio=None,
    ):
        self.id_ejercicio = id_ejercicio
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.duracion_minutos = duracion_minutos
        self.intensidad = intensidad
        self.calorias_estimadas = calorias_estimadas
        self.creado_por = creado_por

    def __repr__(self):
        return (
            f"EjercicioCardio(id_ejercicio={self.id_ejercicio}, "
            f"nombre='{self.nombre}', "
            f"tipo='{self.tipo}', "
            f"duracion_minutos={self.duracion_minutos}, "
            f"intensidad='{self.intensidad}')"
        )