from datetime import datetime

from src.persistencia.cliente_dao import ClienteDAO
from src.persistencia.rutina_dao import RutinaDAO


class ControlSesiones:

    def __init__(self, cliente_dao=None, rutina_dao=None):
        self.cliente_dao = cliente_dao or ClienteDAO()
        self.rutina_dao = rutina_dao or RutinaDAO()

    def iniciar_sesion_entrenamiento(self, id_cliente, id_rutina):
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")

        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if cliente is None:
            raise ValueError("El cliente especificado no existe.")

        rutina = self.rutina_dao.buscar_por_id(id_rutina)
        if rutina is None:
            raise ValueError("La rutina especificada no existe.")

        return {
            "id_cliente": id_cliente,
            "id_rutina": id_rutina,
            "cliente_nombre": cliente.obtener_nombre_completo(),
            "rutina_nombre": rutina.nombre,
            "fecha_inicio": datetime.now(),
            "duracion_estimada_minutos": rutina.calcular_duracion_total(),
            "estado": "EN_PROGRESO",
        }

    def registrar_fin_sesion(self, sesion, minutos_reales, calorias_quemadas):
        if not isinstance(sesion, dict) or sesion.get("estado") != "EN_PROGRESO":
            raise ValueError("La sesión no es válida o no está en progreso.")
        if not isinstance(minutos_reales, (int, float)) or minutos_reales <= 0:
            raise ValueError("Los minutos reales deben ser un número mayor a cero.")
        if not isinstance(calorias_quemadas, (int, float)) or calorias_quemadas < 0:
            raise ValueError("Las calorías quemadas no pueden ser negativas.")

        sesion_finalizada = sesion.copy()
        sesion_finalizada["fecha_fin"] = datetime.now()
        sesion_finalizada["minutos_reales"] = minutos_reales
        sesion_finalizada["calorias_quemadas"] = calorias_quemadas
        sesion_finalizada["estado"] = "FINALIZADA"
        return sesion_finalizada