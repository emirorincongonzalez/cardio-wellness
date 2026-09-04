from datetime import date
from decimal import Decimal
from typing import Optional, Union

from src.controladores.control_base import ControlBase
from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import SesionEntrenamiento
from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO


class ControlSesiones(ControlBase):
    """
    Controlador para la gestión de sesiones de entrenamiento.
    Coordina el registro, consulta y eliminación de sesiones.
    """

    def __init__(
        self,
        sesion_dao: Optional[SesionEntrenamientoDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt"
    ) -> None:
        """
        Inicializa el controlador de sesiones.

        Args:
            sesion_dao (SesionEntrenamientoDAO, optional): DAO de sesiones.
            ruta_log (str): Ruta al archivo de LOG para auditoría.
        """
        super().__init__(ruta_log=ruta_log)
        self.sesion_dao = sesion_dao or SesionEntrenamientoDAO()

    def registrar_sesion(
        self,
        id_cliente: int,
        duracion_real: int,
        intensidad_real: Union[Intensidad, str],
        calorias_quemadas: float,
        observaciones: str = "",
        fecha: Optional[date] = None,
    ) -> SesionEntrenamiento:
        """
        Registra una nueva sesión de entrenamiento para un cliente.

        Args:
            id_cliente (int): ID del cliente.
            duracion_real (int): Duración real en minutos.
            intensidad_real (Intensidad o str): Intensidad percibida.
            calorias_quemadas (float): Calorías quemadas en la sesión.
            observaciones (str): Observaciones adicionales (opcional).
            fecha (date, optional): Fecha de la sesión. Por defecto, hoy.

        Returns:
            SesionEntrenamiento: Sesión guardada con ID asignado.
        """
        #Validaciones
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("El ID del cliente debe ser un entero positivo.")
        if not isinstance(duracion_real, int) or duracion_real <= 0:
            raise ValueError("La duración real debe ser un entero positivo.")
        if not isinstance(calorias_quemadas, (int, float, Decimal)) or calorias_quemadas < 0:
            raise ValueError("Las calorías quemadas no pueden ser negativas.")

        # Normalizar intensidad si es string
        if isinstance(intensidad_real, str):
            try:
                intensidad_real = Intensidad[intensidad_real.upper()]
            except KeyError:
                raise ValueError(
                    f"Intensidad inválida: {intensidad_real}. Debe ser BAJA, MEDIA o ALTA."
                )

        #Crear objeto SesionEntrenamiento
        sesion = SesionEntrenamiento(
            id_cliente=id_cliente,
            fecha=fecha or date.today(),
            duracion_real=duracion_real,
            intensidad_real=intensidad_real,
            calorias_quemadas=calorias_quemadas,
            observaciones=observaciones or "",
            completada=True,  # Al registrar, se asume que está completada
        )

        #Guardar y registrar LOG.
        try:
            sesion_guardada = self.sesion_dao.guardar(sesion)
            self._registrar_log(f"CLIENTE_{id_cliente}", "REGISTRO_SESION")
            return sesion_guardada
        except ValueError as error:
            raise ValueError(f"Error al registrar la sesión: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al registrar la sesión: {error}") from error

    def obtener_sesiones_cliente(self, id_cliente: int) -> list[SesionEntrenamiento]:
        """
        Obtiene todas las sesiones de un cliente, ordenadas por fecha descendente.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            list[SesionEntrenamiento]: Lista de sesiones.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("El ID del cliente debe ser un entero positivo.")
        return self.sesion_dao.listar_por_cliente(id_cliente)

    # Alias para compatibilidad con DCD
    def listar_por_cliente(self, id_cliente: int) -> list[SesionEntrenamiento]:
        """Alias de obtener_sesiones_cliente."""
        return self.obtener_sesiones_cliente(id_cliente)

    def eliminar_sesion(
        self,
        id_sesion: int,
        usuario_accion: Optional[str] = None
    ) -> bool:
        """
        Elimina una sesión de entrenamiento.

        Args:
            id_sesion (int): ID de la sesión a eliminar.
            usuario_accion (str, optional): Usuario que realiza la acción.

        Returns:
            bool: True si se eliminó correctamente.
        """
        if not isinstance(id_sesion, int) or id_sesion <= 0:
            raise ValueError("El ID de sesión debe ser un entero positivo.")

        try:
            resultado = self.sesion_dao.eliminar_por_id(id_sesion)
            self._registrar_log(usuario_accion or f"SESION_{id_sesion}", "ELIMINACION_SESION")
            return resultado
        except ValueError as error:
            raise ValueError(f"Error al eliminar la sesión: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al eliminar la sesión: {error}") from error