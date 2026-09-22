from datetime import date
from typing import Optional


from src.modelos.enums import EstadoAsignacion


class AsignacionRutina:
    """
    Representa la asignación de una rutina a un cliente.
    """

    def __init__(
        self,
        id_cliente: int,
        id_rutina: int,
        fecha_asignacion: date,
        estado: EstadoAsignacion = (
            EstadoAsignacion.ACTIVA
        ),
        observaciones: str = "",
        id_asignacion: Optional[int] = None,
        fecha_finalizacion: Optional[date] = None,
    ) -> None:
        self.id_asignacion = id_asignacion
        self.id_cliente = id_cliente
        self.id_rutina = id_rutina
        self.fecha_asignacion = fecha_asignacion
        self.fecha_finalizacion = fecha_finalizacion
        self.estado = estado
        self.observaciones = observaciones

    @property
    def id_asignacion(self) -> Optional[int]:
        return self._id_asignacion

    @id_asignacion.setter
    def id_asignacion(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if isinstance(valor, bool):
                raise ValueError(
                    "El ID de asignación debe ser entero."
                )

            if not isinstance(valor, int) or valor <= 0:
                raise ValueError(
                    "El ID de asignación debe ser positivo."
                )

        self._id_asignacion = valor

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(
        self,
        valor: int,
    ) -> None:
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
    def id_rutina(self) -> int:
        return self._id_rutina

    @id_rutina.setter
    def id_rutina(
        self,
        valor: int,
    ) -> None:
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
    def fecha_asignacion(self) -> date:
        return self._fecha_asignacion

    @fecha_asignacion.setter
    def fecha_asignacion(
        self,
        valor: date,
    ) -> None:
        if not isinstance(valor, date):
            raise ValueError(
                "La fecha de asignación debe ser una fecha."
            )

        if valor > date.today():
            raise ValueError(
                "La fecha de asignación no puede ser futura."
            )

        self._fecha_asignacion = valor

    @property
    def fecha_finalizacion(
        self,
    ) -> Optional[date]:
        return self._fecha_finalizacion

    @fecha_finalizacion.setter
    def fecha_finalizacion(
        self,
        valor: Optional[date],
    ) -> None:
        if valor is not None:
            if not isinstance(valor, date):
                raise ValueError(
                    "La fecha de finalización debe ser una fecha."
                )

            if valor < self.fecha_asignacion:
                raise ValueError(
                    "La fecha de finalización no puede ser "
                    "anterior a la fecha de asignación."
                )

        self._fecha_finalizacion = valor

    @property
    def estado(self) -> EstadoAsignacion:
        return self._estado

    @estado.setter
    def estado(
        self,
        valor: EstadoAsignacion,
    ) -> None:
        if isinstance(valor, str):
            try:
                valor = EstadoAsignacion(valor)
            except ValueError:
                try:
                    valor = EstadoAsignacion[
                        valor.upper()
                    ]
                except KeyError as error:
                    raise ValueError(
                        f"Estado de asignación inválido: {valor}"
                    ) from error

        if not isinstance(valor, EstadoAsignacion):
            raise ValueError(
                "El estado debe ser un valor válido de "
                "EstadoAsignacion."
            )

        self._estado = valor

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

    def activar(self) -> None:
        """
        Marca la asignación como activa.
        """
        self.estado = EstadoAsignacion.ACTIVA
        self.fecha_finalizacion = None

    def finalizar(self) -> None:
        """
        Marca la asignación como finalizada.
        """
        self.estado = EstadoAsignacion.FINALIZADA
        self.fecha_finalizacion = date.today()

    def cancelar(self) -> None:
        """
        Marca la asignación como cancelada.
        """
        self.estado = EstadoAsignacion.CANCELADA
        self.fecha_finalizacion = date.today()

    def esta_activa(self) -> bool:
        """
        Indica si la asignación está activa.
        """
        return self.estado == EstadoAsignacion.ACTIVA

    def __repr__(self) -> str:
        return (
            "AsignacionRutina("
            f"id_asignacion={self.id_asignacion}, "
            f"id_cliente={self.id_cliente}, "
            f"id_rutina={self.id_rutina}, "
            f"fecha_asignacion="
            f"{self.fecha_asignacion}, "
            f"fecha_finalizacion="
            f"{self.fecha_finalizacion}, "
            f"estado='{self.estado.value}', "
            f"observaciones="
            f"'{self.observaciones}'"
            ")"
        )