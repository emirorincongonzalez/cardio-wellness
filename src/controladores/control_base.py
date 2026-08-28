from datetime import datetime
from pathlib import Path


class ControlBase:

    def __init__(self, ruta_log="logs/LOG_CARDIO.txt"):
        self.ruta_log = Path(ruta_log)

    def _registrar_log(self, usuario, accion, detalle=None):
        try:
            self.ruta_log.parent.mkdir(parents=True, exist_ok=True)
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_str = "SISTEMA" if usuario is None else str(usuario)
            if detalle:
                linea = f"{fecha_actual}, {usuario_str}, {accion}, {detalle}\n"
            else:
                linea = f"{fecha_actual}, {usuario_str}, {accion}\n"

            with open(self.ruta_log, mode="a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except Exception:
            pass

    # Alias para compatibilidad
    def _registrar_auditoria(self, usuario, accion):
        self._registrar_log(usuario, accion)