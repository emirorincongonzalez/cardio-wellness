"""
Controlador para la gestión de rutinas de entrenamiento.
"""
from typing import Optional, Union

from src.modelos.rutina import Rutina, NivelRutina
from src.persistencia.rutina_dao import RutinaDAO
from src.persistencia.asignacion_rutina_dao import AsignacionRutinaDAO
from src.controladores.control_base import ControlBase


def _instanciar_rutina(
    id_rutina: Optional[int] = None,
    nombre: str = "",
    descripcion: str = "",
    nivel_dificultad: Union[str, NivelRutina] = "BASICO",
    duracion_estimada: int = 30,
    objetivo: str = "cardio",
    creado_por: int = 1,
) -> Rutina:
    """
    Función helper para crear instancias de Rutina.
    Útil para tests y creación rápida de objetos.
    """
    nivel = nivel_dificultad if isinstance(nivel_dificultad, NivelRutina) else NivelRutina(nivel_dificultad)
    
    rutina = Rutina(
        nombre=nombre,
        descripcion=descripcion,
        objetivo=objetivo,
        nivel=nivel,
        duracion_semanas=duracion_estimada,
        creado_por=creado_por,
    )
    if id_rutina is not None:
        rutina.id_rutina = id_rutina
    return rutina


class ControlRutinas(ControlBase):
    """
    Controlador para operaciones CRUD de rutinas.
    """

    def __init__(
        self,
        rutina_dao: RutinaDAO,
        asignacion_dao: AsignacionRutinaDAO,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ):
        super().__init__(ruta_log)
        self._rutina_dao = rutina_dao
        self._asignacion_dao = asignacion_dao

    @property
    def rutina_dao(self) -> RutinaDAO:
        return self._rutina_dao

    @property
    def asignacion_dao(self) -> AsignacionRutinaDAO:
        return self._asignacion_dao

    def crear_rutina(
        self,
        nombre: str,
        descripcion: str,
        nivel_dificultad: Union[str, NivelRutina],
        duracion_estimada: Union[int, float],
        creado_por: int,
        objetivo: str = "cardio",
    ) -> Rutina:
        """
        Crea una nueva rutina con validaciones.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la rutina no puede estar vacío")
        if not descripcion or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")
        if not isinstance(duracion_estimada, (int, float)) or duracion_estimada <= 0:
            raise ValueError("La duración debe ser un número positivo")
        if not isinstance(creado_por, int) or creado_por <= 0:
            raise ValueError("El ID del creador debe ser un entero positivo")

        nivel = nivel_dificultad if isinstance(nivel_dificultad, NivelRutina) else NivelRutina(nivel_dificultad)

        rutina = Rutina(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            objetivo=objetivo,
            nivel=nivel,
            duracion_semanas=int(duracion_estimada),
            creado_por=creado_por,
        )

        rutina_guardada = self._rutina_dao.guardar(rutina)
        self._registrar_log(str(creado_por), f"CREACION_RUTINA ID: {rutina_guardada.id_rutina}")
        return rutina_guardada

    def buscar_por_id(self, id_rutina: int) -> Optional[Rutina]:
        """Busca una rutina por su ID."""
        if id_rutina <= 0:
            raise ValueError("El ID debe ser positivo")
        return self._rutina_dao.buscar_por_id(id_rutina)

    def obtener_por_id(self, id_rutina: int) -> Optional[Rutina]:
        """Alias de buscar_por_id."""
        return self.buscar_por_id(id_rutina)

    def listar(self) -> list:
        """Lista todas las rutinas."""
        return self._rutina_dao.listar()

    def listar_rutinas(self) -> list:
        """Alias de listar."""
        return self.listar()

    def actualizar_rutina(self, rutina: Rutina) -> Rutina:
        """Actualiza una rutina existente."""
        if not isinstance(rutina, Rutina):
            raise TypeError("Debe proporcionar una instancia de Rutina")
        return self._rutina_dao.actualizar(rutina)

    def eliminar_rutina(self, id_rutina: int, usuario_accion: int) -> bool:
        """Elimina una rutina por ID."""
        resultado = self._rutina_dao.eliminar_por_id(id_rutina)
        if resultado:
            self._registrar_log(str(usuario_accion), f"ELIMINACION_RUTINA ID: {id_rutina}")
        return resultado

    def agregar_ejercicio_a_rutina(
        self, id_rutina: int, id_ejercicio: int, orden: int = 1, usuario_accion: int = 1
    ) -> bool:
        """Agrega un ejercicio a una rutina."""
        resultado = self._rutina_dao.agregar_ejercicio(id_rutina, id_ejercicio, orden)
        if resultado:
            self._registrar_log(str(usuario_accion), f"AGREGAR_EJERCICIO_A_RUTINA ID: {id_rutina}")
        return resultado

    def eliminar_ejercicio_de_rutina(
        self, id_rutina: int, id_ejercicio: int, usuario_accion: int = 1
    ) -> bool:
        """Elimina un ejercicio de una rutina."""
        resultado = self._rutina_dao.eliminar_ejercicio(id_rutina, id_ejercicio)
        if resultado:
            self._registrar_log(str(usuario_accion), f"ELIMINAR_EJERCICIO_DE_RUTINA ID: {id_rutina}")
        return resultado

    def asignar_rutina(
        self,
        cliente: Union[int, object],
        rutina: Union[int, object],
        asignado_por: int,
        observaciones: str = "",
    ) -> dict:
        """
        Asigna una rutina a un cliente.
        """
        id_cliente = cliente.id_usuario if hasattr(cliente, 'id_usuario') else int(cliente)
        id_rutina = rutina.id_rutina if hasattr(rutina, 'id_rutina') else int(rutina)

        if id_cliente <= 0 or id_rutina <= 0:
            raise ValueError("Los IDs deben ser positivos")

        asignacion_activa = self._asignacion_dao.obtener_activa_por_cliente(id_cliente)
        if asignacion_activa:
            self._asignacion_dao.finalizar_asignacion(asignacion_activa.id_asignacion)

        resultado = self._asignacion_dao.asignar(
            id_cliente=id_cliente,
            id_rutina=id_rutina,
            asignado_por=asignado_por,
            observaciones=observaciones,
        )

        self._registrar_log(str(asignado_por), f"ASIGNACION_RUTINA Cliente: {id_cliente}, Rutina: {id_rutina}")
        return resultado