from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, PropertyMock, patch

import pytest

from src.controladores.control_sesiones import (
    ControlSesiones,
)
from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import (
    SesionEntrenamiento,
)


@pytest.fixture
def mock_sesion_dao():
    """
    Crea un DAO de sesiones simulado.
    """
    return Mock()


@pytest.fixture
def controlador(
    mock_sesion_dao,
    tmp_path,
):
    """
    Crea el controlador con un archivo de auditoría temporal.
    """
    ruta_log = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlSesiones(
        sesion_dao=mock_sesion_dao,
        ruta_log=str(ruta_log),
    )


@pytest.fixture
def sesion_valida():
    """
    Crea una sesión válida para pruebas de actualización,
    porcentaje y conteo.
    """
    sesion = SesionEntrenamiento(
        id_cliente=10,
        id_rutina=5,
        fecha=date(2026, 1, 15),
        nombre_ejercicio="Caminata",
        duracion_real=30,
        intensidad_real=Intensidad.MEDIA,
        calorias_quemadas=Decimal("250"),
        observaciones="Sesión de prueba",
        veces_planificadas=2,
        veces_realizadas=1,
    )

    sesion.id_sesion = 20

    return sesion


def test_constructor_utiliza_dao_recibido(
    mock_sesion_dao,
    tmp_path,
):
    """
    Verifica que el constructor conserve el DAO inyectado.
    """
    controlador = ControlSesiones(
        sesion_dao=mock_sesion_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    assert controlador.sesion_dao is mock_sesion_dao


def test_constructor_crea_dao_por_defecto(
    tmp_path,
):
    """
    Verifica que se cree un DAO si no se proporciona uno.
    """
    dao_creado = Mock()

    with patch(
        "src.controladores.control_sesiones.SesionEntrenamientoDAO",
        return_value=dao_creado,
    ):
        controlador = ControlSesiones(
            ruta_log=str(tmp_path / "registro.txt"),
        )

    assert controlador.sesion_dao is dao_creado


def test_registrar_sesion_exitoso_y_auditoria(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica registro correcto usando objetos cliente y rutina.
    """
    mock_sesion_dao.guardar.side_effect = (
        lambda sesion: sesion
    )

    cliente_mock = Mock()
    cliente_mock.id_usuario = 15

    rutina_mock = Mock()
    rutina_mock.id_rutina = 3

    with patch(
        "src.controladores.control_sesiones.log_generar_progreso",
    ) as mock_generar_progreso:
        sesion = controlador.registrar_sesion(
            cliente=cliente_mock,
            rutina=rutina_mock,
            nombre_ejercicio="  Circuito cardio  ",
            duracion_real=45,
            intensidad_real=Intensidad.ALTA,
            calorias_quemadas=400,
            observaciones="Completó todo el circuito",
            veces_planificadas=2,
            veces_realizadas=2,
        )

    assert sesion is not None
    assert sesion.id_cliente == 15
    assert sesion.id_rutina == 3
    assert sesion.nombre_ejercicio == "Circuito cardio"
    assert sesion.duracion_real == 45
    assert sesion.intensidad_real == Intensidad.ALTA
    assert sesion.calorias_quemadas == Decimal("400")
    assert sesion.veces_planificadas == 2
    assert sesion.veces_realizadas == 2

    mock_sesion_dao.guardar.assert_called_once_with(
        sesion
    )

    mock_generar_progreso.assert_called_once_with(
        "CLIENTE_15"
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "CLIENTE_15, REGISTRO_SESION" in contenido_log
    assert "Rutina: 3" in contenido_log
    assert "Ejercicio: Circuito cardio" in contenido_log
    assert "Realizadas: 2/2" in contenido_log


def test_registrar_sesion_con_ids_directos_y_fecha_datetime(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica registro usando IDs directos y fecha datetime.
    """
    mock_sesion_dao.guardar.side_effect = (
        lambda sesion: sesion
    )

    with patch(
        "src.controladores.control_sesiones.log_generar_progreso",
    ):
        sesion = controlador.registrar_sesion(
            cliente=5,
            rutina=2,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real=" media ",
            calorias_quemadas=Decimal("250.5"),
            fecha=datetime(2026, 2, 10, 8, 30),
            veces_planificadas=3,
            veces_realizadas=1,
        )

    assert sesion.id_cliente == 5
    assert sesion.id_rutina == 2
    assert sesion.fecha == date(2026, 2, 10)
    assert sesion.intensidad_real == Intensidad.MEDIA
    assert sesion.calorias_quemadas == Decimal("250.5")
    assert sesion.observaciones == ""


def test_registrar_sesion_usa_fecha_actual_si_no_se_indica(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica que se use date.today() cuando no llega fecha.
    """
    mock_sesion_dao.guardar.side_effect = (
        lambda sesion: sesion
    )

    with patch(
        "src.controladores.control_sesiones.log_generar_progreso",
    ):
        sesion = controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Bicicleta",
            duracion_real=20,
            intensidad_real="BAJA",
            calorias_quemadas=100,
        )

    assert sesion.fecha == date.today()


@pytest.mark.parametrize(
    "cliente",
    [
        None,
        False,
        0,
        -1,
        "cinco",
        {},
        {"id_usuario": "invalido"},
    ],
)
def test_registrar_sesion_rechaza_cliente_invalido(
    controlador,
    cliente,
):
    """
    Verifica validación de identificador de cliente.
    """
    with pytest.raises(
        ValueError,
        match="ID del cliente",
    ):
        controlador.registrar_sesion(
            cliente=cliente,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
        )


@pytest.mark.parametrize(
    "rutina",
    [
        None,
        False,
        0,
        -2,
        "texto",
        {},
        {"id_rutina": "invalido"},
    ],
)
def test_registrar_sesion_rechaza_rutina_invalida(
    controlador,
    rutina,
):
    """
    Verifica validación de identificador de rutina.
    """
    with pytest.raises(
        ValueError,
        match="ID de rutina",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=rutina,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
        )


@pytest.mark.parametrize(
    "nombre,mensaje",
    [
        (None, "nombre del ejercicio debe ser texto"),
        (10, "nombre del ejercicio debe ser texto"),
        ("", "nombre del ejercicio es obligatorio"),
        ("   ", "nombre del ejercicio es obligatorio"),
        ("x" * 101, "no puede superar 100"),
    ],
)
def test_registrar_sesion_valida_nombre_ejercicio(
    controlador,
    nombre,
    mensaje,
):
    """
    Verifica validaciones del nombre del ejercicio.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio=nombre,
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
        )


@pytest.mark.parametrize(
    "duracion",
    [
        True,
        False,
        0,
        -1,
        "30",
        20.5,
        None,
    ],
)
def test_registrar_sesion_valida_duracion(
    controlador,
    duracion,
):
    """
    Verifica que la duración sea un entero positivo.
    """
    with pytest.raises(
        ValueError,
        match="duración real debe ser un entero positivo",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=duracion,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
        )


@pytest.mark.parametrize(
    "calorias,mensaje",
    [
        (True, "calorías deben ser numéricas"),
        (False, "calorías deben ser numéricas"),
        ("200", "calorías deben ser numéricas"),
        (None, "calorías deben ser numéricas"),
        ([], "calorías deben ser numéricas"),
        (-1, "calorías no pueden ser negativas"),
        (-0.5, "calorías no pueden ser negativas"),
    ],
)
def test_registrar_sesion_valida_calorias(
    controlador,
    calorias,
    mensaje,
):
    """
    Verifica validación de calorías.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=calorias,
        )


@pytest.mark.parametrize(
    "planificadas,realizadas,mensaje",
    [
        (True, 0, "veces planificadas debe ser un entero"),
        (0, 0, "veces planificadas debe ser mayor o igual a 1"),
        (-1, 0, "veces planificadas debe ser mayor o igual a 1"),
        (1, True, "veces realizadas debe ser un entero"),
        (1, -1, "veces realizadas debe ser mayor o igual a 0"),
        (1, 2, "no pueden superar las planificadas"),
    ],
)
def test_registrar_sesion_valida_cantidades(
    controlador,
    planificadas,
    realizadas,
    mensaje,
):
    """
    Verifica validaciones de cantidades planificadas y realizadas.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
            veces_planificadas=planificadas,
            veces_realizadas=realizadas,
        )


@pytest.mark.parametrize(
    "intensidad",
    [
        None,
        True,
        10,
        "",
        "SUAVE",
    ],
)
def test_registrar_sesion_valida_intensidad(
    controlador,
    intensidad,
):
    """
    Verifica validación de intensidad.
    """
    with pytest.raises(
        ValueError,
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real=intensidad,
            calorias_quemadas=200,
        )


@pytest.mark.parametrize(
    "fecha_invalida",
    [
        "2026-01-01",
        10,
        [],
    ],
)
def test_registrar_sesion_valida_fecha(
    controlador,
    fecha_invalida,
):
    """
    Verifica que la fecha sea date o datetime.
    """
    with pytest.raises(
        ValueError,
        match="fecha debe ser un objeto date",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
            fecha=fecha_invalida,
        )


def test_registrar_sesion_maneja_value_error_del_dao(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica que un ValueError del DAO se preserve con contexto.
    """
    mock_sesion_dao.guardar.side_effect = ValueError(
        "Registro duplicado"
    )

    with pytest.raises(
        ValueError,
        match="Error al registrar la sesión: Registro duplicado",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
        )


def test_registrar_sesion_maneja_error_inesperado_del_dao(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica conversión de errores inesperados a RuntimeError.
    """
    mock_sesion_dao.guardar.side_effect = RuntimeError(
        "Base de datos caída"
    )

    with pytest.raises(
        RuntimeError,
        match="Error inesperado al registrar la sesión",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=200,
        )


def test_actualizar_sesion_exitoso(
    controlador,
    mock_sesion_dao,
    sesion_valida,
):
    """
    Verifica actualización correcta de una sesión.
    """
    mock_sesion_dao.actualizar.return_value = sesion_valida

    resultado = controlador.actualizar_sesion(
        sesion_valida,
        usuario_accion="admin",
    )

    assert resultado is sesion_valida

    mock_sesion_dao.actualizar.assert_called_once_with(
        sesion_valida
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "admin, ACTUALIZACION_SESION" in contenido_log


def test_actualizar_sesion_usa_usuario_por_defecto(
    controlador,
    mock_sesion_dao,
    sesion_valida,
):
    """
    Verifica usuario de auditoría por defecto.
    """
    mock_sesion_dao.actualizar.return_value = sesion_valida

    controlador.actualizar_sesion(sesion_valida)

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "SESION_20, ACTUALIZACION_SESION" in contenido_log


def test_actualizar_sesion_rechaza_objeto_invalido(
    controlador,
):
    """
    Verifica que solo se acepten SesionEntrenamiento.
    """
    with pytest.raises(
        TypeError,
        match="instancia de SesionEntrenamiento",
    ):
        controlador.actualizar_sesion(Mock())


def test_actualizar_sesion_rechaza_sesion_sin_id(
    controlador,
    sesion_valida,
):
    """
    Verifica que la sesión de actualización tenga ID.
    """
    sesion_valida.id_sesion = None

    with pytest.raises(
        ValueError,
        match="sesión debe tener un ID",
    ):
        controlador.actualizar_sesion(sesion_valida)


@pytest.mark.parametrize(
    "planificadas,realizadas",
    [
        (0, 0),
        (1, -1),
        (1, 2),
    ],
)
def test_actualizar_sesion_valida_cantidades(
    controlador,
    sesion_valida,
    planificadas,
    realizadas,
):
    """
    Verifica cantidades inválidas durante la actualización.

    SesionEntrenamiento puede validar los valores al asignar
    directamente los atributos; por eso las asignaciones deben estar
    dentro de pytest.raises.
    """
    with pytest.raises(ValueError):
        sesion_valida.veces_planificadas = planificadas
        sesion_valida.veces_realizadas = realizadas

        controlador.actualizar_sesion(sesion_valida)

def test_actualizar_sesion_maneja_value_error_dao(
    controlador,
    mock_sesion_dao,
    sesion_valida,
):
    """
    Verifica manejo de ValueError emitido por el DAO.
    """
    mock_sesion_dao.actualizar.side_effect = ValueError(
        "No existe la sesión"
    )

    with pytest.raises(
        ValueError,
        match="Error al actualizar la sesión",
    ):
        controlador.actualizar_sesion(sesion_valida)


def test_actualizar_sesion_maneja_error_inesperado_dao(
    controlador,
    mock_sesion_dao,
    sesion_valida,
):
    """
    Verifica manejo de excepción inesperada del DAO.
    """
    mock_sesion_dao.actualizar.side_effect = RuntimeError(
        "Error de conexión"
    )

    with pytest.raises(
        RuntimeError,
        match="Error inesperado al actualizar la sesión",
    ):
        controlador.actualizar_sesion(sesion_valida)


def test_obtener_sesiones_cliente_y_alias(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica consulta de sesiones y alias listar_por_cliente.
    """
    sesiones = [
        Mock(),
        Mock(),
    ]

    mock_sesion_dao.listar_por_cliente.return_value = sesiones

    resultado_1 = controlador.obtener_sesiones_cliente(10)
    resultado_2 = controlador.listar_por_cliente(10)

    assert resultado_1 == sesiones
    assert resultado_2 == sesiones

    assert (
        mock_sesion_dao.listar_por_cliente.call_count
        == 2
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "CLIENTE_10, CONSULTA_SESIONES" in contenido_log


def test_obtener_sesiones_cliente_retorna_lista_vacia_si_dao_retorna_none(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica retorno seguro de lista vacía.
    """
    mock_sesion_dao.listar_por_cliente.return_value = None

    resultado = controlador.obtener_sesiones_cliente(10)

    assert resultado == []


@pytest.mark.parametrize(
    "id_cliente",
    [
        True,
        False,
        0,
        -1,
        "10",
        None,
    ],
)
def test_obtener_sesiones_cliente_valida_id(
    controlador,
    id_cliente,
):
    """
    Verifica validación del identificador del cliente.
    """
    with pytest.raises(
        ValueError,
        match="ID de cliente",
    ):
        controlador.obtener_sesiones_cliente(id_cliente)


def test_obtener_sesiones_cliente_maneja_error_dao(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica conversión de error del DAO a RuntimeError.
    """
    mock_sesion_dao.listar_por_cliente.side_effect = RuntimeError(
        "Error de conexión"
    )

    with pytest.raises(
        RuntimeError,
        match="Error al consultar las sesiones",
    ):
        controlador.obtener_sesiones_cliente(10)


def test_buscar_por_id_y_alias_obtener_por_id(
    controlador,
    mock_sesion_dao,
    sesion_valida,
):
    """
    Verifica búsqueda por ID y alias obtener_por_id.
    """
    mock_sesion_dao.buscar_por_id.return_value = sesion_valida

    resultado_1 = controlador.buscar_por_id(20)
    resultado_2 = controlador.obtener_por_id(20)

    assert resultado_1 is sesion_valida
    assert resultado_2 is sesion_valida

    assert (
        mock_sesion_dao.buscar_por_id.call_count
        == 2
    )


@pytest.mark.parametrize(
    "id_sesion",
    [
        True,
        False,
        0,
        -2,
        "20",
        None,
    ],
)
def test_buscar_por_id_valida_identificador(
    controlador,
    id_sesion,
):
    """
    Verifica validación del ID de sesión.
    """
    with pytest.raises(
        ValueError,
        match="ID de sesión",
    ):
        controlador.buscar_por_id(id_sesion)


def test_buscar_por_id_maneja_error_dao(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica manejo de error de búsqueda.
    """
    mock_sesion_dao.buscar_por_id.side_effect = RuntimeError(
        "Consulta no disponible"
    )

    with pytest.raises(
        RuntimeError,
        match="Error al buscar la sesión",
    ):
        controlador.buscar_por_id(20)


def test_eliminar_sesion_y_auditoria(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica eliminación y registro de auditoría.
    """
    mock_sesion_dao.eliminar_por_id.return_value = True

    resultado = controlador.eliminar_sesion(
        99,
        usuario_accion="admin",
    )

    assert resultado is True

    mock_sesion_dao.eliminar_por_id.assert_called_once_with(
        99
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "admin, ELIMINACION_SESION" in contenido_log


def test_eliminar_sesion_usa_usuario_por_defecto(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica auditoría con usuario predeterminado.
    """
    mock_sesion_dao.eliminar_por_id.return_value = True

    controlador.eliminar_sesion(99)

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "SESION_99, ELIMINACION_SESION" in contenido_log


def test_eliminar_sesion_sin_resultado_no_registra_log(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica que no se registre auditoría si no se elimina nada.
    """
    mock_sesion_dao.eliminar_por_id.return_value = False

    resultado = controlador.eliminar_sesion(99)

    assert resultado is False

    assert not controlador.ruta_log.exists()


@pytest.mark.parametrize(
    "id_sesion",
    [
        True,
        False,
        0,
        -1,
        "99",
        None,
    ],
)
def test_eliminar_sesion_valida_identificador(
    controlador,
    id_sesion,
):
    """
    Verifica validación del ID de sesión a eliminar.
    """
    with pytest.raises(
        ValueError,
        match="ID de sesión",
    ):
        controlador.eliminar_sesion(id_sesion)


def test_eliminar_sesion_maneja_value_error_dao(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica propagación controlada de ValueError del DAO.
    """
    mock_sesion_dao.eliminar_por_id.side_effect = ValueError(
        "Sesión protegida"
    )

    with pytest.raises(
        ValueError,
        match="Error al eliminar la sesión",
    ):
        controlador.eliminar_sesion(99)


def test_eliminar_sesion_maneja_error_inesperado_dao(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica conversión de error inesperado en eliminación.
    """
    mock_sesion_dao.eliminar_por_id.side_effect = RuntimeError(
        "Base de datos caída"
    )

    with pytest.raises(
        RuntimeError,
        match="Error inesperado al eliminar la sesión",
    ):
        controlador.eliminar_sesion(99)


def test_contar_sesiones_completadas_con_fecha_indicada(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica conteo de sesiones completadas para una fecha.
    """
    fecha_consulta = date(2026, 3, 1)

    completada = Mock()
    completada.fecha = fecha_consulta
    completada.completada = True

    incompleta = Mock()
    incompleta.fecha = fecha_consulta
    incompleta.completada = False

    otra_fecha = Mock()
    otra_fecha.fecha = date(2026, 3, 2)
    otra_fecha.completada = True

    mock_sesion_dao.listar_por_cliente.return_value = [
        completada,
        incompleta,
        otra_fecha,
    ]

    resultado = controlador.contar_sesiones_completadas(
        10,
        fecha_consulta,
    )

    assert resultado == 1

    mock_sesion_dao.listar_por_cliente.assert_called_once_with(
        10
    )


def test_contar_sesiones_completadas_usa_fecha_actual(
    controlador,
    mock_sesion_dao,
):
    """
    Verifica uso de fecha actual cuando no se indica fecha.
    """
    sesion = Mock()
    sesion.fecha = date.today()
    sesion.completada = True

    mock_sesion_dao.listar_por_cliente.return_value = [
        sesion
    ]

    resultado = controlador.contar_sesiones_completadas(10)

    assert resultado == 1

@pytest.mark.parametrize(
    "objeto,campos,esperado",
    [
        (10, ("id_usuario",), 10),
        (True, ("id_usuario",), None),
        (False, ("id_usuario",), None),
        ({"id_usuario": 15}, ("id_usuario",), 15),
        ({"id_cliente": "20"}, ("id_usuario", "id_cliente"), 20),
        ({"otro": 1}, ("id_usuario",), None),
        ({"id_usuario": False}, ("id_usuario",), None),
    ],
)
def test_extraer_id_con_enteros_y_diccionarios(
    objeto,
    campos,
    esperado,
):
    """
    Verifica extracción de IDs desde enteros y diccionarios.
    """
    resultado = ControlSesiones._extraer_id(
        objeto,
        *campos,
    )

    assert resultado == esperado


def test_extraer_id_con_objeto_y_sin_campos_validos():
    """
    Verifica extracción desde atributos de objetos.
    """
    objeto = SimpleNamespace(
        id_cliente="42",
    )

    resultado = ControlSesiones._extraer_id(
        objeto,
        "id_usuario",
        "id_cliente",
    )

    assert resultado == 42

    objeto_sin_id = object()

    resultado_sin_id = ControlSesiones._extraer_id(
        objeto_sin_id,
        "id_usuario",
    )

    assert resultado_sin_id is None


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (None, None),
        (True, None),
        (False, None),
        (10, 10),
        ("25", 25),
        (20.8, 20),
        ("invalido", None),
        ([], None),
    ],
)
def test_convertir_id(
    valor,
    esperado,
):
    """
    Verifica conversión segura de identificadores.
    """
    assert (
        ControlSesiones._convertir_id(valor)
        == esperado
    )


@pytest.mark.parametrize(
    "valor,nombre,esperado",
    [
        (1, "cliente", 1),
        (99, "sesión", 99),
    ],
)
def test_validar_id_exitoso(
    valor,
    nombre,
    esperado,
):
    """
    Verifica IDs positivos válidos.
    """
    assert (
        ControlSesiones._validar_id(
            valor,
            nombre,
        )
        == esperado
    )


@pytest.mark.parametrize(
    "valor",
    [
        True,
        False,
        0,
        -1,
        "1",
        1.5,
        None,
    ],
)
def test_validar_id_rechaza_valores_invalidos(
    valor,
):
    """
    Verifica rechazo de IDs inválidos.
    """
    with pytest.raises(
        ValueError,
        match="entero positivo",
    ):
        ControlSesiones._validar_id(
            valor,
            "cliente",
        )


@pytest.mark.parametrize(
    "valor,nombre,minimo,esperado",
    [
        (0, "cantidad", 0, 0),
        (1, "cantidad", 1, 1),
        (5, "cantidad", 1, 5),
    ],
)
def test_validar_cantidad_exitoso(
    valor,
    nombre,
    minimo,
    esperado,
):
    """
    Verifica cantidades válidas.
    """
    assert (
        ControlSesiones._validar_cantidad(
            valor,
            nombre,
            minimo,
        )
        == esperado
    )


@pytest.mark.parametrize(
    "valor,nombre,minimo,mensaje",
    [
        (True, "cantidad", 0, "cantidad debe ser un entero"),
        (False, "cantidad", 0, "cantidad debe ser un entero"),
        ("1", "cantidad", 0, "cantidad debe ser un entero"),
        (1.5, "cantidad", 0, "cantidad debe ser un entero"),
        (-1, "cantidad", 0, "cantidad debe ser mayor o igual"),
        (0, "cantidad", 1, "cantidad debe ser mayor o igual"),
    ],
)
def test_validar_cantidad_rechaza_valores_invalidos(
    valor,
    nombre,
    minimo,
    mensaje,
):
    """
    Verifica validación de cantidades inválidas.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        ControlSesiones._validar_cantidad(
            valor,
            nombre,
            minimo,
        )


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (Intensidad.BAJA, Intensidad.BAJA),
        ("BAJA", Intensidad.BAJA),
        (" media ", Intensidad.MEDIA),
        ("alta", Intensidad.ALTA),
    ],
)
def test_normalizar_intensidad_exitoso(
    valor,
    esperado,
):
    """
    Verifica normalización de enums y textos de intensidad.
    """
    assert (
        ControlSesiones._normalizar_intensidad(valor)
        == esperado
    )


@pytest.mark.parametrize(
    "valor",
    [
        None,
        True,
        1,
        "",
        "SUAVE",
        "MAXIMA",
    ],
)
def test_normalizar_intensidad_rechaza_valores_invalidos(
    valor,
):
    """
    Verifica rechazo de intensidades inválidas.
    """
    with pytest.raises(
        ValueError,
    ):
        ControlSesiones._normalizar_intensidad(valor)

def test_registrar_sesion_rechaza_calorias_no_convertibles(
    controlador,
):
    """
    Verifica el manejo de un valor numérico cuyo texto no puede
    convertirse a Decimal.
    """

    class EnteroConTextoInvalido(int):
        def __str__(self):
            return "no_es_decimal"

    with pytest.raises(
        ValueError,
        match="calorías deben ser un valor válido",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=EnteroConTextoInvalido(200),
        )

def test_registrar_sesion_rechaza_calorias_no_convertibles(
    controlador,
):
    """
    Verifica que se rechace un valor numérico cuyo texto
    no puede convertirse a Decimal.
    """

    class EnteroConTextoInvalido(int):
        def __str__(self):
            return "no_es_decimal"

    with pytest.raises(
        ValueError,
        match="calorías deben ser un valor válido",
    ):
        controlador.registrar_sesion(
            cliente=1,
            rutina=1,
            nombre_ejercicio="Caminata",
            duracion_real=30,
            intensidad_real="MEDIA",
            calorias_quemadas=EnteroConTextoInvalido(200),
        )


def test_actualizar_sesion_rechaza_realizadas_mayores_planificadas(
    controlador,
    sesion_valida,
):
    """
    Verifica la validación propia del controlador cuando una
    sesión existente contiene más repeticiones realizadas que
    planificadas.
    """
    with patch.object(
        SesionEntrenamiento,
        "veces_planificadas",
        new_callable=PropertyMock,
        return_value=1,
    ), patch.object(
        SesionEntrenamiento,
        "veces_realizadas",
        new_callable=PropertyMock,
        return_value=2,
    ):
        with pytest.raises(
            ValueError,
            match="no pueden superar las planificadas",
        ):
            controlador.actualizar_sesion(sesion_valida)