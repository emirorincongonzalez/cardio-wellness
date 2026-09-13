from decimal import Decimal
from typing import Optional, Union

from src.controladores.control_base import ControlBase
from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.enums import Intensidad
from src.persistencia.ejercicio_dao import EjercicioDAO


class ControlEjercicios(ControlBase):
    """
    Controlador para la gestión de ejercicios cardiovasculares.
    Coordina la creación, consulta, actualización y eliminación de ejercicios.
    """

    def __init__(
        self,
        ejercicio_dao: Optional[EjercicioDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt"
    ) -> None:
        """
        Inicializa el controlador de ejercicios.

        Args:
            ejercicio_dao (EjercicioDAO, optional): DAO de ejercicios. Si no se
                proporciona, se crea uno por defecto.
            ruta_log (str): Ruta al archivo de LOG para auditoría.
        """
        super().__init__(ruta_log=ruta_log)
        self.ejercicio_dao = ejercicio_dao or EjercicioDAO()

    def crear_ejercicio(
        self,
        nombre: str,
        descripcion: str,
        tipo: str,
        duracion_minutos: int,
        intensidad: Union[Intensidad, str],
        calorias_estimadas: float,
        creado_por: Optional[int] = None,
    ) -> EjercicioCardio:
        """
        Crea un nuevo ejercicio en el catálogo.

        Args:
            nombre (str): Nombre del ejercicio.
            descripcion (str): Descripción detallada.
            tipo (str): Tipo de ejercicio (ej. "LISS", "HIIT").
            duracion_minutos (int): Duración en minutos.
            intensidad (Intensidad o str): Nivel de intensidad.
            calorias_estimadas (float): Calorías estimadas por sesión.
            creado_por (int, optional): ID del administrador que lo crea.

        Returns:
            EjercicioCardio: Ejercicio guardado con ID asignado.
        """
        # Validaciones
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del ejercicio no puede estar vacío.")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción del ejercicio no puede estar vacía.")
        if not isinstance(tipo, str) or not tipo.strip():
            raise ValueError("El tipo del ejercicio no puede estar vacío.")
        if not isinstance(duracion_minutos, int) or duracion_minutos <= 0:
            raise ValueError("La duración en minutos debe ser un entero positivo.")
        if not isinstance(calorias_estimadas, (int, float, Decimal)) or calorias_estimadas <= 0:
            raise ValueError("Las calorías estimadas deben ser un número mayor que cero.")
        if creado_por is not None and (not isinstance(creado_por, int) or creado_por <= 0):
            raise ValueError("El creador debe ser un ID de usuario válido.")

        # Normalizar intensidad si es string
        if isinstance(intensidad, str):
            try:
                intensidad = Intensidad[intensidad.upper()]
            except KeyError:
                raise ValueError(f"Intensidad inválida: {intensidad}. Debe ser BAJA, MEDIA o ALTA.")

        # Crear objeto EjercicioCardio
        ejercicio = EjercicioCardio(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            tipo=tipo.strip(),
            duracion_minutos=duracion_minutos,
            intensidad=intensidad,
            calorias_estimadas=calorias_estimadas,
            creado_por=creado_por,
        )

        # Guardar y registrar LOG
        try:
            ejercicio_guardado = self.ejercicio_dao.guardar(ejercicio)
            self._registrar_log(creado_por or "SISTEMA", "CREACION_EJERCICIO")
            return ejercicio_guardado
        except ValueError as error:
            raise ValueError(f"Error al guardar el ejercicio: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al crear ejercicio: {error}") from error

    def buscar_por_id(self, id_ejercicio: int) -> Optional[EjercicioCardio]:
        """Busca un ejercicio por su ID."""
        if not isinstance(id_ejercicio, int) or id_ejercicio <= 0:
            raise ValueError("El ID de ejercicio debe ser un entero positivo.")
        return self.ejercicio_dao.buscar_por_id(id_ejercicio)

    def obtener_por_id(self, id_ejercicio: int) -> Optional[EjercicioCardio]:
        """Alias de buscar_por_id."""
        return self.buscar_por_id(id_ejercicio)

    def listar(self) -> list[EjercicioCardio]:
        """Lista todos los ejercicios del catálogo."""
        return self.ejercicio_dao.listar()

    def listar_ejercicios(self) -> list[EjercicioCardio]:
        """Alias de listar."""
        return self.listar()

    def actualizar_ejercicio(self, ejercicio: EjercicioCardio) -> EjercicioCardio:
        """
        Actualiza un ejercicio existente.

        Args:
            ejercicio (EjercicioCardio): Objeto EjercicioCardio con datos actualizados.

        Returns:
            EjercicioCardio: Ejercicio actualizado.
        """
        if not isinstance(ejercicio, EjercicioCardio):
            raise TypeError("Se requiere una instancia de EjercicioCardio.")

        try:
            ejercicio_actualizado = self.ejercicio_dao.actualizar(ejercicio)
            self._registrar_log(ejercicio.creado_por or "SISTEMA", "ACTUALIZACION_EJERCICIO")
            return ejercicio_actualizado
        except ValueError as error:
            raise ValueError(f"Error al actualizar ejercicio: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al actualizar ejercicio: {error}") from error

    def eliminar_ejercicio(
        self,
        id_ejercicio: int,
        usuario_accion: Optional[str] = None
    ) -> bool:
        """
        Elimina un ejercicio del catálogo.

        Args:
            id_ejercicio (int): ID del ejercicio a eliminar.
            usuario_accion (str, optional): Usuario que realiza la acción.

        Returns:
            bool: True si se eliminó correctamente.
        """
        if not isinstance(id_ejercicio, int) or id_ejercicio <= 0:
            raise ValueError("El ID de ejercicio debe ser un entero positivo.")

        try:
            resultado = self.ejercicio_dao.eliminar_por_id(id_ejercicio)
            self._registrar_log(usuario_accion or f"ID_{id_ejercicio}", "ELIMINACION_EJERCICIO")
            return resultado
        except ValueError as error:
            raise ValueError(f"Error al eliminar ejercicio: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al eliminar ejercicio: {error}") from error