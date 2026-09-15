"""
Controlador para la gestión de ejercicios cardiovasculares.
"""
from typing import Optional, Union
from decimal import Decimal


from src.modelos.ejercicio_cardio import EjercicioCardio, Intensidad
from src.persistencia.ejercicio_dao import EjercicioDAO
from src.controladores.control_base import ControlBase
from src.utilidades.logger import log_creacion_ejercicio


def _instanciar_ejercicio(
    id_ejercicio: Optional[int] = None,
    nombre: str = "",
    descripcion: str = "",
    duracion_minutos: int = 0,
    calorias_estimadas: float = 0.0,
    tipo: str = "cardio",
    intensidad: Intensidad = Intensidad.MEDIA,
    creado_por: Optional[int] = None,
) -> EjercicioCardio:
    """
    Función helper para crear instancias de EjercicioCardio.
    Útil para tests y creación rápida de objetos.
    """
    ejercicio = EjercicioCardio(
        nombre=nombre,
        descripcion=descripcion,
        tipo=tipo,
        duracion_minutos=duracion_minutos,
        intensidad=intensidad,
        calorias_estimadas=calorias_estimadas,
        creado_por=creado_por,
    )
    if id_ejercicio is not None:
        ejercicio.id_ejercicio = id_ejercicio
    return ejercicio


class ControlEjercicios(ControlBase):
    """
    Controlador para operaciones CRUD de ejercicios cardiovasculares.
    """


    def __init__(self, ejercicio_dao: EjercicioDAO, ruta_log: str = "logs/LOG_CARDIO.txt"):
        super().__init__(ruta_log)
        self._ejercicio_dao = ejercicio_dao


    @property
    def ejercicio_dao(self) -> EjercicioDAO:
        return self._ejercicio_dao


    def crear_ejercicio(
        self,
        nombre: str,
        descripcion: str,
        duracion_minutos: Union[int, float],
        calorias_estimadas: Union[int, float],
        tipo: str = "cardio",
        intensidad: str = "MEDIA",
        usuario_creador: Optional[int] = None,
    ) -> EjercicioCardio:
        """
        Crea un nuevo ejercicio cardiovascular con validaciones.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del ejercicio no puede estar vacío")
        if not descripcion or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")
        if not isinstance(duracion_minutos, (int, float)) or duracion_minutos <= 0:
            raise ValueError("La duración debe ser un número positivo")
        if not isinstance(calorias_estimadas, (int, float)) or calorias_estimadas <= 0:
            raise ValueError("Las calorías deben ser un número positivo")


        ejercicio = EjercicioCardio(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            tipo=tipo,
            duracion_minutos=int(duracion_minutos),
            intensidad=Intensidad(intensidad.upper()) if isinstance(intensidad, str) else intensidad,
            calorias_estimadas=float(calorias_estimadas),
            creado_por=usuario_creador,
        )


        ejercicio_guardado = self._ejercicio_dao.guardar(ejercicio)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(str(usuario_creador) if usuario_creador else "sistema", f"CREACION_EJERCICIO ID: {ejercicio_guardado.id_ejercicio}")
        log_creacion_ejercicio(usuario_creador if usuario_creador else "sistema", ejercicio_guardado.id_ejercicio)
        
        return ejercicio_guardado


    def buscar_por_id(self, id_ejercicio: int) -> Optional[EjercicioCardio]:
        """Busca un ejercicio por su ID."""
        if id_ejercicio <= 0:
            raise ValueError("El ID debe ser positivo")
        return self._ejercicio_dao.buscar_por_id(id_ejercicio)


    def obtener_por_id(self, id_ejercicio: int) -> Optional[EjercicioCardio]:
        """Alias de buscar_por_id."""
        return self.buscar_por_id(id_ejercicio)


    def listar(self) -> list:
        """Lista todos los ejercicios."""
        return self._ejercicio_dao.listar()


    def listar_ejercicios(self) -> list:
        """Alias de listar."""
        return self.listar()


    def actualizar_ejercicio(self, ejercicio: EjercicioCardio) -> EjercicioCardio:
        """Actualiza un ejercicio existente."""
        if not isinstance(ejercicio, EjercicioCardio):
            raise TypeError("Debe proporcionar una instancia de EjercicioCardio")
        
        ejercicio_actualizado = self._ejercicio_dao.actualizar(ejercicio)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(str(ejercicio.creado_por) if ejercicio.creado_por else "sistema", f"ACTUALIZACION_EJERCICIO ID: {ejercicio.id_ejercicio}")
        
        return ejercicio_actualizado


    def eliminar_ejercicio(self, id_ejercicio: int, usuario_accion: Optional[int] = None) -> bool:
        """Elimina un ejercicio por ID."""
        resultado = self._ejercicio_dao.eliminar_por_id(id_ejercicio)
        if resultado:
            # LOG DOBLE: ControlBase + logger.py
            self._registrar_log(str(usuario_accion) if usuario_accion else "sistema", f"ELIMINACION_EJERCICIO ID: {id_ejercicio}")
        return resultado