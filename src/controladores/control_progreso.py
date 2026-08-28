from datetime import date, datetime
from decimal import Decimal
import importlib
import inspect
from pathlib import Path


def _obtener_progreso_dao_default():
    for ruta in ("src.persistencia.progreso_mensual_dao", "src.persistencia.progreso_dao"):
        try:
            modulo = importlib.import_module(ruta)
            if hasattr(modulo, "ProgresoMensualDAO"):
                return getattr(modulo, "ProgresoMensualDAO")()
        except ImportError:
            continue
    return None


def _obtener_sesion_dao_default():
    for ruta in ("src.persistencia.sesion_entrenamiento_dao", "src.persistencia.sesion_dao"):
        try:
            modulo = importlib.import_module(ruta)
            if hasattr(modulo, "SesionEntrenamientoDAO"):
                return getattr(modulo, "SesionEntrenamientoDAO")()
        except ImportError:
            continue
    return None


def _obtener_clase_progreso():
    for ruta in ("src.modelos.progreso_mensual", "src.modelos.progreso"):
        try:
            modulo = importlib.import_module(ruta)
            for attr in ("ProgresoMensual", "Progreso"):
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


def _instanciar_progreso_mensual(
    id_cliente,
    mes,
    anio,
    peso_registrado=None,
    total_sesiones=0,
    total_minutos=0,
    total_calorias=Decimal("0.0"),
    observaciones="",
    id_progreso=None,
):
    cls_prog = _obtener_clase_progreso()
    if cls_prog is None:
        return {
            "id_progreso": id_progreso,
            "id_cliente": id_cliente,
            "mes": mes,
            "anio": anio,
            "peso_registrado": peso_registrado,
            "total_sesiones": total_sesiones,
            "total_minutos": total_minutos,
            "total_calorias": total_calorias,
            "observaciones": observaciones,
        }

    sig = inspect.signature(cls_prog.__init__)
    params = sig.parameters

    valores_base = {
        "id_progreso": id_progreso,
        "id_cliente": id_cliente,
        "id_usuario": id_cliente,
        "cliente": id_cliente,
        "mes": mes,
        "anio": anio,
        "año": anio,
        "peso_registrado": peso_registrado,
        "peso": peso_registrado,
        "total_sesiones": total_sesiones,
        "sesiones_completadas": total_sesiones,
        "total_minutos": total_minutos,
        "minutos_entrenados": total_minutos,
        "total_calorias": total_calorias,
        "calorias_quemadas": total_calorias,
        "observaciones": observaciones or "",
    }

    kwargs = {}
    for param_name, param in params.items():
        if param_name == "self":
            continue
        if param_name in valores_base and valores_base[param_name] is not None:
            kwargs[param_name] = valores_base[param_name]
        elif param.default is inspect.Parameter.empty:
            kwargs[param_name] = None

    return cls_prog(**kwargs)


class ControlProgreso:

    def __init__(
        self,
        progreso_dao=None,
        sesion_dao=None,
        ruta_log="logs/LOG_CARDIO.txt",
    ):
        self.progreso_dao = progreso_dao if progreso_dao is not None else _obtener_progreso_dao_default()
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

    def calcular_resumen_cliente(self, cliente):
        id_cliente = _extraer_id(cliente, "id_cliente", "id_usuario", "id")
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")

        sesiones = []
        if self.sesion_dao and hasattr(self.sesion_dao, "listar_por_cliente"):
            sesiones = self.sesion_dao.listar_por_cliente(id_cliente)

        total_sesiones = len(sesiones)
        total_minutos = 0
        total_calorias = Decimal("0.0")

        for s in sesiones:
            minutos = s.get("duracion_real", 0) if isinstance(s, dict) else getattr(s, "duracion_real", 0)
            calorias = s.get("calorias_quemadas", 0) if isinstance(s, dict) else getattr(s, "calorias_quemadas", 0)
            total_minutos += int(minutos or 0)
            total_calorias += Decimal(str(calorias or 0))

        self._registrar_auditoria(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")

        return {
            "id_cliente": id_cliente,
            "total_sesiones": total_sesiones,
            "total_minutos": total_minutos,
            "total_calorias": total_calorias,
        }

    # Alias
    def obtener_resumen_cliente(self, cliente):
        return self.calcular_resumen_cliente(cliente)

    def calcular_impacto_calorico_rutina(self, rutina, usuario_consulta=None):
        ejercicios = []
        if hasattr(rutina, "ejercicios"):
            ejercicios = rutina.ejercicios or []
        elif isinstance(rutina, dict) and "ejercicios" in rutina:
            ejercicios = rutina["ejercicios"] or []

        total_calorias = Decimal("0.0")
        for ej in ejercicios:
            cal = getattr(ej, "calorias_estimadas", None) or (ej.get("calorias_estimadas") if isinstance(ej, dict) else None) or 0
            total_calorias += Decimal(str(cal))

        id_rutina = _extraer_id(rutina, "id_rutina", "id")
        self._registrar_auditoria(usuario_consulta or f"RUTINA_{id_rutina or 'DESCONOCIDA'}", "CONSULTA_IMPACTO")

        return total_calorias

    # Alias
    def obtener_impacto_rutina(self, rutina, usuario_consulta=None):
        return self.calcular_impacto_calorico_rutina(rutina, usuario_consulta)

    def generar_progreso_mensual(
        self,
        cliente,
        mes=None,
        anio=None,
        peso_actual=None,
        observaciones="",
    ):
        id_cliente = _extraer_id(cliente, "id_cliente", "id_usuario", "id")
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")

        if self.progreso_dao is None:
            raise RuntimeError("El DAO de progreso mensual no está disponible.")

        hoy = date.today()
        mes_val = mes or hoy.month
        anio_val = anio or hoy.year

        resumen = self.calcular_resumen_cliente(cliente)

        peso_val = peso_actual
        if peso_val is None and hasattr(cliente, "peso"):
            peso_val = cliente.peso

        progreso = _instanciar_progreso_mensual(
            id_cliente=id_cliente,
            mes=mes_val,
            anio=anio_val,
            peso_registrado=peso_val,
            total_sesiones=resumen["total_sesiones"],
            total_minutos=resumen["total_minutos"],
            total_calorias=resumen["total_calorias"],
            observaciones=observaciones,
        )

        progreso_guardado = self.progreso_dao.guardar(progreso)
        self._registrar_auditoria(f"CLIENTE_{id_cliente}", "GENERAR_PROGRESO")
        return progreso_guardado

    def consultar_progreso(self, cliente):
        id_cliente = _extraer_id(cliente, "id_cliente", "id_usuario", "id")
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")

        if self.progreso_dao is None:
            raise RuntimeError("El DAO de progreso mensual no está disponible.")

        historial = self.progreso_dao.buscar_por_cliente(id_cliente)
        self._registrar_auditoria(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")
        return historial