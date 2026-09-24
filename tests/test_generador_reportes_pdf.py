from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

from src.modelos.progreso_mensual import ProgresoMensual
from src.servicios.generador_reportes_pdf import (
    GeneradorReportesPDF,
)


def _verificar_pdf(ruta_pdf: str) -> Path:
    """
    Verifica que la ruta exista, no esté vacía y sea un PDF.
    """
    archivo = Path(ruta_pdf)

    assert archivo.exists()
    assert archivo.is_file()
    assert archivo.stat().st_size > 0

    with open(archivo, "rb") as archivo_pdf:
        cabecera = archivo_pdf.read(5)

    assert cabecera == b"%PDF-"

    return archivo


def test_generador_pdf_crea_archivo_con_datos_completos(
    tmp_path,
):
    """
    Genera un PDF con un cliente e historial en formato diccionario.
    """
    directorio_salida = tmp_path / "reportes"

    generador = GeneradorReportesPDF(
        directorio_salida=str(directorio_salida),
    )

    cliente_mock = Mock(
        id_usuario=101,
        nombre="Laura",
        apellido="Martínez",
        objetivo="Quemar grasa",
        peso=Decimal("65.5"),
    )

    resumen_mock = {
        "total_sesiones": 8,
        "total_minutos": 360,
        "total_calorias": Decimal("2400.0"),
    }

    historial_mock = [
        {
            "mes": date(2026, 8, 1),
            "peso_registrado": Decimal("65.5"),
            "sesiones_completadas": 8,
            "sesiones_planificadas": 10,
        }
    ]

    ruta_pdf = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad=resumen_mock,
        historial_progreso=historial_mock,
    )

    archivo = _verificar_pdf(ruta_pdf)

    assert archivo.parent == directorio_salida
    assert archivo.name.startswith(
        "reporte_progreso_cliente_101_",
    )


def test_generador_pdf_con_historial_vacio(
    tmp_path,
):
    """
    Genera un PDF aunque el cliente no tenga progreso registrado.
    """
    directorio_salida = tmp_path / "reportes"

    generador = GeneradorReportesPDF(
        directorio_salida=str(directorio_salida),
    )

    cliente_mock = Mock(
        id_usuario=2,
        nombre="Carlos",
        apellido="Soto",
        objetivo="Salud",
        peso=80,
    )

    resumen_mock = {
        "total_sesiones": 0,
        "total_minutos": 0,
        "total_calorias": 0,
    }

    ruta_pdf = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad=resumen_mock,
        historial_progreso=[],
    )

    _verificar_pdf(ruta_pdf)


def test_generador_pdf_usa_ruta_personalizada(
    tmp_path,
):
    """
    Genera el PDF en una ruta especificada explícitamente.
    """
    generador = GeneradorReportesPDF(
        directorio_salida=str(tmp_path / "salida_predeterminada"),
    )

    cliente_mock = Mock(
        id_usuario=15,
        nombre="Andrea",
        apellido="López",
        objetivo="Resistencia",
        peso=Decimal("71.0"),
    )

    ruta_personalizada = (
        tmp_path
        / "reportes_personalizados"
        / "progreso_andrea.pdf"
    )

    ruta_pdf = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad={
            "total_sesiones": 12,
            "total_minutos": 540,
            "total_calorias": 3200,
        },
        historial_progreso=[],
        ruta_archivo=str(ruta_personalizada),
    )

    archivo = _verificar_pdf(ruta_pdf)

    assert archivo == ruta_personalizada
    assert archivo.parent.exists()


def test_generador_pdf_con_progreso_mensual_objeto(
    tmp_path,
):
    """
    Genera un PDF con una instancia real de ProgresoMensual.

    Se construye mediante __new__ para cubrir la rama isinstance
    sin depender de los argumentos del constructor del modelo.
    """
    generador = GeneradorReportesPDF(
        directorio_salida=str(tmp_path / "reportes"),
    )

    cliente_mock = Mock(
        id_usuario=25,
        nombre="Marcos",
        apellido="Ruiz",
        objetivo="Mejorar condición física",
        peso=Decimal("78.3"),
    )

    progreso = ProgresoMensual.__new__(ProgresoMensual)
    progreso.mes = date(2026, 9, 1)
    progreso.peso = Decimal("78.3")
    progreso.sesiones_completadas = 9
    progreso.sesiones_planificadas = 12

    ruta_pdf = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad={
            "total_sesiones": 9,
            "total_minutos": 420,
            "total_calorias": 2800,
        },
        historial_progreso=[progreso],
    )

    _verificar_pdf(ruta_pdf)


def test_generador_pdf_con_historial_desconocido_y_sin_planificacion(
    tmp_path,
):
    """
    Genera un PDF si el historial contiene objetos no reconocidos.
    """
    generador = GeneradorReportesPDF(
        directorio_salida=str(tmp_path / "reportes"),
    )

    cliente_mock = Mock(
        id_usuario=30,
        nombre="Sofía",
        apellido="Gómez",
        objetivo="Bienestar",
        peso=Decimal("59.8"),
    )

    historial_desconocido = [
        object(),
        {
            "mes": date(2026, 10, 1),
            "peso_registrado": Decimal("59.8"),
            "sesiones_completadas": 0,
            "sesiones_planificadas": 0,
        },
    ]

    ruta_pdf = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad={
            "total_sesiones": 0,
            "total_minutos": 0,
            "total_calorias": 0,
        },
        historial_progreso=historial_desconocido,
    )

    _verificar_pdf(ruta_pdf)


def test_generador_pdf_cliente_sin_atributos_opcionales(
    tmp_path,
):
    """
    Genera un PDF con valores predeterminados para datos ausentes.
    """
    generador = GeneradorReportesPDF(
        directorio_salida=str(tmp_path / "reportes"),
    )

    cliente_sin_datos = object()

    ruta_pdf = generador.generar_reporte_progreso_cliente(
        cliente=cliente_sin_datos,
        resumen_actividad={},
        historial_progreso=[],
    )

    archivo = _verificar_pdf(ruta_pdf)

    assert "desconocido" in archivo.name