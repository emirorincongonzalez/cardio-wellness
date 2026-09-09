from datetime import date
from decimal import Decimal
from typing import Optional



class ProgresoMensual:


    def __init__(
        self,
        mes: date,
        peso: float,
        sesiones_completadas: int = 0,
        sesiones_planificadas: int = 12,
        porcentaje_cumplimiento: float = 0.0,
        id_progreso: Optional[int] = None,
        id_cliente: Optional[int] = None,
    ) -> None:
        self.id_progreso = id_progreso
        self.id_cliente = id_cliente
        self.mes = mes
        self.peso = peso
        # ✅ INICIALIZA PRIMERO sesiones_planificadas
        self._sesiones_planificadas = sesiones_planificadas
        self._sesiones_completadas = 0
        self._porcentaje_cumplimiento = 0.0
        # ✅ LUEGO asigna usando los setters
        self.sesiones_planificadas = sesiones_planificadas
        self.sesiones_completadas = sesiones_completadas
        self.porcentaje_cumplimiento = porcentaje_cumplimiento


    #==Propiedades==
    @property
    def id_progreso(self) -> Optional[int]:
        return self._id_progreso


    @id_progreso.setter
    def id_progreso(self, valor: Optional[int]) -> None:
        self._id_progreso = valor


    @property
    def id_cliente(self) -> Optional[int]:
        return self._id_cliente


    @id_cliente.setter
    def id_cliente(self, valor: Optional[int]) -> None:
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("El id del cliente debe ser un entero positivo.")
        self._id_cliente = valor


    @property
    def mes(self) -> date:
        return self._mes


    @mes.setter
    def mes(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise ValueError("El mes debe ser un objeto date.")
        # Se recomienda que siempre sea el primer dia del mes
        self._mes = valor.replace(day=1)


    @property
    def peso(self) -> Decimal:
        return self._peso


    @peso.setter
    def peso(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("El peso debe ser mayor que cero.")
        self._peso = Decimal(str(valor))


    @property
    def sesiones_completadas(self) -> int:
        return self._sesiones_completadas


    @sesiones_completadas.setter
    def sesiones_completadas(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("Las sesiones completadas no pueden ser negativas.")
        self._sesiones_completadas = valor
        self._actualizar_porcentaje()


    @property
    def sesiones_planificadas(self) -> int:
        return self._sesiones_planificadas


    @sesiones_planificadas.setter
    def sesiones_planificadas(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("Las sesiones planificadas no pueden ser negativas.")
        self._sesiones_planificadas = valor
        self._actualizar_porcentaje()


    @property
    def porcentaje_cumplimiento(self) -> float:
        return self._porcentaje_cumplimiento


    @porcentaje_cumplimiento.setter
    def porcentaje_cumplimiento(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor < 0 or valor > 100:
            raise ValueError("El porcentaje de cumplimiento debe estar entre 0 y 100.")
        self._porcentaje_cumplimiento = float(valor)


    #==Metodos privados==
    def _actualizar_porcentaje(self) -> None:
        """Recalcula el porcentaje de cumplimiento automáticamente."""
        if self.sesiones_planificadas <= 0:
            self._porcentaje_cumplimiento = 0.0
        else:
            self._porcentaje_cumplimiento = round(
                (self.sesiones_completadas / self.sesiones_planificadas) * 100, 2
            )


    #==Metodos de negocio==
    def calcular_cumplimiento(self) -> float:
        self._actualizar_porcentaje()
        return self.porcentaje_cumplimiento


    def actualizar_progreso(self) -> None:
        self._actualizar_porcentaje()


    def generar_resumen(self) -> str:
        return (
            f"Progreso {self.mes.strftime('%B %Y')} | "
            f"Peso: {self.peso:.1f} kg | "
            f"Sesiones: {self.sesiones_completadas}/{self.sesiones_planificadas} | "
            f"Cumplimiento: {self.porcentaje_cumplimiento:.1f}%"
        )


    #==Representacion==
    def __repr__(self) -> str:
        return (
            f"ProgresoMensual(id_progreso={self.id_progreso}, "
            f"mes={self.mes}, "
            f"peso={self.peso}, "
            f"sesiones_completadas={self.sesiones_completadas}, "
            f"sesiones_planificadas={self.sesiones_planificadas}, "
            f"porcentaje_cumplimiento={self.porcentaje_cumplimiento})"
        )