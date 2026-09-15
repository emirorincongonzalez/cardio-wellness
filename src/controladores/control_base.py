from datetime import datetime
from pathlib import Path
from typing import Optional

# IMPORTAR EL NUEVO MÓDULO DE LOGGER
from src.utilidades.logger import registrar_actividad


class ControlBase:
    #Clase base para todos los controladores del sistema.
    #Centraliza el registro de auditoria en un archivo LOG.


    def __init__(self, ruta_log: str = "logs/LOG_CARDIO.txt") -> None:
        """
        Inicializa el controlador base con la ruta del archivo LOG.


        Args:
        ruta_log (str): Ruta al archivo de LOG (por defecto logs/LOG_CARDIO.txt)
        """
        self.ruta_log = Path(ruta_log)


    def _registrar_log(self, usuario: Optional[str], accion: str, detalle: Optional[str] = None) -> None:
        """
        Registra una actvidad en el archivo de auditoria.


        El formato de cada linea es: FECHA, USUARIO, ACTIVIDAD
        (cumple con el requisito de Auditoria de Sistemas)


        Args:
            usuario (str, optional): Nombre o identificador del usuario.
            accion (str): Descripcion de la accion realizada.
            detalle (str, optional): Detalle adicional de la accion.
        """
        try:
            #Crear el directorio si no existe.
            self.ruta_log.parent.mkdir(parents=True, exist_ok=True)


            #Formatear fecha y hora.
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


            #Usuario por defecto si es None.
            usuario_str = "SISTEMA" if usuario is None else str(usuario)


            #Construir línea base
            linea = f"{fecha_actual}, {usuario_str}, {accion}"
            
            #Agregar detalle si existe
            if detalle is not None:
                linea += f", {detalle}"
            
            linea += "\n"


            #Escribir en el archivo (modo append)
            with open(self.ruta_log, mode="a", encoding="utf-8") as archivo:
                archivo.write(linea)
            
            # NUEVO LOGGER INTEGRADO - Registrar también con el módulo logger.py
            # Esto asegura que los datos se registren en tiempo real
            detalle_str = detalle if detalle else ""
            registrar_actividad(usuario_str, accion, detalle_str)
            
        except Exception as e:
            #No interrumpir la ejecucion del sistema si falla el LOG
            #(se podria usar logging para depuracion)
            import logging
            logging.getLogger(__name__).warning(
                f"No se pudo registrar la auditoria: {e}"
            )


    # Alias para compatibilidad
    def _registrar_auditoria(self, usuario: Optional[str], accion: str, detalle: Optional[str] = None) -> None:
        #Alias de _registrar_log para mantener compatibilidad.
        self._registrar_log(usuario, accion, detalle)