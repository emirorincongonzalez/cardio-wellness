from datetime import date, datetime
from decimal import Decimal

import pytest

from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import (
    SesionEntrenamiento,
)


@pytest.fixture
def sesion():
    return SesionEntrenamiento(
        id_sesion=1,
        id_cliente=10,
        id_rutina=5,
        fecha=date(2026, 5, 10),
        nombre_ejercicio="Caminata",
        duracion_real=30,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=Decimal("250.50"),
        observaciones="Buen ritmo",
        veces_planificadas=2,
        veces_realizadas=1,
    )


def test_crear_sesion_correctamente(
    sesion,
):
    assert sesion.id_sesion == 1
    assert sesion.id_cliente == 10
    assert sesion.id_rutina == 5
    assert sesion.fecha == date(2026, 5, 10)
    assert sesion.nombre_ejercicio == "Caminata"
    assert sesion.duracion_real == 30
    assert sesion.intensidad_real == Intensidad.MEDIA
    assert sesion.calorias_quemadas == Decimal("250.50")
    assert sesion.observaciones == "Buen ritmo"
    assert sesion.veces_planificadas == 2
    assert sesion.veces_realizadas == 1
    assert sesion.completada is False
    assert sesion.porcentaje_cumplimiento == 50.0


def test_ids_permiten_none():
    sesion = SesionEntrenamiento(
        fecha=date(2026, 1, 1),
        duracion_real=20,
        intensidad_real="BAJA",
        calorias_quemadas=100,
        id_sesion=None,
        id_cliente=None,
        id_rutina=None,
    )

    assert sesion.id_sesion is None
    assert sesion.id_cliente is None
    assert sesion.id_rutina is None


@pytest.mark.parametrize(
    "atributo,valor,mensaje",
    [
        ("id_sesion", True, "ID de sesión"),
        ("id_sesion", 0, "ID de sesión"),
        ("id_sesion", -1, "ID de sesión"),
        ("id_sesion", "1", "ID de sesión"),
        ("id_cliente", True, "ID de cliente"),
        ("id_cliente", 0, "ID de cliente"),
        ("id_cliente", -1, "ID de cliente"),
        ("id_cliente", "10", "ID de cliente"),
        ("id_rutina", True, "ID de rutina"),
        ("id_rutina", 0, "ID de rutina"),
        ("id_rutina", -1, "ID de rutina"),
        ("id_rutina", "5", "ID de rutina"),
    ],
)
def test_ids_invalidos(
    sesion,
    atributo,
    valor,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        setattr(
            sesion,
            atributo,
            valor,
        )


def test_fecha_datetime_se_convierte_a_date(
    sesion,
):
    sesion.fecha = datetime(
        2026,
        6,
        15,
        10,
        30,
    )

    assert sesion.fecha == date(2026, 6, 15)


@pytest.mark.parametrize(
    "fecha_invalida",
    [
        None,
        "2026-01-01",
        10,
        [],
    ],
)
def test_fecha_invalida(
    sesion,
    fecha_invalida,
):
    with pytest.raises(
        ValueError,
        match="fecha debe ser",
    ):
        sesion.fecha = fecha_invalida


def test_nombre_ejercicio_se_limpia(
    sesion,
):
    sesion.nombre_ejercicio = "  Bicicleta  "

    assert sesion.nombre_ejercicio == "Bicicleta"


def test_nombre_ejercicio_none_es_vacio(
    sesion,
):
    sesion.nombre_ejercicio = None

    assert sesion.nombre_ejercicio == ""


@pytest.mark.parametrize(
    "nombre",
    [
        10,
        [],
        {},
        "x" * 101,
    ],
)
def test_nombre_ejercicio_invalido(
    sesion,
    nombre,
):
    with pytest.raises(ValueError):
        sesion.nombre_ejercicio = nombre


@pytest.mark.parametrize(
    "duracion",
    [
        True,
        False,
        "30",
        30.5,
        None,
    ],
)
def test_duracion_debe_ser_entero(
    sesion,
    duracion,
):
    with pytest.raises(
        ValueError,
        match="duración debe ser un entero",
    ):
        sesion.duracion_real = duracion


@pytest.mark.parametrize(
    "duracion",
    [
        0,
        -1,
    ],
)
def test_duracion_debe_ser_positiva(
    sesion,
    duracion,
):
    with pytest.raises(
        ValueError,
        match="duración debe ser mayor",
    ):
        sesion.duracion_real = duracion


def test_duracion_valida(
    sesion,
):
    sesion.duracion_real = 45

    assert sesion.duracion_real == 45


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (Intensidad.BAJA, Intensidad.BAJA),
        (Intensidad.MEDIA, Intensidad.MEDIA),
        (Intensidad.ALTA, Intensidad.ALTA),
        ("baja", Intensidad.BAJA),
        (" MEDIA ", Intensidad.MEDIA),
        ("Alta", Intensidad.ALTA),
    ],
)
def test_intensidad_valida(
    sesion,
    valor,
    esperado,
):
    sesion.intensidad_real = valor

    assert sesion.intensidad_real == esperado


@pytest.mark.parametrize(
    "intensidad",
    [
        None,
        True,
        10,
        "",
        "SUAVE",
        "MAXIMA",
    ],
)
def test_intensidad_invalida(
    sesion,
    intensidad,
):
    with pytest.raises(ValueError):
        sesion.intensidad_real = intensidad


@pytest.mark.parametrize(
    "calorias,esperado",
    [
        (0, Decimal("0")),
        (150, Decimal("150")),
        (150.5, Decimal("150.5")),
        (Decimal("200.25"), Decimal("200.25")),
    ],
)
def test_calorias_validas(
    sesion,
    calorias,
    esperado,
):
    sesion.calorias_quemadas = calorias

    assert sesion.calorias_quemadas == esperado


@pytest.mark.parametrize(
    "calorias,mensaje",
    [
        (True, "calorías deben ser numéricas"),
        (False, "calorías deben ser numéricas"),
        (None, "calorías deben ser numéricas"),
        ([], "calorías deben ser numéricas"),
        ("texto", "calorías deben ser numéricas"),
        (-1, "calorías no pueden ser negativas"),
        (-0.5, "calorías no pueden ser negativas"),
    ],
)
def test_calorias_invalidas(
    sesion,
    calorias,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        sesion.calorias_quemadas = calorias


def test_observaciones_se_limpian(
    sesion,
):
    sesion.observaciones = "  Sesión completada  "

    assert sesion.observaciones == "Sesión completada"


def test_observaciones_none_es_vacio(
    sesion,
):
    sesion.observaciones = None

    assert sesion.observaciones == ""


@pytest.mark.parametrize(
    "observaciones",
    [
        10,
        [],
        {},
    ],
)
def test_observaciones_invalidas(
    sesion,
    observaciones,
):
    with pytest.raises(
        ValueError,
        match="observaciones",
    ):
        sesion.observaciones = observaciones


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
        0,
        -1,
        "2",
        2.5,
        None,
    ],
)
def test_veces_planificadas_invalidas(
    sesion,
    valor,
):
    with pytest.raises(
        ValueError,
        match="veces planificadas",
    ):
        sesion.veces_planificadas = valor


def test_planificadas_no_pueden_ser_menores_que_realizadas(
    sesion,
):
    sesion.veces_realizadas = 2

    with pytest.raises(
        ValueError,
        match="menores que las realizadas",
    ):
        sesion.veces_planificadas = 1


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
def test_veces_realizadas_invalidas(
    sesion,
    valor,
):
    with pytest.raises(
        ValueError,
        match="veces realizadas",
    ):
        sesion.veces_realizadas = valor


def test_realizadas_no_pueden_superar_planificadas(
    sesion,
):
    with pytest.raises(
        ValueError,
        match="superar las planificadas",
    ):
        sesion.veces_realizadas = 3


def test_sesion_completada_y_porcentaje(
    sesion,
):
    sesion.registrar_resultado(2)

    assert sesion.veces_realizadas == 2
    assert sesion.completada is True
    assert sesion.porcentaje_cumplimiento == 100.0
    assert sesion.obtener_estado_cumplimiento() == (
        "COMPLETADA"
    )


def test_sesion_pendiente_y_porcentaje(
    sesion,
):
    sesion.registrar_resultado(1)

    assert sesion.completada is False
    assert sesion.porcentaje_cumplimiento == 50.0
    assert sesion.obtener_estado_cumplimiento() == (
        "PENDIENTE"
    )


def test_marcar_como_completada_exitoso(
    sesion,
):
    sesion.veces_realizadas = 2

    assert sesion.marcar_como_completada() is None


def test_marcar_como_completada_rechaza_pendiente(
    sesion,
):
    with pytest.raises(
        ValueError,
        match="no puede marcarse",
    ):
        sesion.marcar_como_completada()


def test_parametro_completada_acepta_booleano():
    sesion = SesionEntrenamiento(
        fecha=date(2026, 1, 1),
        duracion_real=20,
        intensidad_real="BAJA",
        calorias_quemadas=100,
        completada=True,
    )

    assert sesion.completada is False


@pytest.mark.parametrize(
    "completada",
    [
        "True",
        1,
        0,
        [],
        {},
    ],
)
def test_parametro_completada_invalido(
    completada,
):
    with pytest.raises(
        ValueError,
        match="Completada debe ser",
    ):
        SesionEntrenamiento(
            fecha=date(2026, 1, 1),
            duracion_real=20,
            intensidad_real="BAJA",
            calorias_quemadas=100,
            completada=completada,
        )


def test_obtener_resumen_con_rutina_y_ejercicio(
    sesion,
):
    resumen = sesion.obtener_resumen()

    assert "Sesión 1" in resumen
    assert "Cliente: 10" in resumen
    assert "Rutina: 5" in resumen
    assert "Ejercicio: Caminata" in resumen
    assert "Duración: 30 min" in resumen
    assert "Intensidad: MEDIA" in resumen
    assert "Calorías: 250.50" in resumen
    assert "Realizadas: 1/2" in resumen
    assert "Cumplimiento: 50.00%" in resumen
    assert "Estado: PENDIENTE" in resumen


def test_obtener_resumen_sin_rutina_ni_ejercicio():
    sesion = SesionEntrenamiento(
        fecha=date(2026, 1, 1),
        duracion_real=20,
        intensidad_real="BAJA",
        calorias_quemadas=100,
        id_sesion=None,
        id_cliente=None,
        id_rutina=None,
        nombre_ejercicio="",
    )

    resumen = sesion.obtener_resumen()

    assert "Rutina: Sin rutina" in resumen
    assert "Ejercicio: Sin ejercicio" in resumen


def test_repr_sesion(
    sesion,
):
    representacion = repr(sesion)

    assert "SesionEntrenamiento(" in representacion
    assert "id_sesion=1" in representacion
    assert "id_cliente=10" in representacion
    assert "id_rutina=5" in representacion
    assert "nombre_ejercicio='Caminata'" in representacion
    assert "duracion_real=30" in representacion
    assert "intensidad_real='MEDIA'" in representacion
    assert "calorias_quemadas=250.50" in representacion
    assert "veces_planificadas=2" in representacion
    assert "veces_realizadas=1" in representacion
    assert "completada=False" in representacion

def test_porcentaje_cumplimiento_con_planificadas_cero(
    sesion,
):
    """
    Verifica protección ante datos históricos inválidos con
    cero sesiones planificadas.
    """
    sesion._veces_planificadas = 0
    sesion._veces_realizadas = 0

    assert sesion.porcentaje_cumplimiento == 0.0