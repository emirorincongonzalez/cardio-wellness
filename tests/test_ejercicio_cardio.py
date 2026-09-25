from decimal import Decimal
from enum import Enum

import pytest

import src.modelos.ejercicio_cardio as modulo_ejercicio

from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
    Intensidad,
)


@pytest.fixture
def ejercicio():
    """
    Crea un ejercicio válido reutilizable.
    """
    return EjercicioCardio(
        id_ejercicio=1,
        nombre="Caminata rápida",
        descripcion="Caminata cardiovascular moderada",
        tipo="cardio",
        duracion_minutos=30,
        intensidad=Intensidad.MEDIA,
        calorias_estimadas=250.50,
        creado_por=5,
    )


def test_crear_ejercicio_valido(
    ejercicio,
):
    """
    Verifica los datos de una instancia válida.
    """
    assert ejercicio.id_ejercicio == 1
    assert ejercicio.nombre == "Caminata rápida"
    assert (
        ejercicio.descripcion
        == "Caminata cardiovascular moderada"
    )
    assert ejercicio.tipo == "cardio"
    assert ejercicio.duracion_minutos == 30
    assert ejercicio.intensidad == Intensidad.MEDIA
    assert ejercicio.calorias_estimadas == Decimal("250.50")
    assert ejercicio.creado_por == 5


def test_crear_ejercicio_sin_ids():
    """
    Verifica los valores opcionales id_ejercicio y creado_por.
    """
    ejercicio = EjercicioCardio(
        nombre="Bicicleta",
        descripcion="Bicicleta estática",
        tipo="cardio",
        duracion_minutos=40,
        intensidad="ALTA",
        calorias_estimadas=350,
    )

    assert ejercicio.id_ejercicio is None
    assert ejercicio.creado_por is None
    assert ejercicio.intensidad == Intensidad.ALTA
    assert ejercicio.calorias_estimadas == Decimal("350.00")


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        -10,
        True,
        False,
        "1",
        1.5,
    ],
)
def test_id_ejercicio_rechaza_valores_invalidos(
    ejercicio,
    valor,
):
    """
    Verifica que id_ejercicio solo acepte enteros positivos.
    """
    with pytest.raises(
        ValueError,
        match="ID del ejercicio debe ser un entero positivo",
    ):
        ejercicio.id_ejercicio = valor


def test_id_ejercicio_permite_none(
    ejercicio,
):
    """
    Verifica que un ID pueda volver a None.
    """
    ejercicio.id_ejercicio = None

    assert ejercicio.id_ejercicio is None


@pytest.mark.parametrize(
    "atributo, valor, mensaje",
    [
        (
            "nombre",
            "",
            "nombre no puede estar vacío",
        ),
        (
            "nombre",
            "   ",
            "nombre no puede estar vacío",
        ),
        (
            "nombre",
            None,
            "nombre no puede estar vacío",
        ),
        (
            "nombre",
            10,
            "nombre no puede estar vacío",
        ),
        (
            "descripcion",
            "",
            "descripción no puede estar vacía",
        ),
        (
            "descripcion",
            "   ",
            "descripción no puede estar vacía",
        ),
        (
            "descripcion",
            None,
            "descripción no puede estar vacía",
        ),
        (
            "tipo",
            "",
            "tipo no puede estar vacío",
        ),
        (
            "tipo",
            "   ",
            "tipo no puede estar vacío",
        ),
        (
            "tipo",
            None,
            "tipo no puede estar vacío",
        ),
    ],
)
def test_campos_texto_rechazan_valores_invalidos(
    ejercicio,
    atributo,
    valor,
    mensaje,
):
    """
    Verifica validación de nombre, descripción y tipo.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        setattr(
            ejercicio,
            atributo,
            valor,
        )


def test_campos_texto_limpian_espacios(
    ejercicio,
):
    """
    Verifica la limpieza de espacios mediante strip.
    """
    ejercicio.nombre = "  Elíptica  "
    ejercicio.descripcion = "  Cardio suave  "
    ejercicio.tipo = "  resistencia  "

    assert ejercicio.nombre == "Elíptica"
    assert ejercicio.descripcion == "Cardio suave"
    assert ejercicio.tipo == "resistencia"


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
        "30",
        None,
        [],
        {},
    ],
)
def test_duracion_rechaza_tipo_no_numerico(
    ejercicio,
    valor,
):
    """
    Cubre la validación de tipo de duración.
    """
    with pytest.raises(
        ValueError,
        match="duración debe ser numérica",
    ):
        ejercicio.duracion_minutos = valor


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        -0.5,
        Decimal("0"),
        Decimal("-2"),
    ],
)
def test_duracion_rechaza_valores_no_positivos(
    ejercicio,
    valor,
):
    """
    Verifica duración cero o negativa.
    """
    with pytest.raises(
        ValueError,
        match="duración debe ser mayor que cero",
    ):
        ejercicio.duracion_minutos = valor


@pytest.mark.parametrize(
    "valor",
    [
        30.5,
        1.2,
        Decimal("45.5"),
    ],
)
def test_duracion_rechaza_decimales_no_enteros(
    ejercicio,
    valor,
):
    """
    Cubre la validación de duración no entera.
    """
    with pytest.raises(
        ValueError,
        match="duración debe ser un número entero",
    ):
        ejercicio.duracion_minutos = valor


def test_duracion_acepta_decimal_entero(
    ejercicio,
):
    """
    Verifica Decimal entero y su conversión a int.
    """
    ejercicio.duracion_minutos = Decimal("45.0")

    assert ejercicio.duracion_minutos == 45
    assert isinstance(ejercicio.duracion_minutos, int)


def test_duracion_rechaza_conversion_decimal_invalida(
    ejercicio,
):
    """
    Cubre el except de conversión a Decimal.
    """

    class EnteroConTextoInvalido(int):
        def __str__(self):
            return "duracion_invalida"

    with pytest.raises(
        ValueError,
        match="duración no es válida",
    ):
        ejercicio.duracion_minutos = (
            EnteroConTextoInvalido(30)
        )


def test_intensidad_acepta_enum(
    ejercicio,
):
    """
    Cubre la ruta cuando recibe Intensidad directamente.
    """
    ejercicio.intensidad = Intensidad.ALTA

    assert ejercicio.intensidad == Intensidad.ALTA


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("BAJA", Intensidad.BAJA),
        ("  baja  ", Intensidad.BAJA),
        ("MEDIA", Intensidad.MEDIA),
        ("media", Intensidad.MEDIA),
        ("ALTA", Intensidad.ALTA),
        ("alta", Intensidad.ALTA),
    ],
)
def test_intensidad_acepta_texto_valido(
    ejercicio,
    valor,
    esperado,
):
    """
    Verifica normalización de nombre de intensidad.
    """
    ejercicio.intensidad = valor

    assert ejercicio.intensidad == esperado


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        "EXTREMA",
        "NINGUNA",
        1,
        True,
        [],
    ],
)
def test_intensidad_rechaza_valores_invalidos(
    ejercicio,
    valor,
):
    """
    Cubre las rutas de error de intensidad.
    """
    with pytest.raises(
        ValueError,
        match="intensidad debe ser un valor válido",
    ):
        ejercicio.intensidad = valor


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
        "250",
        None,
        [],
        {},
    ],
)
def test_calorias_rechaza_tipo_no_numerico(
    ejercicio,
    valor,
):
    """
    Cubre validación de tipo de calorías.
    """
    with pytest.raises(
        ValueError,
        match="calorías deben ser numéricas",
    ):
        ejercicio.calorias_estimadas = valor


@pytest.mark.parametrize(
    "valor",
    [
        -1,
        -0.1,
        Decimal("-0.01"),
    ],
)
def test_calorias_rechaza_valores_negativos(
    ejercicio,
    valor,
):
    """
    Verifica que calorías no permita valores negativos.
    """
    with pytest.raises(
        ValueError,
        match="calorías no pueden ser negativas",
    ):
        ejercicio.calorias_estimadas = valor


def test_calorias_acepta_cero_y_redondea(
    ejercicio,
):
    """
    Verifica cuantización de calorías a dos decimales.
    """
    ejercicio.calorias_estimadas = Decimal("123.456")

    assert ejercicio.calorias_estimadas == Decimal("123.46")

    ejercicio.calorias_estimadas = 0

    assert ejercicio.calorias_estimadas == Decimal("0.00")


def test_calorias_rechaza_conversion_decimal_invalida(
    ejercicio,
):
    """
    Cubre el except de conversión Decimal de calorías.
    """

    class EnteroConTextoInvalido(int):
        def __str__(self):
            return "calorias_invalidas"

    with pytest.raises(
        ValueError,
        match="calorías no son válidas",
    ):
        ejercicio.calorias_estimadas = (
            EnteroConTextoInvalido(200)
        )


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        True,
        False,
        "5",
        2.5,
    ],
)
def test_creado_por_rechaza_valores_invalidos(
    ejercicio,
    valor,
):
    """
    Verifica que creado_por sea un entero positivo o None.
    """
    with pytest.raises(
        ValueError,
        match="creado_por debe ser un ID",
    ):
        ejercicio.creado_por = valor


def test_creado_por_permite_none(
    ejercicio,
):
    """
    Verifica que creado_por pueda ser None.
    """
    ejercicio.creado_por = None

    assert ejercicio.creado_por is None


def test_calcular_calorias_retorna_float(
    ejercicio,
):
    """
    Cubre calcular_calorias.
    """
    resultado = ejercicio.calcular_calorias()

    assert isinstance(resultado, float)
    assert resultado == 250.5


def test_actualizar_datos_actualiza_todos_los_campos(
    ejercicio,
):
    """
    Cubre actualizar_datos y los setters invocados.
    """
    ejercicio.actualizar_datos(
        nombre="  Bicicleta estática  ",
        descripcion="  Intervalos de cardio  ",
        tipo="  resistencia  ",
        duracion_minutos=45.0,
        intensidad="ALTA",
        calorias_estimadas=Decimal("420.567"),
    )

    assert ejercicio.nombre == "Bicicleta estática"
    assert ejercicio.descripcion == "Intervalos de cardio"
    assert ejercicio.tipo == "resistencia"
    assert ejercicio.duracion_minutos == 45
    assert ejercicio.intensidad == Intensidad.ALTA
    assert ejercicio.calorias_estimadas == Decimal("420.57")


def test_repr_ejercicio_cardio(
    ejercicio,
):
    """
    Cubre __repr__ utilizando Intensidad normal.
    """
    representacion = repr(ejercicio)

    assert "EjercicioCardio(" in representacion
    assert "id_ejercicio=1" in representacion
    assert "nombre='Caminata rápida'" in representacion
    assert "tipo='cardio'" in representacion
    assert "duracion_minutos=30" in representacion
    assert "intensidad='MEDIA'" in representacion
    assert "calorias_estimadas=250.50" in representacion


def test_repr_usa_valor_alternativo_si_intensidad_no_tiene_value(
    ejercicio,
):
    """
    Cubre la ruta defensiva de getattr en __repr__.

    Se modifica el atributo privado deliberadamente para
    comprobar la representación ante un estado no convencional.
    """
    ejercicio._intensidad = "PERSONALIZADA"

    representacion = repr(ejercicio)

    assert "intensidad='PERSONALIZADA'" in representacion

def test_intensidad_acepta_valor_del_enum(
    ejercicio,
    monkeypatch,
):
    """
    Cubre la ruta alternativa Intensidad(valor).

    El enum real probablemente tiene nombres y valores iguales,
    por lo que Intensidad["MEDIA"] funciona antes de que el código
    pueda llegar a Intensidad("MEDIA"). Se reemplaza temporalmente
    el enum por uno con nombre distinto al valor.
    """

    class IntensidadPrueba(Enum):
        NIVEL_MEDIO = "MEDIA"
        NIVEL_ALTO = "ALTA"

    monkeypatch.setattr(
        modulo_ejercicio,
        "Intensidad",
        IntensidadPrueba,
    )

    ejercicio.intensidad = "MEDIA"

    assert ejercicio.intensidad == (
        IntensidadPrueba.NIVEL_MEDIO
    )