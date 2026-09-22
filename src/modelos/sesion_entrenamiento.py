from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from src.modelos.enums import Intensidad


class SesionEntrenamiento:
    """
    Representa una sesión de entrenamiento realizada
    por un cliente dentro de una rutina.
    """

    def __init__(
        self,
        fecha: date,
        duracion_real: int,
        intensidad_real: Union[
            Intensidad,
            str,
        ],
        calorias_quemadas: Union[
            int,
            float,
            Decimal,
        ],
        observaciones: str = "",
        completada: bool = False,
        id_sesion: Optional[int] = None,
        id_cliente: Optional[int] = None,
        id_rutina: Optional[int] = None,
        nombre_ejercicio: str = "",
    ) -> None:
        self.id_sesion = id_sesion
        self.id_cliente = id_cliente
        self.id_rutina = id_rutina
        self.fecha = fecha
        self.nombre_ejercicio = nombre_ejercicio
        self.duracion_real = duracion_real
        self.intensidad_real = intensidad_real
        self.calorias_quemadas = calorias_quemadas
        self.observaciones = observaciones
        self.completada = completada

    @property
    def id_sesion(self) -> Optional[int]:
        return self._id_sesion

    @id_sesion.setter
    def id_sesion(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if isinstance(valor, bool):
                raise ValueError(
                    "El ID de sesión debe ser entero."
                )

            if not isinstance(valor, int) or valor <= 0:
                raise ValueError(
                    "El ID de sesión debe ser positivo."
                )

        self._id_sesion = valor

    @property
    def id_cliente(self) -> Optional[int]:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if isinstance(valor, bool):
                raise ValueError(
                    "El ID de cliente debe ser entero."
                )

            if not isinstance(valor, int) or valor <= 0:
                raise ValueError(
                    "El ID de cliente debe ser positivo."
                )

        self._id_cliente = valor

    @property
    def id_rutina(self) -> Optional[int]:
        return self._id_rutina

    @id_rutina.setter
    def id_rutina(
        self,
        valor: Optional[int],
    ) -> None:
        """
        Puede ser None para sesiones antiguas.
        """
        if valor is not None:
            if isinstance(valor, bool):
                raise ValueError(
                    "El ID de rutina debe ser entero."
                )

            if not isinstance(valor, int) or valor <= 0:
                raise ValueError(
                    "El ID de rutina debe ser positivo."
                )

        self._id_rutina = valor

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(
        self,
        valor: date,
    ) -> None:
        if isinstance(valor, datetime):
            valor = valor.date()

        if not isinstance(valor, date):
            raise ValueError(
                "La fecha debe ser un objeto date."
            )

        self._fecha = valor

    @property
    def nombre_ejercicio(self) -> str:
        return self._nombre_ejercicio

    @nombre_ejercicio.setter
    def nombre_ejercicio(
        self,
        valor: str,
    ) -> None:
        """
        Nombre del ejercicio realizado.
        """
        if valor is None:
            self._nombre_ejercicio = ""
            return

        if not isinstance(valor, str):
            raise ValueError(
                "El nombre del ejercicio debe ser texto."
            )

        nombre = valor.strip()

        if len(nombre) > 100:
            raise ValueError(
                "El nombre del ejercicio no puede superar "
                "100 caracteres."
            )

        self._nombre_ejercicio = nombre

    @property
    def duracion_real(self) -> int:
        return self._duracion_real

    @duracion_real.setter
    def duracion_real(
        self,
        valor: int,
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "La duración debe ser un entero."
            )

        try:
            duracion = int(valor)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "La duración debe ser un entero."
            ) from error

        if duracion <= 0:
            raise ValueError(
                "La duración debe ser mayor que cero."
            )

        self._duracion_real = duracion

    @property
    def intensidad_real(self) -> Intensidad:
        return self._intensidad_real

    @intensidad_real.setter
    def intensidad_real(
        self,
        valor: Union[
            Intensidad,
            str,
        ],
    ) -> None:
        if isinstance(valor, Intensidad):
            self._intensidad_real = valor
            return

        if not isinstance(valor, str):
            raise ValueError(
                "La intensidad debe ser válida."
            )

        texto = valor.strip().upper()

        try:
            self._intensidad_real = Intensidad(texto)
        except ValueError as error:
            raise ValueError(
                f"Intensidad inválida: {valor!r}"
            ) from error

    @property
    def calorias_quemadas(self) -> Decimal:
        return self._calorias_quemadas

    @calorias_quemadas.setter
    def calorias_quemadas(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if isinstance(valor, bool):
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
                "Las calorías deben ser numéricas."
            ) from error

        if calorias < Decimal("0"):
            raise ValueError(
                "Las calorías no pueden ser negativas."
            )

        self._calorias_quemadas = calorias

    @property
    def observaciones(self) -> str:
        return self._observaciones

    @observaciones.setter
    def observaciones(
        self,
        valor: str,
    ) -> None:
        self._observaciones = (
            valor.strip()
            if isinstance(valor, str)
            else ""
        )

    @property
    def completada(self) -> bool:
        return self._completada

    @completada.setter
    def completada(
        self,
        valor: bool,
    ) -> None:
        if not isinstance(valor, bool):
            raise ValueError(
                "Completada debe ser un booleano."
            )

        self._completada = valor

    def registrar_resultado(self) -> None:
        """
        Marca la sesión como completada.
        """
        self.completada = True

    def marcar_como_completada(self) -> None:
        """
        Marca la sesión como completada.
        """
        self.completada = True

    def obtener_resumen(self) -> str:
        """
        Devuelve un resumen legible de la sesión.
        """
        estado = (
            "Completada"
            if self.completada
            else "Pendiente"
        )

        rutina = (
            str(self.id_rutina)
            if self.id_rutina is not None
            else "Sin rutina"
        )

        ejercicio = (
            self.nombre_ejercicio
            or "Sin ejercicio"
        )

        return (
            f"Sesion {self.id_sesion} | "
            f"Cliente: {self.id_cliente} | "
            f"Rutina: {rutina} | "
            f"Ejercicio: {ejercicio} | "
            f"Fecha: {self.fecha} | "
            f"Duracion: {self.duracion_real} min | "
            f"Intensidad: "
            f"{self.intensidad_real.value} | "
            f"Calorias: "
            f"{self.calorias_quemadas:.2f} | "
            f"Estado: {estado}"
        )

    def __repr__(self) -> str:
        return (
            "SesionEntrenamiento("
            f"id_sesion={self.id_sesion}, "
            f"id_cliente={self.id_cliente}, "
            f"id_rutina={self.id_rutina}, "
            f"fecha={self.fecha}, "
            f"nombre_ejercicio="
            f"'{self.nombre_ejercicio}', "
            f"duracion_real={self.duracion_real}, "
            "intensidad_real="
            f"'{self.intensidad_real.value}', "
            f"calorias_quemadas="
            f"{self.calorias_quemadas}, "
            f"completada={self.completada}"
            ")"
        )