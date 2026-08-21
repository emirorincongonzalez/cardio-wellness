from decimal import Decimal

from src.modelos.enums import Intensidad


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

    @property
    def id_ejercicio(self):
        return self._id_ejercicio

    @id_ejercicio.setter
    def id_ejercicio(self, valor):
        self._id_ejercicio = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")

        self._nombre = valor.strip()

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La descripción no puede estar vacía.")

        self._descripcion = valor.strip()

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El tipo no puede estar vacío.")

        self._tipo = valor.strip()

    @property
    def duracion_minutos(self):
        return self._duracion_minutos

    @duracion_minutos.setter
    def duracion_minutos(self, valor):
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "La duración debe ser mayor que cero."
            )

        self._duracion_minutos = valor

    @property
    def intensidad(self):
        return self._intensidad

    @intensidad.setter
    def intensidad(self, valor):
        if isinstance(valor, Intensidad):
            self._intensidad = valor
            return

        if isinstance(valor, str):
            valor_normalizado = valor.strip().upper()

            try:
                self._intensidad = Intensidad[valor_normalizado]
                return
            except KeyError:
                try:
                    self._intensidad = Intensidad(valor_normalizado)
                    return
                except ValueError:
                    pass

        raise ValueError(
            "La intensidad debe ser un valor válido de Intensidad."
        )

    @property
    def calorias_estimadas(self):
        return self._calorias_estimadas

    @calorias_estimadas.setter
    def calorias_estimadas(self, valor):
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor < 0
        ):
            raise ValueError(
                "Las calorías estimadas no pueden ser negativas."
            )

        self._calorias_estimadas = valor

    @property
    def creado_por(self):
        return self._creado_por

    @creado_por.setter
    def creado_por(self, valor):
        if valor is not None and (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "creado_por debe ser un id de usuario válido."
            )

        self._creado_por = valor

    def calcular_calorias(self):
        return float(self.calorias_estimadas)

    def __repr__(self):
        return (
            f"EjercicioCardio(id_ejercicio={self.id_ejercicio}, "
            f"nombre='{self.nombre}', "
            f"tipo='{self.tipo}', "
            f"duracion_minutos={self.duracion_minutos}, "
            f"intensidad='{self.intensidad.value}', "
            f"calorias_estimadas={self.calorias_estimadas})"
        )