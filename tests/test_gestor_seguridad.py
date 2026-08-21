import pytest

from src.servicios.gestor_seguridad import GestorSeguridad


def test_generar_hash_no_devuelve_la_contrasenia():
    contrasenia = "ClaveSegura123"

    hash_generado = GestorSeguridad.generar_hash(
        contrasenia
    )

    assert hash_generado != contrasenia
    assert hash_generado.startswith("$2")


def test_generar_hash_verifica_contrasenia_correcta():
    contrasenia = "ClaveSegura123"

    hash_generado = GestorSeguridad.generar_hash(
        contrasenia
    )

    resultado = GestorSeguridad.verificar_contrasenia(
        contrasenia,
        hash_generado,
    )

    assert resultado is True


def test_verificar_contrasenia_incorrecta():
    hash_generado = GestorSeguridad.generar_hash(
        "ClaveSegura123"
    )

    resultado = GestorSeguridad.verificar_contrasenia(
        "ClaveIncorrecta",
        hash_generado,
    )

    assert resultado is False


def test_generar_hash_rechaza_none():
    with pytest.raises(ValueError):
        GestorSeguridad.generar_hash(None)


def test_generar_hash_rechaza_cadena_vacia():
    with pytest.raises(ValueError):
        GestorSeguridad.generar_hash("")


def test_generar_hash_rechaza_espacios():
    with pytest.raises(ValueError):
        GestorSeguridad.generar_hash("   ")


def test_verificar_rechaza_contrasenia_none():
    hash_generado = GestorSeguridad.generar_hash(
        "ClaveSegura123"
    )

    resultado = GestorSeguridad.verificar_contrasenia(
        None,
        hash_generado,
    )

    assert resultado is False


def test_verificar_rechaza_contrasenia_vacia():
    hash_generado = GestorSeguridad.generar_hash(
        "ClaveSegura123"
    )

    resultado = GestorSeguridad.verificar_contrasenia(
        "",
        hash_generado,
    )

    assert resultado is False


def test_verificar_rechaza_hash_none():
    resultado = GestorSeguridad.verificar_contrasenia(
        "ClaveSegura123",
        None,
    )

    assert resultado is False


def test_verificar_rechaza_hash_vacio():
    resultado = GestorSeguridad.verificar_contrasenia(
        "ClaveSegura123",
        "",
    )

    assert resultado is False


def test_hashes_diferentes_para_misma_contrasenia():
    hash_uno = GestorSeguridad.generar_hash(
        "ClaveSegura123"
    )
    hash_dos = GestorSeguridad.generar_hash(
        "ClaveSegura123"
    )

    assert hash_uno != hash_dos

    assert GestorSeguridad.verificar_contrasenia(
        "ClaveSegura123",
        hash_uno,
    ) is True

    assert GestorSeguridad.verificar_contrasenia(
        "ClaveSegura123",
        hash_dos,
    ) is True