from datetime import datetime
import importlib
import inspect
from pathlib import Path
import sys
import unicodedata

from src.modelos.rutina import Rutina
from src.persistencia.rutina_dao import RutinaDAO


def _obtener_asignacion_dao_default():
    for ruta in ("src.persistencia.asignacion_rutina_dao", "src.persistencia.asignaciones_rutinas_dao"):
        try:
            modulo = importlib.import_module(ruta)
            if hasattr(modulo, "AsignacionRutinaDAO"):
                return getattr(modulo, "AsignacionRutinaDAO")()
        except ImportError:
            continue
    return None


def _quitar_tildes(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )


def _obtener_clase_nivel():
    modulo_rutina = sys.modules.get("src.modelos.rutina")
    if modulo_rutina and hasattr(modulo_rutina, "NivelRutina"):
        return getattr(modulo_rutina, "NivelRutina")
    return getattr(Rutina, "NivelRutina", None)


def _obtener_nivel_valido(valor):
    cls_nivel = _obtener_clase_nivel()
    if not cls_nivel:
        return valor

    if isinstance(valor, cls_nivel):
        return valor

    cadena = _quitar_tildes(str(valor)).strip().upper()

    # Búsqueda por clave o valor directo
    for miembro in cls_nivel:
        if miembro.name.upper() == cadena:
            return miembro
        if _quitar_tildes(str(miembro.value)).strip().upper() == cadena:
            return miembro

    # Mapeo de sinónimos
    mapeo = {
        "FACIL": "PRINCIPIANTE",
        "BAJO": "PRINCIPIANTE",
        "PRINCIPIANTE": "PRINCIPIANTE",
        "MEDIA": "INTERMEDIO",
        "MEDIO": "INTERMEDIO",
        "INTERMEDIO": "INTERMEDIO",
        "DIFICIL": "AVANZADO",
        "ALTO": "AVANZADO",
        "AVANZADO": "AVANZADO",
    }
    clave_mapeada = mapeo.get(cadena)
    if clave_mapeada:
        for miembro in cls_nivel:
            if miembro.name.upper() == clave_mapeada or _quitar_tildes(str(miembro.value)).strip().upper() == clave_mapeada:
                return miembro

    # Coincidencia parcial
    for miembro in cls_nivel:
        if miembro.name.upper() in cadena or cadena in miembro.name.upper():
            return miembro

    return list(cls_nivel)[0] if len(cls_nivel) > 0 else valor


def _instanciar_rutina(
    nombre,
    descripcion,
    nivel_dificultad,
    duracion_estimada,
    creado_por=None,
    id_rutina=None,
    objetivo=None,
    duracion_semanas=None,
):
    sig = inspect.signature(Rutina.__init__)
    params = sig.parameters

    nivel_normalizado = _obtener_nivel_valido(nivel_dificultad)

    valores_base = {
        "id_rutina": id_rutina,
        "nombre": nombre,
        "descripcion": descripcion,
        "nivel_dificultad": nivel_normalizado,
        "dificultad": nivel_normalizado,
        "nivel": nivel_normalizado,
        "duracion_estimada": duracion_estimada,
        "duracion": duracion_estimada,
        "duracion_minutos": duracion_estimada,
        "duracion_semanas": duracion_semanas or max(1, int(duracion_estimada // 7) if duracion_estimada else 4),
        "objetivo": objetivo or descripcion or "Acondicionamiento físico",
        "creado_por": creado_por,
        "id_entrenador": creado_por,
        "id_creador": creado_por,
    }

    kwargs = {}
    for param_name, param in params.items():
        if param_name == "self":
            continue
        if param_name in valores_base and valores_base[param_name] is not None:
            kwargs[param_name] = valores_base[param_name]
        elif param.default is inspect.Parameter.empty:
            if "duracion" in param_name:
                kwargs[param_name] = 4
            elif "objetivo" in param_name:
                kwargs[param_name] = "General"
            elif "nivel" in param_name or "dificultad" in param_name:
                kwargs[param_name] = nivel_normalizado
            else:
                kwargs[param_name] = None

    return Rutina(**kwargs)


class ControlRutinas:

    def __init__(
        self,
        rutina_dao=None,
        asignacion_dao=None,
        ruta_log="logs/LOG_CARDIO.txt",
    ):
        self.rutina_dao = rutina_dao or RutinaDAO()
        self.asignacion_dao = asignacion_dao if asignacion_dao is not None else _obtener_asignacion_dao_default()
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

    def crear_rutina(
        self,
        nombre,
        descripcion,
        nivel_dificultad,
        duracion_estimada,
        creado_por=None,
        objetivo=None,
        duracion_semanas=None,
    ):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre de la rutina no puede estar vacío.")

        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía.")

        if not isinstance(nivel_dificultad, (str, object)) or (isinstance(nivel_dificultad, str) and not nivel_dificultad.strip()):
            raise ValueError("El nivel de dificultad no puede estar vacío.")

        if (
            not isinstance(duracion_estimada, int)
            or isinstance(duracion_estimada, bool)
            or duracion_estimada <= 0
        ):
            raise ValueError("La duración estimada debe ser un entero positivo mayor que cero.")

        if creado_por is not None:
            if (
                not isinstance(creado_por, int)
                or isinstance(creado_por, bool)
                or creado_por <= 0
            ):
                raise ValueError("El id del creador debe ser un entero positivo o None.")

        rutina = _instanciar_rutina(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            nivel_dificultad=nivel_dificultad,
            duracion_estimada=duracion_estimada,
            creado_por=creado_por,
            objetivo=objetivo,
            duracion_semanas=duracion_semanas,
        )

        try:
            rutina_creada = self.rutina_dao.guardar(rutina)
            self._registrar_auditoria(creado_por, "CREACION_RUTINA")
            return rutina_creada
        except ValueError as error:
            raise ValueError(f"Error al guardar la rutina: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error al guardar la rutina: {error}") from error

    def buscar_por_id(self, id_rutina):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de rutina debe ser un entero positivo.")
        return self.rutina_dao.buscar_por_id(id_rutina)

    # Alias
    def obtener_por_id(self, id_rutina):
        return self.buscar_por_id(id_rutina)

    def listar(self):
        return self.rutina_dao.listar()

    # Alias
    def listar_rutinas(self):
        return self.listar()

    def actualizar_rutina(self, rutina):
        if not isinstance(rutina, Rutina):
            raise TypeError("Se requiere una instancia de Rutina.")
        try:
            return self.rutina_dao.actualizar(rutina)
        except ValueError as error:
            raise ValueError(f"Error al actualizar la rutina: {error}") from error

    def eliminar_rutina(self, id_rutina, usuario_accion=None):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de rutina debe ser un entero positivo.")

        resultado = self.rutina_dao.eliminar_por_id(id_rutina)
        self._registrar_auditoria(usuario_accion or f"ID_{id_rutina}", "ELIMINACION_RUTINA")
        return resultado

    def agregar_ejercicio_a_rutina(
        self,
        id_rutina,
        id_ejercicio,
        series=3,
        repeticiones=10,
        descanso_segundos=60,
        usuario_accion=None,
    ):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de rutina debe ser un entero positivo.")
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id de ejercicio debe ser un entero positivo.")

        try:
            resultado = self.rutina_dao.agregar_ejercicio(
                id_rutina=id_rutina,
                id_ejercicio=id_ejercicio,
                series=series,
                repeticiones=repeticiones,
                descanso_segundos=descanso_segundos,
            )
            self._registrar_auditoria(usuario_accion or f"RUTINA_{id_rutina}", "AGREGAR_EJERCICIO_A_RUTINA")
            return resultado
        except ValueError as error:
            raise ValueError(f"Error al asociar ejercicio a la rutina: {error}") from error

    def eliminar_ejercicio_de_rutina(self, id_rutina, id_ejercicio, usuario_accion=None):
        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de rutina debe ser un entero positivo.")
        if not isinstance(id_ejercicio, int) or isinstance(id_ejercicio, bool) or id_ejercicio <= 0:
            raise ValueError("El id de ejercicio debe ser un entero positivo.")

        resultado = self.rutina_dao.eliminar_ejercicio(id_rutina, id_ejercicio)
        self._registrar_auditoria(usuario_accion or f"RUTINA_{id_rutina}", "ELIMINAR_EJERCICIO_DE_RUTINA")
        return resultado

    def asignar_rutina(self, cliente, rutina, asignado_por=None):
        id_cliente = getattr(cliente, "id_usuario", cliente)
        id_rutina = getattr(rutina, "id_rutina", rutina)

        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo.")

        if not isinstance(id_rutina, int) or isinstance(id_rutina, bool) or id_rutina <= 0:
            raise ValueError("El id de la rutina debe ser un entero positivo.")

        if self.asignacion_dao is None:
            raise RuntimeError("El DAO de asignación de rutinas no está disponible.")

        try:
            asignacion_activa = self.asignacion_dao.obtener_activa_por_cliente(id_cliente)
            if asignacion_activa:
                id_asignacion = (
                    asignacion_activa.id_asignacion
                    if hasattr(asignacion_activa, "id_asignacion")
                    else (asignacion_activa.get("id_asignacion") if isinstance(asignacion_activa, dict) else None)
                )
                if id_asignacion:
                    self.asignacion_dao.finalizar_asignacion(id_asignacion)

            nueva_asignacion = self.asignacion_dao.asignar(
                id_cliente=id_cliente,
                id_rutina=id_rutina,
                asignado_por=asignado_por,
            )
            self._registrar_auditoria(asignado_por or f"CLIENTE_{id_cliente}", "ASIGNACION_RUTINA")
            return nueva_asignacion
        except ValueError as error:
            raise ValueError(f"Error al asignar la rutina: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al asignar rutina: {error}") from error