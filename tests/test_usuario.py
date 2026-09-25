from datetime import date
from unittest.mock import patch

import pytest

from src.modelos.usuario import Usuario


class UsuarioPrueba(Usuario):
    """
    Implementación mínima de Usuario para pruebas.
    """

    def obtener_tipo_usuario(self) -> str:
        return self.tipo_usuario


@pytest.fixture
def usuario():
    return UsuarioPrueba(
        id_usuario=10,
        nombre="  Laura  ",
        apellido="  Gómez  ",
        correo_electronico="  laura@email.com  ",
        contrasenia_hash="hash_original",
        edad=30,
        tipo_usuario="CLIENTE",
        fecha_registro=date(2026, 1, 15),
    )


def test_usuario_se_inicializa_correctamente(
    usuario,
):
    """
    Verifica valores iniciales y limpieza de texto.
    """
    assert usuario.id_usuario == 10
    assert usuario.nombre == "Laura"
    assert usuario.apellido == "Gómez"
    assert usuario.correo_electronico == "laura@email.com"
    assert usuario.contrasenia_hash == "hash_original"
    assert usuario.edad == 30
    assert usuario.tipo_usuario == "cliente"
    assert usuario.fecha_registro == date(2026, 1, 15)


def test_usuario_asigna_fecha_actual_si_no_recibe_fecha():
    """
    Verifica la fecha automática cuando fecha_registro es None.
    """
    usuario = UsuarioPrueba(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@email.com",
        contrasenia_hash="hash_carlos",
        edad=40,
    )

    assert usuario.fecha_registro == date.today()


def test_propiedades_usuario(
    usuario,
):
    """
    Cubre los getters de las propiedades del usuario.
    """
    assert usuario.id_usuario == 10
    assert usuario.nombre == "Laura"
    assert usuario.apellido == "Gómez"
    assert usuario.correo_electronico == "laura@email.com"
    assert usuario.contrasenia_hash == "hash_original"
    assert usuario.edad == 30
    assert usuario.tipo_usuario == "cliente"
    assert usuario.fecha_registro == date(2026, 1, 15)


def test_usuario_permite_actualizar_id_y_fecha(
    usuario,
):
    """
    Verifica setters sin validación adicional.
    """
    nueva_fecha = date(2026, 6, 20)

    usuario.id_usuario = 25
    usuario.fecha_registro = nueva_fecha

    assert usuario.id_usuario == 25
    assert usuario.fecha_registro == nueva_fecha


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        10,
        True,
        [],
    ],
)
def test_nombre_rechaza_valores_invalidos(
    usuario,
    valor,
):
    with pytest.raises(
        ValueError,
        match="nombre no puede estar vacío",
    ):
        usuario.nombre = valor


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        10,
        True,
        [],
    ],
)
def test_apellido_rechaza_valores_invalidos(
    usuario,
    valor,
):
    with pytest.raises(
        ValueError,
        match="apellido no puede estar vacío",
    ):
        usuario.apellido = valor


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        10,
        True,
        [],
    ],
)
def test_correo_rechaza_valores_invalidos(
    usuario,
    valor,
):
    with pytest.raises(
        ValueError,
        match="correo electrónico no puede estar vacío",
    ):
        usuario.correo_electronico = valor


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        10,
        True,
        [],
    ],
)
def test_contrasenia_hash_rechaza_valores_invalidos(
    usuario,
    valor,
):
    with pytest.raises(
        ValueError,
        match="hash de la contraseña no puede estar vacío",
    ):
        usuario.contrasenia_hash = valor


@pytest.mark.parametrize(
    "valor",
    [
        None,
        True,
        False,
        0,
        -1,
        -10,
        20.5,
        "30",
    ],
)
def test_edad_rechaza_valores_invalidos(
    usuario,
    valor,
):
    with pytest.raises(
        ValueError,
        match="edad debe ser un entero",
    ):
        usuario.edad = valor


@pytest.mark.parametrize(
    "valor",
    [
        None,
        "",
        "   ",
        10,
        True,
        [],
    ],
)
def test_tipo_usuario_rechaza_valores_invalidos(
    usuario,
    valor,
):
    with pytest.raises(
        ValueError,
        match="tipo de usuario no puede estar vacío",
    ):
        usuario.tipo_usuario = valor


def test_tipo_usuario_se_normaliza_a_minusculas(
    usuario,
):
    usuario.tipo_usuario = "  ADMINISTRADOR  "

    assert usuario.tipo_usuario == "administrador"


def test_actualizar_datos_personales(
    usuario,
):
    """
    Cubre la actualización coordinada de los datos.
    """
    usuario.actualizar_datos_personales(
        nombre="  Ana  ",
        apellido="  Ruiz  ",
        correo="  ana.ruiz@email.com  ",
        edad=26,
    )

    assert usuario.nombre == "Ana"
    assert usuario.apellido == "Ruiz"
    assert usuario.correo_electronico == "ana.ruiz@email.com"
    assert usuario.edad == 26


def test_cambiar_contrasenia_rechaza_nueva_contrasenia_vacia(
    usuario,
):
    """
    Verifica la validación antes de consultar el gestor.
    """
    for nueva_contrasenia in (
        None,
        "",
        123,
        [],
    ):
        with pytest.raises(
            ValueError,
            match="nueva contraseña no puede estar vacía",
        ):
            usuario.cambiar_contrasenia(
                "clave_actual",
                nueva_contrasenia,
            )


def test_cambiar_contrasenia_retorna_false_si_actual_incorrecta(
    usuario,
):
    """
    Verifica que no se genere un hash si la clave actual falla.
    """
    with patch(
        "src.modelos.usuario.GestorSeguridad."
        "verificar_contrasenia",
        return_value=False,
    ) as mock_verificar:
        with patch(
            "src.modelos.usuario.GestorSeguridad."
            "generar_hash",
        ) as mock_generar_hash:
            resultado = usuario.cambiar_contrasenia(
                "clave_incorrecta",
                "clave_nueva",
            )

    assert resultado is False
    assert usuario.contrasenia_hash == "hash_original"

    mock_verificar.assert_called_once_with(
        "clave_incorrecta",
        "hash_original",
    )

    mock_generar_hash.assert_not_called()


def test_cambiar_contrasenia_actualiza_hash_si_actual_correcta(
    usuario,
):
    """
    Cubre la ruta exitosa: verificar, generar hash y retornar True.
    """
    with patch(
        "src.modelos.usuario.GestorSeguridad."
        "verificar_contrasenia",
        return_value=True,
    ) as mock_verificar:
        with patch(
            "src.modelos.usuario.GestorSeguridad."
            "generar_hash",
            return_value="hash_nuevo_seguro",
        ) as mock_generar_hash:
            resultado = usuario.cambiar_contrasenia(
                "clave_actual",
                "clave_nueva_segura",
            )

    assert resultado is True
    assert usuario.contrasenia_hash == "hash_nuevo_seguro"

    mock_verificar.assert_called_once_with(
        "clave_actual",
        "hash_original",
    )

    mock_generar_hash.assert_called_once_with(
        "clave_nueva_segura",
    )


def test_obtener_nombre_completo(
    usuario,
):
    """
    Verifica la composición del nombre completo.
    """
    assert usuario.obtener_nombre_completo() == "Laura Gómez"


def test_obtener_tipo_usuario_subclase(
    usuario,
):
    """
    Verifica la implementación concreta usada para pruebas.
    """
    assert usuario.obtener_tipo_usuario() == "cliente"


def test_metodo_abstracto_base_retorna_none(
    usuario,
):
    """
    Ejecuta el cuerpo abstracto original de Usuario,
    cuyo contenido es pass.
    """
    resultado = Usuario.obtener_tipo_usuario(usuario)

    assert resultado is None


def test_repr_usuario(
    usuario,
):
    """
    Verifica la representación textual del usuario.
    """
    representacion = repr(usuario)

    assert representacion == (
        "UsuarioPrueba("
        "id_usuario=10, "
        "nombre='Laura', "
        "correo='laura@email.com', "
        "tipo='cliente'"
        ")"
    )