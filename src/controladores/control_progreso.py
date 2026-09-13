from datetime import date
from decimal import Decimal
from typing import List, Optional

from src.controladores.control_base import ControlBase
from src.modelos.progreso_mensual import ProgresoMensual
from src.modelos.rutina import Rutina
from src.persistencia.progreso_mensual_dao import ProgresoMensualDAO
from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO


class ControlProgreso(ControlBase):
    """
    Controlador para la gestión del progreso de los clientes.
    Coordina el cálculo de resúmenes, impacto calórico y generación de progreso mensual.
    """


    def __init__(
        self,
        progreso_dao: Optional[ProgresoMensualDAO] = None,
        sesion_dao: Optional[SesionEntrenamientoDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt"
    ) -> None:
        """
        Inicializa el controlador de progreso.

        Args:
            progreso_dao (ProgresoMensualDAO, optional): DAO de progreso mensual.
            sesion_dao (SesionEntrenamientoDAO, optional): DAO de sesiones.
            ruta_log (str): Ruta al archivo de LOG para auditoría.
        """
        super().__init__(ruta_log=ruta_log)
        self.progreso_dao = progreso_dao or ProgresoMensualDAO()
        self.sesion_dao = sesion_dao or SesionEntrenamientoDAO()

    def calcular_resumen_cliente(self, id_cliente: int) -> dict:
        """
        Calcula un resumen del progreso de un cliente basado en sus sesiones.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            dict: Resumen con total_sesiones, total_minutos, total_calorias.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("El ID del cliente debe ser un entero positivo.")

        # Obtener sesiones del cliente
        sesiones = self.sesion_dao.listar_por_cliente(id_cliente)


        total_sesiones = len(sesiones)
        total_minutos = sum(s.duracion_real for s in sesiones)
        total_calorias = sum(s.calorias_quemadas for s in sesiones)

        # Registrar auditoría
        self._registrar_log(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")


        return {
            "id_cliente": id_cliente,
            "total_sesiones": total_sesiones,
            "total_minutos": total_minutos,
            "total_calorias": total_calorias,
        }

    def obtener_resumen_cliente(self, id_cliente: int) -> dict:
        """Alias de calcular_resumen_cliente."""
        return self.calcular_resumen_cliente(id_cliente)

    def calcular_impacto_calorico_rutina(self, rutina: Rutina) -> Decimal:
        """
        Calcula el total de calorías estimadas de una rutina.

        Args:
            rutina (Rutina): Objeto Rutina.

        Returns:
            Decimal: Total de calorías estimadas.
        """
        if not isinstance(rutina, Rutina):
            raise TypeError("Se requiere una instancia de Rutina.")


        total_calorias = Decimal("0.0")
        for ejercicio in rutina.ejercicios:
            total_calorias += ejercicio.calorias_estimadas

        self._registrar_log(f"RUTINA_{rutina.id_rutina}", "CONSULTA_IMPACTO")
        return total_calorias

    def obtener_impacto_rutina(self, rutina: Rutina) -> Decimal:
        """Alias de calcular_impacto_calorico_rutina."""
        return self.calcular_impacto_calorico_rutina(rutina)


    def generar_progreso_mensual(
        self,
        id_cliente: int,
        peso: float,
        mes: Optional[date] = None,
        sesiones_completadas: Optional[int] = None,
        sesiones_planificadas: Optional[int] = None,
    ) -> ProgresoMensual:
        """
        Genera un registro de progreso mensual para un cliente.

        Args:
            id_cliente (int): ID del cliente.
            peso (float): Peso actual del cliente.
            mes (date, optional): Mes del progreso (por defecto, mes actual).
            sesiones_completadas (int, optional): Sesiones completadas en el mes.
            sesiones_planificadas (int, optional): Sesiones planificadas en el mes.

        Returns:
            ProgresoMensual: Registro de progreso guardado.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("El ID del cliente debe ser un entero positivo.")
        if not isinstance(peso, (int, float, Decimal)) or peso <= 0:
            raise ValueError("El peso debe ser un número mayor que cero.")

        # Usar mes actual si no se especifica
        mes_actual = mes or date.today().replace(day=1)

        # Obtener sesiones del mes para calcular cumplimiento
        sesiones = self.sesion_dao.listar_por_cliente(id_cliente)
        sesiones_mes = [s for s in sesiones if s.fecha >= mes_actual and s.fecha < mes_actual.replace(day=28) + date.resolution * 4]

        completadas = sesiones_completadas if sesiones_completadas is not None else len(sesiones_mes)
        planificadas = sesiones_planificadas if sesiones_planificadas is not None else 4  # Valor por defecto

        # Crear objeto ProgresoMensual
        progreso = ProgresoMensual(
            id_cliente=id_cliente,
            mes=mes_actual,
            peso=peso,
            sesiones_completadas=completadas,
            sesiones_planificadas=planificadas,
        )
        progreso.calcular_cumplimiento()

        # Guardar y registrar LOG
        try:
            progreso_guardado = self.progreso_dao.guardar(progreso)
            self._registrar_log(f"CLIENTE_{id_cliente}", "GENERAR_PROGRESO")
            return progreso_guardado
        except ValueError as error:
            raise ValueError(f"Error al generar el progreso: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al generar progreso: {error}") from error

    def consultar_progreso(self, id_cliente: int) -> List[ProgresoMensual]:
        """
        Consulta el historial de progreso mensual de un cliente.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            List[ProgresoMensual]: Lista de registros de progreso.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("El ID del cliente debe ser un entero positivo.")


        historial = self.progreso_dao.buscar_por_cliente(id_cliente)
        self._registrar_log(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")
        return historial