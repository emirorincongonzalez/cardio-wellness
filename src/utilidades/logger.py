"""
Módulo de logging automático para registrar todas las actividades reales del programa.
"""

import logging
from datetime import datetime
from pathlib import Path
import os


# Configurar logger
logger = logging.getLogger('cardio_wellness')
logger.setLevel(logging.INFO)

# Crear carpeta logs si no existe
logs_dir = Path(__file__).parent.parent.parent / 'logs'
logs_dir.mkdir(exist_ok=True)

# Handler para archivo
archivo_log = logs_dir / 'LOG_CARDIO.txt'
handler = logging.FileHandler(archivo_log, encoding='utf-8', mode='a')
handler.setLevel(logging.INFO)

# Formato: YYYY-MM-DD HH:MM:SS, USUARIO, ACCION, DETALLE
formatter = logging.Formatter('%(asctime)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Agregar handler al logger (solo si no tiene handlers)
if not logger.handlers:
    logger.addHandler(handler)


def registrar_actividad(usuario, accion, detalle=''):
    """
    Registra una actividad real en el log.
    
    Args:
        usuario: ID o email del usuario
        accion: Tipo de acción (CONSULTA_PROGRESO, GENERAR_PROGRESO, etc.)
        detalle: Detalles adicionales de la acción
    """
    mensaje = f"{usuario}, {accion}, {detalle}".strip()
    logger.info(mensaje)


# Funciones específicas para cada tipo de acción
def log_consulta_progreso(usuario):
    registrar_actividad(usuario, 'CONSULTA_PROGRESO', 'Cliente consultó su progreso')


def log_generar_progreso(usuario):
    registrar_actividad(usuario, 'GENERAR_PROGRESO', 'Se generó reporte de progreso')


def log_calculo_diferencia_peso(usuario, diferencia):
    registrar_actividad(usuario, 'CALCULO_DIFERENCIA_PESO', f'DIF: {diferencia:.1f}')


def log_reporte_pdf_generado(usuario, nombre_archivo):
    registrar_actividad(usuario, 'REPORTE_PDF_GENERADO', nombre_archivo)


def log_registro_cliente(email):
    registrar_actividad(email, 'REGISTRO_CLIENTE', 'Nuevo cliente registrado')


def log_registro_administrador(email):
    registrar_actividad(email, 'REGISTRO_ADMINISTRADOR', 'Nuevo administrador registrado')


def log_login_exitoso(email):
    registrar_actividad(email, 'LOGIN_EXITOSO', 'Inicio de sesión exitoso')


def log_login_fallido(email):
    registrar_actividad(email, 'LOGIN_FALLIDO', 'Intento de inicio de sesión fallido')


def log_creacion_rutina(usuario, id_rutina):
    registrar_actividad(str(usuario), 'CREACION_RUTINA', f'ID: {id_rutina}')


def log_creacion_ejercicio(usuario, id_ejercicio):
    registrar_actividad(str(usuario), 'CREACION_EJERCICIO', f'ID: {id_ejercicio}')


def log_sugerencia_rutina(usuario, tipo):
    registrar_actividad(str(usuario), 'SUGERENCIA_RUTINA', tipo)


def log_consulta_impacto(usuario):
    registrar_actividad(usuario, 'CONSULTA_IMPACTO', 'Se consultó impacto de rutina')


if __name__ == "__main__":
    # Prueba
    print("Configurando logger...")
    log_consulta_progreso('CLIENTE_PRUEBA')
    log_generar_progreso('CLIENTE_PRUEBA')
    log_calculo_diferencia_peso('CLIENTE_PRUEBA', -2.5)
    print("✅ Logger configurado correctamente. Revisa logs/LOG_CARDIO.txt")