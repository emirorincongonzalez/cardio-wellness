from unittest.mock import MagicMock, patch

import psycopg2
import pytest

import src.persistencia.conexion_bd as modulo_conexion

from src.persistencia.conexion_bd import ConexionBD


@pytest.fixture(autouse=True)
def reiniciar_singleton(monkeypatch):
    """
    Reinicia el estado compartido de ConexionBD.

    ConexionBD implementa Singleton, por lo que es necesario
    limpiar la instancia entre pruebas.

    También se desactiva load_dotenv para que las pruebas
    controlen por completo las variables de entorno mediante
    monkeypatch y no dependan del archivo .env local.
    """
    ConexionBD._instancia = None
    ConexionBD._conexion = None

    monkeypatch.setattr(
        modulo_conexion,
        "load_dotenv",
        lambda: None,
    )

    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "cardio_test")
    monkeypatch.setenv("DB_USER", "usuario_test")
    monkeypatch.setenv("DB_PASSWORD", "clave_test")

    yield

    ConexionBD._instancia = None
    ConexionBD._conexion = None

def crear_cursor(
    descripcion=None,
    filas=None,
    rowcount=1,
):
    """
    Crea un cursor simulado compatible con context manager.
    """
    cursor = MagicMock()
    cursor.description = descripcion
    cursor.fetchall.return_value = filas or []
    cursor.rowcount = rowcount
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = False

    return cursor


def crear_conexion(
    closed=False,
    cursor=None,
):
    """
    Crea una conexión simulada compatible con la clase.
    """
    conexion = MagicMock()
    conexion.closed = closed

    if cursor is None:
        cursor = crear_cursor()

    conexion.cursor.return_value = cursor

    return conexion


def test_singleton_retorna_misma_instancia():
    """
    Cubre __new__ y confirma el patrón Singleton.
    """
    conexion_1 = ConexionBD()
    conexion_2 = ConexionBD()

    assert conexion_1 is conexion_2


def test_obtener_instancia_retorna_singleton():
    """
    Cubre obtener_instancia.
    """
    conexion = ConexionBD.obtener_instancia()

    assert isinstance(conexion, ConexionBD)
    assert conexion is ConexionBD()


def test_constructor_carga_configuracion():
    """
    Verifica valores obtenidos desde las variables de entorno.
    """
    conexion = ConexionBD()

    assert conexion._config == {
        "host": "localhost",
        "port": "5432",
        "dbname": "cardio_test",
        "user": "usuario_test",
        "password": "clave_test",
    }


def test_constructor_usa_host_y_puerto_por_defecto(
    monkeypatch,
):
    """
    Cubre defaults de DB_HOST y DB_PORT.
    """
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)

    conexion = ConexionBD()

    assert conexion._config["host"] == "localhost"
    assert conexion._config["port"] == "5432"


@pytest.mark.parametrize(
    "variable_faltante",
    [
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ],
)
def test_constructor_rechaza_configuracion_incompleta(
    monkeypatch,
    variable_faltante,
):
    """
    Cubre _validar_configuracion cuando falta una variable.
    """
    monkeypatch.delenv(
        variable_faltante,
        raising=False,
    )

    with pytest.raises(
        EnvironmentError,
        match="Faltan variables de entorno",
    ) as error:
        ConexionBD()

    assert variable_faltante.replace(
        "DB_",
        "",
    ).lower() in str(error.value).lower()


def test_validar_configuracion_reporta_varias_faltantes(
    monkeypatch,
):
    """
    Verifica que se informen todas las variables requeridas.
    """
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    with pytest.raises(
        EnvironmentError,
        match="dbname, user, password",
    ):
        ConexionBD()


def test_abrir_conexion_establece_conexion_y_timezone(
    capsys,
):
    """
    Cubre conexión nueva, cursor de timezone y print exitoso.
    """
    cursor = crear_cursor()
    conexion_mock = crear_conexion(cursor=cursor)

    with patch.object(
        modulo_conexion.psycopg2,
        "connect",
        return_value=conexion_mock,
    ) as mock_connect:
        conexion = ConexionBD()
        conexion.abrir_conexion()

    mock_connect.assert_called_once_with(**conexion._config)

    cursor.execute.assert_called_once_with(
        "SET TIME ZONE 'UTC'",
    )

    assert conexion._conexion is conexion_mock

    salida = capsys.readouterr().out

    assert (
        "Conexión a la base de datos establecida."
        in salida
    )


def test_abrir_conexion_no_reconecta_si_esta_activa():
    """
    Cubre retorno temprano cuando la conexión ya está abierta.
    """
    conexion = ConexionBD()
    conexion._conexion = crear_conexion(closed=False)

    with patch.object(
        modulo_conexion.psycopg2,
        "connect",
    ) as mock_connect:
        conexion.abrir_conexion()

    mock_connect.assert_not_called()


def test_abrir_conexion_reemplaza_conexion_cerrada():
    """
    Una conexión cerrada debe abrirse nuevamente.
    """
    cursor = crear_cursor()
    conexion_nueva = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = crear_conexion(closed=True)

    with patch.object(
        modulo_conexion.psycopg2,
        "connect",
        return_value=conexion_nueva,
    ) as mock_connect:
        conexion.abrir_conexion()

    mock_connect.assert_called_once_with(**conexion._config)
    assert conexion._conexion is conexion_nueva


def test_abrir_conexion_convierte_operational_error():
    """
    Cubre OperationalError convertido a RuntimeError.
    """
    conexion = ConexionBD()

    with patch.object(
        modulo_conexion.psycopg2,
        "connect",
        side_effect=psycopg2.OperationalError(
            "servidor no disponible",
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="Error al conectar a la base de datos",
        ) as error:
            conexion.abrir_conexion()

    assert "servidor no disponible" in str(error.value)


def test_cerrar_conexion_cierra_conexion_activa(
    capsys,
):
    """
    Cubre cierre exitoso y limpieza de _conexion.
    """
    conexion = ConexionBD()
    conexion_mock = crear_conexion(closed=False)

    conexion._conexion = conexion_mock

    conexion.cerrar_conexion()

    conexion_mock.close.assert_called_once()
    assert conexion._conexion is None

    salida = capsys.readouterr().out

    assert (
        "Conexión a la base de datos cerrada."
        in salida
    )


@pytest.mark.parametrize(
    "conexion_actual",
    [
        None,
        "cerrada",
    ],
)
def test_cerrar_conexion_no_hace_nada_sin_activa(
    conexion_actual,
):
    """
    Cubre ramas sin conexión o con conexión cerrada.
    """
    conexion = ConexionBD()

    if conexion_actual == "cerrada":
        conexion._conexion = crear_conexion(closed=True)
    else:
        conexion._conexion = None

    conexion.cerrar_conexion()

    if conexion_actual == "cerrada":
        conexion._conexion.close.assert_not_called()


def test_obtener_cursor_abre_conexion_si_no_existe():
    """
    Cubre _obtener_cursor con conexión None.
    """
    cursor = crear_cursor()
    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = None

    with patch.object(
        conexion,
        "abrir_conexion",
    ) as mock_abrir:
        mock_abrir.side_effect = lambda: setattr(
            conexion,
            "_conexion",
            conexion_mock,
        )

        resultado = conexion._obtener_cursor()

    mock_abrir.assert_called_once()
    assert resultado is cursor


def test_obtener_cursor_abre_conexion_si_esta_cerrada():
    """
    Cubre _obtener_cursor con conexión cerrada.
    """
    cursor = crear_cursor()
    conexion_nueva = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = crear_conexion(closed=True)

    with patch.object(
        conexion,
        "abrir_conexion",
    ) as mock_abrir:
        mock_abrir.side_effect = lambda: setattr(
            conexion,
            "_conexion",
            conexion_nueva,
        )

        resultado = conexion._obtener_cursor()

    mock_abrir.assert_called_once()
    assert resultado is cursor


def test_obtener_cursor_reutiliza_conexion_activa():
    """
    Cubre _obtener_cursor sin necesidad de abrir conexión.
    """
    cursor = crear_cursor()
    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    with patch.object(
        conexion,
        "abrir_conexion",
    ) as mock_abrir:
        resultado = conexion._obtener_cursor()

    mock_abrir.assert_not_called()
    assert resultado is cursor


def test_ejecutar_consulta_sin_filas_retorna_lista_vacia():
    """
    Cubre consulta sin description, commit y retorno [].
    """
    cursor = crear_cursor(descripcion=None)
    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    resultado = conexion.ejecutar_consulta(
        "UPDATE clientes SET activo = TRUE",
    )

    assert resultado == []

    cursor.execute.assert_called_once_with(
        "UPDATE clientes SET activo = TRUE",
        (),
    )

    conexion_mock.commit.assert_called_once()


def test_ejecutar_consulta_convierte_filas_en_diccionarios():
    """
    Cubre description, fetchall, zip y creación de dict.
    """
    descripcion = [
        ("id_usuario",),
        ("nombre",),
        ("edad",),
    ]

    filas = [
        (1, "Laura", 30),
        (2, "Carlos", 35),
    ]

    cursor = crear_cursor(
        descripcion=descripcion,
        filas=filas,
    )

    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    resultado = conexion.ejecutar_consulta(
        "SELECT id_usuario, nombre, edad FROM usuarios "
        "WHERE edad > %s",
        (18,),
    )

    assert resultado == [
        {
            "id_usuario": 1,
            "nombre": "Laura",
            "edad": 30,
        },
        {
            "id_usuario": 2,
            "nombre": "Carlos",
            "edad": 35,
        },
    ]

    cursor.execute.assert_called_once_with(
        "SELECT id_usuario, nombre, edad FROM usuarios "
        "WHERE edad > %s",
        (18,),
    )

    cursor.fetchall.assert_called_once()
    conexion_mock.commit.assert_called_once()


def test_ejecutar_consulta_hace_rollback_ante_integrity_error():
    """
    Cubre except IntegrityError, rollback y re-raise.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = psycopg2.IntegrityError(
        "clave duplicada",
    )

    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    with pytest.raises(psycopg2.IntegrityError):
        conexion.ejecutar_consulta(
            "INSERT INTO usuarios VALUES (%s)",
            (1,),
        )

    conexion_mock.rollback.assert_called_once()


def test_ejecutar_consulta_convierte_error_psycopg_a_runtime_error():
    """
    Cubre except psycopg2.Error.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = psycopg2.ProgrammingError(
        "consulta inválida",
    )

    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    with pytest.raises(
        RuntimeError,
        match="Error al ejecutar la consulta",
    ) as error:
        conexion.ejecutar_consulta("SELECT ERROR")

    assert "consulta inválida" in str(error.value)
    conexion_mock.rollback.assert_called_once()


@pytest.mark.parametrize(
    "rowcount, esperado",
    [
        (1, True),
        (3, True),
        (0, False),
        (-1, False),
    ],
)
def test_ejecutar_actualizacion_retorna_segun_rowcount(
    rowcount,
    esperado,
):
    """
    Cubre resultado True y False según filas afectadas.
    """
    cursor = crear_cursor(rowcount=rowcount)
    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    resultado = conexion.ejecutar_actualizacion(
        "DELETE FROM ejercicios WHERE id_ejercicio = %s",
        (5,),
    )

    assert resultado is esperado

    cursor.execute.assert_called_once_with(
        "DELETE FROM ejercicios WHERE id_ejercicio = %s",
        (5,),
    )

    conexion_mock.commit.assert_called_once()


def test_ejecutar_actualizacion_convierte_error_a_runtime_error():
    """
    Cubre rollback y RuntimeError en actualización.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = psycopg2.DatabaseError(
        "fallo de actualización",
    )

    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    with pytest.raises(
        RuntimeError,
        match="Error al ejecutar la actualizacion",
    ) as error:
        conexion.ejecutar_actualizacion(
            "UPDATE clientes SET nombre = %s",
            ("Laura",),
        )

    assert "fallo de actualización" in str(error.value)
    conexion_mock.rollback.assert_called_once()


def test_context_manager_abre_y_cierra_conexion():
    """
    Cubre __enter__ y __exit__.
    """
    conexion = ConexionBD()

    with patch.object(
        conexion,
        "abrir_conexion",
    ) as mock_abrir:
        with patch.object(
            conexion,
            "cerrar_conexion",
        ) as mock_cerrar:
            with conexion as resultado:
                assert resultado is conexion

    mock_abrir.assert_called_once()
    mock_cerrar.assert_called_once()


def test_verificar_integridad_retorna_false_sin_conexion():
    """
    Cubre retorno False cuando no hay conexión.
    """
    conexion = ConexionBD()
    conexion._conexion = None

    assert conexion.verificar_integridad() is False


def test_verificar_integridad_retorna_false_con_conexion_cerrada():
    """
    Cubre retorno False con conexión cerrada.
    """
    conexion = ConexionBD()
    conexion._conexion = crear_conexion(closed=True)

    assert conexion.verificar_integridad() is False


def test_verificar_integridad_retorna_true_con_conexion_valida():
    """
    Cubre consulta SELECT 1 y retorno True.
    """
    cursor = crear_cursor()
    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    assert conexion.verificar_integridad() is True

    cursor.execute.assert_called_once_with("SELECT 1")
    cursor.fetchone.assert_called_once()


def test_verificar_integridad_retorna_false_ante_excepcion():
    """
    Cubre except Exception de verificar_integridad.
    """
    cursor = crear_cursor()
    cursor.execute.side_effect = RuntimeError(
        "conexión interrumpida",
    )

    conexion_mock = crear_conexion(cursor=cursor)

    conexion = ConexionBD()
    conexion._conexion = conexion_mock

    assert conexion.verificar_integridad() is False


def test_obtener_configuracion_oculta_password():
    """
    Verifica configuración pública sin contraseña.
    """
    conexion = ConexionBD()

    resultado = conexion.obtener_configuracion()

    assert resultado == {
        "host": "localhost",
        "port": "5432",
        "dbname": "cardio_test",
        "user": "usuario_test",
    }

    assert "password" not in resultado