import pytest

from src.modelos.cliente import Cliente
from src.persistencia.usuario_dao import UsuarioDAO
from src.servicios.gestor_seguridad import GestorSeguridad


def crear_usuario(correo):
    return Cliente(
        nombre="Miguel",
        apellido="Rodriguez",
        correo_electronico=correo,
        contrasenia_hash="ClaveInicial123",
        edad=40,
        peso=80.0,
        altura=1.78,
        objetivo="Mantener salud",
    )


def eliminar_usuario_seguro(dao, usuario):
    if usuario is not None and usuario.id_usuario is not None:
        dao.eliminar_por_id(usuario.id_usuario)


def test_usuario_dao_actualizar():
    dao = UsuarioDAO()
    correo = "usuario.actualizar@example.com"
    usuario_guardado = None

    try:
        usuario_guardado = dao.guardar(
            crear_usuario(correo)
        )

        usuario_guardado.nombre = "Miguel Actualizado"
        usuario_guardado.apellido = "Rodriguez Nuevo"
        usuario_guardado.edad = 45

        usuario_actualizado = dao.actualizar(
            usuario_guardado
        )

        assert usuario_actualizado is not None
        assert usuario_actualizado.id_usuario == (
            usuario_guardado.id_usuario
        )

        usuario_encontrado = dao.buscar_por_correo(correo)

        assert usuario_encontrado is not None
        assert usuario_encontrado.id_usuario == (
            usuario_guardado.id_usuario
        )
        assert usuario_encontrado.nombre == "Miguel Actualizado"
        assert usuario_encontrado.apellido == "Rodriguez Nuevo"
        assert usuario_encontrado.edad == 45

    finally:
        eliminar_usuario_seguro(dao, usuario_guardado)


def test_usuario_dao_actualizar_correo():
    dao = UsuarioDAO()
    correo_original = "usuario.correo.original@example.com"
    correo_nuevo = "usuario.correo.nuevo@example.com"
    usuario_guardado = None

    try:
        usuario_guardado = dao.guardar(
            crear_usuario(correo_original)
        )

        usuario_guardado.correo_electronico = correo_nuevo

        dao.actualizar(usuario_guardado)

        usuario_nuevo = dao.buscar_por_correo(correo_nuevo)
        usuario_original = dao.buscar_por_correo(correo_original)

        assert usuario_nuevo is not None
        assert usuario_nuevo.id_usuario == (
            usuario_guardado.id_usuario
        )
        assert usuario_original is None

    finally:
        eliminar_usuario_seguro(dao, usuario_guardado)


def test_usuario_dao_actualizar_preserva_hash():
    dao = UsuarioDAO()
    correo = "usuario.preservar.hash@example.com"
    usuario_guardado = None

    try:
        usuario_guardado = dao.guardar(
            crear_usuario(correo)
        )

        usuario_encontrado = dao.buscar_por_correo(correo)

        assert usuario_encontrado is not None
        hash_original = usuario_encontrado.contrasenia_hash

        usuario_encontrado.nombre = "Nombre Modificado"

        dao.actualizar(usuario_encontrado)

        usuario_actualizado = dao.buscar_por_correo(correo)

        assert usuario_actualizado is not None
        assert usuario_actualizado.nombre == "Nombre Modificado"
        assert usuario_actualizado.contrasenia_hash == hash_original

        assert GestorSeguridad.verificar_contrasenia(
            "ClaveInicial123",
            usuario_actualizado.contrasenia_hash,
        ) is True

    finally:
        eliminar_usuario_seguro(dao, usuario_guardado)


def test_usuario_dao_actualizar_sin_id():
    dao = UsuarioDAO()

    usuario = crear_usuario(
        "usuario.sin.id@example.com"
    )

    with pytest.raises(
        ValueError,
        match="debe tener un id",
    ):
        dao.actualizar(usuario)


def test_usuario_dao_actualizar_usuario_inexistente():
    dao = UsuarioDAO()

    usuario = crear_usuario(
        "usuario.inexistente@example.com"
    )

    usuario.id_usuario = 999999999

    with pytest.raises(
        ValueError,
        match="No se encontró el usuario",
    ):
        dao.actualizar(usuario)


def test_usuario_dao_eliminar_retorna_true():
    dao = UsuarioDAO()
    usuario_guardado = None

    try:
        usuario_guardado = dao.guardar(
            crear_usuario(
                "usuario.eliminar.true@example.com"
            )
        )

        resultado = dao.eliminar_por_id(
            usuario_guardado.id_usuario
        )

        assert resultado is True

        usuario_guardado = None

    finally:
        eliminar_usuario_seguro(dao, usuario_guardado)


def test_usuario_dao_eliminar_retorna_false():
    dao = UsuarioDAO()

    resultado = dao.eliminar_por_id(999999999)

    assert resultado is False


def test_usuario_dao_rechaza_correo_duplicado():
    dao = UsuarioDAO()
    correo = "usuario.duplicado@example.com"
    primer_usuario = None
    segundo_usuario = None

    try:
        primer_usuario = dao.guardar(
            crear_usuario(correo)
        )

        segundo_usuario = crear_usuario(correo)

        with pytest.raises(
            ValueError,
            match="El correo ya está registrado",
        ):
            dao.guardar(segundo_usuario)

    finally:
        eliminar_usuario_seguro(dao, primer_usuario)

        if (
            segundo_usuario is not None
            and segundo_usuario.id_usuario is not None
        ):
            dao.eliminar_por_id(
                segundo_usuario.id_usuario
            )