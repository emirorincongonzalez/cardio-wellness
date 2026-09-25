from datetime import date

from src.modelos.administrador import Administrador


def crear_administrador():
    return Administrador(
        id_usuario=15,
        nombre="Laura",
        apellido="Gómez",
        correo_electronico="laura.gomez@cardio.com",
        contrasenia_hash="hash_seguro_123",
        edad=32,
        fecha_registro=date(2026, 1, 15),
    )


def test_administrador_obtener_tipo_usuario():
    """
    Verifica que Administrador fuerce correctamente
    el tipo de usuario esperado.
    """
    administrador = crear_administrador()

    assert administrador.obtener_tipo_usuario() == "administrador"


def test_administrador_repr():
    """
    Verifica la representación de texto del administrador.
    """
    administrador = crear_administrador()

    representacion = repr(administrador)

    assert representacion == (
        "Administrador("
        "id_usuario=15, "
        "nombre='Laura', "
        "correo='laura.gomez@cardio.com'"
        ")"
    )


def test_administrador_hereda_datos_de_usuario():
    """
    Verifica que el constructor conserve los datos
    enviados a la clase Usuario.
    """
    fecha_registro = date(2026, 5, 20)

    administrador = Administrador(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos.perez@cardio.com",
        contrasenia_hash="hash_carlos",
        edad=40,
        id_usuario=8,
        fecha_registro=fecha_registro,
    )

    assert administrador.id_usuario == 8
    assert administrador.nombre == "Carlos"
    assert administrador.apellido == "Pérez"
    assert (
        administrador.correo_electronico
        == "carlos.perez@cardio.com"
    )
    assert administrador.edad == 40
    assert administrador.fecha_registro == fecha_registro
    assert administrador.tipo_usuario == "administrador"


def test_administrador_permite_id_y_fecha_none():
    """
    Verifica el uso de valores opcionales del constructor.
    """
    administrador = Administrador(
        nombre="Ana",
        apellido="Ruiz",
        correo_electronico="ana.ruiz@cardio.com",
        contrasenia_hash="hash_ana",
        edad=28,
    )

    assert administrador.id_usuario is None
    assert administrador.obtener_tipo_usuario() == "administrador"