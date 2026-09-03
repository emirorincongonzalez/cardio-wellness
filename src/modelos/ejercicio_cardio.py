from decimal import Decimal
from typing import Optional

from src.modelos.enums import Intensidad


class EjercicioCardio:

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tipo: str,
        duracion_minutos: int,
        intensidad: Intensidad,
        calorias_estimadas: float,
        creado_por: Optional[int] = None,
        id_ejercicio: Optional[int] = None,
    ) -> None:
        self.id_ejercicio = id_ejercicio
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.duracion_minutos = duracion_minutos
        self.intensidad = intensidad
        self.calorias_estimadas = calorias_estimadas
        self.creado_por = creado_por

#==Propiedades==
    @property
    def id_ejercicio(self) -> Optional[int]:
        return self._id_ejercicio

    @id_ejercicio.setter
    def id_ejercicio(self, valor: Optional[int]) -> None:
        self._id_ejercicio = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")

        self._nombre = valor.strip()

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La descripción no puede estar vacía.")

        self._descripcion = valor.strip()

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El tipo no puede estar vacío.")

        self._tipo = valor.strip()

    @property
    def duracion_minutos(self) -> int:
        return self._duracion_minutos

    @duracion_minutos.setter
    def duracion_minutos(self, valor: int) -> None:
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "La duración debe ser mayor que cero."
            )

        self._duracion_minutos = int(valor)

    @property
    def intensidad(self) -> Intensidad:
        return self._intensidad

    @intensidad.setter
    def intensidad(self, valor: Intensidad) -> None:
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
    def calorias_estimadas(self) -> Decimal:
        return self._calorias_estimadas

    @calorias_estimadas.setter
    def calorias_estimadas(self, valor: float) -> None:
        if (
            not isinstance(valor, (int, float, Decimal))
            or isinstance(valor, bool)
            or valor < 0
        ):
            raise ValueError(
                "Las calorías estimadas no pueden ser negativas."
            )

        self._calorias_estimadas = Decimal(str(valor))

    @property
    def creado_por(self) -> Optional[int]:
        return self._creado_por

    @creado_por.setter
    def creado_por(self, valor: Optional[int]) -> None:
        if valor is not None and (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "creado_por debe ser un id de usuario válido."
            )

        self._creado_por = valor

#==Metodos==
    def calcular_calorias(self) -> float:
        return float(self.calorias_estimadas)

#==Representacion==
    def __repr__(self):
        return (
            f"EjercicioCardio(id_ejercicio={self.id_ejercicio}, "
            f"nombre='{self.nombre}', "
            f"tipo='{self.tipo}', "
            f"duracion_minutos={self.duracion_minutos}, "
            f"intensidad='{self.intensidad.value}', "
            f"calorias_estimadas={self.calorias_estimadas})"
        )