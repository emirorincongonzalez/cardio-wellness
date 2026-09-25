from datetime import date, datetime
from decimal import Decimal

import pytest

from src.modelos.progreso_mensual import ProgresoMensual


@pytest.fixture
def progreso():
    return ProgresoMensual(
        id_progreso=1,
        id_cliente=10,
        mes=date(2026, 5, 15),
        peso=Decimal("70.5"),
        sesiones_completadas=6,
        sesiones_planificadas=12,
    )


def test_crear_progreso_correctamente(
    progreso,
):
    assert progreso.id_progreso == 1
    assert progreso.id_cliente == 10
    assert progreso.mes == date(2026, 5, 1)
    assert progreso.peso == Decimal("70.50")
    assert progreso.sesiones_completadas == 6
    assert progreso.sesiones_planificadas == 12
    assert progreso.porcentaje_cumplimiento == 50.0


def test_ids_permiten_none():
    progreso = ProgresoMensual(
        id_progreso=None,
        id_cliente=None,
        mes=date(2026, 1, 1),
        peso=70,
    )

    assert progreso.id_progreso is None
    assert progreso.id_cliente is None


@pytest.mark.parametrize(
    "atributo,valor,mensaje",
    [
        ("id_progreso", True, "ID de progreso"),
        ("id_progreso", 0, "ID de progreso"),
        ("id_progreso", -1, "ID de progreso"),
        ("id_progreso", "1", "ID de progreso"),
        ("id_cliente", True, "ID de cliente"),
        ("id_cliente", 0, "ID de cliente"),
        ("id_cliente", -1, "ID de cliente"),
        ("id_cliente", "10", "ID de cliente"),
    ],
)
def test_ids_invalidos(
    progreso,
    atributo,
    valor,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        setattr(
            progreso,
            atributo,
            valor,
        )


def test_mes_datetime_se_convierte_a_primer_dia():
    progreso = ProgresoMensual(
        mes=datetime(2026, 7, 25, 10, 30),
        peso=70,
    )

    assert progreso.mes == date(2026, 7, 1)


def test_mes_se_normaliza_primer_dia(
    progreso,
):
    progreso.mes = date(2026, 8, 30)

    assert progreso.mes == date(2026, 8, 1)


@pytest.mark.parametrize(
    "mes",
    [
        None,
        "2026-05-01",
        10,
        [],
    ],
)
def test_mes_invalido(
    progreso,
    mes,
):
    with pytest.raises(
        ValueError,
        match="mes debe ser",
    ):
        progreso.mes = mes


@pytest.mark.parametrize(
    "peso,esperado",
    [
        (70, Decimal("70.00")),
        (70.5, Decimal("70.50")),
        (Decimal("68.125"), Decimal("68.12")),
        (Decimal("68.129"), Decimal("68.13")),
    ],
)
def test_peso_valido_y_redondeado(
    progreso,
    peso,
    esperado,
):
    progreso.peso = peso

    assert progreso.peso == esperado


@pytest.mark.parametrize(
    "peso,mensaje",
    [
        (True, "peso debe ser numérico"),
        (False, "peso debe ser numérico"),
        (None, "peso debe ser numérico"),
        ("70", "peso debe ser numérico"),
        ([], "peso debe ser numérico"),
        (0, "peso debe ser mayor"),
        (-1, "peso debe ser mayor"),
    ],
)
def test_peso_invalido(
    progreso,
    peso,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        progreso.peso = peso


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
        -1,
        "1",
        1.5,
        None,
    ],
)
def test_sesiones_completadas_invalidas(
    progreso,
    valor,
):
    with pytest.raises(
        ValueError,
        match="sesiones completadas",
    ):
        progreso.sesiones_completadas = valor


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
        -1,
        "1",
        1.5,
        None,
    ],
)
def test_sesiones_planificadas_invalidas(
    progreso,
    valor,
):
    with pytest.raises(
        ValueError,
        match="sesiones planificadas",
    ):
        progreso.sesiones_planificadas = valor


def test_actualiza_porcentaje_al_actualizar_completadas(
    progreso,
):
    progreso.sesiones_completadas = 9

    assert progreso.sesiones_completadas == 9
    assert progreso.porcentaje_cumplimiento == 75.0


def test_actualiza_porcentaje_al_actualizar_planificadas(
    progreso,
):
    progreso.sesiones_planificadas = 6

    assert progreso.sesiones_planificadas == 6
    assert progreso.porcentaje_cumplimiento == 100.0


@pytest.mark.parametrize(
    "porcentaje,esperado",
    [
        (0, 0.0),
        (50, 50.0),
        (66.666, 66.67),
        (Decimal("80.555"), 80.56),
        (150, 100.0),
    ],
)
def test_porcentaje_valido(
    progreso,
    porcentaje,
    esperado,
):
    progreso.porcentaje_cumplimiento = porcentaje

    assert progreso.porcentaje_cumplimiento == esperado


@pytest.mark.parametrize(
    "porcentaje,mensaje",
    [
        (True, "porcentaje debe ser numérico"),
        (False, "porcentaje debe ser numérico"),
        (None, "porcentaje debe ser numérico"),
        ("50", "porcentaje debe ser numérico"),
        ([], "porcentaje debe ser numérico"),
        (-1, "porcentaje no puede ser negativo"),
    ],
)
def test_porcentaje_invalido(
    progreso,
    porcentaje,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        progreso.porcentaje_cumplimiento = porcentaje


def test_actualizar_peso(
    progreso,
):
    progreso.actualizar_peso(Decimal("68.75"))

    assert progreso.peso == Decimal("68.75")


def test_actualizar_sesiones_solo_completadas(
    progreso,
):
    progreso.actualizar_sesiones(
        sesiones_completadas=9,
    )

    assert progreso.sesiones_completadas == 9
    assert progreso.sesiones_planificadas == 12
    assert progreso.porcentaje_cumplimiento == 75.0


def test_actualizar_sesiones_completadas_y_planificadas(
    progreso,
):
    progreso.actualizar_sesiones(
        sesiones_completadas=8,
        sesiones_planificadas=10,
    )

    assert progreso.sesiones_completadas == 8
    assert progreso.sesiones_planificadas == 10
    assert progreso.porcentaje_cumplimiento == 80.0


def test_calcular_porcentaje_con_cero_planificadas(
    progreso,
):
    progreso._sesiones_planificadas = 0
    progreso._sesiones_completadas = 0

    assert progreso._calcular_porcentaje() == 0.0


def test_calcular_porcentaje_limita_a_cien(
    progreso,
):
    progreso._sesiones_planificadas = 5
    progreso._sesiones_completadas = 10

    assert progreso._calcular_porcentaje() == 100.0


def test_calcular_cumplimiento(
    progreso,
):
    progreso._sesiones_completadas = 3
    progreso._sesiones_planificadas = 4

    resultado = progreso.calcular_cumplimiento()

    assert resultado == 75.0
    assert progreso.porcentaje_cumplimiento == 75.0


def test_actualizar_progreso(
    progreso,
):
    progreso._sesiones_completadas = 10
    progreso._sesiones_planificadas = 20
    progreso.porcentaje_cumplimiento = 0

    assert progreso.porcentaje_cumplimiento == 0.0

    progreso.actualizar_progreso()

    assert progreso.porcentaje_cumplimiento == 50.0


def test_obtener_mes_texto(
    progreso,
):
    progreso.mes = date(2026, 1, 1)

    assert progreso.obtener_mes_texto() == "January 2026"


def test_generar_resumen(
    progreso,
):
    resumen = progreso.generar_resumen()

    assert "Progreso May 2026" in resumen
    assert "Peso: 70.50 kg" in resumen
    assert "Sesiones: 6/12" in resumen
    assert "Cumplimiento: 50.00%" in resumen


def test_repr_progreso(
    progreso,
):
    representacion = repr(progreso)

    assert "ProgresoMensual(" in representacion
    assert "id_progreso=1" in representacion
    assert "id_cliente=10" in representacion
    assert "mes=2026-05-01" in representacion
    assert "peso=70.50" in representacion
    assert "sesiones_completadas=6" in representacion
    assert "sesiones_planificadas=12" in representacion
    assert "porcentaje_cumplimiento=50.0" in representacion

def test_constructor_acepta_porcentaje_explicito():
    """
    Verifica la rama del constructor cuando se proporciona
    porcentaje_cumplimiento explícitamente.
    """
    progreso = ProgresoMensual(
        id_progreso=1,
        id_cliente=10,
        mes=date(2026, 5, 1),
        peso=70,
        sesiones_completadas=2,
        sesiones_planificadas=10,
        porcentaje_cumplimiento=35.5,
    )

    assert progreso.porcentaje_cumplimiento == 35.5


def test_peso_rechaza_numero_con_texto_no_convertible(
    progreso,
):
    """
    Verifica el manejo de un número válido por tipo, pero
    cuyo texto no puede convertirse a Decimal.
    """

    class EnteroConTextoInvalido(int):
        def __str__(self):
            return "peso_invalido"

    with pytest.raises(
        ValueError,
        match="peso no tiene un formato",
    ):
        progreso.peso = EnteroConTextoInvalido(70)


def test_porcentaje_rechaza_numero_con_texto_no_convertible(
    progreso,
):
    """
    Verifica el manejo de un porcentaje numérico cuyo texto
    no puede convertirse a Decimal.
    """

    class EnteroConTextoInvalido(int):
        def __str__(self):
            return "porcentaje_invalido"

    with pytest.raises(
        ValueError,
        match="porcentaje no tiene un formato",
    ):
        progreso.porcentaje_cumplimiento = (
            EnteroConTextoInvalido(50)
        )