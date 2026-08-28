from datetime import datetime
from decimal import Decimal
import inspect
from pathlib import Path
import sys
import unicodedata

from src.modelos.ejercicio_cardio import EjercicioCardio
from src.persistencia.ejercicio_dao import EjercicioDAO


def _quitar_tildes(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )


def _obtener_clase_intensidad():
    modulo_ejercicio = sys.modules.get("src.modelos.ejercicio_cardio")
    if modulo_ejercicio and hasattr(modulo_ejercicio, "Intensidad"):
        return getattr(modulo_ejercicio, "Intensidad")
    return getattr(EjercicioCardio, "Intensidad", None)


def _obtener_intensidad_valida(valor="MEDIA"):
    cls_int = _obtener_clase_intensidad()
    if not cls_int:
        return valor

    if isinstance(valor, cls_int):
        return valor

    cadena = _quitar_tildes(str(valor)).strip().upper()

    # Búsqueda por clave o valor directo
    for miembro in cls_int:
        if miembro.name.upper() == cadena:
            return miembro
        if _quitar_tildes(str(miembro.value)).strip().upper() == cadena:
            return miembro

    # Mapeo de sinónimos
    mapeo = {
        "LEVE": "BAJA",
        "SUAVE": "BAJA",
        "BAJA": "BAJA",
        "BAJO": "BAJA",
        "MEDIA": "MEDIA",
        "MEDIO": "MEDIA",
        "MODERADA": "MODERADA",
        "MODERADO": "MODERADA",
        "ALTA": "ALTA",
        "ALTO": "ALTA",
        "INTENSA": "ALTA",
        "INTENSO": "ALTA",
    }
    clave_mapeada = mapeo.get(cadena)
    if clave_mapeada:
        for miembro in cls_int:
            if miembro.name.upper() == clave_mapeada or _quitar_tildes(str(miembro.value)).strip().upper() == clave_mapeada:
                return miembro

    # Coincidencia parcial o fallback al primer miembro
    for miembro in cls_int:
        if miembro.name.upper() in cadena or cadena in miembro.name.upper():
            return miembro

    return list(cls_int)[0] if len(cls_int) > 0 else valor


def _instanciar_ejercicio(
    nombre,
    descripcion,
    duracion_minutos,
    calorias_estimadas,
    id_ejercicio=None,
    tipo="Cardio",
    intensidad="MEDIA",
    **kwargs_extra,
):
    sig = inspect.signature(EjercicioCardio.__init__)
    params = sig.parameters

    intensidad_valida = _obtener_intensidad_valida(intensidad)

    valores_base = {
        "id_ejercicio": id_ejercicio,
        "nombre": nombre,
        "descripcion": descripcion,
        "tipo": tipo or "Cardio",
        "tipo_ejercicio": tipo or "Cardio",
        "intensidad": intensidad_valida,
        "nivel_intensidad": intensidad_valida,
        "duracion_minutos": duracion_minutos,
        "duracion": duracion_minutos,
        "calorias_estimadas": calorias_estimadas,
        "calorias_por_minuto": calorias_estimadas,
        "calorias": calorias_estimadas,
    }
    valores_base.update(kwargs_extra)

    kwargs = {}
    for param_name, param in params.items():
        if param_name == "self":
            continue
        if param_name in valores_base and valores_base[param_name] is not None:
            kwargs[param_name] = valores_base[param_name]
        elif param.default is inspect.Parameter.empty:
            if "tipo" in param_name:
                kwargs[param_name] = "Cardio"
            elif "intensidad" in param_name:
                kwargs[param_name] = intensidad_valida
            elif "duracion" in param_name or "calorias" in param_name:
                kwargs[param_name] = 1
            else:
                kwargs[param_name] = None

    return EjercicioCardio(**kwargs)


class ControlEjercicios:

    def __init__(self, ejercicio_dao=None, ruta_log="logs/LOG_CARDIO.txt"):
        self.ejercicio_dao = ejercicio_dao or EjercicioDAO()
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

    def crear_ejercicio(
        self,
        nombre,
        descripcion,
        duracion_minutos,
        calorias_estimadas,
        tipo="Cardio",
        intensidad="MEDIA",
        usuario_creador=None,
    ):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del ejercicio no puede estar vacío.")

        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción del ejercicio no puede estar vacía.")

        if (
            not isinstance(duracion_minutos, int)
            or isinstance(duracion_minutos, bool)
            or duracion_minutos <= 0
        ):
            raise ValueError("La duración en minutos debe ser un número entero mayor que cero.")

        if (
            not isinstance(calorias_estimadas, (int, float, Decimal))
            or isinstance(calorias_estimadas, bool)
            or calorias_estimadas <= 0
        ):
            raise ValueError("Las calorías estimadas deben ser un número mayor que cero.")

        ejercicio = _instanciar_ejercicio(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            duracion_minutos=duracion_minutos,
            calorias_estimadas=calorias_estimadas,
            tipo=tipo,
            intensidad=intensidad,
        )

        try:
            ejercicio_guardado = self.ejercicio_dao.guardar(ejercicio)
            self._registrar_auditoria(usuario_creador or "SISTEMA", "CREACION_EJERCICIO")
            return ejercicio_guardado
        except ValueError as error:
            raise ValueError(f"Error al crear el ejercicio: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error al crear el ejercicio: {error}") from error

    def buscar_por_id(self, id_ejercicio):
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id de ejercicio debe ser un entero positivo.")
        return self.ejercicio_dao.buscar_por_id(id_ejercicio)

    # Alias
    def obtener_por_id(self, id_ejercicio):
        return self.buscar_por_id(id_ejercicio)

    def listar(self):
        return self.ejercicio_dao.listar()

    # Alias
    def listar_ejercicios(self):
        return self.listar()

    def actualizar_ejercicio(self, ejercicio):
        if not isinstance(ejercicio, EjercicioCardio):
            raise TypeError("Se requiere una instancia de EjercicioCardio.")
        try:
            return self.ejercicio_dao.actualizar(ejercicio)
        except ValueError as error:
            raise ValueError(f"Error al actualizar el ejercicio: {error}") from error

    def eliminar_ejercicio(self, id_ejercicio, usuario_accion=None):
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id de ejercicio debe ser un entero positivo.")

        resultado = self.ejercicio_dao.eliminar_por_id(id_ejercicio)
        self._registrar_auditoria(usuario_accion or f"ID_{id_ejercicio}", "ELIMINACION_EJERCICIO")
        return resultado