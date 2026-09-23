from datetime import date
from typing import List, Optional, Tuple, Union

from src.modelos.enums import NivelRutina
from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
)


class Rutina:
    """
    Representa una rutina de entrenamiento.
    """

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        objetivo: str,
        nivel: Union[
            NivelRutina,
            str,
        ],
        duracion_semanas: int,
        creado_por: Optional[int] = None,
        id_rutina: Optional[int] = None,
        fecha_creacion: Optional[date] = None,
        ejercicios: Optional[
            List[EjercicioCardio]
        ] = None,
    ) -> None:
        self.id_rutina = id_rutina
        self.nombre = nombre
        self.descripcion = descripcion
        self.objetivo = objetivo
        self.nivel = nivel
        self.duracion_semanas = (
            duracion_semanas
        )
        self.creado_por = creado_por
        self.fecha_creacion = fecha_creacion

        self._ejercicios = []

        if ejercicios is not None:
            for ejercicio in ejercicios:
                self.agregar_ejercicio(
                    ejercicio
                )

    @property
    def id_rutina(self) -> Optional[int]:
        return self._id_rutina

    @id_rutina.setter
    def id_rutina(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    "El ID de la rutina debe ser "
                    "un entero positivo."
                )

        self._id_rutina = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "El nombre no puede estar vacío."
            )

        self._nombre = valor.strip()

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "La descripción no puede estar vacía."
            )

        self._descripcion = valor.strip()

    @property
    def objetivo(self) -> str:
        return self._objetivo

    @objetivo.setter
    def objetivo(self, valor: str) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "El objetivo no puede estar vacío."
            )

        self._objetivo = valor.strip()

    @property
    def nivel(self) -> NivelRutina:
        return self._nivel

    @nivel.setter
    def nivel(
        self,
        valor: Union[
            NivelRutina,
            str,
        ],
    ) -> None:
        if isinstance(valor, NivelRutina):
            self._nivel = valor
            return

        if isinstance(valor, str):
            valor_normalizado = (
                valor.strip().upper()
            )

            try:
                self._nivel = (
                    NivelRutina[
                        valor_normalizado
                    ]
                )
                return

            except KeyError:
                pass

            try:
                self._nivel = (
                    NivelRutina(
                        valor_normalizado
                    )
                )
                return

            except ValueError:
                pass

        raise ValueError(
            "El nivel debe ser un valor válido "
            "de NivelRutina."
        )

    @property
    def duracion_semanas(self) -> int:
        return self._duracion_semanas

    @duracion_semanas.setter
    def duracion_semanas(
        self,
        valor: int,
    ) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(valor, int)
            or valor <= 0
        ):
            raise ValueError(
                "La duración debe ser un entero "
                "mayor que cero."
            )

        self._duracion_semanas = valor

    @property
    def creado_por(self) -> Optional[int]:
        return self._creado_por

    @creado_por.setter
    def creado_por(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    "creado_por debe ser un ID "
                    "de usuario válido."
                )

        self._creado_por = valor

    @property
    def fecha_creacion(self) -> date:
        return self._fecha_creacion

    @fecha_creacion.setter
    def fecha_creacion(
        self,
        valor: Optional[date],
    ) -> None:
        if valor is not None and not isinstance(
            valor,
            date,
        ):
            raise ValueError(
                "La fecha de creación no es válida."
            )

        self._fecha_creacion = (
            valor
            if valor is not None
            else date.today()
        )

    @property
    def ejercicios(
        self,
    ) -> Tuple[EjercicioCardio, ...]:
        """
        Devuelve los ejercicios como tupla.
        """
        return tuple(self._ejercicios)

    @property
    def id_ejercicios(self) -> Tuple[int, ...]:
        """
        Devuelve los IDs de los ejercicios.
        """
        return tuple(
            ejercicio.id_ejercicio
            for ejercicio in self._ejercicios
            if ejercicio.id_ejercicio
            is not None
        )

    def agregar_ejercicio(
        self,
        ejercicio: EjercicioCardio,
    ) -> None:
        """
        Agrega un ejercicio a la rutina.
        """
        if not isinstance(
            ejercicio,
            EjercicioCardio,
        ):
            raise TypeError(
                "Solo se pueden agregar objetos "
                "de tipo EjercicioCardio."
            )

        if ejercicio.id_ejercicio is not None:
            for ejercicio_actual in (
                self._ejercicios
            ):
                if (
                    ejercicio_actual.id_ejercicio
                    == ejercicio.id_ejercicio
                ):
                    raise ValueError(
                        "El ejercicio ya pertenece "
                        "a la rutina."
                    )

        elif ejercicio in self._ejercicios:
            raise ValueError(
                "El ejercicio ya pertenece "
                "a la rutina."
            )

        self._ejercicios.append(ejercicio)

    def eliminar_ejercicio(
        self,
        ejercicio: EjercicioCardio,
    ) -> None:
        """
        Elimina un ejercicio de la rutina.
        """
        if not isinstance(
            ejercicio,
            EjercicioCardio,
        ):
            raise TypeError(
                "Solo se pueden eliminar objetos "
                "de tipo EjercicioCardio."
            )

        for indice, ejercicio_actual in enumerate(
            self._ejercicios
        ):
            mismo_id = (
                ejercicio_actual.id_ejercicio
                is not None
                and ejercicio.id_ejercicio
                is not None
                and (
                    ejercicio_actual.id_ejercicio
                    == ejercicio.id_ejercicio
                )
            )

            mismo_objeto = (
                ejercicio_actual is ejercicio
            )

            if mismo_id or mismo_objeto:
                del self._ejercicios[indice]
                return

        raise ValueError(
            "El ejercicio no pertenece a la rutina."
        )

    def eliminar_ejercicio_por_id(
        self,
        id_ejercicio: int,
    ) -> None:
        """
        Elimina un ejercicio usando su ID.
        """
        if (
            isinstance(id_ejercicio, bool)
            or not isinstance(id_ejercicio, int)
            or id_ejercicio <= 0
        ):
            raise ValueError(
                "El ID del ejercicio debe ser "
                "positivo."
            )

        for ejercicio in self._ejercicios:
            if (
                ejercicio.id_ejercicio
                == id_ejercicio
            ):
                self.eliminar_ejercicio(
                    ejercicio
                )
                return

        raise ValueError(
            "El ejercicio no pertenece a la rutina."
        )

    def reemplazar_ejercicios(
        self,
        ejercicios: List[EjercicioCardio],
    ) -> None:
        """
        Reemplaza todos los ejercicios de la rutina.
        """
        if not isinstance(ejercicios, list):
            raise TypeError(
                "Los ejercicios deben recibirse "
                "como una lista."
            )

        self._ejercicios = []

        for ejercicio in ejercicios:
            self.agregar_ejercicio(
                ejercicio
            )

    def contiene_ejercicio(
        self,
        id_ejercicio: int,
    ) -> bool:
        """
        Indica si la rutina contiene un ejercicio.
        """
        return id_ejercicio in self.id_ejercicios

    def calcular_duracion_total(self) -> int:
        """
        Calcula la duración total de ejercicios.
        """
        return sum(
            ejercicio.duracion_minutos
            for ejercicio in self._ejercicios
        )

    def cantidad_ejercicios(self) -> int:
        """
        Devuelve la cantidad de ejercicios.
        """
        return len(self._ejercicios)

    def obtener_nivel_texto(self) -> str:
        """
        Devuelve el valor textual del nivel.
        """
        return getattr(
            self.nivel,
            "value",
            str(self.nivel),
        )

    def __repr__(self) -> str:
        return (
            "Rutina("
            f"id_rutina={self.id_rutina}, "
            f"nombre='{self.nombre}', "
            f"objetivo='{self.objetivo}', "
            f"nivel='{self.obtener_nivel_texto()}', "
            "duracion_semanas="
            f"{self.duracion_semanas}, "
            "ejercicios="
            f"{self.cantidad_ejercicios()}"
            ")"
        )