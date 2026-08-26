from src.modelos.rutina import Rutina
from src.persistencia.rutina_dao import RutinaDAO


class ControlRutinas:

    def __init__(self, rutina_dao=None):
        self.rutina_dao = rutina_dao or RutinaDAO()

    def crear_rutina(
        self,
        nombre,
        descripcion,
        objetivo,
        nivel,
        duracion_semanas,
        creado_por=None,
    ):
        rutina = Rutina(
            nombre=nombre,
            descripcion=descripcion,
            objetivo=objetivo,
            nivel=nivel,
            duracion_semanas=duracion_semanas,
            creado_por=creado_por,
        )
        return self.rutina_dao.guardar(rutina)

    def obtener_por_id(self, id_rutina):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")
        return self.rutina_dao.buscar_por_id(id_rutina)

    def listar_rutinas(self):
        return self.rutina_dao.listar()

    def actualizar_rutina(self, rutina):
        if not isinstance(rutina, Rutina):
            raise TypeError("Se requiere una instancia de Rutina.")
        return self.rutina_dao.actualizar(rutina)

    def agregar_ejercicio_a_rutina(self, id_rutina, id_ejercicio, orden_ejercicio):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id del ejercicio debe ser un entero positivo.")
        if not isinstance(orden_ejercicio, int) or isinstance(orden_ejercicio, bool) or orden_ejercicio <= 0:
            raise ValueError("El orden del ejercicio debe ser un entero mayor que cero.")

        return self.rutina_dao.agregar_ejercicio(
            id_rutina=id_rutina,
            id_ejercicio=id_ejercicio,
            orden_ejercicio=orden_ejercicio,
        )

    def eliminar_ejercicio_de_rutina(self, id_rutina, id_ejercicio):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id del ejercicio debe ser un entero positivo.")

        return self.rutina_dao.eliminar_ejercicio(
            id_rutina=id_rutina,
            id_ejercicio=id_ejercicio,
        )

    def listar_ejercicios_de_rutina(self, id_rutina):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")
        return self.rutina_dao.listar_ejercicios(id_rutina)

    def eliminar_rutina(self, id_rutina):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")
        return self.rutina_dao.eliminar_por_id(id_rutina)