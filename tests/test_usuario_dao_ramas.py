from unittest.mock import MagicMock, patch
from types import SimpleNamespace

import pytest

from src.modelos.cliente import Cliente
from src.modelos.administrador import Administrador
from src.persistencia.usuario_dao import UsuarioDAO
from src.servicios.gestor_seguridad import GestorSeguridad

class ErrorIntegridadSimulado(Exception):
    def __init__(self, pgcode, mensaje="Error de integridad simulado"):
        super().__init__(mensaje)
        self.pgcode = pgcode

@pytest.fixture
def dao():
    instancia = UsuarioDAO()
    instancia._conexion = MagicMock()
    instancia._conexion._conexion = MagicMock()
    return instancia


def crear_administrador(
    correo="admin.prueba@example.com",
    edad=30,
    id_usuario=1,
):
    hash_valido = GestorSeguridad.generar_hash("Clave123!")

    return Administrador(
        id_usuario=id_usuario,
        nombre="Ana",
        apellido="Prueba",
        correo_electronico=correo,
        contrasenia_hash=hash_valido,
        edad=edad,
    )

@pytest.mark.parametrize(
    ("correo", "mensaje"),
    [
        (None, "El correo debe ser una cadena"),
        (123, "El correo debe ser una cadena"),
        ("", "El correo no puede estar vacío"),
        ("   ", "El correo no puede estar vacío"),
    ],
)
def test_normalizar_correo_invalido(correo, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        UsuarioDAO._normalizar_correo(correo)


def test_normalizar_correo_limpia_espacios_y_mayusculas():
    resultado = UsuarioDAO._normalizar_correo(
        "  ANA.PRUEBA@EXAMPLE.COM  "
    )

    assert resultado == "ana.prueba@example.com"


@pytest.mark.parametrize(
    ("genero", "esperado"),
    [
        (None, "PREFIERO NO DECIRLO"),
        ("", "PREFIERO NO DECIRLO"),
        ("   ", "PREFIERO NO DECIRLO"),
        (" hombre ", "HOMBRE"),
        ("mujer", "MUJER"),
        ("OTRO", "OTRO"),
        ("prefiero no decirlo", "PREFIERO NO DECIRLO"),
    ],
)
def test_normalizar_genero_valido(genero, esperado):
    assert UsuarioDAO._normalizar_genero(genero) == esperado


@pytest.mark.parametrize("genero", [1, True, [], {}])
def test_normalizar_genero_rechaza_tipo_no_texto(genero):
    with pytest.raises(ValueError, match="El género debe ser texto"):
        UsuarioDAO._normalizar_genero(genero)


def test_normalizar_genero_rechaza_valor_desconocido():
    with pytest.raises(ValueError, match="El género debe ser"):
        UsuarioDAO._normalizar_genero("DESCONOCIDO")


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("admin", "administrador"),
        ("ADMIN", "administrador"),
        ("cliente", "cliente"),
        (" TipoUsuario.CLIENTE ", "cliente"),
        ("TipoUsuario.ADMIN", "administrador"),
    ],
)
def test_obtener_tipo_usuario_normaliza(valor, esperado):
    assert UsuarioDAO._obtener_tipo_usuario(valor) == esperado


@pytest.mark.parametrize(
    "usuario",
    [
        None,
        MagicMock(nombre="", apellido="Apellido", edad=20),
        MagicMock(nombre="   ", apellido="Apellido", edad=20),
        MagicMock(nombre="Nombre", apellido="", edad=20),
        MagicMock(nombre="Nombre", apellido="   ", edad=20),
        MagicMock(nombre="Nombre", apellido="Apellido", edad="20"),
        MagicMock(nombre="Nombre", apellido="Apellido", edad=True),
        MagicMock(nombre="Nombre", apellido="Apellido", edad=0),
        MagicMock(nombre="Nombre", apellido="Apellido", edad=-1),
    ],
)
def test_validar_usuario_rechaza_datos_invalidos(usuario):
    with pytest.raises(ValueError):
        UsuarioDAO._validar_usuario(usuario)


@pytest.mark.parametrize("id_usuario", [None, 0, -1, True, "1", 1.5])
def test_validar_id_rechaza_ids_invalidos(id_usuario):
    with pytest.raises(ValueError, match="El ID debe ser un entero positivo"):
        UsuarioDAO._validar_id(id_usuario)


def test_validar_id_acepta_entero_positivo():
    assert UsuarioDAO._validar_id(1) is None


@pytest.mark.parametrize(
    ("correo", "contrasenia"),
    [
        (None, "Clave123!"),
        ("admin@example.com", None),
        ("admin@example.com", ""),
    ],
)
def test_iniciar_sesion_retorna_none_con_entrada_invalida(
    dao,
    correo,
    contrasenia,
):
    assert dao.iniciar_sesion(correo, contrasenia) is None


def test_iniciar_sesion_retorna_none_si_busqueda_falla(dao):
    with patch.object(
        dao,
        "buscar_por_correo",
        side_effect=ValueError("Correo inválido"),
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "Clave123!",
        )

    assert resultado is None


def test_iniciar_sesion_retorna_none_si_usuario_no_existe(dao):
    with patch.object(
        dao,
        "buscar_por_correo",
        return_value=None,
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "Clave123!",
        )

    assert resultado is None


def test_iniciar_sesion_retorna_none_si_hash_no_es_texto(dao):
    usuario = SimpleNamespace(contrasenia_hash=None)

    with patch.object(
        dao,
        "buscar_por_correo",
        return_value=usuario,
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "Clave123!",
        )

    assert resultado is None

def test_iniciar_sesion_retorna_none_si_hash_no_es_bcrypt(dao):
    usuario = crear_administrador()
    usuario.contrasenia_hash = "hash-invalido"

    with patch.object(
        dao,
        "buscar_por_correo",
        return_value=usuario,
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "Clave123!",
        )

    assert resultado is None


def test_iniciar_sesion_retorna_none_si_hash_bcrypt_tiene_longitud_invalida(
    dao,
):
    usuario = crear_administrador()
    usuario.contrasenia_hash = "$2b$" + ("a" * 20)

    with patch.object(
        dao,
        "buscar_por_correo",
        return_value=usuario,
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "Clave123!",
        )

    assert resultado is None


def test_iniciar_sesion_retorna_usuario_con_credenciales_validas(dao):
    usuario = crear_administrador()
    usuario.contrasenia_hash = GestorSeguridad.generar_hash(
        "Clave123!"
    )

    with patch.object(
        dao,
        "buscar_por_correo",
        return_value=usuario,
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "Clave123!",
        )

    assert resultado is usuario


def test_iniciar_sesion_retorna_none_con_contrasenia_incorrecta(dao):
    usuario = crear_administrador()
    usuario.contrasenia_hash = GestorSeguridad.generar_hash(
        "ClaveCorrecta1!"
    )

    with patch.object(
        dao,
        "buscar_por_correo",
        return_value=usuario,
    ):
        resultado = dao.iniciar_sesion(
            "admin@example.com",
            "ClaveIncorrecta1!",
        )

    assert resultado is None

@pytest.mark.parametrize("contrasenia", [None, "", 123])
def test_cambiar_contrasenia_rechaza_contrasenia_invalida(
    dao,
    contrasenia,
):
    with pytest.raises(ValueError, match="La contraseña no puede estar vacía"):
        dao.cambiar_contrasenia(1, contrasenia)


def test_cambiar_contrasenia_actualiza_y_confirma_transaccion(dao):
    dao._conexion.ejecutar_actualizacion.return_value = True

    resultado = dao.cambiar_contrasenia(1, "NuevaClave123!")

    assert resultado is True
    dao._conexion.ejecutar_actualizacion.assert_called_once()
    dao._conexion._conexion.commit.assert_called_once()


def test_cambiar_contrasenia_retorna_false_si_no_actualiza(dao):
    dao._conexion.ejecutar_actualizacion.return_value = False

    resultado = dao.cambiar_contrasenia(1, "NuevaClave123!")

    assert resultado is False
    dao._conexion._conexion.commit.assert_called_once()


def test_cambiar_contrasenia_hace_rollback_si_falla(dao):
    dao._conexion.ejecutar_actualizacion.side_effect = RuntimeError(
        "Error de base de datos"
    )

    with pytest.raises(RuntimeError, match="Error de base de datos"):
        dao.cambiar_contrasenia(1, "NuevaClave123!")

    dao._conexion._conexion.rollback.assert_called_once()


def test_eliminar_por_id_retorna_true_y_confirma(dao):
    dao._conexion.ejecutar_actualizacion.return_value = 1

    assert dao.eliminar_por_id(1) is True
    dao._conexion._conexion.commit.assert_called_once()


def test_eliminar_por_id_retorna_false_si_no_encuentra_usuario(dao):
    dao._conexion.ejecutar_actualizacion.return_value = 0

    assert dao.eliminar_por_id(1) is False
    dao._conexion._conexion.commit.assert_called_once()


def test_eliminar_por_id_hace_rollback_si_falla(dao):
    dao._conexion.ejecutar_actualizacion.side_effect = RuntimeError(
        "Error al eliminar"
    )

    with pytest.raises(RuntimeError, match="Error al eliminar"):
        dao.eliminar_por_id(1)

    dao._conexion._conexion.rollback.assert_called_once()


def test_actualizar_rechaza_usuario_sin_id(dao):
    usuario = crear_administrador(id_usuario=None)

    with pytest.raises(ValueError, match="El usuario debe tener un ID"):
        dao.actualizar(usuario)


def test_actualizar_rechaza_tipo_de_usuario_invalido(dao):
    usuario = crear_administrador()
    usuario.tipo_usuario = "invitado"

    with pytest.raises(ValueError, match="El tipo de usuario no es válido"):
        dao.actualizar(usuario)


def test_actualizar_retorna_error_si_usuario_no_existe(dao):
    usuario = crear_administrador()
    dao._conexion.ejecutar_actualizacion.return_value = False

    with pytest.raises(ValueError, match="No se encontró el usuario"):
        dao.actualizar(usuario)

    dao._conexion._conexion.rollback.assert_called_once()


def test_actualizar_hace_rollback_y_convierte_error_inesperado(dao):
    usuario = crear_administrador()
    dao._conexion.ejecutar_actualizacion.side_effect = RuntimeError(
        "Fallo inesperado"
    )

    with pytest.raises(ValueError, match="Error al actualizar el usuario"):
        dao.actualizar(usuario)

    dao._conexion._conexion.rollback.assert_called_once()

@pytest.mark.parametrize("contrasenia", [None, "", 123, False])
def test_guardar_rechaza_contrasenia_invalida(dao, contrasenia):
    usuario = crear_administrador()

    with pytest.raises(
        ValueError,
        match="La contraseña debe ser una cadena no vacía",
    ):
        dao.guardar(usuario, contrasenia)


def test_guardar_rechaza_tipo_usuario_invalido(dao):
    usuario = crear_administrador()
    usuario.tipo_usuario = "invitado"

    with pytest.raises(
        ValueError,
        match="El tipo de usuario no es válido",
    ):
        dao.guardar(usuario, "Clave123!")


def test_guardar_lanza_error_si_insert_no_devuelve_resultado(dao):
    usuario = crear_administrador()
    dao._conexion.ejecutar_consulta.return_value = []

    with pytest.raises(
        RuntimeError,
        match="No se pudo guardar el usuario",
    ):
        dao.guardar(usuario, "Clave123!")

    dao._conexion._conexion.rollback.assert_called_once()


def test_guardar_convierte_error_integridad_clave_foranea(dao):
    usuario = crear_administrador()

    dao._conexion.ejecutar_consulta.side_effect = (
        ErrorIntegridadSimulado("23503")
    )

    with patch(
        "src.persistencia.usuario_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="La información relacionada no existe",
        ):
            dao.guardar(usuario, "Clave123!")

    dao._conexion._conexion.rollback.assert_called_once()


def test_guardar_convierte_error_integridad_generico(dao):
    usuario = crear_administrador()

    dao._conexion.ejecutar_consulta.side_effect = (
        ErrorIntegridadSimulado("99999", "Restricción desconocida")
    )

    with patch(
        "src.persistencia.usuario_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            RuntimeError,
            match="Error de integridad al guardar el usuario",
        ):
            dao.guardar(usuario, "Clave123!")

    dao._conexion._conexion.rollback.assert_called_once()


def test_guardar_hace_rollback_y_relanzar_error_inesperado(dao):
    usuario = crear_administrador()

    dao._conexion.ejecutar_consulta.side_effect = RuntimeError(
        "Error inesperado de conexión"
    )

    with pytest.raises(
        RuntimeError,
        match="Error inesperado de conexión",
    ):
        dao.guardar(usuario, "Clave123!")

    dao._conexion._conexion.rollback.assert_called_once()


def test_buscar_por_correo_rechaza_tipo_usuario_desconocido(dao):
    dao._conexion.ejecutar_consulta.return_value = [
        {
            "tipo_usuario": "superusuario",
        }
    ]

    with pytest.raises(
        ValueError,
        match="Tipo de usuario desconocido: superusuario",
    ):
        dao.buscar_por_correo("admin@example.com")


def crear_fila_cliente(**cambios):
    fila = {
        "id_usuario": 1,
        "nombre": "Ana",
        "apellido": "Prueba",
        "correo_electronico": "ana.prueba@example.com",
        "contrasenia_hash": GestorSeguridad.generar_hash(
            "Clave123!"
        ),
        "edad": 30,
        "peso": 70.0,
        "peso_objetivo": 65.0,
        "altura": 1.70,
        "objetivo": "Mejorar resistencia",
        "genero": "MUJER",
        "fecha_registro": None,
        "fecha_ingreso": None,
    }

    fila.update(cambios)

    return fila


def test_crear_cliente_rechaza_peso_ausente():
    fila = crear_fila_cliente(peso=None)

    with pytest.raises(
        ValueError,
        match="El cliente no tiene peso registrado",
    ):
        UsuarioDAO._crear_cliente_desde_fila(fila)


def test_crear_cliente_usa_peso_actual_si_no_hay_peso_objetivo():
    fila = crear_fila_cliente(
        peso=70.0,
        peso_objetivo=None,
    )

    cliente = UsuarioDAO._crear_cliente_desde_fila(fila)

    assert cliente.peso == 70.0
    assert cliente.peso_objetivo == 70.0


def test_crear_cliente_rechaza_altura_ausente():
    fila = crear_fila_cliente(altura=None)

    with pytest.raises(
        ValueError,
        match="El cliente no tiene altura registrada",
    ):
        UsuarioDAO._crear_cliente_desde_fila(fila)


def test_actualizar_convierte_error_integridad_correo_duplicado(dao):
    usuario = crear_administrador()

    dao._conexion.ejecutar_actualizacion.side_effect = (
        ErrorIntegridadSimulado("23505")
    )

    with patch(
        "src.persistencia.usuario_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="El correo ya está registrado",
        ):
            dao.actualizar(usuario)

    dao._conexion._conexion.rollback.assert_called_once()


def test_actualizar_convierte_error_integridad_generico(dao):
    usuario = crear_administrador()

    dao._conexion.ejecutar_actualizacion.side_effect = (
        ErrorIntegridadSimulado("99999", "Restricción inesperada")
    )

    with patch(
        "src.persistencia.usuario_dao.IntegrityError",
        ErrorIntegridadSimulado,
    ):
        with pytest.raises(
            ValueError,
            match="Error de integridad al actualizar el usuario",
        ):
            dao.actualizar(usuario)

    dao._conexion._conexion.rollback.assert_called_once()

def test_actualizar_cliente_actualiza_datos_generales_y_cliente(dao):
    cliente = Cliente(
        id_usuario=25,
        nombre="Laura",
        apellido="Gomez",
        correo_electronico="laura.gomez@example.com",
        contrasenia_hash=GestorSeguridad.generar_hash(
            "Clave123!"
        ),
        edad=28,
        genero="mujer",
        peso=72.5,
        peso_objetivo=65.0,
        altura=1.68,
        objetivo="Bajar de peso",
    )

    dao._conexion.ejecutar_actualizacion.return_value = True

    resultado = dao.actualizar(cliente)

    assert resultado is cliente

    assert (
        dao._conexion.ejecutar_actualizacion.call_count == 2
    )

    primera_llamada = (
        dao._conexion.ejecutar_actualizacion.call_args_list[0]
    )
    segunda_llamada = (
        dao._conexion.ejecutar_actualizacion.call_args_list[1]
    )

    sql_usuario, parametros_usuario = primera_llamada.args

    assert "UPDATE usuarios" in sql_usuario
    assert parametros_usuario == (
        "Laura",
        "Gomez",
        "laura.gomez@example.com",
        28,
        "cliente",
        25,
    )

    sql_cliente, parametros_cliente = segunda_llamada.args

    assert "UPDATE clientes" in sql_cliente
    assert parametros_cliente == (
        cliente.peso,
        cliente.peso_objetivo,
        cliente.altura,
        "Bajar de peso",
        "MUJER",
        25,
    )

    dao._conexion._conexion.commit.assert_called_once()