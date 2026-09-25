from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.modelos.progreso_mensual import ProgresoMensual
from src.servicios.sistema_wellness import (
    SistemaWellness,
    _normalizar_texto,
)


@pytest.fixture
def mock_clientes():
    return Mock()


@pytest.fixture
def mock_rutinas():
    return Mock()


@pytest.fixture
def mock_progreso():
    return Mock()


@pytest.fixture
def mock_pdf():
    return Mock()


@pytest.fixture
def sistema(
    mock_clientes,
    mock_rutinas,
    mock_progreso,
    mock_pdf,
    tmp_path,
):
    """
    Crea el servicio con dependencias simuladas y log temporal.
    """
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    return SistemaWellness(
        control_clientes=mock_clientes,
        control_rutinas=mock_rutinas,
        control_progreso=mock_progreso,
        generador_pdf=mock_pdf,
        ruta_log=str(log_file),
    )


def test_normalizar_texto_con_tildes_y_tipos():
    """
    Verifica mayúsculas, eliminación de tildes y conversión a texto.
    """
    assert _normalizar_texto("PÉSO") == "PESO"
    assert _normalizar_texto("MÚSCULO") == "MUSCULO"
    assert _normalizar_texto("cardio") == "CARDIO"
    assert _normalizar_texto(123) == "123"
    assert _normalizar_texto(None) == "NONE"


@pytest.mark.parametrize(
    "clientes, rutinas, progreso",
    [
        (None, Mock(), Mock()),
        (Mock(), None, Mock()),
        (Mock(), Mock(), None),
    ],
)
def test_constructor_requiere_controladores(
    clientes,
    rutinas,
    progreso,
    tmp_path,
):
    """
    SistemaWellness exige los tres controladores principales.
    """
    with pytest.raises(
        ValueError,
        match="SistemaWellness requiere",
    ):
        SistemaWellness(
            control_clientes=clientes,
            control_rutinas=rutinas,
            control_progreso=progreso,
            ruta_log=str(tmp_path / "log.txt"),
        )


def test_constructor_crea_generador_pdf_por_defecto(
    mock_clientes,
    mock_rutinas,
    mock_progreso,
    tmp_path,
):
    """
    Cubre la rama generador_pdf=None.
    """
    sistema = SistemaWellness(
        control_clientes=mock_clientes,
        control_rutinas=mock_rutinas,
        control_progreso=mock_progreso,
        generador_pdf=None,
        ruta_log=str(tmp_path / "log.txt"),
    )

    assert sistema.generador_pdf is not None


def test_registrar_log_sin_detalle(
    sistema,
):
    """
    Cubre la llamada al log base cuando detalle es None.
    """
    sistema._registrar_log(
        "USUARIO_1",
        "ACCION_SIN_DETALLE",
    )

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "USUARIO_1, ACCION_SIN_DETALLE" in contenido


def test_registrar_log_con_detalle(
    sistema,
):
    """
    Cubre la llamada al log base con detalle.
    """
    sistema._registrar_log(
        "USUARIO_2",
        "ACCION_CON_DETALLE",
        "DETALLE_PRUEBA",
    )

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "USUARIO_2, ACCION_CON_DETALLE, "
        "DETALLE_PRUEBA"
    ) in contenido


def test_sugerir_rutina_sin_rutinas(
    sistema,
    mock_rutinas,
):
    """
    No hay sugerencia cuando no existen rutinas disponibles.
    """
    mock_rutinas.listar.return_value = []

    cliente = SimpleNamespace(
        id_usuario=1,
        objetivo="Perder peso",
    )

    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(
        cliente,
    )

    assert resultado is None

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "1, SUGERENCIA_RUTINA, SIN_RUTINAS" in contenido


def test_sugerir_rutina_cardio_desde_diccionario(
    sistema,
    mock_rutinas,
):
    """
    Sugiere rutina cardio usando una rutina representada por dict.
    """
    rutina_cardio = {
        "nombre": "Cardio Quema Grasa",
        "descripcion": "Rutina de resistencia",
    }

    rutina_fuerza = {
        "nombre": "Fuerza Muscular",
        "descripcion": "Pesas",
    }

    mock_rutinas.listar.return_value = [
        rutina_cardio,
        rutina_fuerza,
    ]

    cliente = SimpleNamespace(
        id_usuario=2,
        objetivo="Quiero adelgazar y perder peso",
    )

    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(
        cliente,
    )

    assert resultado == rutina_cardio

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "2, SUGERENCIA_RUTINA, CARDIO_QUEMA_GRASA"
        in contenido
    )


def test_sugerir_rutina_cardio_desde_descripcion_objeto(
    sistema,
    mock_rutinas,
):
    """
    Cubre cardio detectado por GRASA en la descripción.
    """
    rutina_cardio = SimpleNamespace(
        nombre="Rutina metabólica",
        descripcion="Ejercicios para quema de grasa",
    )

    mock_rutinas.listar.return_value = [rutina_cardio]

    cliente = SimpleNamespace(
        id_usuario=3,
        objetivo="Mejorar cardio",
    )

    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(
        cliente,
    )

    assert resultado is rutina_cardio


def test_sugerir_rutina_fuerza(
    sistema,
    mock_rutinas,
):
    """
    Sugiere rutina de fuerza usando coincidencia por nombre.
    """
    rutina_cardio = SimpleNamespace(
        nombre="Cardio ligero",
        descripcion="Actividad aeróbica",
    )

    rutina_fuerza = SimpleNamespace(
        nombre="Fuerza e Hipertrofia",
        descripcion="Trabajo de pesas",
    )

    mock_rutinas.listar.return_value = [
        rutina_cardio,
        rutina_fuerza,
    ]

    cliente = SimpleNamespace(
        id_usuario=4,
        objetivo="Aumentar músculo y volumen",
    )

    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(
        cliente,
    )

    assert resultado is rutina_fuerza

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "4, SUGERENCIA_RUTINA, FUERZA_HIPERTROFIA"
        in contenido
    )


def test_sugerir_rutina_usa_default_si_no_hay_coincidencia(
    sistema,
    mock_rutinas,
):
    """
    Devuelve la primera rutina si el objetivo no coincide.
    """
    rutina_default = SimpleNamespace(
        nombre="Rutina general",
        descripcion="Rutina básica",
    )

    otra_rutina = SimpleNamespace(
        nombre="Rutina movilidad",
        descripcion="Estiramiento",
    )

    mock_rutinas.listar.return_value = [
        rutina_default,
        otra_rutina,
    ]

    cliente = SimpleNamespace(
        id_usuario=5,
        objetivo="Prepararme para una carrera de natación",
    )

    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(
        cliente,
    )

    assert resultado is rutina_default

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "5, SUGERENCIA_RUTINA, DEFAULT" in contenido


def test_sugerir_rutina_cliente_sin_id_usa_identificador_generico(
    sistema,
    mock_rutinas,
):
    """
    Cubre _identificador_cliente cuando no existe id_usuario.
    """
    rutina = SimpleNamespace(
        nombre="Rutina general",
        descripcion="Sin coincidencia",
    )

    mock_rutinas.listar.return_value = [rutina]

    cliente = SimpleNamespace(
        objetivo="Objetivo desconocido",
    )

    resultado = sistema.evaluar_objetivo_y_sugerir_rutina(
        cliente,
    )

    assert resultado is rutina

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "CLIENTE, SUGERENCIA_RUTINA, DEFAULT" in contenido


@pytest.mark.parametrize(
    "historial",
    [
        [],
        None,
        [{"peso_registrado": 70}],
    ],
)
def test_calcular_diferencia_peso_historial_insuficiente(
    sistema,
    mock_progreso,
    historial,
):
    """
    Retorna Decimal 0 cuando hay menos de dos registros.
    """
    mock_progreso.consultar_progreso.return_value = historial

    resultado = sistema.calcular_diferencia_peso_mensual(10)

    assert resultado == Decimal("0.0")

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "CLIENTE_10, CALCULO_DIFERENCIA_PESO, "
        "HISTORIAL_INSUFICIENTE"
    ) in contenido


def test_calcular_diferencia_peso_con_diccionarios(
    sistema,
    mock_progreso,
):
    """
    Cubre pesos obtenidos desde peso_registrado en dict.
    """
    mock_progreso.consultar_progreso.return_value = [
        {"peso_registrado": Decimal("68.5")},
        {"peso_registrado": Decimal("70.0")},
    ]

    resultado = sistema.calcular_diferencia_peso_mensual(11)

    assert resultado == Decimal("-1.5")

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "CLIENTE_11, CALCULO_DIFERENCIA_PESO, DIF: -1.5"
        in contenido
    )


def test_calcular_diferencia_peso_con_clave_peso(
    sistema,
    mock_progreso,
):
    """
    Cubre fallback de dict desde peso_registrado a peso.
    """
    mock_progreso.consultar_progreso.return_value = [
        {"peso": "75.2"},
        {"peso": "74.0"},
    ]

    resultado = sistema.calcular_diferencia_peso_mensual(12)

    assert resultado == Decimal("1.2")


def test_calcular_diferencia_peso_con_objeto_peso(
    sistema,
    mock_progreso,
):
    """
    Cubre objetos que poseen atributo peso.
    """
    registro_actual = SimpleNamespace(peso=80)
    registro_anterior = SimpleNamespace(peso=78)

    mock_progreso.consultar_progreso.return_value = [
        registro_actual,
        registro_anterior,
    ]

    resultado = sistema.calcular_diferencia_peso_mensual(13)

    assert resultado == Decimal("2")


def test_calcular_diferencia_peso_con_objeto_peso_registrado(
    sistema,
    mock_progreso,
):
    """
    Cubre objetos que poseen atributo peso_registrado.
    """
    registro_actual = SimpleNamespace(
        peso_registrado=Decimal("70.5"),
    )

    registro_anterior = SimpleNamespace(
        peso_registrado=Decimal("72.0"),
    )

    mock_progreso.consultar_progreso.return_value = [
        registro_actual,
        registro_anterior,
    ]

    resultado = sistema.calcular_diferencia_peso_mensual(14)

    assert resultado == Decimal("-1.5")


def test_obtener_peso_con_progreso_mensual(
    sistema,
):
    """
    Cubre la rama específica isinstance(ProgresoMensual).
    """
    progreso = ProgresoMensual(
        id_cliente=1,
        mes=date(2026, 1, 1),
        peso=Decimal("71.25"),
        sesiones_planificadas=4,
        sesiones_completadas=2,
    )

    assert sistema._obtener_peso(progreso) == Decimal("71.25")


def test_obtener_peso_rechaza_registro_sin_peso(
    sistema,
):
    """
    Cubre TypeError cuando no existen atributos de peso.
    """
    with pytest.raises(
        TypeError,
        match="no contiene un peso válido",
    ):
        sistema._obtener_peso(SimpleNamespace())


def test_emitir_reporte_retorna_none_si_cliente_por_id_no_existe(
    sistema,
    mock_clientes,
):
    """
    Cubre búsqueda de cliente fallida mediante ID.
    """
    mock_clientes.buscar_por_id.return_value = None

    resultado = sistema.emitir_reporte_pdf_cliente(99)

    assert resultado is None

    mock_clientes.buscar_por_id.assert_called_once_with(99)

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "ID_99, REPORTE_PDF_ERROR, CLIENTE_NO_ENCONTRADO"
        in contenido
    )


def test_emitir_reporte_retorna_none_si_cliente_objeto_es_none(
    sistema,
):
    """
    Cubre identificador CLIENTE_DESCONOCIDO.
    """
    resultado = sistema.emitir_reporte_pdf_cliente(None)

    assert resultado is None

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "CLIENTE_DESCONOCIDO, REPORTE_PDF_ERROR, "
        "CLIENTE_NO_ENCONTRADO"
    ) in contenido


def test_emitir_reporte_requiere_id_cliente(
    sistema,
):
    """
    Un objeto cliente sin id_usuario no puede generar reporte.
    """
    cliente_sin_id = SimpleNamespace(
        correo_electronico="sinid@email.com",
    )

    with pytest.raises(
        ValueError,
        match="no tiene un id_usuario válido",
    ):
        sistema.emitir_reporte_pdf_cliente(cliente_sin_id)


def test_emitir_reporte_pdf_exitoso_con_objeto_cliente(
    sistema,
    mock_progreso,
    mock_pdf,
):
    """
    Genera reporte usando directamente un objeto cliente.
    """
    cliente = SimpleNamespace(
        id_usuario=20,
        nombre="Laura",
        correo_electronico="laura@email.com",
    )

    resumen = {"sesiones": 10}
    historial = [{"peso_registrado": 70}]
    ruta = "reportes/progreso_laura.pdf"

    mock_progreso.calcular_resumen_cliente.return_value = resumen
    mock_progreso.consultar_progreso.return_value = historial

    mock_pdf.generar_reporte_progreso_cliente.return_value = ruta

    resultado = sistema.emitir_reporte_pdf_cliente(
        cliente,
        ruta_archivo="reportes/personalizado.pdf",
    )

    assert resultado == ruta

    mock_pdf.generar_reporte_progreso_cliente.assert_called_once_with(
        cliente=cliente,
        resumen_actividad=resumen,
        historial_progreso=historial,
        ruta_archivo="reportes/personalizado.pdf",
    )

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "laura@email.com, REPORTE_PDF_GENERADO, "
        "reportes/progreso_laura.pdf"
    ) in contenido


def test_emitir_reporte_usa_id_como_usuario_si_no_hay_correo(
    sistema,
    mock_progreso,
    mock_pdf,
):
    """
    Cubre valor por defecto ID_n cuando no existe correo.
    """
    cliente = SimpleNamespace(id_usuario=21)

    mock_progreso.calcular_resumen_cliente.return_value = {}
    mock_progreso.consultar_progreso.return_value = []
    mock_pdf.generar_reporte_progreso_cliente.return_value = (
        "reporte.pdf"
    )

    resultado = sistema.emitir_reporte_pdf_cliente(cliente)

    assert resultado == "reporte.pdf"

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert "ID_21, REPORTE_PDF_GENERADO, reporte.pdf" in contenido


def test_emitir_reporte_convierte_error_a_runtime_error(
    sistema,
    mock_progreso,
):
    """
    Cubre el bloque except al fallar la generación del reporte.
    """
    cliente = SimpleNamespace(
        id_usuario=30,
        correo_electronico="error@email.com",
    )

    mock_progreso.calcular_resumen_cliente.side_effect = (
        ValueError("Resumen no disponible")
    )

    with pytest.raises(
        RuntimeError,
        match="Error al generar el reporte PDF",
    ) as error:
        sistema.emitir_reporte_pdf_cliente(cliente)

    assert "Resumen no disponible" in str(error.value)

    contenido = sistema.ruta_log.read_text(
        encoding="utf-8",
    )

    assert (
        "error@email.com, REPORTE_PDF_ERROR, "
        "Resumen no disponible"
    ) in contenido


def test_obtener_cliente_retorna_objeto_directamente(
    sistema,
):
    """
    Cubre _obtener_cliente cuando recibe un objeto.
    """
    cliente = SimpleNamespace(id_usuario=40)

    assert sistema._obtener_cliente(cliente) is cliente


def test_identificador_cliente(
    sistema,
):
    """
    Cubre identificador con ID y sin ID.
    """
    cliente_con_id = SimpleNamespace(id_usuario=50)
    cliente_sin_id = SimpleNamespace()

    assert sistema._identificador_cliente(cliente_con_id) == "50"
    assert sistema._identificador_cliente(cliente_sin_id) == "CLIENTE"


def test_obtener_textos_rutina_para_dict_y_objeto(
    sistema,
):
    """
    Cubre textos de rutina como dict y como objeto.
    """
    rutina_dict = {
        "nombre": "Cardio Élite",
        "descripcion": "Quema de Grása",
    }

    rutina_objeto = SimpleNamespace(
        nombre="Fuerza Máxima",
        descripcion="Hipertrofía",
    )

    assert sistema._obtener_textos_rutina(rutina_dict) == (
        "CARDIO ELITE",
        "QUEMA DE GRASA",
    )

    assert sistema._obtener_textos_rutina(rutina_objeto) == (
        "FUERZA MAXIMA",
        "HIPERTROFIA",
    )