from typing import Optional, Union

from src.controladores.control_base import ControlBase
from src.modelos.enums import NivelRutina
from src.modelos.rutina import Rutina
from src.persistencia.asignacion_rutina_dao import AsignacionRutinaDAO
from src.persistencia.rutina_dao import RutinaDAO


class ControlRutinas(ControlBase):
    """
    Controlador para la gestión de rutinas.
    Coordina la creación, actualización, eliminación y asignación de rutinas.
    """

    def __init__(
        self,
        rutina_dao: Optional[RutinaDAO] = None,
        asignacion_dao: Optional[AsignacionRutinaDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt"
    ) -> None:
        """
        Inicializa el controlador de rutinas.

        Args:
            rutina_dao (RutinaDAO, optional): DAO de rutinas.
            asignacion_dao (AsignacionRutinaDAO, optional): DAO de asignaciones.
            ruta_log (str): Ruta al archivo de LOG.
        """
        super().__init__(ruta_log=ruta_log)
        self.rutina_dao = rutina_dao or RutinaDAO()
        self.asignacion_dao = asignacion_dao or AsignacionRutinaDAO()

    def crear_rutina(
        self,
        nombre: str,
        descripcion: str,
        objetivo: str,
        nivel: Union[NivelRutina, str],
        duracion_semanas: int,
        creado_por: Optional[int] = None,
    ) -> Rutina:
        """
        Crea una nueva rutina en el sistema.

        Args:
            nombre (str): Nombre de la rutina.
            descripcion (str): Descripción detallada.
            objetivo (str): Objetivo de la rutina.
            nivel (NivelRutina o str): Nivel de dificultad.
            duracion_semanas (int): Duración en semanas.
            creado_por (int, optional): ID del administrador que la crea.

        Returns:
            Rutina: Rutina guardada con ID asignado.
        """
        # Validaciones
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre de la rutina no puede estar vacío.")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía.")
        if not isinstance(objetivo, str) or not objetivo.strip():
            raise ValueError("El objetivo no puede estar vacío.")
        if not isinstance(duracion_semanas, int) or duracion_semanas <= 0:
            raise ValueError("La duración en semanas debe ser un entero positivo.")
        if creado_por is not None and (not isinstance(creado_por, int) or creado_por <= 0):
            raise ValueError("El creador debe ser un ID de usuario válido.")

        # Normalizar nivel si es string
        if isinstance(nivel, str):
            try:
                nivel = NivelRutina[nivel.upper()]
            except KeyError:
                raise ValueError(f"Nivel inválido: {nivel}. Debe ser BASICO, INTERMEDIO o AVANZADO.")

        # Crear objeto Rutina
        rutina = Rutina(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            objetivo=objetivo.strip(),
            nivel=nivel,
            duracion_semanas=duracion_semanas,
            creado_por=creado_por,
        )

        # Guardar y registrar LOG
        try:
            rutina_guardada = self.rutina_dao.guardar(rutina)
            self._registrar_log(creado_por or "SISTEMA", "CREACION_RUTINA")
            return rutina_guardada
        except ValueError as error:
            raise ValueError(f"Error al guardar la rutina: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al crear rutina: {error}") from error

    def buscar_por_id(self, id_rutina: int) -> Optional[Rutina]:
        """Busca una rutina por su ID."""
        if not isinstance(id_rutina, int) or id_rutina <= 0:
            raise ValueError("El ID de rutina debe ser un entero positivo.")
        return self.rutina_dao.buscar_por_id(id_rutina)

    def obtener_por_id(self, id_rutina: int) -> Optional[Rutina]:
        """Alias de buscar_por_id."""
        return self.buscar_por_id(id_rutina)

    def listar(self) -> list[Rutina]:
        """Lista todas las rutinas."""
        return self.rutina_dao.listar()

    def listar_rutinas(self) -> list[Rutina]:
        """Alias de listar."""
        return self.listar()

    def actualizar_rutina(self, rutina: Rutina) -> Rutina:
        """
        Actualiza una rutina existente.

        Args:
            rutina (Rutina): Objeto Rutina con datos actualizados.

        Returns:
            Rutina: Rutina actualizada.
        """
        if not isinstance(rutina, Rutina):
            raise TypeError("Se requiere una instancia de Rutina.")
        try:
            rutina_actualizada = self.rutina_dao.actualizar(rutina)
            self._registrar_log(rutina.creado_por or "SISTEMA", "ACTUALIZACION_RUTINA")
            return rutina_actualizada
        except ValueError as error:
            raise ValueError(f"Error al actualizar rutina: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al actualizar rutina: {error}") from error

    def agregar_ejercicio_a_rutina(
        self,
        id_rutina: int,
        id_ejercicio: int,
        orden_ejercicio: int,
    ) -> bool:
        """
        Asocia un ejercicio a una rutina con un orden específico.

        Args:
            id_rutina (int): ID de la rutina.
            id_ejercicio (int): ID del ejercicio.
            orden_ejercicio (int): Orden dentro de la rutina.

        Returns:
            bool: True si se agregó correctamente.
        """
        if not isinstance(id_rutina, int) or id_rutina <= 0:
            raise ValueError("El ID de rutina debe ser un entero positivo.")
        if not isinstance(id_ejercicio, int) or id_ejercicio <= 0:
            raise ValueError("El ID de ejercicio debe ser un entero positivo.")
        if not isinstance(orden_ejercicio, int) or orden_ejercicio <= 0:
            raise ValueError("El orden debe ser un entero positivo.")

        try:
            resultado = self.rutina_dao.agregar_ejercicio(id_rutina, id_ejercicio, orden_ejercicio)
            self._registrar_log(f"RUTINA_{id_rutina}", "AGREGAR_EJERCICIO")
            return resultado
        except ValueError as error:
            raise ValueError(f"Error al asociar ejercicio: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al agregar ejercicio: {error}") from error

    def eliminar_ejercicio_de_rutina(
        self,
        id_rutina: int,
        id_ejercicio: int,
    ) -> bool:
        """
        Elimina la asociación entre una rutina y un ejercicio.

        Args:
            id_rutina (int): ID de la rutina.
            id_ejercicio (int): ID del ejercicio.

        Returns:
            bool: True si se eliminó correctamente.
        """
        if not isinstance(id_rutina, int) or id_rutina <= 0:
            raise ValueError("El ID de rutina debe ser un entero positivo.")
        if not isinstance(id_ejercicio, int) or id_ejercicio <= 0:
            raise ValueError("El ID de ejercicio debe ser un entero positivo.")

        try:
            resultado = self.rutina_dao.eliminar_ejercicio(id_rutina, id_ejercicio)
            self._registrar_log(f"RUTINA_{id_rutina}", "ELIMINAR_EJERCICIO")
            return resultado
        except Exception as error:
            raise RuntimeError(f"Error inesperado al eliminar ejercicio: {error}") from error

    def asignar_rutina(
        self,
        id_cliente: int,
        id_rutina: int,
        observaciones: str = "",
        usuario_accion: Optional[str] = None,
    ) -> bool:
        """
        Asigna una rutina a un cliente.
        Si el cliente ya tiene una rutina activa, la finaliza automáticamente.

        Args:
            id_cliente (int): ID del cliente.
            id_rutina (int): ID de la rutina.
            observaciones (str): Observaciones de la asignación.
            usuario_accion (str, optional): Usuario que realiza la acción.

        Returns:
            bool: True si la asignación fue exitosa.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("El ID de cliente debe ser un entero positivo.")
        if not isinstance(id_rutina, int) or id_rutina <= 0:
            raise ValueError("El ID de rutina debe ser un entero positivo.")

        try:
            # Verificar si el cliente ya tiene una rutina activa
            asignacion_activa = self.asignacion_dao.buscar_activa(id_cliente)
            if asignacion_activa:
                # Finalizar la asignación activa
                self.asignacion_dao.actualizar(asignacion_activa)
                self._registrar_log(
                    usuario_accion or f"CLIENTE_{id_cliente}",
                    "FINALIZAR_ASIGNACION_ACTIVA"
                )

            # Crear nueva asignación
            from src.modelos.asignacion_rutina import AsignacionRutina
            from src.modelos.enums import EstadoAsignacion

            nueva_asignacion = AsignacionRutina(
                id_cliente=id_cliente,
                id_rutina=id_rutina,
                observaciones=observaciones,
                estado=EstadoAsignacion.ACTIVA,
            )
            self.asignacion_dao.guardar(nueva_asignacion)

            self._registrar_log(
                usuario_accion or f"CLIENTE_{id_cliente}",
                f"ASIGNACION_RUTINA_{id_rutina}"
            )
            return True

        except ValueError as error:
            raise ValueError(f"Error al asignar rutina: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al asignar rutina: {error}") from error

    def eliminar_rutina(self, id_rutina: int, usuario_accion: Optional[str] = None) -> bool:
        """
        Elimina una rutina del sistema.

        Args:
            id_rutina (int): ID de la rutina a eliminar.
            usuario_accion (str, optional): Usuario que realiza la acción.

        Returns:
            bool: True si se eliminó correctamente.
        """
        if not isinstance(id_rutina, int) or id_rutina <= 0:
            raise ValueError("El ID de rutina debe ser un entero positivo.")

        try:
            resultado = self.rutina_dao.eliminar_por_id(id_rutina)
            self._registrar_log(usuario_accion or f"RUTINA_{id_rutina}", "ELIMINACION_RUTINA")
            return resultado
        except ValueError as error:
            raise ValueError(f"Error al eliminar rutina: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al eliminar rutina: {error}") from error