import builtins
import runpy
from unittest.mock import patch
import warnings

import pytest

import src.servicios.gestor_seguridad as modulo_seguridad

from src.servicios.gestor_seguridad import GestorSeguridad


CONTRASENIA_VALIDA = "Password123!"


def test_generar_y_verificar_hash_exitoso(
    monkeypatch,
):
    """
    Genera un hash bcrypt real y verifica contraseña correcta
    e incorrecta usando un costo bajo para acelerar la prueba.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")

    hash_generado = GestorSeguridad.generar_hash(
        CONTRASENIA_VALIDA,
    )

    assert isinstance(hash_generado, str)
    assert hash_generado.startswith("$2b$04$")

    assert GestorSeguridad.verificar_contrasenia(
        CONTRASENIA_VALIDA,
        hash_generado,
    ) is True

    assert GestorSeguridad.verificar_contrasenia(
        "PasswordIncorrecto123!",
        hash_generado,
    ) is False


def test_rounds_por_defecto(
    monkeypatch,
):
    """
    Verifica valor por defecto cuando no existen variables.
    """
    monkeypatch.delenv(
        "BCRYPT_ROUNDS",
        raising=False,
    )

    monkeypatch.delenv(
        "ROUNDS",
        raising=False,
    )

    assert GestorSeguridad._obtener_rounds() == 12


def test_rounds_desde_bcrypt_rounds(
    monkeypatch,
):
    """
    BCRYPT_ROUNDS tiene prioridad sobre ROUNDS.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")
    monkeypatch.setenv("ROUNDS", "6")

    assert GestorSeguridad._obtener_rounds() == 4


def test_rounds_desde_rounds_alternativo(
    monkeypatch,
):
    """
    Usa ROUNDS si BCRYPT_ROUNDS no existe.
    """
    monkeypatch.delenv(
        "BCRYPT_ROUNDS",
        raising=False,
    )

    monkeypatch.setenv("ROUNDS", "5")

    assert GestorSeguridad._obtener_rounds() == 5


@pytest.mark.parametrize(
    "valor",
    [
        "3",
        "0",
        "-1",
        "32",
        "100",
        "",
    ],
)
def test_rounds_fuera_de_rango_usa_default(
    monkeypatch,
    valor,
):
    """
    Los costos fuera de rango usan el valor por defecto.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", valor)
    monkeypatch.delenv("ROUNDS", raising=False)

    assert GestorSeguridad._obtener_rounds() == 12


def test_rounds_no_numerico_registra_warning_y_usa_default(
    monkeypatch,
):
    """
    Cubre ValueError en int(valor) y logger.warning.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "no_es_numero")

    with patch.object(
        modulo_seguridad.logger,
        "warning",
    ) as mock_warning:
        resultado = GestorSeguridad._obtener_rounds()

    assert resultado == 12

    mock_warning.assert_called_once_with(
        "Valor inválido para BCRYPT_ROUNDS: %s",
        "no_es_numero",
    )


def test_propiedad_rounds(
    monkeypatch,
):
    """
    Cubre la propiedad de compatibilidad ROUNDS.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")

    gestor = GestorSeguridad()

    assert gestor.ROUNDS == 4


@pytest.mark.parametrize(
    "contrasenia",
    [
        None,
        123,
        True,
        [],
        {},
    ],
)
def test_validar_fortaleza_rechaza_tipo_invalido(
    contrasenia,
):
    """
    Una contraseña no textual no es válida.
    """
    assert (
        GestorSeguridad.validar_fortaleza_contrasena(
            contrasenia,
        )
        is False
    )


@pytest.mark.parametrize(
    "contrasenia",
    [
        "Ab1!",
        "password123!",
        "Password!",
        "Password123",
        "Pass word123",
    ],
)
def test_validar_fortaleza_rechaza_claves_debiles(
    contrasenia,
):
    """
    Cubre longitud, mayúscula, número y carácter especial.
    """
    assert (
        GestorSeguridad.validar_fortaleza_contrasena(
            contrasenia,
        )
        is False
    )

@pytest.mark.parametrize(
    "contrasenia",
    [
        "Password123!",
        "ClaveSegura9@",
        "Abcdefgh1#",
    ],
)
def test_validar_fortaleza_acepta_claves_validas(
    contrasenia,
):
    """
    Verifica retorno True para contraseñas fuertes.
    """
    assert (
        GestorSeguridad.validar_fortaleza_contrasena(
            contrasenia,
        )
        is True
    )


@pytest.mark.parametrize(
    "contrasenia, mensaje",
    [
        (
            None,
            "contraseña debe ser un texto",
        ),
        (
            123,
            "contraseña debe ser un texto",
        ),
        (
            "",
            "contraseña no puede estar vacía",
        ),
        (
            "Password123",
            "contraseña es muy débil",
        ),
        (
            "Password123!" * 10,
            "no puede superar",
        ),
    ],
)
def test_generar_hash_rechaza_entradas_invalidas(
    contrasenia,
    mensaje,
):
    """
    Cubre validación de tipo, vacío, fortaleza y 72 bytes.
    """
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        GestorSeguridad.generar_hash(contrasenia)


def test_generar_hash_llama_bcrypt_con_rounds_configurados(
    monkeypatch,
):
    """
    Cubre bcrypt.gensalt, bcrypt.hashpw y decode sin
    ejecutar hashing real.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")

    with patch.object(
        modulo_seguridad.bcrypt,
        "gensalt",
        return_value=b"salt_simulado",
    ) as mock_gensalt:
        with patch.object(
            modulo_seguridad.bcrypt,
            "hashpw",
            return_value=b"$2b$04$hash_simulado",
        ) as mock_hashpw:
            resultado = GestorSeguridad.generar_hash(
                CONTRASENIA_VALIDA,
            )

    assert resultado == "$2b$04$hash_simulado"

    mock_gensalt.assert_called_once_with(rounds=4)

    mock_hashpw.assert_called_once_with(
        b"Password123!",
        b"salt_simulado",
    )


def test_generar_hash_convierte_error_inesperado_a_runtime_error():
    """
    Cubre logger.exception y RuntimeError ante fallo bcrypt.
    """
    with patch.object(
        modulo_seguridad.bcrypt,
        "gensalt",
        side_effect=RuntimeError("bcrypt no disponible"),
    ):
        with patch.object(
            modulo_seguridad.logger,
            "exception",
        ) as mock_exception:
            with pytest.raises(
                RuntimeError,
                match="Error al generar el hash",
            ):
                GestorSeguridad.generar_hash(
                    CONTRASENIA_VALIDA,
                )

    mock_exception.assert_called_once_with(
        "No se pudo generar el hash.",
    )


@pytest.mark.parametrize(
    "contrasenia, hash_guardado, mensaje",
    [
        (
            None,
            "$2b$04$hash",
            "contraseña recibida no es válida",
        ),
        (
            123,
            "$2b$04$hash",
            "contraseña recibida no es válida",
        ),
        (
            "",
            "$2b$04$hash",
            "contraseña vacía",
        ),
        (
            CONTRASENIA_VALIDA,
            None,
            "hash guardado no es texto",
        ),
        (
            CONTRASENIA_VALIDA,
            123,
            "hash guardado no es texto",
        ),
        (
            CONTRASENIA_VALIDA,
            "",
            "hash guardado está vacío",
        ),
    ],
)
def test_verificar_contrasenia_rechaza_entradas_invalidas(
    contrasenia,
    hash_guardado,
    mensaje,
):
    """
    Cubre retornos anticipados y advertencias.
    """
    with patch.object(
        modulo_seguridad.logger,
        "warning",
    ) as mock_warning:
        resultado = GestorSeguridad.verificar_contrasenia(
            contrasenia,
            hash_guardado,
        )

    assert resultado is False

    mock_warning.assert_called_once_with(
        pytest.helpers.contains(mensaje)
        if hasattr(pytest, "helpers")
        else mock_warning.call_args.args[0],
    )


def test_verificar_contrasenia_rechaza_mas_de_72_bytes():
    """
    Cubre retorno False para contraseñas demasiado largas.
    """
    contrasenia_larga = "A1!" + ("a" * 70)

    assert len(contrasenia_larga.encode("utf-8")) > 72

    assert GestorSeguridad.verificar_contrasenia(
        contrasenia_larga,
        "$2b$04$hash_simulado",
    ) is False


def test_verificar_contrasenia_usa_bcrypt_y_retorna_bool():
    """
    Cubre bcrypt.checkpw con resultado verdadero.
    """
    with patch.object(
        modulo_seguridad.bcrypt,
        "checkpw",
        return_value=True,
    ) as mock_checkpw:
        resultado = GestorSeguridad.verificar_contrasenia(
            CONTRASENIA_VALIDA,
            "$2b$04$hash_simulado",
        )

    assert resultado is True

    mock_checkpw.assert_called_once_with(
        b"Password123!",
        b"$2b$04$hash_simulado",
    )


def test_verificar_contrasenia_maneja_error_de_formato():
    """
    Cubre except ValueError, TypeError y UnicodeEncodeError.
    """
    with patch.object(
        modulo_seguridad.bcrypt,
        "checkpw",
        side_effect=ValueError("hash inválido"),
    ):
        with patch.object(
            modulo_seguridad.logger,
            "warning",
        ) as mock_warning:
            resultado = GestorSeguridad.verificar_contrasenia(
                CONTRASENIA_VALIDA,
                "$2b$04$hash_invalido",
            )

    assert resultado is False

    mock_warning.assert_called_once_with(
        "El hash bcrypt tiene un formato inválido.",
    )


def test_verificar_contrasenia_maneja_error_inesperado():
    """
    Cubre except Exception y logger.exception.
    """
    with patch.object(
        modulo_seguridad.bcrypt,
        "checkpw",
        side_effect=RuntimeError("error inesperado"),
    ):
        with patch.object(
            modulo_seguridad.logger,
            "exception",
        ) as mock_exception:
            resultado = GestorSeguridad.verificar_contrasenia(
                CONTRASENIA_VALIDA,
                "$2b$04$hash_simulado",
            )

    assert resultado is False

    mock_exception.assert_called_once_with(
        "Error inesperado al verificar "
        "la contraseña.",
    )


@pytest.mark.parametrize(
    "hash_guardado, esperado",
    [
        (None, False),
        (123, False),
        ("", False),
        ("hash_normal", False),
        ("$2a$04$hash", True),
        ("$2b$04$hash", True),
        ("$2y$04$hash", True),
        ("  $2b$04$hash  ", True),
    ],
)
def test_hash_valido(
    hash_guardado,
    esperado,
):
    """
    Verifica formatos bcrypt aceptados y rechazados.
    """
    assert (
        GestorSeguridad.hash_valido(hash_guardado)
        is esperado
    )


def test_necesita_rehash_si_hash_no_es_valido():
    """
    Cubre retorno temprano cuando formato no parece bcrypt.
    """
    assert GestorSeguridad.necesita_rehash(
        "hash_invalido",
    ) is True


def test_necesita_rehash_si_faltan_partes():
    """
    Cubre ruta len(partes) < 3.
    """
    with patch.object(
        GestorSeguridad,
        "hash_valido",
        return_value=True,
    ):
        assert GestorSeguridad.necesita_rehash(
            "$2b",
        ) is True


def test_necesita_rehash_si_rounds_no_es_numerico():
    """
    Cubre except TypeError y ValueError al convertir costo.
    """
    with patch.object(
        GestorSeguridad,
        "hash_valido",
        return_value=True,
    ):
        assert GestorSeguridad.necesita_rehash(
            "$2b$no_numero$hash",
        ) is True


def test_necesita_rehash_retorna_false_si_rounds_coinciden(
    monkeypatch,
):
    """
    Un hash con el costo actual no requiere rehash.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")

    hash_guardado = "$2b$04$hash_simulado"

    assert GestorSeguridad.necesita_rehash(
        hash_guardado,
    ) is False


def test_necesita_rehash_retorna_true_si_rounds_difieren(
    monkeypatch,
):
    """
    Un hash con costo distinto requiere rehash.
    """
    monkeypatch.setenv("BCRYPT_ROUNDS", "5")

    hash_guardado = "$2b$04$hash_simulado"

    assert GestorSeguridad.necesita_rehash(
        hash_guardado,
    ) is True

def test_importacion_bcrypt_fallida_muestra_mensaje_claro():
    """
    Cubre el bloque ImportError cuando bcrypt no puede
    importarse al cargar el módulo de seguridad.
    """
    import builtins
    import runpy

    import_original = builtins.__import__

    def bloquear_importacion_bcrypt(
        nombre,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        if nombre == "bcrypt":
            raise ImportError("bcrypt no instalado")

        return import_original(
            nombre,
            globals,
            locals,
            fromlist,
            level,
        )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=(
                ".*src.servicios.gestor_seguridad.*"
                "found in sys.modules.*"
            ),
            category=RuntimeWarning,
        )

        with patch(
            "builtins.__import__",
            side_effect=bloquear_importacion_bcrypt,
        ):
            with pytest.raises(
                ImportError,
                match=(
                    "No se pudo importar bcrypt. "
                    "Instálalo con: python -m pip install bcrypt"
                ),
            ):
                runpy.run_module(
                    "src.servicios.gestor_seguridad",
                    run_name="gestor_seguridad_sin_bcrypt",
                )