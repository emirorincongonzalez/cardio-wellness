import pytest

from src.modelos.cliente import Cliente
from src.persistencia.cliente_dao import ClienteDAO
from src.persistencia.usuario_dao import UsuarioDAO
from src.servicios.gestor_seguridad import GestorSeguridad


def crear_cliente(correo):
    return Cliente(
        nombre="Laura",
        apellido="Gomez",
        correo_electronico=correo,
        contrasenia_hash="ClaveInicial123",
        edad=32,
        peso=68.5,
        altura=1.65,
        objetivo="Mejorar resistencia",
    )


def eliminar_cliente_seguro(dao, cliente):
    if cliente is not None and cliente.id_usuario is not None:
        dao.eliminar_por_id(cliente.id_usuario)


def test_cliente_dao_buscar_por_correo():
    dao = ClienteDAO()
    correo = "cliente.buscar.correo@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        cliente_encontrado = dao.buscar_por_correo(correo)

        assert cliente_encontrado is not None
        assert cliente_encontrado.id_usuario == (
            cliente_guardado.id_usuario
        )
        assert cliente_encontrado.correo_electronico == correo
        assert cliente_encontrado.nombre == "Laura"
        assert cliente_encontrado.apellido == "Gomez"
        assert cliente_encontrado.contrasenia_hash is not None
        assert cliente_encontrado.contrasenia_hash != (
            "ClaveInicial123"
        )

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_dao_buscar_por_correo_inexistente():
    dao = ClienteDAO()

    cliente_encontrado = dao.buscar_por_correo(
        "correo.inexistente@example.com"
    )

    assert cliente_encontrado is None


def test_cliente_dao_buscar_por_id_inexistente():
    dao = ClienteDAO()

    cliente_encontrado = dao.buscar_por_id(999999999)

    assert cliente_encontrado is None


def test_cliente_dao_recupera_hash():
    dao = ClienteDAO()
    correo = "cliente.hash.prueba@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        cliente_recuperado = dao.buscar_por_id(
            cliente_guardado.id_usuario
        )

        assert cliente_recuperado is not None
        assert cliente_recuperado.contrasenia_hash is not None
        assert cliente_recuperado.contrasenia_hash != (
            "ClaveInicial123"
        )

        assert GestorSeguridad.verificar_contrasenia(
            "ClaveInicial123",
            cliente_recuperado.contrasenia_hash,
        ) is True

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_cambiar_contrasenia_en_memoria():
    dao = ClienteDAO()
    correo = "cliente.cambio.memoria@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        cliente_recuperado = dao.buscar_por_id(
            cliente_guardado.id_usuario
        )

        assert cliente_recuperado is not None

        hash_original = cliente_recuperado.contrasenia_hash

        cambio_realizado = (
            cliente_recuperado.cambiar_contrasenia(
                "ClaveInicial123",
                "ClaveNueva456",
            )
        )

        assert cambio_realizado is True
        assert cliente_recuperado.contrasenia_hash != hash_original

        assert GestorSeguridad.verificar_contrasenia(
            "ClaveNueva456",
            cliente_recuperado.contrasenia_hash,
        ) is True

        assert GestorSeguridad.verificar_contrasenia(
            "ClaveInicial123",
            cliente_recuperado.contrasenia_hash,
        ) is False

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_cambiar_contrasenia_rechaza_actual_incorrecta():
    dao = ClienteDAO()
    correo = "cliente.cambio.incorrecto@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        cliente_recuperado = dao.buscar_por_id(
            cliente_guardado.id_usuario
        )

        assert cliente_recuperado is not None

        hash_original = cliente_recuperado.contrasenia_hash

        cambio_realizado = (
            cliente_recuperado.cambiar_contrasenia(
                "ContraseniaIncorrecta",
                "ClaveNueva456",
            )
        )

        assert cambio_realizado is False
        assert cliente_recuperado.contrasenia_hash == hash_original

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_dao_actualizar_datos():
    dao = ClienteDAO()
    correo = "cliente.actualizar@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        cliente_guardado.nombre = "Laura Actualizada"
        cliente_guardado.apellido = "Gomez Nueva"
        cliente_guardado.edad = 35
        cliente_guardado.peso = 70.0
        cliente_guardado.altura = 1.66
        cliente_guardado.objetivo = "Bajar de peso"

        cliente_actualizado = dao.actualizar(
            cliente_guardado
        )

        assert cliente_actualizado.id_usuario == (
            cliente_guardado.id_usuario
        )

        cliente_encontrado = dao.buscar_por_id(
            cliente_guardado.id_usuario
        )

        assert cliente_encontrado is not None
        assert cliente_encontrado.nombre == "Laura Actualizada"
        assert cliente_encontrado.apellido == "Gomez Nueva"
        assert cliente_encontrado.edad == 35
        assert cliente_encontrado.correo_electronico == correo
        assert float(cliente_encontrado.peso) == 70.0
        assert float(cliente_encontrado.altura) == 1.66
        assert cliente_encontrado.objetivo == "Bajar de peso"
        assert cliente_encontrado.contrasenia_hash is not None

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_dao_actualizar_correo():
    dao = ClienteDAO()
    correo_original = "cliente.correo.original@example.com"
    correo_nuevo = "cliente.correo.nuevo@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo_original)
        )

        cliente_guardado.correo_electronico = correo_nuevo

        dao.actualizar(cliente_guardado)

        cliente_por_correo_nuevo = dao.buscar_por_correo(
            correo_nuevo
        )

        cliente_por_correo_original = dao.buscar_por_correo(
            correo_original
        )

        assert cliente_por_correo_nuevo is not None
        assert cliente_por_correo_nuevo.id_usuario == (
            cliente_guardado.id_usuario
        )
        assert cliente_por_correo_original is None

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_dao_actualizar_sin_id():
    dao = ClienteDAO()

    cliente = crear_cliente(
        "cliente.sin.id@example.com"
    )

    with pytest.raises(
        ValueError,
        match="debe tener un id",
    ):
        dao.actualizar(cliente)


def test_cliente_dao_rechaza_correo_duplicado():
    dao = ClienteDAO()
    correo = "cliente.duplicado@example.com"
    primer_cliente = None
    segundo_cliente = None

    try:
        primer_cliente = dao.guardar(
            crear_cliente(correo)
        )

        segundo_cliente = crear_cliente(correo)

        with pytest.raises(
            ValueError,
            match="El correo ya está registrado",
        ):
            dao.guardar(segundo_cliente)

    finally:
        eliminar_cliente_seguro(dao, primer_cliente)

        if (
            segundo_cliente is not None
            and segundo_cliente.id_usuario is not None
        ):
            dao.eliminar_por_id(segundo_cliente.id_usuario)


def test_cliente_dao_actualizar_contrasenia():
    dao = ClienteDAO()
    usuario_dao = UsuarioDAO()
    correo = "cliente.actualizar.password@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        resultado = dao.actualizar_contrasenia(
            cliente_guardado.id_usuario,
            "ClaveInicial123",
            "ClaveActualizada789",
        )

        assert resultado is True

        sesion_correcta = usuario_dao.iniciar_sesion(
            correo,
            "ClaveActualizada789",
        )

        sesion_incorrecta = usuario_dao.iniciar_sesion(
            correo,
            "ClaveInicial123",
        )

        assert sesion_correcta is not None
        assert sesion_incorrecta is None

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_dao_rechaza_contrasenia_actual_incorrecta():
    dao = ClienteDAO()
    usuario_dao = UsuarioDAO()
    correo = "cliente.password.incorrecta@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        resultado = dao.actualizar_contrasenia(
            cliente_guardado.id_usuario,
            "ContraseniaIncorrecta",
            "NuevaClave789",
        )

        assert resultado is False

        sesion_original = usuario_dao.iniciar_sesion(
            correo,
            "ClaveInicial123",
        )

        sesion_nueva = usuario_dao.iniciar_sesion(
            correo,
            "NuevaClave789",
        )

        assert sesion_original is not None
        assert sesion_nueva is None

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)


def test_cliente_dao_rechaza_nueva_contrasenia_vacia():
    dao = ClienteDAO()
    correo = "cliente.password.vacia@example.com"
    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(
            crear_cliente(correo)
        )

        with pytest.raises(
            ValueError,
            match="La nueva contraseña no puede estar vacía",
        ):
            dao.actualizar_contrasenia(
                cliente_guardado.id_usuario,
                "ClaveInicial123",
                "",
            )

    finally:
        eliminar_cliente_seguro(dao, cliente_guardado)