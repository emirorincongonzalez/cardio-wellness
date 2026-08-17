class Rutina:
    def __init__(
        self,
        nombre,
        descripcion,
        objetivo,
        nivel,
        duracion_semanas,
        creado_por=None,
        id_rutina=None,
        fecha_creacion=None,
    ):
        self.id_rutina = id_rutina
        self.nombre = nombre
        self.descripcion = descripcion
        self.objetivo = objetivo
        self.nivel = nivel
        self.duracion_semanas = duracion_semanas
        self.creado_por = creado_por
        self.fecha_creacion = fecha_creacion

    def __repr__(self):
        return (
            f"Rutina(id_rutina={self.id_rutina}, "
            f"nombre='{self.nombre}', "
            f"objetivo='{self.objetivo}', "
            f"nivel='{self.nivel}', "
            f"duracion_semanas={self.duracion_semanas})"
        )