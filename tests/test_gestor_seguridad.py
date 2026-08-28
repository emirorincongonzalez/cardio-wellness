import pytest

from src.servicios.gestor_seguridad import GestorSeguridad


def test_generar_y_verificar_hash_exitoso():
    contrasenia = "MiClaveSuperSegura123!"
    hash_generado = GestorSeguridad.generar_hash(contrasenia)

    assert isinstance(hash_generado, str)
    assert hash_generado.startswith("$2b$")
    assert GestorSeguridad.verificar_contrasenia(contrasenia, hash_generado) is True
    assert GestorSeguridad.verificar_contrasenia("ClaveIncorrecta", hash_generado) is False


def test_rounds_por_defecto(monkeypatch):
    monkeypatch.delenv("BCRYPT_ROUNDS", raising=False)
    monkeypatch.delenv("ROUNDS", raising=False)

    assert GestorSeguridad._obtener_rounds() == 12


def test_rounds_desde_variable_entorno_bcrypt_rounds(monkeypatch):
    # Usamos 4 para que sea rápido en pruebas
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")

    assert GestorSeguridad._obtener_rounds() == 4
    hash_generado = GestorSeguridad.generar_hash("Password123")
    assert hash_generado.startswith("$2b$04$")


def test_rounds_desde_variable_entorno_rounds(monkeypatch):
    monkeypatch.delenv("BCRYPT_ROUNDS", raising=False)
    monkeypatch.setenv("ROUNDS", "5")

    assert GestorSeguridad._obtener_rounds() == 5
    hash_generado = GestorSeguridad.generar_hash("Password123")
    assert hash_generado.startswith("$2b$05$")


@pytest.mark.parametrize("valor_invalido", ["no_numero", "-1", "0", "3", "32", ""])
def test_rounds_fallback_ante_valores_invalidos(monkeypatch, valor_invalido):
    monkeypatch.setenv("BCRYPT_ROUNDS", valor_invalido)
    assert GestorSeguridad._obtener_rounds() == 12


@pytest.mark.parametrize("clave_invalida", ["", "   ", None, 12345, []])
def test_generar_hash_rechaza_entradas_invalidas(clave_invalida):
    with pytest.raises(ValueError):
        GestorSeguridad.generar_hash(clave_invalida)


@pytest.mark.parametrize(
    "clave, hash_guardado",
    [
        ("", "$2b$12$eIn071M4Xdgs8P93mnMYGu..."),
        ("   ", "$2b$12$eIn071M4Xdgs8P93mnMYGu..."),
        (None, "$2b$12$eIn071M4Xdgs8P93mnMYGu..."),
        (1234, "$2b$12$eIn071M4Xdgs8P93mnMYGu..."),
        ("Valida123", ""),
        ("Valida123", "   "),
        ("Valida123", None),
        ("Valida123", 12345),
        ("Valida123", "formato_invalido_de_hash"),
    ],
)
def test_verificar_contrasenia_entradas_invalidas(clave, hash_guardado):
    assert GestorSeguridad.verificar_contrasenia(clave, hash_guardado) is False