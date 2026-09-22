from enum import Enum


class NivelRutina(Enum):
    """
    Niveles disponibles para una rutina.
    """

    BASICO = "BASICO"
    INTERMEDIO = "INTERMEDIO"
    AVANZADO = "AVANZADO"


class Intensidad(Enum):
    """
    Intensidades disponibles.
    """

    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class EstadoAsignacion(Enum):
    """
    Estados posibles de una asignación.
    """

    ACTIVA = "ACTIVA"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"