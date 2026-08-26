from src.persistencia.cliente_dao import ClienteDAO
from src.persistencia.rutina_dao import RutinaDAO


class ControlProgreso:

    def __init__(self, cliente_dao=None, rutina_dao=None):
        self.cliente_dao = cliente_dao or ClienteDAO()
        self.rutina_dao = rutina_dao or RutinaDAO()

    def calcular_resumen_cliente(self, id_cliente):
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")

        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if cliente is None:
            raise ValueError("El cliente especificado no existe.")

        return {
            "id_cliente": cliente.id_usuario,
            "nombre_completo": cliente.obtener_nombre_completo(),
            "peso_actual": cliente.peso,
            "altura": cliente.altura,
            "objetivo": cliente.objetivo,
            "fecha_ingreso": cliente.fecha_ingreso,
        }

    def calcular_impacto_calorico_rutina(self, id_rutina):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")

        rutina = self.rutina_dao.buscar_por_id(id_rutina)
        if rutina is None:
            raise ValueError("La rutina especificada no existe.")

        total_calorias = sum(
            float(ejercicio.calorias_estimadas)
            for ejercicio in rutina.ejercicios
        )

        return {
            "id_rutina": id_rutina,
            "nombre_rutina": rutina.nombre,
            "cantidad_ejercicios": len(rutina.ejercicios),
            "duracion_total_minutos": rutina.calcular_duracion_total(),
            "calorias_estimadas_totales": total_calorias,
        }