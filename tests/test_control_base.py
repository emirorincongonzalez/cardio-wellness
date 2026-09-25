from unittest.mock import patch

from src.controladores.control_base import ControlBase


def test_control_base_registro_log(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    control._registrar_log(
        "usuario_demo",
        "ACCION_PRUEBA",
    )

    contenido = log_file.read_text(
        encoding="utf-8",
    )

    assert "usuario_demo, ACCION_PRUEBA" in contenido


def test_control_base_registro_log_con_detalle(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    control._registrar_log(
        "usuario_demo",
        "ACCION_PRUEBA",
        detalle="META: Bajar de peso",
    )

    contenido = log_file.read_text(
        encoding="utf-8",
    )

    assert (
        "usuario_demo, ACCION_PRUEBA, "
        "META: Bajar de peso"
    ) in contenido


def test_control_base_usa_sistema_si_usuario_es_none(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    control._registrar_log(
        None,
        "ACCION_SISTEMA",
    )

    contenido = log_file.read_text(
        encoding="utf-8",
    )

    assert "SISTEMA, ACCION_SISTEMA" in contenido


def test_control_base_registra_actividad_externa(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    with patch(
        "src.controladores.control_base.registrar_actividad",
    ) as mock_registrar_actividad:
        control._registrar_log(
            "usuario_demo",
            "ACCION_PRUEBA",
            detalle="Detalle adicional",
        )

    mock_registrar_actividad.assert_called_once_with(
        "usuario_demo",
        "ACCION_PRUEBA",
        "Detalle adicional",
    )


def test_control_base_envia_detalle_vacio_a_logger(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    with patch(
        "src.controladores.control_base.registrar_actividad",
    ) as mock_registrar_actividad:
        control._registrar_log(
            "usuario_demo",
            "ACCION_SIN_DETALLE",
        )

    mock_registrar_actividad.assert_called_once_with(
        "usuario_demo",
        "ACCION_SIN_DETALLE",
        "",
    )


def test_control_base_alias_registrar_auditoria(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    control._registrar_auditoria(
        "admin",
        "ACCION_AUDITORIA",
        detalle="Prueba de alias",
    )

    contenido = log_file.read_text(
        encoding="utf-8",
    )

    assert (
        "admin, ACCION_AUDITORIA, "
        "Prueba de alias"
    ) in contenido


def test_control_base_no_interrumpe_si_falla_logger_externo(
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    control = ControlBase(
        ruta_log=str(log_file),
    )

    with patch(
        "src.controladores.control_base.registrar_actividad",
        side_effect=RuntimeError("Error de logger externo"),
    ):
        with patch(
            "logging.Logger.warning",
        ) as mock_warning:
            control._registrar_log(
                "usuario_demo",
                "ACCION_CON_ERROR",
            )

    mock_warning.assert_called_once()

    mensaje = mock_warning.call_args.args[0]

    assert "No se pudo registrar la auditoria" in mensaje
    assert "Error de logger externo" in mensaje

    contenido = log_file.read_text(
        encoding="utf-8",
    )

    assert "usuario_demo, ACCION_CON_ERROR" in contenido