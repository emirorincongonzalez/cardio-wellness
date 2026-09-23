"""
Controlador para la gestión de rutinas de entrenamiento.
"""

from typing import List, Optional, Union

from src.modelos.rutina import Rutina
from src.modelos.enums import NivelRutina
from src.persistencia.rutina_dao import RutinaDAO
from src.persistencia.asignacion_rutina_dao import (
    AsignacionRutinaDAO,
)
from src.controladores.control_base import ControlBase
from src.utilidades.logger import (
    log_creacion_rutina,
    log_sugerencia_rutina,
)


def _convertir_nivel(
    nivel_dificultad: Union[
        str,
        NivelRutina,
    ],
) -> NivelRutina:
    """
    Convierte el nivel recibido a NivelRutina.
    """
    if isinstance(
        nivel_dificultad,
        NivelRutina,
    ):
        return nivel_dificultad

    if not isinstance(
        nivel_dificultad,
        str,
    ):
        raise ValueError(
            "El nivel de dificultad no es válido."
        )

    valor = nivel_dificultad.strip().upper()

    try:
        return NivelRutina[valor]

    except KeyError:
        pass

    try:
        return NivelRutina(valor)

    except ValueError as error:
        raise ValueError(
            "El nivel debe ser BASICO, INTERMEDIO "
            "o AVANZADO."
        ) from error


def _validar_id(
    valor: object,
    nombre: str,
) -> int:
    """
    Convierte y valida un ID entero positivo.
    """
    if valor is None or isinstance(
        valor,
        bool,
    ):
        raise ValueError(
            f"{nombre} debe ser un entero positivo."
        )

    try:
        identificador = int(valor)

    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            f"{nombre} debe ser un entero positivo."
        ) from error

    if identificador <= 0:
        raise ValueError(
            f"{nombre} debe ser un entero positivo."
        )

    return identificador


def _instanciar_rutina(
    id_rutina: Optional[int] = None,
    nombre: str = "",
    descripcion: str = "",
    nivel_dificultad: Union[
        str,
        NivelRutina,
    ] = "BASICO",
    duracion_estimada: Union[
        int,
        float,
    ] = 1,
    objetivo: str = "cardio",
    creado_por: Optional[int] = None,
) -> Rutina:
    """
    Crea una instancia de Rutina.
    """
    if creado_por is None:
        raise ValueError(
            "Debe indicar el ID del administrador "
            "creador."
        )

    nivel = _convertir_nivel(
        nivel_dificultad
    )

    creador_id = _validar_id(
        creado_por,
        "El ID del creador",
    )

    if id_rutina is not None:
        id_rutina = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

    if isinstance(
        duracion_estimada,
        bool,
    ):
        raise ValueError(
            "La duración debe ser un entero "
            "positivo."
        )

    if not isinstance(
        duracion_estimada,
        (
            int,
            float,
        ),
    ):
        raise ValueError(
            "La duración debe ser numérica."
        )

    if duracion_estimada <= 0:
        raise ValueError(
            "La duración debe ser mayor que cero."
        )

    if int(duracion_estimada) != duracion_estimada:
        raise ValueError(
            "La duración debe ser un número entero."
        )

    return Rutina(
        id_rutina=id_rutina,
        nombre=nombre,
        descripcion=descripcion,
        objetivo=objetivo,
        nivel=nivel,
        duracion_semanas=int(
            duracion_estimada
        ),
        creado_por=creador_id,
    )


class ControlRutinas(ControlBase):
    """
    Controlador para operaciones CRUD de rutinas.
    """

    def __init__(
        self,
        rutina_dao: RutinaDAO,
        asignacion_dao: AsignacionRutinaDAO,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ) -> None:
        super().__init__(ruta_log)

        if rutina_dao is None:
            raise ValueError(
                "El DAO de rutinas es obligatorio."
            )

        if asignacion_dao is None:
            raise ValueError(
                "El DAO de asignaciones es obligatorio."
            )

        self._rutina_dao = rutina_dao
        self._asignacion_dao = asignacion_dao

    @property
    def rutina_dao(self) -> RutinaDAO:
        return self._rutina_dao

    @property
    def asignacion_dao(
        self,
    ) -> AsignacionRutinaDAO:
        return self._asignacion_dao

    def crear_rutina(
        self,
        nombre: str,
        descripcion: str,
        nivel_dificultad: Union[
            str,
            NivelRutina,
        ],
        duracion_estimada: Union[
            int,
            float,
        ],
        creado_por: int,
        objetivo: str = "cardio",
    ) -> Rutina:
        """
        Crea una nueva rutina.
        """
        if not isinstance(
            nombre,
            str,
        ) or not nombre.strip():
            raise ValueError(
                "El nombre de la rutina "
                "no puede estar vacío."
            )

        if not isinstance(
            descripcion,
            str,
        ) or not descripcion.strip():
            raise ValueError(
                "La descripción no puede estar vacía."
            )

        if not isinstance(
            objetivo,
            str,
        ) or not objetivo.strip():
            raise ValueError(
                "El objetivo no puede estar vacío."
            )

        if isinstance(
            duracion_estimada,
            bool,
        ):
            raise ValueError(
                "La duración debe ser un número "
                "positivo."
            )

        if not isinstance(
            duracion_estimada,
            (
                int,
                float,
            ),
        ):
            raise ValueError(
                "La duración debe ser un número "
                "positivo."
            )

        if duracion_estimada <= 0:
            raise ValueError(
                "La duración debe ser un número "
                "positivo."
            )

        if int(duracion_estimada) != duracion_estimada:
            raise ValueError(
                "La duración debe ser un número "
                "entero."
            )

        creador_id = _validar_id(
            creado_por,
            "El ID del creador",
        )

        rutina = _instanciar_rutina(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            nivel_dificultad=nivel_dificultad,
            duracion_estimada=int(
                duracion_estimada
            ),
            objetivo=objetivo.strip(),
            creado_por=creador_id,
        )

        rutina_guardada = (
            self._rutina_dao.guardar(
                rutina
            )
        )

        self._registrar_log(
            str(creador_id),
            (
                "CREACION_RUTINA "
                f"ID: {rutina_guardada.id_rutina}"
            ),
        )

        log_creacion_rutina(
            creador_id,
            rutina_guardada.id_rutina,
        )

        return rutina_guardada

    def buscar_por_id(
        self,
        id_rutina: int,
    ) -> Optional[Rutina]:
        """
        Busca una rutina por su ID.
        """
        rutina_id = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        return self._rutina_dao.buscar_por_id(
            rutina_id
        )

    def obtener_por_id(
        self,
        id_rutina: int,
    ) -> Optional[Rutina]:
        """
        Alias de buscar_por_id.
        """
        return self.buscar_por_id(
            id_rutina
        )

    def listar(self) -> List[Rutina]:
        """
        Lista todas las rutinas.
        """
        return self._rutina_dao.listar()

    def listar_rutinas(self) -> List[Rutina]:
        """
        Alias de listar.
        """
        return self.listar()

    def actualizar_rutina(
        self,
        rutina: Rutina,
        usuario_accion: Optional[int] = None,
    ) -> Rutina:
        """
        Actualiza una rutina existente.
        """
        if not isinstance(
            rutina,
            Rutina,
        ):
            raise TypeError(
                "Debe proporcionar una instancia "
                "de Rutina."
            )

        if rutina.id_rutina is None:
            raise ValueError(
                "La rutina debe tener un ID."
            )

        rutina_actualizada = (
            self._rutina_dao.actualizar(
                rutina
            )
        )

        usuario_log = (
            usuario_accion
            if usuario_accion is not None
            else rutina.creado_por
        )

        usuario_log_id = _validar_id(
            usuario_log,
            "El usuario de la acción",
        )

        self._registrar_log(
            str(usuario_log_id),
            (
                "ACTUALIZACION_RUTINA "
                f"ID: {rutina.id_rutina}"
            ),
        )

        return rutina_actualizada

    def eliminar_rutina(
        self,
        id_rutina: int,
        usuario_accion: int,
    ) -> bool:
        """
        Elimina una rutina por su ID.
        """
        rutina_id = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        usuario_id = _validar_id(
            usuario_accion,
            "El usuario de la acción",
        )

        resultado = (
            self._rutina_dao.eliminar_por_id(
                rutina_id
            )
        )

        if resultado:
            self._registrar_log(
                str(usuario_id),
                (
                    "ELIMINACION_RUTINA "
                    f"ID: {rutina_id}"
                ),
            )

        return resultado

    def agregar_ejercicio_a_rutina(
        self,
        id_rutina: int,
        id_ejercicio: int,
        orden: int = 1,
        usuario_accion: Optional[int] = None,
    ) -> bool:
        """
        Agrega un ejercicio a una rutina.
        """
        rutina_id = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        ejercicio_id = _validar_id(
            id_ejercicio,
            "El ID del ejercicio",
        )

        orden_id = _validar_id(
            orden,
            "El orden del ejercicio",
        )

        if usuario_accion is None:
            raise ValueError(
                "Debe indicar el usuario que realiza "
                "la acción."
            )

        usuario_id = _validar_id(
            usuario_accion,
            "El usuario de la acción",
        )

        resultado = (
            self._rutina_dao.agregar_ejercicio(
                id_rutina=rutina_id,
                id_ejercicio=ejercicio_id,
                orden_ejercicio=orden_id,
            )
        )

        if resultado:
            self._registrar_log(
                str(usuario_id),
                (
                    "AGREGAR_EJERCICIO_A_RUTINA "
                    f"Rutina: {rutina_id}, "
                    f"Ejercicio: {ejercicio_id}"
                ),
            )

        return resultado

    def eliminar_ejercicio_de_rutina(
        self,
        id_rutina: int,
        id_ejercicio: int,
        usuario_accion: Optional[int] = None,
    ) -> bool:
        """
        Elimina un ejercicio de una rutina.
        """
        rutina_id = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        ejercicio_id = _validar_id(
            id_ejercicio,
            "El ID del ejercicio",
        )

        if usuario_accion is None:
            raise ValueError(
                "Debe indicar el usuario que realiza "
                "la acción."
            )

        usuario_id = _validar_id(
            usuario_accion,
            "El usuario de la acción",
        )

        resultado = (
            self._rutina_dao.eliminar_ejercicio(
                id_rutina=rutina_id,
                id_ejercicio=ejercicio_id,
            )
        )

        if resultado:
            self._registrar_log(
                str(usuario_id),
                (
                    "ELIMINAR_EJERCICIO_DE_RUTINA "
                    f"Rutina: {rutina_id}, "
                    f"Ejercicio: {ejercicio_id}"
                ),
            )

        return resultado

    def listar_ejercicios_de_rutina(
        self,
        id_rutina: int,
    ) -> list:
        """
        Devuelve los ejercicios de una rutina.
        """
        rutina_id = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        return (
            self._rutina_dao.listar_ejercicios(
                rutina_id
            )
        )

    def obtener_ejercicios_de_rutina(
        self,
        id_rutina: int,
    ) -> list:
        """
        Alias de listar_ejercicios_de_rutina.
        """
        return self.listar_ejercicios_de_rutina(
            id_rutina
        )

    def ejercicio_asociado(
        self,
        id_rutina: int,
        id_ejercicio: int,
    ) -> bool:
        """
        Comprueba si un ejercicio pertenece
        a una rutina.
        """
        rutina_id = _validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        ejercicio_id = _validar_id(
            id_ejercicio,
            "El ID del ejercicio",
        )

        metodo = getattr(
            self._rutina_dao,
            "ejercicio_asociado",
            None,
        )

        if metodo is not None:
            return metodo(
                rutina_id,
                ejercicio_id,
            )

        ejercicios = (
            self._rutina_dao.listar_ejercicios(
                rutina_id
            )
        )

        return any(
            ejercicio.id_ejercicio
            == ejercicio_id
            for ejercicio in ejercicios
        )

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
        id_cliente = self._obtener_id_objeto(
            cliente,
            "El ID del cliente",
            "id_usuario",
        )

        id_rutina = self._obtener_id_objeto(
            rutina,
            "El ID de la rutina",
            "id_rutina",
        )

        usuario_id = _validar_id(
            asignado_por,
            "El usuario que asigna",
        )

        if observaciones is None:
            observaciones = ""

        if not isinstance(
            observaciones,
            str,
        ):
            raise ValueError(
                "Las observaciones deben ser texto."
            )

        asignacion_activa = (
            self._asignacion_dao
            .obtener_activa_por_cliente(
                id_cliente
            )
        )

        if asignacion_activa:
            (
                self._asignacion_dao
                .finalizar_asignacion(
                    asignacion_activa.id_asignacion
                )
            )

        resultado = (
            self._asignacion_dao.asignar(
                id_cliente=id_cliente,
                id_rutina=id_rutina,
                asignado_por=usuario_id,
                observaciones=(
                    observaciones.strip()
                ),
            )
        )

        self._registrar_log(
            str(usuario_id),
            (
                "ASIGNACION_RUTINA "
                f"Cliente: {id_cliente}, "
                f"Rutina: {id_rutina}"
            ),
        )

        return resultado

    def sugerir_rutina(
        self,
        id_cliente: int,
        tipo_sugerencia: str = "DEFAULT",
    ) -> Optional[Rutina]:
        """
        Sugiere una rutina para un cliente.
        """
        cliente_id = _validar_id(
            id_cliente,
            "El ID del cliente",
        )

        if not isinstance(
            tipo_sugerencia,
            str,
        ) or not tipo_sugerencia.strip():
            raise ValueError(
                "El tipo de sugerencia no es válido."
            )

        metodo_sugerencia = getattr(
            self._rutina_dao,
            "sugerir_rutina",
            None,
        )

        if metodo_sugerencia is None:
            raise NotImplementedError(
                "RutinaDAO no implementa "
                "sugerir_rutina()."
            )

        tipo = tipo_sugerencia.strip().upper()

        rutina_sugerida = metodo_sugerencia(
            cliente_id,
            tipo,
        )

        self._registrar_log(
            f"CLIENTE_{cliente_id}",
            "SUGERENCIA_RUTINA",
            tipo,
        )

        log_sugerencia_rutina(
            f"CLIENTE_{cliente_id}",
            tipo,
        )

        return rutina_sugerida

    @staticmethod
    def _obtener_id_objeto(
        objeto: Union[int, object],
        nombre: str,
        atributo: str,
    ) -> int:
        """
        Obtiene un ID desde un entero o desde
        un objeto.
        """
        if hasattr(
            objeto,
            atributo,
        ):
            objeto = getattr(
                objeto,
                atributo,
            )

        return _validar_id(
            objeto,
            nombre,
        )