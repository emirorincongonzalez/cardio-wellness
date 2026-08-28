from datetime import date, datetime
from decimal import Decimal
import importlib
import inspect
from pathlib import Path


def _obtener_sesion_dao_default():
    for ruta in ("src.persistencia.sesion_entrenamiento_dao", "src.persistencia.sesion_dao"):
        try:
            modulo = importlib.import_module(ruta)
            if hasattr(modulo, "SesionEntrenamientoDAO"):
                return getattr(modulo, "SesionEntrenamientoDAO")()
        except ImportError:
            continue
    return None


def _obtener_clase_sesion():
    for ruta in ("src.modelos.sesion_entrenamiento", "src.modelos.sesion"):
        try:
            modulo = importlib.import_module(ruta)
            for attr in ("SesionEntrenamiento", "Sesion"):
                if hasattr(modulo, attr):
                    return getattr(modulo, attr)
        except ImportError:
            continue
    return None


def _extraer_id(objeto, *nombres_atributos):
    if isinstance(objeto, int) and not isinstance(objeto, bool):
        return objeto
    if isinstance(objeto, dict):
        for nombre in nombres_atributos:
            if nombre in objeto:
                return objeto[nombre]
    for nombre in nombres_atributos:
        if hasattr(objeto, nombre):
            val = getattr(objeto, nombre)
            if isinstance(val, int) and not isinstance(val, bool):
                return val
    return None


def _instanciar_sesion_entrenamiento(
    id_cliente,
    id_rutina,
    duracion_real,
    intensidad_real,
    calorias_quemadas,
    observaciones="",
    fecha_sesion=None,
    id_sesion=None,
):
    cls_sesion = _obtener_clase_sesion()
    if cls_sesion is None:
        return {
            "id_sesion": id_sesion,
            "id_cliente": id_cliente,
            "id_rutina": id_rutina,
            "duracion_real": duracion_real,
            "intensidad_real": intensidad_real,
            "calorias_quemadas": calorias_quemadas,
            "observaciones": observaciones,
            "fecha_sesion": fecha_sesion or date.today(),
        }

    sig = inspect.signature(cls_sesion.__init__)
    params = sig.parameters

    valores_base = {
        "id_sesion": id_sesion,
        "id_cliente": id_cliente,
        "id_usuario": id_cliente,
        "cliente": id_cliente,
        "id_rutina": id_rutina,
        "rutina": id_rutina,
        "duracion_real": duracion_real,
        "duracion": duracion_real,
        "duracion_minutos": duracion_real,
        "intensidad_real": intensidad_real,
        "intensidad": intensidad_real,
        "calorias_quemadas": calorias_quemadas,
        "calorias": calorias_quemadas,
        "observaciones": observaciones or "",
        "fecha_sesion": fecha_sesion or date.today(),
        "fecha": fecha_sesion or date.today(),
    }

    kwargs = {}
    for param_name, param in params.items():
        if param_name == "self":
            continue
        if param_name in valores_base and valores_base[param_name] is not None:
            kwargs[param_name] = valores_base[param_name]
        elif param.default is inspect.Parameter.empty:
            kwargs[param_name] = None

    return cls_sesion(**kwargs)


class ControlSesiones:

    def __init__(self, sesion_dao=None, ruta_log="logs/LOG_CARDIO.txt"):
        self.sesion_dao = sesion_dao if sesion_dao is not None else _obtener_sesion_dao_default()
        self.ruta_log = Path(ruta_log)

    def _registrar_auditoria(self, usuario, accion):
        try:
            self.ruta_log.parent.mkdir(parents=True, exist_ok=True)
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_str = "SISTEMA" if usuario is None else str(usuario)
            linea_log = f"{fecha_actual}, {usuario_str}, {accion}\n"
            with open(self.ruta_log, mode="a", encoding="utf-8") as archivo:
                archivo.write(linea_log)
        except Exception:
            pass

    def registrar_sesion(
        self,
        cliente,
        rutina,
        duracion_real,
        intensidad_real,
        calorias_quemadas,
        observaciones="",
    ):
        id_cliente = _extraer_id(cliente, "id_cliente", "id_usuario", "id")
        id_rutina = _extraer_id(rutina, "id_rutina", "id")

        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")

        if rutina is not None and (not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0):
            raise ValueError("El id de la rutina debe ser un entero positivo o None.")

        if (
            not isinstance(duracion_real, int)
            or isinstance(duracion_real, bool)
            or duracion_real <= 0
        ):
            raise ValueError("La duración real debe ser un entero positivo mayor que cero.")

        if (
            not isinstance(calorias_quemadas, (int, float, Decimal))
            or isinstance(calorias_quemadas, bool)
            or calorias_quemadas < 0
        ):
            raise ValueError("Las calorías quemadas deben ser un número mayor o igual a cero.")

        if self.sesion_dao is None:
            raise RuntimeError("El DAO de sesiones no está disponible.")

        sesion = _instanciar_sesion_entrenamiento(
            id_cliente=id_cliente,
            id_rutina=id_rutina,
            duracion_real=duracion_real,
            intensidad_real=intensidad_real,
            calorias_quemadas=calorias_quemadas,
            observaciones=observaciones,
        )

        try:
            sesion_guardada = self.sesion_dao.guardar(sesion)
            self._registrar_auditoria(f"CLIENTE_{id_cliente}", "REGISTRO_SESION")
            return sesion_guardada
        except ValueError as error:
            raise ValueError(f"Error al registrar la sesión: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al registrar la sesión: {error}") from error

    def obtener_sesiones_cliente(self, id_cliente):
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")
        if self.sesion_dao is None:
            raise RuntimeError("El DAO de sesiones no está disponible.")
        return self.sesion_dao.listar_por_cliente(id_cliente)

    # Alias
    def listar_por_cliente(self, id_cliente):
        return self.obtener_sesiones_cliente(id_cliente)

    def eliminar_sesion(self, id_sesion, usuario_accion=None):
        if not isinstance(id_sesion, int) or isinstance(id_sesion, bool) or id_sesion <= 0:
            raise ValueError("El id de la sesión debe ser un entero positivo.")
        if self.sesion_dao is None:
            raise RuntimeError("El DAO de sesiones no está disponible.")

        resultado = self.sesion_dao.eliminar_por_id(id_sesion)
        self._registrar_auditoria(usuario_accion or f"SESION_{id_sesion}", "ELIMINACION_SESION")
        return resultado