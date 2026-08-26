from decimal import Decimal

from src.modelos.ejercicio_cardio import EjercicioCardio
from src.persistencia.ejercicio_dao import EjercicioDAO


class ControlEjercicios:

    def __init__(self, ejercicio_dao=None):
        self.ejercicio_dao = ejercicio_dao or EjercicioDAO()

    def crear_ejercicio(
        self,
        nombre,
        descripcion,
        tipo,
        duracion_minutos,
        intensidad,
        calorias_estimadas,
        creado_por=None,
    ):
        ejercicio = EjercicioCardio(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            duracion_minutos=duracion_minutos,
            intensidad=intensidad,
            calorias_estimadas=calorias_estimadas,
            creado_por=creado_por,
        )
        return self.ejercicio_dao.guardar(ejercicio)

    def obtener_por_id(self, id_ejercicio):
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id del ejercicio debe ser un entero positivo.")
        return self.ejercicio_dao.buscar_por_id(id_ejercicio)

    def listar_ejercicios(self):
        return self.ejercicio_dao.listar()

    def actualizar_ejercicio(self, ejercicio):
        if not isinstance(ejercicio, EjercicioCardio):
            raise TypeError("Se requiere una instancia de EjercicioCardio.")
        return self.ejercicio_dao.actualizar(ejercicio)

    def eliminar_ejercicio(self, id_ejercicio):
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id del ejercicio debe ser un entero positivo.")
        return self.ejercicio_dao.eliminar_por_id(id_ejercicio)