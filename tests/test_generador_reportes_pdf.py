from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

from src.servicios.generador_reportes_pdf import GeneradorReportesPDF


def test_generador_pdf_crea_archivo_con_datos_completos(tmp_path):
    dir_salida = tmp_path / "reportes"
    generador = GeneradorReportesPDF(directorio_salida=str(dir_salida))

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
            "anio": 2026,
            "mes": 8,
            "peso_registrado": Decimal("65.5"),
            "total_sesiones": 8,
            "total_minutos": 360,
            "total_calorias": Decimal("2400.0"),
            "observaciones": "Completó el plan",
        }
    ]

    ruta = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad=resumen_mock,
        historial_progreso=historial_mock,
    )

    archivo = Path(ruta)
    assert archivo.exists()
    assert archivo.stat().st_size > 0

    with open(archivo, "rb") as f:
        cabecera = f.read(5)
        assert cabecera == b"%PDF-"


def test_generador_pdf_con_historial_vacio(tmp_path):
    dir_salida = tmp_path / "reportes"
    generador = GeneradorReportesPDF(directorio_salida=str(dir_salida))

    cliente_mock = Mock(id_usuario=2, nombre="Carlos", apellido="Soto", objetivo="Salud", peso=80)
    resumen_mock = {"total_sesiones": 0, "total_minutos": 0, "total_calorias": 0}

    ruta = generador.generar_reporte_progreso_cliente(
        cliente=cliente_mock,
        resumen_actividad=resumen_mock,
        historial_progreso=[],
    )

    archivo = Path(ruta)
    assert archivo.exists()
    assert archivo.stat().st_size > 0