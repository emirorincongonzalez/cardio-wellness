import runpy
from unittest.mock import Mock, patch

import pytest

import src.utilidades.logger as modulo_logger


def test_registrar_actividad_envia_mensaje_a_logger():
    """
    Verifica que registrar_actividad construya el mensaje
    esperado y lo envíe mediante logger.info.
    """
    with patch.object(
        modulo_logger.logger,
        "info",
    ) as mock_info:
        modulo_logger.registrar_actividad(
            "usuario_1",
            "ACCION_PRUEBA",
            "Detalle de prueba",
        )

    mock_info.assert_called_once_with(
        "usuario_1, ACCION_PRUEBA, Detalle de prueba",
    )


def test_registrar_actividad_permite_detalle_vacio():
    """
    Verifica que detalle sea opcional.
    """
    with patch.object(
        modulo_logger.logger,
        "info",
    ) as mock_info:
        modulo_logger.registrar_actividad(
            "usuario_2",
            "ACCION_SIN_DETALLE",
        )

    mock_info.assert_called_once_with(
        "usuario_2, ACCION_SIN_DETALLE,",
    )


@pytest.mark.parametrize(
    "funcion, argumentos, esperados",
    [
        (
            modulo_logger.log_consulta_progreso,
            ("cliente_1",),
            (
                "cliente_1",
                "CONSULTA_PROGRESO",
                "Cliente consultó su progreso",
            ),
        ),
        (
            modulo_logger.log_generar_progreso,
            ("cliente_2",),
            (
                "cliente_2",
                "GENERAR_PROGRESO",
                "Se generó reporte de progreso",
            ),
        ),
        (
            modulo_logger.log_calculo_diferencia_peso,
            ("cliente_3", -2.56),
            (
                "cliente_3",
                "CALCULO_DIFERENCIA_PESO",
                "DIF: -2.6",
            ),
        ),
        (
            modulo_logger.log_reporte_pdf_generado,
            ("cliente_4", "reporte_mensual.pdf"),
            (
                "cliente_4",
                "REPORTE_PDF_GENERADO",
                "reporte_mensual.pdf",
            ),
        ),
        (
            modulo_logger.log_registro_cliente,
            ("cliente@email.com",),
            (
                "cliente@email.com",
                "REGISTRO_CLIENTE",
                "Nuevo cliente registrado",
            ),
        ),
        (
            modulo_logger.log_registro_administrador,
            ("admin@email.com",),
            (
                "admin@email.com",
                "REGISTRO_ADMINISTRADOR",
                "Nuevo administrador registrado",
            ),
        ),
        (
            modulo_logger.log_login_exitoso,
            ("usuario@email.com",),
            (
                "usuario@email.com",
                "LOGIN_EXITOSO",
                "Inicio de sesión exitoso",
            ),
        ),
        (
            modulo_logger.log_login_fallido,
            ("usuario@email.com",),
            (
                "usuario@email.com",
                "LOGIN_FALLIDO",
                "Intento de inicio de sesión fallido",
            ),
        ),
        (
            modulo_logger.log_creacion_rutina,
            (15, 80),
            (
                "15",
                "CREACION_RUTINA",
                "ID: 80",
            ),
        ),
        (
            modulo_logger.log_creacion_ejercicio,
            (22, 9),
            (
                "22",
                "CREACION_EJERCICIO",
                "ID: 9",
            ),
        ),
        (
            modulo_logger.log_sugerencia_rutina,
            (33, "RESISTENCIA"),
            (
                "33",
                "SUGERENCIA_RUTINA",
                "RESISTENCIA",
            ),
        ),
        (
            modulo_logger.log_consulta_impacto,
            ("cliente_impacto",),
            (
                "cliente_impacto",
                "CONSULTA_IMPACTO",
                "Se consultó impacto de rutina",
            ),
        ),
    ],
)
def test_funciones_especificas_llaman_registrar_actividad(
    funcion,
    argumentos,
    esperados,
):
    """
    Verifica que cada helper use registrar_actividad
    con usuario, acción y detalle correctos.
    """
    with patch.object(
        modulo_logger,
        "registrar_actividad",
    ) as mock_registrar:
        funcion(*argumentos)

    mock_registrar.assert_called_once_with(*esperados)


def test_configuracion_del_logger_tiene_nivel_info():
    """
    Verifica configuración básica del logger global.
    """
    assert modulo_logger.logger.name == "cardio_wellness"
    assert modulo_logger.logger.level == 20


def test_archivo_log_y_handler_existen():
    """
    Verifica la creación/configuración del handler de archivo.
    """
    assert modulo_logger.logs_dir.exists()
    assert modulo_logger.archivo_log.name == "LOG_CARDIO.txt"
    assert modulo_logger.handler is not None
    assert modulo_logger.handler.level == 20


def test_ejecucion_directa_del_modulo(
    capsys,
):
    """
    Ejecuta el bloque if __name__ == '__main__'
    sin mostrar la advertencia esperada de runpy.
    """
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=(
                ".*src.utilidades.logger.*"
                "found in sys.modules.*"
            ),
            category=RuntimeWarning,
        )

        with patch(
            "logging.Logger.info",
        ):
            runpy.run_module(
                "src.utilidades.logger",
                run_name="__main__",
            )

    salida = capsys.readouterr().out

    assert "Configurando logger..." in salida
    assert "Logger configurado correctamente" in salida