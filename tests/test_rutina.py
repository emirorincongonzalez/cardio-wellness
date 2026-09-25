from datetime import date
from enum import Enum

import pytest

import src.modelos.rutina as modulo_rutina

from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
    Intensidad,
)
from src.modelos.enums import NivelRutina
from src.modelos.rutina import Rutina


def crear_ejercicio(
    id_ejercicio=1,
    nombre="Caminata",
    duracion=30,
):
    """
    Crea un ejercicio válido para asociar a rutinas.
    """
    return EjercicioCardio(
        id_ejercicio=id_ejercicio,
        nombre=nombre,
        descripcion=f"{nombre} cardiovascular",
        tipo="cardio",
        duracion_minutos=duracion,
        intensidad=Intensidad.MEDIA,
        calorias_estimadas=200,
        creado_por=1,
    )


@pytest.fixture
def rutina():
    """
    Crea una rutina válida reutilizable.
    """
    return Rutina(
        id_rutina=1,
        nombre="Rutina inicial",
        descripcion="Rutina para principiantes",
        objetivo="cardio",
        nivel=NivelRutina.BASICO,
        duracion_semanas=4,
        creado_por=10,
        fecha_creacion=date(2026, 1, 15),
    )


def test_crear_rutina_valida(
    rutina,
):
    """
    Verifica datos iniciales de una rutina válida.
    """
    assert rutina.id_rutina == 1
    assert rutina.nombre == "Rutina inicial"
    assert rutina.descripcion == "Rutina para principiantes"
    assert rutina.objetivo == "cardio"
    assert rutina.nivel == NivelRutina.BASICO
    assert rutina.duracion_semanas == 4
    assert rutina.creado_por == 10
    assert rutina.fecha_creacion == date(2026, 1, 15)
    assert rutina.ejercicios == ()
    assert rutina.id_ejercicios == ()


def test_crear_rutina_sin_valores_opcionales():
    """
    Verifica ID, creador y fecha opcionales.
    """
    rutina = Rutina(
        nombre="Rutina nueva",
        descripcion="Rutina sin identificador",
        objetivo="resistencia",
        nivel="INTERMEDIO",
        duracion_semanas=6,
    )

    assert rutina.id_rutina is None
    assert rutina.creado_por is None
    assert rutina.fecha_creacion == date.today()
    assert rutina.nivel == NivelRutina.INTERMEDIO


def test_constructor_agrega_lista_de_ejercicios():
    """
    Cubre el constructor cuando recibe ejercicios.
    """
    ejercicio_1 = crear_ejercicio(
        id_ejercicio=1,
        nombre="Caminata",
        duracion=20,
    )

    ejercicio_2 = crear_ejercicio(
        id_ejercicio=2,
        nombre="Bicicleta",
        duracion=40,
    )

    rutina = Rutina(
        nombre="Rutina con ejercicios",
        descripcion="Rutina de prueba",
        objetivo="cardio",
        nivel="BASICO",
        duracion_semanas=4,
        ejercicios=[ejercicio_1, ejercicio_2],
    )

    assert rutina.ejercicios == (
        ejercicio_1,
        ejercicio_2,
    )

    assert rutina.id_ejercicios == (1, 2)
    assert rutina.cantidad_ejercicios() == 2


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        True,
        False,
        "1",
        1.5,
    ],
)
def test_id_rutina_rechaza_valores_invalidos(
    rutina,
    valor,
):
    """
    Verifica que id_rutina acepte solo enteros positivos o None.
    """
    with pytest.raises(
        ValueError,
        match="ID de la rutina debe ser un entero positivo",
    ):
        rutina.id_rutina = valor


def test_id_rutina_permite_none(
    rutina,
):
    """
    Verifica que el ID pueda asignarse a None.
    """
    rutina.id_rutina = None

    assert rutina.id_rutina is None


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
            "objetivo",
            "",
            "objetivo no puede estar vacío",
        ),
        (
            "objetivo",
            "   ",
            "objetivo no puede estar vacío",
        ),
        (
            "objetivo",
            None,
            "objetivo no puede estar vacío",
        ),
    ],
)
def test_textos_rechazan_valores_invalidos(
    rutina,
    atributo,
    valor,
    mensaje,
):
    """
    Valida nombre, descripción y objetivo.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        setattr(
            rutina,
            atributo,
            valor,
        )


def test_textos_eliminan_espacios(
    rutina,
):
    """
    Verifica limpieza mediante strip.
    """
    rutina.nombre = "  Rutina nueva  "
    rutina.descripcion = "  Descripción nueva  "
    rutina.objetivo = "  resistencia  "

    assert rutina.nombre == "Rutina nueva"
    assert rutina.descripcion == "Descripción nueva"
    assert rutina.objetivo == "resistencia"


def test_nivel_acepta_enum(
    rutina,
):
    """
    Cubre nivel recibido como NivelRutina.
    """
    rutina.nivel = NivelRutina.AVANZADO

    assert rutina.nivel == NivelRutina.AVANZADO


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("BASICO", NivelRutina.BASICO),
        ("  basico  ", NivelRutina.BASICO),
        ("INTERMEDIO", NivelRutina.INTERMEDIO),
        ("avanzado", NivelRutina.AVANZADO),
    ],
)
def test_nivel_acepta_texto_valido(
    rutina,
    valor,
    esperado,
):
    """
    Cubre normalización de texto del nivel.
    """
    rutina.nivel = valor

    assert rutina.nivel == esperado


def test_nivel_acepta_valor_del_enum(
    rutina,
    monkeypatch,
):
    """
    Cubre la conversión alternativa NivelRutina(valor).

    El enum temporal tiene nombres diferentes de sus valores,
    así se fuerza que NivelRutina["BASICO"] falle y que
    NivelRutina("BASICO") sea la ruta utilizada.
    """

    class NivelRutinaPrueba(Enum):
        NIVEL_BASICO = "BASICO"
        NIVEL_AVANZADO = "AVANZADO"

    monkeypatch.setattr(
        modulo_rutina,
        "NivelRutina",
        NivelRutinaPrueba,
    )

    rutina.nivel = "BASICO"

    assert rutina.nivel == NivelRutinaPrueba.NIVEL_BASICO


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        "EXPERTO",
        "FACIL",
        1,
        True,
        [],
    ],
)
def test_nivel_rechaza_valores_invalidos(
    rutina,
    valor,
):
    """
    Verifica error final del setter de nivel.
    """
    with pytest.raises(
        ValueError,
        match="nivel debe ser un valor válido",
    ):
        rutina.nivel = valor


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        True,
        False,
        4.0,
        "4",
        None,
    ],
)
def test_duracion_semanas_rechaza_valores_invalidos(
    rutina,
    valor,
):
    """
    Duración debe ser un entero positivo.
    """
    with pytest.raises(
        ValueError,
        match="duración debe ser un entero mayor que cero",
    ):
        rutina.duracion_semanas = valor


def test_duracion_semanas_acepta_entero(
    rutina,
):
    """
    Verifica setter de duración válido.
    """
    rutina.duracion_semanas = 8

    assert rutina.duracion_semanas == 8


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        True,
        False,
        "1",
        1.5,
    ],
)
def test_creado_por_rechaza_valores_invalidos(
    rutina,
    valor,
):
    """
    Verifica validación de creado_por.
    """
    with pytest.raises(
        ValueError,
        match="creado_por debe ser un ID",
    ):
        rutina.creado_por = valor


def test_creado_por_permite_none(
    rutina,
):
    """
    Verifica creador opcional.
    """
    rutina.creado_por = None

    assert rutina.creado_por is None


def test_fecha_creacion_usa_hoy_si_es_none(
    rutina,
):
    """
    Cubre fecha automática.
    """
    rutina.fecha_creacion = None

    assert rutina.fecha_creacion == date.today()


def test_fecha_creacion_rechaza_tipo_invalido(
    rutina,
):
    """
    Verifica que fecha_creacion sea date o None.
    """
    with pytest.raises(
        ValueError,
        match="fecha de creación no es válida",
    ):
        rutina.fecha_creacion = "2026-01-15"


def test_agregar_ejercicio_y_propiedades(
    rutina,
):
    """
    Agrega ejercicios y cubre ejercicios e id_ejercicios.
    """
    ejercicio_1 = crear_ejercicio(
        id_ejercicio=1,
        nombre="Caminata",
        duracion=30,
    )

    ejercicio_2 = crear_ejercicio(
        id_ejercicio=2,
        nombre="Bicicleta",
        duracion=45,
    )

    rutina.agregar_ejercicio(ejercicio_1)
    rutina.agregar_ejercicio(ejercicio_2)

    assert rutina.ejercicios == (
        ejercicio_1,
        ejercicio_2,
    )

    assert rutina.id_ejercicios == (1, 2)
    assert rutina.cantidad_ejercicios() == 2
    assert rutina.calcular_duracion_total() == 75
    assert rutina.contiene_ejercicio(1) is True
    assert rutina.contiene_ejercicio(99) is False


def test_id_ejercicios_omite_ejercicio_sin_id(
    rutina,
):
    """
    Cubre el filtro de id_ejercicios para IDs None.
    """
    ejercicio_sin_id = crear_ejercicio(
        id_ejercicio=None,
        nombre="Elíptica",
        duracion=25,
    )

    rutina.agregar_ejercicio(ejercicio_sin_id)

    assert rutina.ejercicios == (ejercicio_sin_id,)
    assert rutina.id_ejercicios == ()


def test_agregar_ejercicio_rechaza_tipo_incorrecto(
    rutina,
):
    """
    No se pueden agregar objetos distintos de EjercicioCardio.
    """
    with pytest.raises(
        TypeError,
        match="Solo se pueden agregar objetos",
    ):
        rutina.agregar_ejercicio("ejercicio")


def test_agregar_ejercicio_rechaza_id_duplicado(
    rutina,
):
    """
    Cubre duplicado usando el mismo id_ejercicio.
    """
    ejercicio_original = crear_ejercicio(
        id_ejercicio=4,
        nombre="Caminata",
    )

    ejercicio_duplicado = crear_ejercicio(
        id_ejercicio=4,
        nombre="Caminata diferente",
    )

    rutina.agregar_ejercicio(ejercicio_original)

    with pytest.raises(
        ValueError,
        match="ya pertenece a la rutina",
    ):
        rutina.agregar_ejercicio(ejercicio_duplicado)


def test_agregar_ejercicio_rechaza_mismo_objeto_sin_id(
    rutina,
):
    """
    Cubre duplicado por identidad cuando el ejercicio no tiene ID.
    """
    ejercicio_sin_id = crear_ejercicio(
        id_ejercicio=None,
        nombre="Remo",
    )

    rutina.agregar_ejercicio(ejercicio_sin_id)

    with pytest.raises(
        ValueError,
        match="ya pertenece a la rutina",
    ):
        rutina.agregar_ejercicio(ejercicio_sin_id)


def test_eliminar_ejercicio_por_mismo_id(
    rutina,
):
    """
    Cubre eliminación cuando dos objetos comparten ID.
    """
    ejercicio_guardado = crear_ejercicio(
        id_ejercicio=7,
        nombre="Spinning",
    )

    ejercicio_equivalente = crear_ejercicio(
        id_ejercicio=7,
        nombre="Otro objeto",
    )

    rutina.agregar_ejercicio(ejercicio_guardado)

    rutina.eliminar_ejercicio(ejercicio_equivalente)

    assert rutina.ejercicios == ()
    assert rutina.cantidad_ejercicios() == 0


def test_eliminar_ejercicio_por_mismo_objeto_sin_id(
    rutina,
):
    """
    Cubre eliminación por identidad si no existe ID.
    """
    ejercicio_sin_id = crear_ejercicio(
        id_ejercicio=None,
        nombre="Remo",
    )

    rutina.agregar_ejercicio(ejercicio_sin_id)

    rutina.eliminar_ejercicio(ejercicio_sin_id)

    assert rutina.ejercicios == ()


def test_eliminar_ejercicio_rechaza_tipo_incorrecto(
    rutina,
):
    """
    No se pueden eliminar objetos no válidos.
    """
    with pytest.raises(
        TypeError,
        match="Solo se pueden eliminar objetos",
    ):
        rutina.eliminar_ejercicio("ejercicio")


def test_eliminar_ejercicio_rechaza_ejercicio_ausente(
    rutina,
):
    """
    Cubre error cuando el ejercicio no pertenece a la rutina.
    """
    ejercicio = crear_ejercicio(
        id_ejercicio=10,
        nombre="Caminata",
    )

    with pytest.raises(
        ValueError,
        match="no pertenece a la rutina",
    ):
        rutina.eliminar_ejercicio(ejercicio)


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        True,
        False,
        "1",
        1.5,
    ],
)
def test_eliminar_ejercicio_por_id_rechaza_id_invalido(
    rutina,
    valor,
):
    """
    Verifica validación del ID recibido.
    """
    with pytest.raises(
        ValueError,
        match="ID del ejercicio debe ser positivo",
    ):
        rutina.eliminar_ejercicio_por_id(valor)


def test_eliminar_ejercicio_por_id(
    rutina,
):
    """
    Cubre búsqueda y eliminación exitosa por ID.
    """
    ejercicio = crear_ejercicio(
        id_ejercicio=8,
        nombre="Bicicleta",
    )

    rutina.agregar_ejercicio(ejercicio)

    rutina.eliminar_ejercicio_por_id(8)

    assert rutina.ejercicios == ()


def test_eliminar_ejercicio_por_id_rechaza_ausente(
    rutina,
):
    """
    Cubre ruta donde no se encuentra el ID.
    """
    with pytest.raises(
        ValueError,
        match="no pertenece a la rutina",
    ):
        rutina.eliminar_ejercicio_por_id(999)


def test_reemplazar_ejercicios(
    rutina,
):
    """
    Cubre reemplazo completo de ejercicios.
    """
    ejercicio_anterior = crear_ejercicio(
        id_ejercicio=1,
        nombre="Caminata",
    )

    ejercicio_nuevo = crear_ejercicio(
        id_ejercicio=2,
        nombre="Bicicleta",
    )

    rutina.agregar_ejercicio(ejercicio_anterior)

    rutina.reemplazar_ejercicios([ejercicio_nuevo])

    assert rutina.ejercicios == (ejercicio_nuevo,)
    assert rutina.id_ejercicios == (2,)


def test_reemplazar_ejercicios_rechaza_no_lista(
    rutina,
):
    """
    Verifica que reemplazar requiera una lista.
    """
    with pytest.raises(
        TypeError,
        match="ejercicios deben recibirse como una lista",
    ):
        rutina.reemplazar_ejercicios(
            (crear_ejercicio(),),
        )


def test_obtener_nivel_texto(
    rutina,
):
    """
    Cubre el valor textual habitual del nivel.
    """
    assert rutina.obtener_nivel_texto() == "BASICO"


def test_obtener_nivel_texto_sin_atributo_value(
    rutina,
):
    """
    Cubre el valor alternativo de getattr.

    Se modifica el atributo privado de forma intencional
    para probar la ruta defensiva.
    """
    rutina._nivel = "PERSONALIZADO"

    assert rutina.obtener_nivel_texto() == "PERSONALIZADO"


def test_repr_rutina(
    rutina,
):
    """
    Cubre representación textual de Rutina.
    """
    ejercicio = crear_ejercicio(
        id_ejercicio=1,
        nombre="Caminata",
    )

    rutina.agregar_ejercicio(ejercicio)

    representacion = repr(rutina)

    assert "Rutina(" in representacion
    assert "id_rutina=1" in representacion
    assert "nombre='Rutina inicial'" in representacion
    assert "objetivo='cardio'" in representacion
    assert "nivel='BASICO'" in representacion
    assert "duracion_semanas=4" in representacion
    assert "ejercicios=1" in representacion