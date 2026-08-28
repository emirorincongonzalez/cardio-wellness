from src.controladores.control_base import ControlBase


def test_control_base_registro_log(tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    control = ControlBase(ruta_log=str(log_file))

    control._registrar_log("usuario_demo", "ACCION_PRUEBA")
    contenido = log_file.read_text(encoding="utf-8")

    assert "usuario_demo, ACCION_PRUEBA" in contenido


def test_control_base_registro_log_con_detalle(tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    control = ControlBase(ruta_log=str(log_file))

    control._registrar_log("usuario_demo", "ACCION_PRUEBA", detalle="META: Bajar de peso")
    contenido = log_file.read_text(encoding="utf-8")

    assert "usuario_demo, ACCION_PRUEBA, META: Bajar de peso" in contenido