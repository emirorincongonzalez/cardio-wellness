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
def mock_progreso_dao():
    return Mock()


@pytest.fixture
def mock_sesion_dao():
    return Mock()


@pytest.fixture
def mock_cliente_dao():
    return Mock()


@pytest.fixture
def controlador(
    mock_progreso_dao,
    mock_sesion_dao,
    mock_cliente_dao,
    tmp_path,
):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlProgreso(
        progreso_dao=mock_progreso_dao,
        sesion_dao=mock_sesion_dao,
        cliente_dao=mock_cliente_dao,
        ruta_log=str(log_file),
    )


@pytest.fixture
def cliente():
    return SimpleNamespace(
        id_usuario=10,
        peso=Decimal("70"),
    )


def test_constructor_utiliza_daos_recibidos(
    mock_progreso_dao,
    mock_sesion_dao,
    mock_cliente_dao,
    tmp_path,
):
    controlador = ControlProgreso(
        progreso_dao=mock_progreso_dao,
        sesion_dao=mock_sesion_dao,
        cliente_dao=mock_cliente_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    assert controlador.progreso_dao is mock_progreso_dao
    assert controlador.sesion_dao is mock_sesion_dao
    assert controlador.cliente_dao is mock_cliente_dao


def test_constructor_crea_daos_por_defecto(
    tmp_path,
):
    progreso_dao = Mock()
    sesion_dao = Mock()

    with patch(
        "src.controladores.control_progreso."
        "_obtener_progreso_dao_default",
        return_value=progreso_dao,
    ), patch(
        "src.controladores.control_progreso."
        "_obtener_sesion_dao_default",
        return_value=sesion_dao,
    ):
        controlador = ControlProgreso(
            ruta_log=str(tmp_path / "registro.txt"),
        )

    assert controlador.progreso_dao is progreso_dao
    assert controlador.sesion_dao is sesion_dao
    assert controlador.cliente_dao is None


def test_propiedades_de_daos(
    controlador,
):
    progreso_dao = Mock()
    sesion_dao = Mock()
    cliente_dao = Mock()

    controlador.progreso_dao = progreso_dao
    controlador.sesion_dao = sesion_dao
    controlador.cliente_dao = cliente_dao

    assert controlador.progreso_dao is progreso_dao
    assert controlador.sesion_dao is sesion_dao
    assert controlador.cliente_dao is cliente_dao


@pytest.mark.parametrize(
    "objeto,campos,esperado",
    [
        (15, ("id",), 15),
        (True, ("id",), None),
        (False, ("id",), None),
        ({"id_cliente": 20}, ("id_cliente",), 20),
        (
            {"id_usuario": Mock(), "id_cliente": "25"},
            ("id_usuario", "id_cliente"),
            25,
        ),
        ({"otro": 1}, ("id_cliente",), None),
    ],
)
def test_extraer_id_con_enteros_y_diccionarios(
    objeto,
    campos,
    esperado,
):
    assert _extraer_id(
        objeto,
        *campos,
    ) == esperado


def test_extraer_id_con_objetos():
    objeto = SimpleNamespace(
        id_cliente="30",
    )

    assert _extraer_id(
        objeto,
        "id_usuario",
        "id_cliente",
    ) == 30

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
        ("15", 15),
        (20.8, 20),
        ("invalido", None),
        ([], None),
    ],
)
def test_convertir_id(
    valor,
    esperado,
):
    assert _convertir_id(valor) == esperado


def test_obtener_valor_desde_diccionario_y_objeto():
    assert _obtener_valor(
        {"peso": 70},
        "peso",
        predeterminado=0,
    ) == 70

    assert _obtener_valor(
        {
            "peso": Mock(),
            "peso_actual": 72,
        },
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
    "valor,esperado",
    [
        ("70.5", Decimal("70.5")),
        (None, Decimal("0")),
        ("invalido", Decimal("0")),
        (Decimal("12.25"), Decimal("12.25")),
    ],
)
def test_obtener_decimal(
    valor,
    esperado,
):
    assert _obtener_decimal(
        {"peso": valor},
        "peso",
    ) == esperado


@pytest.mark.parametrize(
    "valor,predeterminado,esperado",
    [
        ("5", 0, 5),
        (None, 2, 2),
        ("invalido", 3, 3),
    ],
)
def test_obtener_entero(
    valor,
    predeterminado,
    esperado,
):
    assert _obtener_entero(
        {"cantidad": valor},
        "cantidad",
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
            "2026-07-20 10:00:00",
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
            datetime(2026, 8, 1),
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
    "mes,anio",
    [
        ("texto", 2026),
        (5, None),
        (5, "texto"),
        (0, 2026),
        (13, 2026),
    ],
)
def test_normalizar_fecha_mes_invalido(
    mes,
    anio,
):
    with pytest.raises(ValueError):
        _normalizar_fecha_mes(
            mes,
            anio,
        )


def test_instanciar_progreso_mensual_con_diccionario():
    with patch(
        "src.controladores.control_progreso."
        "_obtener_clase_progreso",
        return_value=None,
    ):
        progreso = _instanciar_progreso_mensual(
            id_cliente=1,
            mes=5,
            anio=2026,
            peso_registrado=Decimal("70"),
        )

    assert progreso["id_cliente"] == 1
    assert progreso["mes"] == 5
    assert progreso["anio"] == 2026
    assert progreso["peso_registrado"] == Decimal("70")


def test_obtener_sesiones_cliente_exitoso(
    controlador,
    mock_sesion_dao,
    cliente,
):
    mock_sesion_dao.listar_por_cliente.return_value = [
        {"id_sesion": 1},
    ]

    resultado = controlador.obtener_sesiones_cliente(
        cliente
    )

    assert resultado == [{"id_sesion": 1}]

    mock_sesion_dao.listar_por_cliente.assert_called_once_with(
        10
    )


def test_obtener_sesiones_cliente_retorna_lista_vacia(
    controlador,
    mock_sesion_dao,
    cliente,
):
    mock_sesion_dao.listar_por_cliente.return_value = None

    assert controlador.obtener_sesiones_cliente(cliente) == []


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
def test_obtener_sesiones_cliente_rechaza_cliente_invalido(
    controlador,
    cliente_invalido,
):
    with pytest.raises(ValueError):
        controlador.obtener_sesiones_cliente(
            cliente_invalido
        )


def test_obtener_sesiones_cliente_rechaza_dao_none(
    controlador,
    cliente,
):
    controlador.sesion_dao = None

    with pytest.raises(RuntimeError):
        controlador.obtener_sesiones_cliente(cliente)


def test_calcular_resumen_cliente_y_auditoria(
    controlador,
    mock_sesion_dao,
    cliente,
):
    mock_sesion_dao.listar_por_cliente.return_value = [
        {
            "duracion_real": 30,
            "calorias_quemadas": "250.5",
            "veces_planificadas": 2,
            "veces_realizadas": 2,
        },
        {
            "duracion_minutos": 45,
            "calorias": "300",
            "sesiones_planificadas": 3,
            "sesiones_realizadas": 1,
        },
    ]

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        resumen = controlador.calcular_resumen_cliente(
            cliente
        )

    assert resumen["id_cliente"] == 10
    assert resumen["total_sesiones"] == 2
    assert resumen["total_minutos"] == 75
    assert resumen["total_calorias"] == Decimal("550.50")
    assert resumen["total_veces_planificadas"] == 5
    assert resumen["total_veces_realizadas"] == 3
    assert resumen["sesiones_completadas"] == 1
    assert resumen["porcentaje_cumplimiento"] == 60.0

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "CLIENTE_10, CONSULTA_PROGRESO" in contenido_log


def test_obtener_resumen_cliente_alias(
    controlador,
    mock_sesion_dao,
    cliente,
):
    mock_sesion_dao.listar_por_cliente.return_value = []

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        resultado = controlador.obtener_resumen_cliente(
            cliente
        )

    assert resultado["total_sesiones"] == 0


def test_calcular_impacto_calorico_rutina(
    controlador,
):
    rutina = {
        "ejercicios": [
            {"calorias_estimadas": "150.25"},
            {"calorias": "200.50"},
            {"calorias": "invalido"},
        ],
    }

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_impacto",
    ) as mock_log:
        impacto = (
            controlador.calcular_impacto_calorico_rutina(
                rutina,
                usuario_consulta="entrenador1",
            )
        )

    assert impacto == Decimal("350.75")

    mock_log.assert_called_once_with("entrenador1")


def test_obtener_impacto_rutina_alias(
    controlador,
):
    with patch(
        "src.controladores.control_progreso."
        "log_consulta_impacto",
    ) as mock_log:
        impacto = controlador.obtener_impacto_rutina(
            {"ejercicios": []}
        )

    assert impacto == Decimal("0.00")

    mock_log.assert_called_once_with("SISTEMA")


def test_generar_progreso_mensual_exitoso(
    controlador,
    mock_progreso_dao,
    mock_sesion_dao,
    mock_cliente_dao,
    cliente,
):
    mock_sesion_dao.listar_por_cliente.return_value = [
        {
            "fecha": "2026-05-10",
            "veces_planificadas": 2,
            "veces_realizadas": 2,
        },
        {
            "fecha": datetime(2026, 5, 15),
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

    mock_progreso_dao.guardar.side_effect = (
        lambda progreso: progreso
    )

    with patch(
        "src.controladores.control_progreso."
        "log_generar_progreso",
    ) as mock_log:
        progreso = controlador.generar_progreso_mensual(
            cliente=cliente,
            mes=5,
            anio=2026,
            peso_actual=Decimal("69.5"),
            observaciones="Buen avance",
        )

    assert progreso.id_cliente == 10
    assert progreso.sesiones_completadas == 1
    assert progreso.sesiones_planificadas == 5

    mock_cliente_dao.actualizar_peso.assert_called_once_with(
        10,
        Decimal("69.5"),
    )

    mock_log.assert_called_once_with("CLIENTE_10")


@pytest.mark.parametrize(
    "peso",
    [
        "invalido",
        0,
        -1,
    ],
)
def test_generar_progreso_rechaza_peso_invalido(
    controlador,
    cliente,
    peso,
):
    with pytest.raises(ValueError):
        controlador.generar_progreso_mensual(
            cliente,
            mes=5,
            anio=2026,
            peso_actual=peso,
        )


def test_generar_progreso_rechaza_peso_ausente(
    controlador,
):
    cliente = SimpleNamespace(
        id_usuario=10,
    )

    with pytest.raises(ValueError):
        controlador.generar_progreso_mensual(
            cliente,
            mes=5,
            anio=2026,
        )


def test_generar_progreso_rechaza_dao_none(
    controlador,
    cliente,
):
    controlador.progreso_dao = None

    with pytest.raises(RuntimeError):
        controlador.generar_progreso_mensual(
            cliente,
            mes=5,
            anio=2026,
            peso_actual=70,
        )


def test_consultar_progreso_exitoso(
    controlador,
    mock_progreso_dao,
    cliente,
):
    mock_progreso_dao.buscar_por_cliente.return_value = [
        {"id_progreso": 1},
    ]

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        historial = controlador.consultar_progreso(cliente)

    assert historial == [{"id_progreso": 1}]

    mock_progreso_dao.buscar_por_cliente.assert_called_once_with(
        10
    )


def test_consultar_progreso_retorna_lista_vacia(
    controlador,
    mock_progreso_dao,
    cliente,
):
    mock_progreso_dao.buscar_por_cliente.return_value = None

    with patch(
        "src.controladores.control_progreso."
        "log_consulta_progreso",
    ):
        assert controlador.consultar_progreso(cliente) == []


def test_consultar_progreso_rechaza_dao_none(
    controlador,
    cliente,
):
    controlador.progreso_dao = None

    with pytest.raises(RuntimeError):
        controlador.consultar_progreso(cliente)


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

def test_obtener_progreso_dao_default():
    """
    Verifica creación del DAO predeterminado de progreso.
    """
    with patch(
        "src.controladores.control_progreso.ProgresoMensualDAO",
    ) as mock_dao:
        from src.controladores.control_progreso import (
            _obtener_progreso_dao_default,
        )

        resultado = _obtener_progreso_dao_default()

    mock_dao.assert_called_once_with()
    assert resultado is mock_dao.return_value


def test_obtener_sesion_dao_default():
    """
    Verifica creación del DAO predeterminado de sesiones.
    """
    with patch(
        "src.controladores.control_progreso."
        "SesionEntrenamientoDAO",
    ) as mock_dao:
        from src.controladores.control_progreso import (
            _obtener_sesion_dao_default,
        )

        resultado = _obtener_sesion_dao_default()

    mock_dao.assert_called_once_with()
    assert resultado is mock_dao.return_value


def test_extraer_id_omite_atributo_mock():
    """
    Verifica que _extraer_id ignore atributos Mock y continúe
    buscando el siguiente identificador disponible.
    """
    objeto = SimpleNamespace(
        id_usuario=Mock(),
        id_cliente=25,
    )

    resultado = _extraer_id(
        objeto,
        "id_usuario",
        "id_cliente",
    )

    assert resultado == 25


def test_obtener_valor_omite_atributo_mock():
    """
    Verifica que _obtener_valor ignore atributos Mock y continúe
    buscando el siguiente atributo válido.
    """
    objeto = SimpleNamespace(
        peso=Mock(),
        peso_actual=Decimal("72.5"),
    )

    resultado = _obtener_valor(
        objeto,
        "peso",
        "peso_actual",
        predeterminado=Decimal("0"),
    )

    assert resultado == Decimal("72.5")


@pytest.mark.parametrize(
    "nombre_metodo",
    [
        "buscar_por_cliente",
        "obtener_por_cliente",
    ],
)
def test_obtener_sesiones_cliente_usa_metodos_alternativos(
    mock_progreso_dao,
    mock_cliente_dao,
    tmp_path,
    cliente,
    nombre_metodo,
):
    """
    Verifica las alternativas buscar_por_cliente y
    obtener_por_cliente cuando no existe listar_por_cliente.
    """
    dao_sesion = SimpleNamespace()

    metodo = Mock(
        return_value=[
            {
                "id_sesion": 1,
            }
        ]
    )

    setattr(
        dao_sesion,
        nombre_metodo,
        metodo,
    )

    controlador = ControlProgreso(
        progreso_dao=mock_progreso_dao,
        sesion_dao=dao_sesion,
        cliente_dao=mock_cliente_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    resultado = controlador.obtener_sesiones_cliente(
        cliente
    )

    assert resultado == [
        {
            "id_sesion": 1,
        }
    ]

    metodo.assert_called_once_with(10)


def test_obtener_sesiones_cliente_rechaza_dao_sin_metodo(
    mock_progreso_dao,
    mock_cliente_dao,
    tmp_path,
    cliente,
):
    """
    Verifica error cuando el DAO de sesiones no expone ningún
    método compatible para listar sesiones por cliente.
    """
    controlador = ControlProgreso(
        progreso_dao=mock_progreso_dao,
        sesion_dao=SimpleNamespace(),
        cliente_dao=mock_cliente_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    with pytest.raises(
        AttributeError,
        match="no tiene un método",
    ):
        controlador.obtener_sesiones_cliente(cliente)


def test_calcular_resumen_cliente_rechaza_cliente_invalido(
    controlador,
):
    """
    Verifica la validación específica de calcular_resumen_cliente.
    """
    with pytest.raises(
        ValueError,
        match="id del cliente",
    ):
        controlador.calcular_resumen_cliente(
            SimpleNamespace(
                id_usuario=-1,
            )
        )


def test_generar_progreso_rechaza_cliente_invalido(
    controlador,
):
    """
    Verifica validación del identificador al generar progreso.
    """
    with pytest.raises(
        ValueError,
        match="id del cliente",
    ):
        controlador.generar_progreso_mensual(
            cliente=SimpleNamespace(
                id_usuario=-1,
                peso=70,
            ),
            mes=5,
            anio=2026,
            peso_actual=70,
        )


def test_generar_progreso_asigna_observaciones(
    controlador,
    mock_progreso_dao,
    mock_sesion_dao,
    cliente,
):
    """
    Verifica asignación de observaciones cuando el modelo de
    progreso expone dicho atributo.
    """
    progreso = SimpleNamespace(
        observaciones=None,
    )

    mock_sesion_dao.listar_por_cliente.return_value = []

    mock_progreso_dao.guardar.side_effect = (
        lambda valor: valor
    )

    with patch(
        "src.controladores.control_progreso."
        "_instanciar_progreso_mensual",
        return_value=progreso,
    ), patch(
        "src.controladores.control_progreso."
        "log_generar_progreso",
    ):
        resultado = controlador.generar_progreso_mensual(
            cliente=cliente,
            mes=5,
            anio=2026,
            peso_actual=70,
            observaciones="Excelente avance",
        )

    assert resultado is progreso
    assert progreso.observaciones == "Excelente avance"


def test_actualizar_peso_cliente_usa_metodo_del_cliente(
    controlador,
    mock_cliente_dao,
):
    """
    Verifica actualización de peso mediante actualizar_peso()
    cuando el cliente ofrece ese método.
    """
    cliente = SimpleNamespace(
        id_usuario=10,
    )

    cliente.actualizar_peso = Mock()

    controlador._actualizar_peso_cliente(
        cliente=cliente,
        peso=Decimal("68.5"),
    )

    cliente.actualizar_peso.assert_called_once_with(
        Decimal("68.5")
    )

    mock_cliente_dao.actualizar_peso.assert_called_once_with(
        10,
        Decimal("68.5"),
    )


def test_actualizar_peso_cliente_sin_cliente_dao():
    """
    Verifica retorno temprano si no existe cliente_dao.
    """
    controlador = ControlProgreso(
        progreso_dao=Mock(),
        sesion_dao=Mock(),
        cliente_dao=None,
    )

    cliente = SimpleNamespace(
        id_usuario=10,
        peso=70,
    )

    controlador._actualizar_peso_cliente(
        cliente=cliente,
        peso=Decimal("68"),
    )

    assert cliente.peso == Decimal("68")


def test_actualizar_peso_cliente_sin_identificador(
    controlador,
    mock_cliente_dao,
):
    """
    Verifica retorno temprano cuando el cliente no tiene
    identificador válido.
    """
    cliente = SimpleNamespace(
        peso=70,
    )

    controlador._actualizar_peso_cliente(
        cliente=cliente,
        peso=Decimal("68"),
    )

    assert cliente.peso == Decimal("68")

    mock_cliente_dao.actualizar_peso.assert_not_called()


def test_consultar_progreso_rechaza_cliente_invalido(
    controlador,
):
    """
    Verifica validación de cliente al consultar historial.
    """
    with pytest.raises(
        ValueError,
        match="id del cliente",
    ):
        controlador.consultar_progreso(
            SimpleNamespace(
                id_usuario=-1,
            )
        )