from datetime import date
from decimal import Decimal

import pytest

from src.modelos.cliente import Cliente


@pytest.fixture
def cliente():
    return Cliente(
        nombre="Laura",
        apellido="Martínez",
        correo_electronico="laura@example.com",
        contrasenia_hash="hash_prueba",
        edad=30,
        genero="MUJER",
        peso=Decimal("70"),
        altura=Decimal("1.65"),
        objetivo="Bajar de peso",
        peso_objetivo=Decimal("65"),
        id_usuario=10,
        fecha_ingreso=date(2026, 1, 15),
    )


def test_crear_cliente_correctamente(
    cliente,
):
    assert cliente.id_usuario == 10
    assert cliente.nombre == "Laura"
    assert cliente.apellido == "Martínez"
    assert cliente.correo_electronico == "laura@example.com"
    assert cliente.edad == 30
    assert cliente.tipo_usuario == "cliente"
    assert cliente.genero == "MUJER"
    assert cliente.peso == Decimal("70")
    assert cliente.peso_objetivo == Decimal("65")
    assert cliente.altura == Decimal("1.65")
    assert cliente.objetivo == "Bajar de peso"
    assert cliente.fecha_ingreso == date(2026, 1, 15)


def test_cliente_usa_peso_actual_como_objetivo_por_defecto():
    cliente = Cliente(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@example.com",
        contrasenia_hash="hash",
        edad=25,
        peso=80,
        altura=1.80,
        objetivo="Mantener peso",
    )

    assert cliente.peso == Decimal("80")
    assert cliente.peso_objetivo == Decimal("80")
    assert cliente.genero == "PREFIERO NO DECIRLO"


def test_cliente_usa_fecha_actual_por_defecto():
    cliente = Cliente(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@example.com",
        contrasenia_hash="hash",
        edad=25,
        peso=80,
        altura=1.80,
        objetivo="Mantener peso",
    )

    assert cliente.fecha_ingreso == date.today()


@pytest.mark.parametrize(
    "genero,esperado",
    [
        ("HOMBRE", "HOMBRE"),
        (" mujer ", "MUJER"),
        ("otro", "OTRO"),
        (
            "prefiero no decirlo",
            "PREFIERO NO DECIRLO",
        ),
    ],
)
def test_genero_valido(
    cliente,
    genero,
    esperado,
):
    cliente.genero = genero

    assert cliente.genero == esperado


@pytest.mark.parametrize(
    "genero",
    [
        None,
        10,
        "",
        "   ",
        "MASCULINO",
        "DESCONOCIDO",
    ],
)
def test_genero_invalido(
    cliente,
    genero,
):
    with pytest.raises(
        ValueError,
        match="género",
    ):
        cliente.genero = genero


@pytest.mark.parametrize(
    "peso,esperado",
    [
        (70, Decimal("70")),
        (70.5, Decimal("70.5")),
        (Decimal("68.25"), Decimal("68.25")),
    ],
)
def test_peso_valido(
    cliente,
    peso,
    esperado,
):
    cliente.peso = peso

    assert cliente.peso == esperado


@pytest.mark.parametrize(
    "peso",
    [
        None,
        True,
        False,
        0,
        -1,
        "70",
        [],
    ],
)
def test_peso_invalido(
    cliente,
    peso,
):
    with pytest.raises(
        ValueError,
        match="peso debe ser mayor",
    ):
        cliente.peso = peso


@pytest.mark.parametrize(
    "peso_objetivo,esperado",
    [
        (65, Decimal("65")),
        (65.5, Decimal("65.5")),
        (Decimal("60.25"), Decimal("60.25")),
    ],
)
def test_peso_objetivo_valido(
    cliente,
    peso_objetivo,
    esperado,
):
    cliente.peso_objetivo = peso_objetivo

    assert cliente.peso_objetivo == esperado


@pytest.mark.parametrize(
    "peso_objetivo",
    [
        None,
        True,
        False,
        0,
        -1,
        "65",
        [],
    ],
)
def test_peso_objetivo_invalido(
    cliente,
    peso_objetivo,
):
    with pytest.raises(
        ValueError,
        match="peso objetivo",
    ):
        cliente.peso_objetivo = peso_objetivo


@pytest.mark.parametrize(
    "altura,esperado",
    [
        (1.70, Decimal("1.7")),
        (2, Decimal("2")),
        (Decimal("1.65"), Decimal("1.65")),
    ],
)
def test_altura_valida(
    cliente,
    altura,
    esperado,
):
    cliente.altura = altura

    assert cliente.altura == esperado


@pytest.mark.parametrize(
    "altura",
    [
        None,
        True,
        False,
        0,
        -1,
        "1.70",
        [],
    ],
)
def test_altura_invalida(
    cliente,
    altura,
):
    with pytest.raises(
        ValueError,
        match="altura debe ser mayor",
    ):
        cliente.altura = altura


@pytest.mark.parametrize(
    "objetivo,esperado",
    [
        (
            "  Ganar resistencia  ",
            "Ganar resistencia",
        ),
        ("Mantener peso", "Mantener peso"),
        ("Subir de peso", "Subir de peso"),
    ],
)
def test_objetivo_valido(
    cliente,
    objetivo,
    esperado,
):
    cliente.objetivo = objetivo

    assert cliente.objetivo == esperado


@pytest.mark.parametrize(
    "objetivo",
    [
        None,
        "",
        "   ",
        10,
        [],
    ],
)
def test_objetivo_invalido(
    cliente,
    objetivo,
):
    with pytest.raises(
        ValueError,
        match="objetivo",
    ):
        cliente.objetivo = objetivo


def test_actualizar_peso(
    cliente,
):
    cliente.actualizar_peso(Decimal("68.5"))

    assert cliente.peso == Decimal("68.5")


def test_actualizar_peso_objetivo(
    cliente,
):
    cliente.actualizar_peso_objetivo(
        Decimal("63.5")
    )

    assert cliente.peso_objetivo == Decimal("63.5")


def test_actualizar_objetivo(
    cliente,
):
    cliente.actualizar_objetivo("Mantener peso")

    assert cliente.objetivo == "Mantener peso"


def test_objetivo_normalizado(
    cliente,
):
    cliente.objetivo = "  BAJAR DE PESO  "

    assert cliente._objetivo_normalizado() == (
        "bajar de peso"
    )


def test_obtener_rango_mantenimiento(
    cliente,
):
    cliente.peso_objetivo = Decimal("70")

    minimo, maximo = (
        cliente.obtener_rango_mantenimiento()
    )

    assert minimo == Decimal("66.0")
    assert maximo == Decimal("74.0")


@pytest.mark.parametrize(
    "objetivo,peso,peso_objetivo,esperado",
    [
        (
            "Bajar de peso",
            Decimal("65"),
            Decimal("65"),
            True,
        ),
        (
            "Bajar peso",
            Decimal("70"),
            Decimal("65"),
            False,
        ),
        (
            "Subir de peso",
            Decimal("75"),
            Decimal("75"),
            True,
        ),
        (
            "Subir peso",
            Decimal("70"),
            Decimal("75"),
            False,
        ),
        (
            "Mantener peso",
            Decimal("70"),
            Decimal("70"),
            True,
        ),
        (
            "Mantener",
            Decimal("75"),
            Decimal("70"),
            False,
        ),
        (
            "Otro objetivo",
            Decimal("70"),
            Decimal("65"),
            False,
        ),
    ],
)
def test_meta_alcanzada(
    cliente,
    objetivo,
    peso,
    peso_objetivo,
    esperado,
):
    cliente.objetivo = objetivo
    cliente.peso = peso
    cliente.peso_objetivo = peso_objetivo

    assert cliente.meta_alcanzada() is esperado


@pytest.mark.parametrize(
    "objetivo,peso,peso_objetivo,esperado",
    [
        (
            "Bajar de peso",
            Decimal("70"),
            Decimal("65"),
            Decimal("5"),
        ),
        (
            "Bajar de peso",
            Decimal("64"),
            Decimal("65"),
            Decimal("0"),
        ),
        (
            "Subir de peso",
            Decimal("70"),
            Decimal("75"),
            Decimal("5"),
        ),
        (
            "Subir de peso",
            Decimal("76"),
            Decimal("75"),
            Decimal("0"),
        ),
        (
            "Mantener peso",
            Decimal("60"),
            Decimal("70"),
            Decimal("6.0"),
        ),
        (
            "Mantener peso",
            Decimal("80"),
            Decimal("70"),
            Decimal("6.0"),
        ),
        (
            "Mantener peso",
            Decimal("72"),
            Decimal("70"),
            Decimal("0"),
        ),
        (
            "Otro objetivo",
            Decimal("70"),
            Decimal("65"),
            Decimal("5"),
        ),
    ],
)
def test_obtener_diferencia_meta(
    cliente,
    objetivo,
    peso,
    peso_objetivo,
    esperado,
):
    cliente.objetivo = objetivo
    cliente.peso = peso
    cliente.peso_objetivo = peso_objetivo

    assert cliente.obtener_diferencia_meta() == esperado


def test_obtener_estado_meta_alcanzada(
    cliente,
):
    cliente.peso = Decimal("65")
    cliente.peso_objetivo = Decimal("65")

    assert cliente.obtener_estado_meta() == (
        "META ALCANZADA"
    )


def test_obtener_estado_meta_en_progreso(
    cliente,
):
    cliente.peso = Decimal("70")
    cliente.peso_objetivo = Decimal("65")

    assert cliente.obtener_estado_meta() == (
        "EN PROGRESO"
    )


def test_descripcion_meta_mantener_peso(
    cliente,
):
    cliente.objetivo = "Mantener peso"
    cliente.peso_objetivo = Decimal("70")

    assert cliente.obtener_descripcion_meta() == (
        "Rango objetivo: 66.0 - 74.0 kg"
    )


def test_descripcion_meta_otro_objetivo(
    cliente,
):
    cliente.objetivo = "Bajar de peso"
    cliente.peso_objetivo = Decimal("65")

    assert cliente.obtener_descripcion_meta() == (
        "Peso objetivo: 65.0 kg"
    )


def test_obtener_progreso_meta_alcanzada(
    cliente,
):
    cliente.peso = Decimal("65")
    cliente.peso_objetivo = Decimal("65")

    assert cliente.obtener_progreso_meta() == 100.0


def test_obtener_progreso_meta_en_progreso(
    cliente,
):
    cliente.peso = Decimal("70")
    cliente.peso_objetivo = Decimal("65")

    assert cliente.obtener_progreso_meta() == 0.0


def test_obtener_tipo_usuario(
    cliente,
):
    assert cliente.obtener_tipo_usuario() == "cliente"


def test_repr_cliente(
    cliente,
):
    representacion = repr(cliente)

    assert "Cliente(" in representacion
    assert "id_usuario=10" in representacion
    assert "nombre='Laura'" in representacion
    assert "correo='laura@example.com'" in representacion
    assert "edad=30" in representacion
    assert "genero='MUJER'" in representacion
    assert "peso=70" in representacion
    assert "peso_objetivo=65" in representacion
    assert "altura=1.65" in representacion
    assert "objetivo='Bajar de peso'" in representacion