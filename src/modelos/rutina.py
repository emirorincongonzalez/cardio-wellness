from datetime import date
from typing import List, Optional, Tuple

from src.modelos.enums import NivelRutina
from src.modelos.ejercicio_cardio import EjercicioCardio


class Rutina:

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        objetivo: str,
        nivel: NivelRutina,
        duracion_semanas: int,
        creado_por: Optional[int] = None,
        id_rutina: Optional[int] = None,
        fecha_creacion: Optional[date] = None,
        ejercicios: Optional[List[EjercicioCardio]] = None,
    ) -> None:
        self.id_rutina = id_rutina
        self.nombre = nombre
        self.descripcion = descripcion
        self.objetivo = objetivo
        self.nivel = nivel
        self.duracion_semanas = duracion_semanas
        self.creado_por = creado_por
        self.fecha_creacion = fecha_creacion or date.today()
        self._ejercicios = []

        if ejercicios is not None:
            for ejercicio in ejercicios:
                self.agregar_ejercicio(ejercicio)

    @property
    def id_rutina(self) -> Optional[int]:
        return self._id_rutina

    @id_rutina.setter
    def id_rutina(self, valor: Optional[int]) -> None:
        self._id_rutina = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")

        self._nombre = valor.strip()

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La descripción no puede estar vacía.")

        self._descripcion = valor.strip()

    @property
    def objetivo(self) -> str:
        return self._objetivo

    @objetivo.setter
    def objetivo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El objetivo no puede estar vacío.")

        self._objetivo = valor.strip()

    @property
    def nivel(self) -> NivelRutina:
        return self._nivel

    @nivel.setter
    def nivel(self, valor: NivelRutina) -> None:
        if isinstance(valor, NivelRutina):
            self._nivel = valor
            return

        if isinstance(valor, str):
            valor_normalizado = valor.strip().upper()

            try:
                self._nivel = NivelRutina[valor_normalizado]
                return
            except KeyError:
                try:
                    self._nivel = NivelRutina(valor_normalizado)
                    return
                except ValueError:
                    pass

        raise ValueError(
            "El nivel debe ser un valor válido de NivelRutina."
        )

    @property
    def duracion_semanas(self) -> int:
        return self._duracion_semanas

    @duracion_semanas.setter
    def duracion_semanas(self, valor: int) -> None:
        if (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "La duración debe ser un entero mayor que cero."
            )

        self._duracion_semanas = valor

    @property
    def creado_por(self) -> Optional[int]:
        return self._creado_por

    @creado_por.setter
    def creado_por(self, valor: Optional[int]) -> None:
        if valor is not None and (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "creado_por debe ser un id de usuario válido."
            )

        self._creado_por = valor

    @property
    def fecha_creacion(self) -> date:
        return self._fecha_creacion

    @fecha_creacion.setter
    def fecha_creacion(self, valor: Optional[date]) -> None:
        self._fecha_creacion = valor or date.today()

    @property
    def ejercicios(self) -> Tuple[EjercicioCardio, ...]:
        return tuple(self._ejercicios)

    @property
    def id_ejercicios(self) -> Tuple[int, ...]:
        return tuple(
            ejercicio.id_ejercicio
            for ejercicio in self._ejercicios
            if ejercicio.id_ejercicio is not None
        )

#==Metodos de negocio==
    def agregar_ejercicio(self, ejercicio: EjercicioCardio) -> None:
        if not isinstance(ejercicio, EjercicioCardio):
            raise TypeError(
                "Solo se pueden agregar objetos de tipo "
                "EjercicioCardio."
            )

        if ejercicio in self._ejercicios:
            raise ValueError(
                "El ejercicio ya pertenece a la rutina."
            )

        self._ejercicios.append(ejercicio)

    def eliminar_ejercicio(self, ejercicio: EjercicioCardio) -> None:
        if not isinstance(ejercicio, EjercicioCardio):
            raise TypeError(
                "Solo se pueden eliminar objetos de tipo "
                "EjercicioCardio."
            )

        if ejercicio not in self._ejercicios:
            raise ValueError(
                "El ejercicio no pertenece a la rutina."
            )

        self._ejercicios.remove(ejercicio)

    def calcular_duracion_total(self) -> int:
        return sum(
            ejercicio.duracion_minutos
            for ejercicio in self._ejercicios
        )

#==Representacion==
    def __repr__(self) -> str:
        return (
            f"Rutina(id_rutina={self.id_rutina}, "
            f"nombre='{self.nombre}', "
            f"objetivo='{self.objetivo}', "
            f"nivel='{self.nivel.value}', "
            f"duracion_semanas={self.duracion_semanas})"
        )
