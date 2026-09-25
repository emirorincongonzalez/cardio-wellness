from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from src.controladores.control_progreso import (
    ControlProgreso,
    _convertir_id,
    _extraer_id,
    _instanciar_progreso_mensual,
    _normalizar_fecha,
    _normalizar_fecha_mes,
    _obtener_decimal,
    _obtener_entero,
    _obtener_valor,
)


@pytest.fixture
def progreso_dao():
    return Mock()


@pytest.fixture
def sesion_dao():
    return Mock()


@pytest.fixture
def cliente_dao():
    return Mock()


@pytest.fixture
def control(
    progreso_dao,
    sesion_dao,
    cliente_dao,
    tmp_path,
):
    return ControlProgreso(
        progreso_dao=progreso_dao,
        sesion_dao=sesion_dao,
        cliente_dao=cliente_dao,
        ruta_log=str(
            tmp_path / "logs" / "LOG_CARDIO.txt"
        ),
    )


@pytest.fixture
def cliente():
    return SimpleNamespace(
        id_usuario=10,
        peso=Decimal("70"),
    )


def test_constructor_crea_daos_por_defecto(
    tmp_path,
):
    dao_progreso = Mock()
    dao_sesion = Mock()

    with patch(
        "src.controladores.control_progreso."
        "_obtener_progreso_dao_default",
        return_value=dao_progreso,
    ), patch(
        "src.controladores.control_progreso."
        "_obtener_sesion_dao_default",
        return_value=dao_sesion,
    ):
        controlador = ControlProgreso(
            ruta_log=str(tmp_path / "registro.txt"),
        )

    assert controlador.progreso_dao is dao_progreso
    assert controlador.sesion_dao is dao_sesion
    assert controlador.cliente_dao is None


def test_propiedades_dao(
    control,
):
    progreso = Mock()
    sesion = Mock()
    cliente = Mock()

    control.progreso_dao = progreso
    control.sesion_dao = sesion
    control.cliente_dao = cliente

    assert control.progreso_dao is progreso
    assert control.sesion_dao is sesion
    assert control.cliente_dao is cliente


@pytest.mark.parametrize(
    "objeto,campos,esperado",
    [
        (10, ("id",), 10),
        (True, ("id",), None),
        (False, ("id",), None),
        ({"id_cliente": 20}, ("id_cliente",), 20),
        (
            {"id_usuario": Mock(), "id_cliente": "30"},
            ("id_usuario", "id_cliente"),
            30,
        ),
        ({"otro": 1}, ("id_cliente",), None),
    ],
)
def test_extraer_id_diccionarios(
    objeto,
    campos,
    esperado,
):
    assert _extraer_id(
        objeto,
        *campos,
    ) == esperado


def test_extraer_id_objetos():
    objeto = SimpleNamespace(
        id_cliente="40",
    )

    assert _extraer_id(
        objeto,
        "id_usuario",
        "id_cliente",
    ) == 40

    assert _extraer_id(
        SimpleNamespace(),
        "id_cliente",
    ) is None


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (None, None),
        (True, None),
        (False, None),
        (10, 10),
        ("25", 25),
        (20.5, 20),
        ("invalido", None),
        ([], None),
    ],
)
def test_convertir_id(
    valor,
    esperado,
):
    assert _convertir_id(valor) == esperado


def test_obtener_valor_dict_y_objeto():
    assert _obtener_valor(
        {"peso": 70},
        "peso",
        predeterminado=0,
    ) == 70

    assert _obtener_valor(
        {"peso": Mock(), "peso_actual": 72},
        "peso",
        "peso_actual",
        predeterminado=0,
    ) == 72

    assert _obtener_valor(
        {},
        "peso",
        predeterminado=0,
    ) == 0

    objeto = SimpleNamespace(
        peso=75,
    )

    assert _obtener_valor(
        objeto,
        "peso",
        predeterminado=0,
    ) == 75

    assert _obtener_valor(
        SimpleNamespace(),
        "peso",
        predeterminado=0,
    ) == 0


@pytest.mark.parametrize(
    "objeto,nombres,esperado",
    [
        (
            {"peso": "70.5"},
            ("peso",),
            Decimal("70.5"),
        ),
        (
            {"peso": None},
            ("peso",),
            Decimal("0"),
        ),
        (
            {"peso": "invalido"},
            ("peso",),
            Decimal("0"),
        ),
        (
            {"cantidad": "3"},
            ("cantidad",),
            Decimal("3"),
        ),
    ],
)
def test_obtener_decimal(
    objeto,
    nombres,
    esperado,
):
    assert _obtener_decimal(
        objeto,
        *nombres,
    ) == esperado


@pytest.mark.parametrize(
    "objeto,nombres,predeterminado,esperado",
    [
        (
            {"cantidad": "5"},
            ("cantidad",),
            0,
            5,
        ),
        (
            {"cantidad": None},
            ("cantidad",),
            2,
            2,
        ),
        (
            {"cantidad": "invalido"},
            ("cantidad",),
            3,
            3,
        ),
        (
            {},
            ("cantidad",),
            4,
            4,
        ),
    ],
)
def test_obtener_entero(
    objeto,
    nombres,
    predeterminado,
    esperado,
):
    assert _obtener_entero(
        objeto,
        *nombres,
        predeterminado=predeterminado,
    ) == esperado


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (None, None),
        (
            datetime(2026, 5, 10, 12, 0),
            date(2026, 5, 10),
        ),
        (
            date(2026, 6, 15),
            date(2026, 6, 15),
        ),
        (
            "2026-07-20",
            date(2026, 7, 20),
        ),
        (
            "2026-07-20 10:30:00",
            date(2026, 7, 20),
        ),
        ("fecha inválida", None),
        (10, None),
    ],
)
def test_normalizar_fecha(
    valor,
    esperado,
):
    assert _normalizar_fecha(valor) == esperado


@pytest.mark.parametrize(
    "mes,anio,esperado",
    [
        (5, 2026, (5, 2026)),
        ("6", "2026", (6, 2026)),
        (
            date(2026, 7, 1),
            None,
            (7, 2026),
        ),
        (
            datetime(2026, 8, 2),
            None,
            (8, 2026),
        ),
    ],
)
def test_normalizar_fecha_mes_exitoso(
    mes,
    anio,
    esperado,
):
    assert _normalizar_fecha_mes(
        mes,
        anio,
    ) == esperado


@pytest.mark.parametrize(
    "mes,anio,mensaje",
    [
        ("texto", 2026, "mes debe ser"),
        (5, None, "requiere el año"),
        (5, "texto", "año debe ser"),
        (0, 2026, "entre 1 y 12"),
        (13, 2026, "entre 1 y 12"),
    ],
)
def test_normalizar_fecha_mes_rechaza_invalido(
    mes,
    anio,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        _normalizar_fecha_mes(
            mes,
            anio,
        )


def test_instanciar_progreso_modelo_real():
    progreso = _instanciar_progreso_mensual(
        id_cliente=10,
        mes=5,
        anio=2026,
        peso_registrado=Decimal("70"),
        sesiones_completadas=2,
        sesiones_planificadas=3,
        id_progreso=1,
    )

    assert progreso.id_cliente == 10
    assert progreso.mes == date(2026, 5, 1)
    assert progreso.peso == Decimal("70")


def test_instanciar_progreso_diccionario():
    with patch(
        "src.controladores.control_progreso."
        "_obtener_clase_progreso",
        return_value=None,
    ):
        progreso = _instanciar_progreso_mensual(
            id_cliente=10,
            mes=5,
            anio=2026,
            peso_registrado=70,
        )

    assert progreso["id_cliente"] == 10
    assert progreso["mes"] == 5
    assert progreso["anio"] == 2026


@pytest.mark.parametrize(
    "cliente_invalido",
    [
        None,
        True,
        False,
        0,
        -1,
        "10",
        {},
        SimpleNamespace(id_usuario=-1),
    ],
)
def test_obtener_sesiones_rechaza_cliente_invalido(
    control,
    cliente_invalido,
):
    with pytest.raises(
        ValueError,
        match="id del cliente",
    ):
        control.obtener_sesiones_cliente(
            cliente_invalido
        )


def test_obtener_sesiones_rechaza_dao_none(
    control,
    cliente,
):
    control.sesion_dao = None

    with pytest.raises(
        RuntimeError,
        match="DAO de sesiones",
    ):
        control.obtener_sesiones_cliente(cliente)


def test_obtener_sesiones_listar_por_cliente(
    control,
    sesion_dao,
    cliente,
):
    sesion_dao.listar_por_cliente.return_value = [
        "sesion_1",
    ]

    assert control.obtener_sesiones_cliente(cliente) == [
        "sesion_1",
    ]

    sesion_dao.listar_por_cliente.assert_called_once_with(
        10
    )


@pytest.mark.parametrize(
    "nombre_metodo",
    [
        "buscar_por_cliente",
        "obtener_por_cliente",
    ],
)
def test_obtener_sesiones_usa_metodos_alternativos(
    cliente,
    progreso_dao,
    cliente_dao,
    tmp_path,
    nombre_metodo,
):
    dao = SimpleNamespace()

    setattr(
        dao,
        nombre_metodo,
        Mock(return_value=["sesion"]),
    )

    control = ControlProgreso(
        progreso_dao=progreso_dao,
        sesion_dao=dao,
        cliente_dao=cliente_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    assert control.obtener_sesiones_cliente(cliente) == [
        "sesion",
    ]

    getattr(
        dao,
        nombre_metodo,
    ).assert_called_once_with(10)


def test_obtener_sesiones_rechaza_dao_sin_metodo(
    cliente,
    progreso_dao,
    cliente_dao,
    tmp_path,
):
    control = ControlProgreso(
        progreso_dao=progreso_dao,
        sesion_dao=SimpleNamespace(),
        cliente_dao=cliente_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    with pytest.raises(
        AttributeError,
        match="no tiene un método",
    ):
        control.obtener_sesiones_cliente(cliente)


def test_calcular_resumen_cliente(
    control,
    sesion_dao,
    cliente,
):
    sesion_dao.listar_por_cliente.return_value = [
        {
            "duracion_real": 30,
            "calorias_quemadas": "200.5",
            "veces_planificadas": 2,
            "veces_realizadas": 2,
        },
        {
            "duracion_minutos": 45,
            "calorias": "150.25",
            "sesiones_planificadas": 3,
            "sesiones_realizadas": 1,
        },
    ]

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        resultado = control.calcular_resumen_cliente(
            cliente
        )

    assert resultado["total_sesiones"] == 2
    assert resultado["total_minutos"] == 75
    assert resultado["total_calorias"] == Decimal("350.75")
    assert resultado["total_veces_planificadas"] == 5
    assert resultado["total_veces_realizadas"] == 3
    assert resultado["sesiones_completadas"] == 1
    assert resultado["porcentaje_cumplimiento"] == 60.0


def test_obtener_resumen_cliente_alias(
    control,
    sesion_dao,
    cliente,
):
    sesion_dao.listar_por_cliente.return_value = []

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        resultado = control.obtener_resumen_cliente(
            cliente
        )

    assert resultado["total_sesiones"] == 0


def test_calcular_impacto_calorico(
    control,
):
    rutina = {
        "ejercicios": [
            {"calorias_estimadas": "150.5"},
            {"calorias": "200.25"},
            {"calorias": "invalido"},
        ]
    }

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_impacto",
    ) as mock_log:
        resultado = control.calcular_impacto_calorico_rutina(
            rutina,
            "ADMIN",
        )

    assert resultado == Decimal("350.75")
    mock_log.assert_called_once_with("ADMIN")


def test_calcular_impacto_usa_sistema_y_alias(
    control,
):
    rutina = {
        "ejercicios": [],
    }

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_impacto",
    ) as mock_log:
        resultado = control.obtener_impacto_rutina(rutina)

    assert resultado == Decimal("0.00")
    mock_log.assert_called_once_with("SISTEMA")


def test_generar_progreso_mensual_exitoso(
    control,
    progreso_dao,
    sesion_dao,
    cliente_dao,
    cliente,
):
    sesion_dao.listar_por_cliente.return_value = [
        {
            "fecha": "2026-05-10",
            "veces_planificadas": 2,
            "veces_realizadas": 2,
        },
        {
            "fecha": datetime(2026, 5, 20),
            "veces_planificadas": 3,
            "veces_realizadas": 1,
        },
        {
            "fecha": "2026-04-20",
            "veces_planificadas": 5,
            "veces_realizadas": 5,
        },
        {
            "fecha": "invalida",
            "veces_planificadas": 1,
            "veces_realizadas": 1,
        },
    ]

    progreso_dao.guardar.side_effect = (
        lambda progreso: progreso
    )

    with patch(
        "src.controladores.control_progreso."
        "log_generar_progreso",
    ) as mock_log:
        resultado = control.generar_progreso_mensual(
            cliente=cliente,
            mes=5,
            anio=2026,
            peso_actual=Decimal("69.5"),
            observaciones="Buen avance",
        )

    assert resultado.id_cliente == 10
    assert resultado.sesiones_completadas == 1
    assert resultado.sesiones_planificadas == 5

    cliente_dao.actualizar_peso.assert_called_once_with(
        10,
        Decimal("69.5"),
    )

    mock_log.assert_called_once_with("CLIENTE_10")


@pytest.mark.parametrize(
    "peso",
    [
        None,
        "invalido",
        0,
        -1,
    ],
)
def test_generar_progreso_valida_peso(
    control,
    cliente,
    peso,
):
    if peso is None:
        cliente.peso = None

    with pytest.raises(ValueError):
        control.generar_progreso_mensual(
            cliente=cliente,
            mes=5,
            anio=2026,
            peso_actual=peso,
        )


def test_generar_progreso_rechaza_dao_none(
    control,
    cliente,
):
    control.progreso_dao = None

    with pytest.raises(
        RuntimeError,
        match="DAO de progreso",
    ):
        control.generar_progreso_mensual(
            cliente,
            mes=5,
            anio=2026,
            peso_actual=70,
        )


def test_actualizar_peso_cliente_con_metodo(
    control,
    cliente_dao,
):
    cliente = Mock()
    cliente.id_usuario = 10

    control._actualizar_peso_cliente(
        cliente,
        Decimal("68"),
    )

    cliente.actualizar_peso.assert_called_once_with(
        Decimal("68")
    )

    cliente_dao.actualizar_peso.assert_called_once_with(
        10,
        Decimal("68"),
    )


def test_actualizar_peso_cliente_con_atributo_y_sin_dao(
    control,
):
    cliente = SimpleNamespace(
        id_cliente=10,
        peso=70,
    )

    control.cliente_dao = None

    control._actualizar_peso_cliente(
        cliente,
        Decimal("68"),
    )

    assert cliente.peso == Decimal("68")


def test_consultar_progreso_exitoso_y_vacio(
    control,
    progreso_dao,
    cliente,
):
    progreso_dao.buscar_por_cliente.return_value = None

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        resultado = control.consultar_progreso(cliente)

    assert resultado == []


def test_consultar_progreso_rechaza_dao_none(
    control,
    cliente,
):
    control.progreso_dao = None

    with pytest.raises(
        RuntimeError,
        match="DAO de progreso",
    ):
        control.consultar_progreso(cliente)


@pytest.mark.parametrize(
    "sesion,esperado",
    [
        (
            {
                "veces_planificadas": 2,
                "veces_realizadas": 2,
            },
            True,
        ),
        (
            {
                "sesiones_planificadas": 3,
                "sesiones_realizadas": 2,
            },
            False,
        ),
        (
            {
                "veces_planificadas": 0,
                "veces_realizadas": 0,
            },
            False,
        ),
    ],
)
def test_sesion_completada(
    sesion,
    esperado,
):
    assert (
        ControlProgreso._sesion_completada(sesion)
        is esperado
    )


@pytest.mark.parametrize(
    "planificadas,realizadas,esperado",
    [
        (0, 5, 0.0),
        (-1, 5, 0.0),
        (10, 5, 50.0),
        (10, 10, 100.0),
        (10, 20, 100.0),
        (3, 1, 33.33),
    ],
)
def test_calcular_porcentaje(
    planificadas,
    realizadas,
    esperado,
):
    assert (
        ControlProgreso._calcular_porcentaje(
            planificadas,
            realizadas,
        )
        == esperado
    )