from datetime import date
from typing import Optional

from src.modelos.enums import Intensidad


class SesionEntrenamiento:

    def __init__(
        self,
        fecha: date,
        duracion_real: int,
        intensidad_real: Intensidad,
        calorias_quemadas: float,
        observaciones: str = "",
        completada: bool = False,
        id_sesion: Optional[int] = None,
        id_cliente: Optional[int] = None,
    ) -> None:
        self.id_sesion = id_sesion
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.duracion_real = duracion_real
        self.intensidad_real = intensidad_real
        self.calorias_quemadas = calorias_quemadas
        self.observaciones = observaciones
        self.completada = completada

    #==Propiedades==
    @property
    def id_sesion(self) -> Optional[int]:
        return self._id_sesion

    @id_sesion.setter
    def id_sesion(self, valor: Optional[int]) -> None:
        self._id_sesion = valor

    @property
    def id_cliente(self) -> Optional[int]:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: Optional[int]) -> None:
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("El id del cliente debe ser un entero positivo.")
        self._id_cliente = valor

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser un objeto date.")
        self._fecha = valor

    @property
    def duracion_real(self) -> int:
        return self._duracion_real

    @duracion_real.setter
    def duracion_real(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("La duración real debe ser mayor que cero.")
        self._duracion_real = valor

    @property
    def intensidad_real(self) -> Intensidad:
        return self._intensidad_real

    @intensidad_real.setter
    def intensidad_real(self, valor: Intensidad) -> None:
        if not isinstance(valor, Intensidad):
            raise ValueError("La intensidad debe ser un valor válido de Intensidad.")
        self._intensidad_real = valor

    @property
    def calorias_quemadas(self) -> float:
        return self._calorias_quemadas

    @calorias_quemadas.setter
    def calorias_quemadas(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("Las calorías quemadas no pueden ser negativas.")
        self._calorias_quemadas = float(valor)

    @property
    def observaciones(self) -> str:
        return self._observaciones

    @observaciones.setter
    def observaciones(self, valor: str) -> None:
        self._observaciones = valor.strip() if isinstance(valor, str) else ""

    @property
    def completada(self) -> bool:
        return self._completada

    @completada.setter
    def completada(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ValueError("completada debe ser un booleano.")
        self._completada = valor

    #==Metodos de negocio==
    def registrar_resultado(self) -> None:
        self.completada = True

    def marcar_como_completada(self) -> None:
        self.completada = True

    def obtener_resumen(self) -> str:
        estado = "Completada" if self.completada else "Pendiente"
        return (
            f"Sesión {self.id_sesion} | Fecha: {self.fecha} | "
            f"Duración: {self.duracion_real} min | "
            f"Intensidad: {self.intensidad_real.value} | "
            f"Calorías: {self.calorias_quemadas:.1f} | "
            f"Estado: {estado}"
        )

    #==Representacion==
    def __repr__(self) -> str:
        return (
            f"SesionEntrenamiento(id_sesion={self.id_sesion}, "
            f"fecha={self.fecha}, "
            f"duracion_real={self.duracion_real}, "
            f"intensidad_real='{self.intensidad_real.value}', "
            f"calorias_quemadas={self.calorias_quemadas}, "
            f"completada={self.completada})"
        )