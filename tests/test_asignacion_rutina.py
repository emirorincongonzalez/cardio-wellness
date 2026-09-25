from datetime import date, timedelta

import pytest

from src.modelos.asignacion_rutina import AsignacionRutina
from src.modelos.enums import EstadoAsignacion


@pytest.fixture
def asignacion():
    """
    Crea una asignación válida reutilizable.
    """
    return AsignacionRutina(
        id_asignacion=1,
        id_cliente=10,
        id_rutina=5,
        fecha_asignacion=date(2026, 1, 15),
        fecha_finalizacion=None,
        estado=EstadoAsignacion.ACTIVA,
        observaciones="Asignación inicial",
    )


def test_crear_asignacion_valida(
    asignacion,
):
    """
    Verifica todos los valores iniciales válidos.
    """
    assert asignacion.id_asignacion == 1
    assert asignacion.id_cliente == 10
    assert asignacion.id_rutina == 5
    assert asignacion.fecha_asignacion == date(2026, 1, 15)
    assert asignacion.fecha_finalizacion is None
    assert asignacion.estado == EstadoAsignacion.ACTIVA
    assert asignacion.observaciones == "Asignación inicial"


def test_crear_asignacion_sin_id_y_sin_observaciones():
    """
    Verifica los valores opcionales del constructor.
    """
    asignacion = AsignacionRutina(
        id_cliente=2,
        id_rutina=3,
        fecha_asignacion=date.today(),
    )

    assert asignacion.id_asignacion is None
    assert asignacion.fecha_finalizacion is None
    assert asignacion.estado == EstadoAsignacion.ACTIVA
    assert asignacion.observaciones == ""


def test_getters_de_asignacion(
    asignacion,
):
    """
    Cubre todos los getters de propiedades.
    """
    assert asignacion.id_asignacion == 1
    assert asignacion.id_cliente == 10
    assert asignacion.id_rutina == 5
    assert asignacion.fecha_asignacion == date(2026, 1, 15)
    assert asignacion.fecha_finalizacion is None
    assert asignacion.estado == EstadoAsignacion.ACTIVA
    assert asignacion.observaciones == "Asignación inicial"


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
    ],
)
def test_id_asignacion_rechaza_booleanos(
    asignacion,
    valor,
):
    """
    Cubre la validación específica de bool para id_asignacion.
    """
    with pytest.raises(
        ValueError,
        match="ID de asignación debe ser entero",
    ):
        asignacion.id_asignacion = valor


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        -100,
        "1",
        1.5,
        None,
    ],
)
def test_id_asignacion_rechaza_valores_no_positivos(
    asignacion,
    valor,
):
    """
    id_asignacion solo permite entero positivo o None.

    None se prueba mediante una instancia temporal porque
    sí es permitido por el setter.
    """
    if valor is None:
        asignacion.id_asignacion = None

        assert asignacion.id_asignacion is None
        return

    with pytest.raises(
        ValueError,
        match="ID de asignación debe ser positivo",
    ):
        asignacion.id_asignacion = valor


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
    ],
)
def test_id_cliente_rechaza_booleanos(
    asignacion,
    valor,
):
    """
    Cubre rama exclusiva para booleanos de id_cliente.
    """
    with pytest.raises(
        ValueError,
        match="ID de cliente debe ser entero",
    ):
        asignacion.id_cliente = valor


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        "10",
        2.5,
        None,
    ],
)
def test_id_cliente_rechaza_valores_invalidos(
    asignacion,
    valor,
):
    """
    id_cliente debe ser entero positivo.
    """
    with pytest.raises(
        ValueError,
        match="ID de cliente debe ser positivo",
    ):
        asignacion.id_cliente = valor


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
    ],
)
def test_id_rutina_rechaza_booleanos(
    asignacion,
    valor,
):
    """
    Cubre rama exclusiva para booleanos de id_rutina.
    """
    with pytest.raises(
        ValueError,
        match="ID de rutina debe ser entero",
    ):
        asignacion.id_rutina = valor


@pytest.mark.parametrize(
    "valor",
    [
        0,
        -1,
        "5",
        2.5,
        None,
    ],
)
def test_id_rutina_rechaza_valores_invalidos(
    asignacion,
    valor,
):
    """
    id_rutina debe ser entero positivo.
    """
    with pytest.raises(
        ValueError,
        match="ID de rutina debe ser positivo",
    ):
        asignacion.id_rutina = valor


def test_fecha_asignacion_rechaza_tipo_invalido(
    asignacion,
):
    """
    Verifica que fecha_asignacion sea date.
    """
    with pytest.raises(
        ValueError,
        match="fecha de asignación debe ser una fecha",
    ):
        asignacion.fecha_asignacion = "2026-01-15"


def test_fecha_asignacion_rechaza_fecha_futura(
    asignacion,
):
    """
    Cubre validación de fecha futura.
    """
    fecha_futura = date.today() + timedelta(days=1)

    with pytest.raises(
        ValueError,
        match="fecha de asignación no puede ser futura",
    ):
        asignacion.fecha_asignacion = fecha_futura


def test_fecha_finalizacion_acepta_fecha_posterior(
    asignacion,
):
    """
    Verifica una fecha de finalización válida.
    """
    fecha_final = date(2026, 1, 20)

    asignacion.fecha_finalizacion = fecha_final

    assert asignacion.fecha_finalizacion == fecha_final


def test_fecha_finalizacion_rechaza_tipo_invalido(
    asignacion,
):
    """
    Cubre validación de tipo de fecha_finalizacion.
    """
    with pytest.raises(
        ValueError,
        match="fecha de finalización debe ser una fecha",
    ):
        asignacion.fecha_finalizacion = "2026-01-20"


def test_fecha_finalizacion_rechaza_fecha_anterior(
    asignacion,
):
    """
    Cubre validación de finalización anterior a asignación.
    """
    with pytest.raises(
        ValueError,
        match="no puede ser anterior",
    ):
        asignacion.fecha_finalizacion = date(2026, 1, 14)


def test_estado_acepta_enum(
    asignacion,
):
    """
    Cubre estado recibido directamente como enum.
    """
    asignacion.estado = EstadoAsignacion.FINALIZADA

    assert asignacion.estado == EstadoAsignacion.FINALIZADA


def test_estado_acepta_valor_del_enum(
    asignacion,
):
    """
    Cubre la primera conversión desde texto:
    EstadoAsignacion(valor).
    """
    asignacion.estado = EstadoAsignacion.CANCELADA.value

    assert asignacion.estado == EstadoAsignacion.CANCELADA


def test_estado_acepta_nombre_del_enum(
    asignacion,
    monkeypatch,
):
    """
    Cubre conversión alternativa por nombre:

        EstadoAsignacion[valor.upper()]

    Se usa un enum temporal con nombres distintos de
    los valores para forzar que EstadoAsignacion(valor)
    produzca ValueError antes de buscar por nombre.
    """
    from enum import Enum

    import src.modelos.asignacion_rutina as modulo_asignacion

    class EstadoAsignacionPrueba(Enum):
        ACTIVA_INTERNA = "activa"
        FINALIZADA_INTERNA = "finalizada"
        CANCELADA_INTERNA = "cancelada"

    monkeypatch.setattr(
        modulo_asignacion,
        "EstadoAsignacion",
        EstadoAsignacionPrueba,
    )

    asignacion.estado = "ACTIVA_INTERNA"

    assert asignacion.estado == (
        EstadoAsignacionPrueba.ACTIVA_INTERNA
    )


def test_estado_rechaza_texto_invalido(
    asignacion,
):
    """
    Cubre KeyError y ValueError para texto inexistente.
    """
    with pytest.raises(
        ValueError,
        match="Estado de asignación inválido",
    ):
        asignacion.estado = "PENDIENTE"


@pytest.mark.parametrize(
    "valor",
    [
        None,
        1,
        True,
        [],
        {},
    ],
)
def test_estado_rechaza_tipos_invalidos(
    asignacion,
    valor,
):
    """
    Cubre validación final cuando el valor no es enum.
    """
    with pytest.raises(
        ValueError,
        match="estado debe ser un valor válido",
    ):
        asignacion.estado = valor


def test_observaciones_limpia_espacios(
    asignacion,
):
    """
    Verifica normalización de observaciones.
    """
    asignacion.observaciones = "  Rutina de cardio  "

    assert asignacion.observaciones == "Rutina de cardio"


@pytest.mark.parametrize(
    "valor",
    [
        None,
        10,
        True,
        [],
        {},
    ],
)
def test_observaciones_convierte_no_texto_a_vacio(
    asignacion,
    valor,
):
    """
    Cubre la alternativa del setter de observaciones.
    """
    asignacion.observaciones = valor

    assert asignacion.observaciones == ""


def test_activar_reestablece_estado_y_limpia_finalizacion(
    asignacion,
):
    """
    Cubre activar.
    """
    asignacion.estado = EstadoAsignacion.FINALIZADA
    asignacion.fecha_finalizacion = date(2026, 1, 20)

    asignacion.activar()

    assert asignacion.estado == EstadoAsignacion.ACTIVA
    assert asignacion.fecha_finalizacion is None


def test_finalizar_actualiza_estado_y_fecha(
    asignacion,
):
    """
    Cubre finalizar.
    """
    asignacion.finalizar()

    assert asignacion.estado == EstadoAsignacion.FINALIZADA
    assert asignacion.fecha_finalizacion == date.today()


def test_cancelar_actualiza_estado_y_fecha(
    asignacion,
):
    """
    Cubre cancelar.
    """
    asignacion.cancelar()

    assert asignacion.estado == EstadoAsignacion.CANCELADA
    assert asignacion.fecha_finalizacion == date.today()


def test_esta_activa_retorna_true_y_false(
    asignacion,
):
    """
    Cubre ambos resultados de esta_activa.
    """
    assert asignacion.esta_activa() is True

    asignacion.finalizar()

    assert asignacion.esta_activa() is False


def test_repr_asignacion_rutina(
    asignacion,
):
    """
    Cubre representación textual del modelo.
    """
    representacion = repr(asignacion)

    assert "AsignacionRutina(" in representacion
    assert "id_asignacion=1" in representacion
    assert "id_cliente=10" in representacion
    assert "id_rutina=5" in representacion
    assert "fecha_asignacion=2026-01-15" in representacion
    assert "fecha_finalizacion=None" in representacion
    assert f"estado='{EstadoAsignacion.ACTIVA.value}'" in representacion
    assert "observaciones='Asignación inicial'" in representacion