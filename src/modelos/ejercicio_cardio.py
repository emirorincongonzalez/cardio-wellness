from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from src.modelos.enums import Intensidad


class EjercicioCardio:
    """
    Representa un ejercicio cardiovascular.
    """

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tipo: str,
        duracion_minutos: Union[
            int,
            float,
            Decimal,
        ],
        intensidad: Union[
            Intensidad,
            str,
        ],
        calorias_estimadas: Union[
            int,
            float,
            Decimal,
        ],
        creado_por: Optional[int] = None,
        id_ejercicio: Optional[int] = None,
    ) -> None:
        self.id_ejercicio = id_ejercicio
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.duracion_minutos = duracion_minutos
        self.intensidad = intensidad
        self.calorias_estimadas = (
            calorias_estimadas
        )
        self.creado_por = creado_por

    @property
    def id_ejercicio(self) -> Optional[int]:
        return self._id_ejercicio

    @id_ejercicio.setter
    def id_ejercicio(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    "El ID del ejercicio debe ser "
                    "un entero positivo."
                )

        self._id_ejercicio = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "El nombre no puede estar vacío."
            )

        self._nombre = valor.strip()

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "La descripción no puede estar vacía."
            )

        self._descripcion = valor.strip()

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "El tipo no puede estar vacío."
            )

        self._tipo = valor.strip()

    @property
    def duracion_minutos(self) -> int:
        return self._duracion_minutos

    @duracion_minutos.setter
    def duracion_minutos(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(
                valor,
                (
                    int,
                    float,
                    Decimal,
                ),
            )
        ):
            raise ValueError(
                "La duración debe ser numérica."
            )

        try:
            duracion = Decimal(str(valor))

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "La duración no es válida."
            ) from error

        if duracion <= Decimal("0"):
            raise ValueError(
                "La duración debe ser mayor "
                "que cero."
            )

        if duracion != duracion.to_integral_value():
            raise ValueError(
                "La duración debe ser un número entero."
            )

        self._duracion_minutos = int(duracion)

    @property
    def intensidad(self) -> Intensidad:
        return self._intensidad

    @intensidad.setter
    def intensidad(
        self,
        valor: Union[
            Intensidad,
            str,
        ],
    ) -> None:
        if isinstance(valor, Intensidad):
            self._intensidad = valor
            return

        if isinstance(valor, str):
            valor_normalizado = valor.strip().upper()

            try:
                self._intensidad = Intensidad[
                    valor_normalizado
                ]
                return

            except KeyError:
                pass

            try:
                self._intensidad = Intensidad(
                    valor_normalizado
                )
                return

            except ValueError:
                pass

        raise ValueError(
            "La intensidad debe ser un valor "
            "válido de Intensidad."
        )

    @property
    def calorias_estimadas(self) -> Decimal:
        return self._calorias_estimadas

    @calorias_estimadas.setter
    def calorias_estimadas(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(
                valor,
                (
                    int,
                    float,
                    Decimal,
                ),
            )
        ):
            raise ValueError(
                "Las calorías deben ser numéricas."
            )

        try:
            calorias = Decimal(str(valor))

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Las calorías no son válidas."
            ) from error

        if calorias < Decimal("0"):
            raise ValueError(
                "Las calorías no pueden ser negativas."
            )

        self._calorias_estimadas = calorias.quantize(
            Decimal("0.01")
        )

    @property
    def creado_por(self) -> Optional[int]:
        return self._creado_por

    @creado_por.setter
    def creado_por(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    "creado_por debe ser un ID "
                    "de usuario válido."
                )

        self._creado_por = valor

    def calcular_calorias(self) -> float:
        """
        Devuelve las calorías como float.
        """
        return float(
            self.calorias_estimadas
        )

    def actualizar_datos(
        self,
        nombre: str,
        descripcion: str,
        tipo: str,
        duracion_minutos: Union[
            int,
            float,
            Decimal,
        ],
        intensidad: Union[
            Intensidad,
            str,
        ],
        calorias_estimadas: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        """
        Actualiza los datos del ejercicio.
        """
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.duracion_minutos = duracion_minutos
        self.intensidad = intensidad
        self.calorias_estimadas = (
            calorias_estimadas
        )

    def __repr__(self) -> str:
        intensidad = getattr(
            self.intensidad,
            "value",
            str(self.intensidad),
        )

        return (
            "EjercicioCardio("
            f"id_ejercicio={self.id_ejercicio}, "
            f"nombre='{self.nombre}', "
            f"tipo='{self.tipo}', "
            "duracion_minutos="
            f"{self.duracion_minutos}, "
            f"intensidad='{intensidad}', "
            "calorias_estimadas="
            f"{self.calorias_estimadas}"
            ")"
        )