from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from src.controladores.control_clientes import ControlClientes
from src.modelos.cliente import Cliente


@pytest.fixture
def mock_cliente_dao():
    return Mock()


@pytest.fixture
def controlador(
    mock_cliente_dao,
    tmp_path,
):
    ruta_log = tmp_path / "logs" / "LOG_CARDIO.txt"

    return ControlClientes(
        cliente_dao=mock_cliente_dao,
        ruta_log=str(ruta_log),
    )


@pytest.fixture
def cliente_valido():
    return Cliente(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@example.com",
        contrasenia_hash="hash_prueba",
        edad=28,
        genero="HOMBRE",
        peso=Decimal("75"),
        altura=Decimal("1.78"),
        objetivo="Ganar resistencia",
        peso_objetivo=Decimal("70"),
    )


def test_constructor_usa_dao_recibido(
    mock_cliente_dao,
    tmp_path,
):
    controlador = ControlClientes(
        cliente_dao=mock_cliente_dao,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    assert controlador.cliente_dao is mock_cliente_dao


def test_constructor_crea_dao_por_defecto(
    tmp_path,
):
    dao_creado = Mock()

    with patch(
        "src.controladores.control_clientes.ClienteDAO",
        return_value=dao_creado,
    ):
        controlador = ControlClientes(
            ruta_log=str(tmp_path / "registro.txt"),
        )

    assert controlador.cliente_dao is dao_creado


@pytest.mark.parametrize(
    "genero,esperado",
    [
        ("HOMBRE", "HOMBRE"),
        (" mujer ", "MUJER"),
        ("otro", "OTRO"),
        (
            "prefiero no decirlo",
            "PREFIERO NO DECIRLO",
        ),
    ],
)
def test_normalizar_genero_exitoso(
    genero,
    esperado,
):
    assert (
        ControlClientes._normalizar_genero(genero)
        == esperado
    )


@pytest.mark.parametrize(
    "genero",
    [
        None,
        10,
        "",
        "   ",
        "DESCONOCIDO",
        "MASCULINO",
    ],
)
def test_normalizar_genero_rechaza_valores_invalidos(
    genero,
):
    with pytest.raises(ValueError):
        ControlClientes._normalizar_genero(genero)


@pytest.mark.parametrize(
    "contrasenia",
    [
        "Password123",
        "ClaveSegura9",
        "Aa123456",
    ],
)
def test_validar_contrasenia_registro_valida(
    contrasenia,
):
    assert (
        ControlClientes._validar_contrasenia_registro(
            contrasenia
        )
        is True
    )


@pytest.mark.parametrize(
    "contrasenia",
    [
        None,
        12345678,
        "",
        "Corta1",
        "password123",
        "PASSWORD123",
        "PasswordSinNumero",
        "12345678",
    ],
)
def test_validar_contrasenia_registro_invalida(
    contrasenia,
):
    assert (
        ControlClientes._validar_contrasenia_registro(
            contrasenia
        )
        is False
    )


def test_registrar_cliente_exitoso_y_auditoria(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.guardar.side_effect = (
        lambda cliente: cliente
    )

    with patch(
        "src.controladores.control_clientes.log_registro_cliente",
    ) as mock_log_registro:
        cliente = controlador.registrar_cliente(
            nombre="  Carlos  ",
            apellido="  Pérez  ",
            correo_electronico=" CARLOS@EXAMPLE.COM ",
            contrasenia_plana="Password123",
            edad=28,
            peso=75.5,
            altura=1.78,
            objetivo="Ganar masa muscular",
            genero="hombre",
            peso_objetivo=80,
        )

    assert isinstance(cliente, Cliente)
    assert cliente.nombre == "Carlos"
    assert cliente.apellido == "Pérez"
    assert cliente.correo_electronico == "carlos@example.com"
    assert cliente.genero == "HOMBRE"
    assert cliente.peso == 75.5
    assert cliente.peso_objetivo == 80

    mock_cliente_dao.guardar.assert_called_once_with(
        cliente
    )

    mock_log_registro.assert_called_once_with(
        "carlos@example.com"
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "carlos@example.com" in contenido_log
    assert "REGISTRO_CLIENTE" in contenido_log


def test_registrar_cliente_usa_meta_si_objetivo_esta_vacio(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.guardar.side_effect = (
        lambda cliente: cliente
    )

    with patch(
        "src.controladores.control_clientes.log_registro_cliente",
    ):
        cliente = controlador.registrar_cliente(
            nombre="Laura",
            apellido="Díaz",
            correo_electronico="laura@example.com",
            contrasenia_plana="Password123",
            edad=30,
            peso=70,
            altura=1.65,
            objetivo="",
            meta="Mantener peso",
            peso_objetivo=70,
        )

    assert cliente.objetivo == "Mantener peso"


def test_registrar_cliente_usa_peso_actual_como_meta(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.guardar.side_effect = (
        lambda cliente: cliente
    )

    with patch(
        "src.controladores.control_clientes.log_registro_cliente",
    ):
        cliente = controlador.registrar_cliente(
            nombre="Laura",
            apellido="Díaz",
            correo_electronico="laura@example.com",
            contrasenia_plana="Password123",
            edad=30,
            peso=70,
            altura=1.65,
            objetivo="Mantener peso",
        )

    assert cliente.peso_objetivo == 70


@pytest.mark.parametrize(
    "datos",
    [
        {
            "nombre": "",
        },
        {
            "nombre": None,
        },
        {
            "apellido": "",
        },
        {
            "correo_electronico": "",
        },
        {
            "contrasenia_plana": "",
        },
        {
            "edad": 0,
        },
        {
            "edad": True,
        },
        {
            "genero": "",
        },
        {
            "peso": 0,
        },
        {
            "peso": True,
        },
        {
            "altura": 0,
        },
        {
            "altura": True,
        },
        {
            "objetivo": "",
        },
        {
            "peso_objetivo": 0,
        },
        {
            "contrasenia_plana": "debil123",
        },
    ],
)
def test_registrar_cliente_rechaza_datos_invalidos(
    controlador,
    datos,
):
    valores = {
        "nombre": "Carlos",
        "apellido": "Pérez",
        "correo_electronico": "carlos@example.com",
        "contrasenia_plana": "Password123",
        "edad": 28,
        "peso": 75,
        "altura": 1.78,
        "objetivo": "Ganar resistencia",
        "genero": "HOMBRE",
        "peso_objetivo": 70,
    }

    valores.update(datos)

    with pytest.raises(ValueError):
        controlador.registrar_cliente(**valores)


@pytest.mark.parametrize(
    "objetivo,peso,peso_objetivo",
    [
        ("Bajar de peso", 70, 70),
        ("Bajar peso", 70, 80),
        ("Subir de peso", 70, 70),
        ("Subir peso", 70, 60),
        ("Mantener peso", 70, 65),
        ("Mantener", 70, 75),
    ],
)
def test_registrar_cliente_valida_relacion_peso_meta(
    controlador,
    objetivo,
    peso,
    peso_objetivo,
):
    with pytest.raises(ValueError):
        controlador.registrar_cliente(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana="Password123",
            edad=28,
            peso=peso,
            altura=1.78,
            objetivo=objetivo,
            peso_objetivo=peso_objetivo,
        )


def test_registrar_cliente_maneja_value_error_del_dao(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.guardar.side_effect = ValueError(
        "El correo ya está registrado."
    )

    with pytest.raises(
        ValueError,
        match="Error al registrar el cliente",
    ):
        controlador.registrar_cliente(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana="Password123",
            edad=28,
            peso=75,
            altura=1.78,
            objetivo="Ganar resistencia",
        )


def test_registrar_cliente_maneja_error_inesperado_del_dao(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.guardar.side_effect = RuntimeError(
        "Error de conexión"
    )

    with pytest.raises(
        RuntimeError,
        match="Error inesperado al registrar cliente",
    ):
        controlador.registrar_cliente(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana="Password123",
            edad=28,
            peso=75,
            altura=1.78,
            objetivo="Ganar resistencia",
        )


def test_buscar_por_id_y_alias(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.buscar_por_id.return_value = (
        "cliente_dummy"
    )

    assert (
        controlador.buscar_por_id(10)
        == "cliente_dummy"
    )

    assert (
        controlador.obtener_por_id(10)
        == "cliente_dummy"
    )

    assert (
        mock_cliente_dao.buscar_por_id.call_count
        == 2
    )


@pytest.mark.parametrize(
    "id_usuario",
    [
        None,
        True,
        False,
        0,
        -1,
        "10",
        10.5,
    ],
)
def test_buscar_por_id_rechaza_id_invalido(
    controlador,
    id_usuario,
):
    with pytest.raises(
        ValueError,
        match="id de usuario",
    ):
        controlador.buscar_por_id(id_usuario)


def test_buscar_por_correo_y_alias(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.buscar_por_correo.return_value = (
        "cliente_dummy"
    )

    assert (
        controlador.buscar_por_correo(
            " CARLOS@EXAMPLE.COM "
        )
        == "cliente_dummy"
    )

    assert (
        controlador.obtener_por_correo(
            "carlos@example.com"
        )
        == "cliente_dummy"
    )

    mock_cliente_dao.buscar_por_correo.assert_any_call(
        "carlos@example.com"
    )


@pytest.mark.parametrize(
    "correo",
    [
        None,
        "",
        "   ",
        10,
        [],
    ],
)
def test_buscar_por_correo_rechaza_correo_invalido(
    controlador,
    correo,
):
    with pytest.raises(
        ValueError,
        match="correo electrónico",
    ):
        controlador.buscar_por_correo(correo)


def test_listar_y_alias(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.listar.return_value = [
        "cliente_1",
        "cliente_2",
    ]

    assert controlador.listar() == [
        "cliente_1",
        "cliente_2",
    ]

    assert controlador.listar_clientes() == [
        "cliente_1",
        "cliente_2",
    ]

    assert mock_cliente_dao.listar.call_count == 2


def test_actualizar_cliente_exitoso(
    controlador,
    mock_cliente_dao,
    cliente_valido,
):
    cliente_valido.genero = " mujer "

    mock_cliente_dao.actualizar.return_value = cliente_valido

    resultado = controlador.actualizar_cliente(
        cliente_valido
    )

    assert resultado is cliente_valido
    assert cliente_valido.genero == "MUJER"

    mock_cliente_dao.actualizar.assert_called_once_with(
        cliente_valido
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "ACTUALIZACION_CLIENTE" in contenido_log


@pytest.mark.parametrize(
    "cliente",
    [
        None,
        "cliente",
        10,
        {},
        Mock(),
    ],
)
def test_actualizar_cliente_rechaza_tipo_invalido(
    controlador,
    cliente,
):
    with pytest.raises(
        TypeError,
        match="instancia de Cliente",
    ):
        controlador.actualizar_cliente(cliente)


def test_actualizar_cliente_maneja_value_error_dao(
    controlador,
    mock_cliente_dao,
    cliente_valido,
):
    mock_cliente_dao.actualizar.side_effect = ValueError(
        "Cliente inexistente"
    )

    with pytest.raises(
        ValueError,
        match="Error al actualizar cliente",
    ):
        controlador.actualizar_cliente(cliente_valido)


def test_actualizar_cliente_maneja_error_inesperado_dao(
    controlador,
    mock_cliente_dao,
    cliente_valido,
):
    mock_cliente_dao.actualizar.side_effect = RuntimeError(
        "Error de conexión"
    )

    with pytest.raises(
        RuntimeError,
        match="Error inesperado al actualizar cliente",
    ):
        controlador.actualizar_cliente(cliente_valido)


@pytest.mark.parametrize(
    "nuevo_peso",
    [
        None,
        True,
        False,
        0,
        -1,
        "70",
        [],
    ],
)
def test_registrar_actualizacion_peso_rechaza_peso_invalido(
    controlador,
    nuevo_peso,
):
    with pytest.raises(
        ValueError,
        match="nuevo peso",
    ):
        controlador.registrar_actualizacion_peso(
            1,
            nuevo_peso,
        )


@pytest.mark.parametrize(
    "id_cliente",
    [
        None,
        True,
        False,
        0,
        -1,
        "1",
    ],
)
def test_registrar_actualizacion_peso_rechaza_id_invalido(
    controlador,
    id_cliente,
):
    with pytest.raises(
        ValueError,
        match="id de cliente",
    ):
        controlador.registrar_actualizacion_peso(
            id_cliente,
            70,
        )


def test_registrar_actualizacion_peso_rechaza_cliente_inexistente(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="No se encontró el cliente",
    ):
        controlador.registrar_actualizacion_peso(
            1,
            70,
        )


def test_registrar_actualizacion_peso_exitoso_y_auditoria(
    controlador,
    mock_cliente_dao,
    cliente_valido,
):
    mock_cliente_dao.buscar_por_id.return_value = (
        cliente_valido
    )

    mock_cliente_dao.actualizar.return_value = cliente_valido

    resultado = controlador.registrar_actualizacion_peso(
        10,
        Decimal("72.5"),
    )

    assert resultado is cliente_valido
    assert cliente_valido.peso == Decimal("72.5")

    mock_cliente_dao.buscar_por_id.assert_called_once_with(
        10
    )

    mock_cliente_dao.actualizar.assert_called_once_with(
        cliente_valido
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "CLIENTE_10" in contenido_log
    assert "ACTUALIZACION_PESO" in contenido_log


@pytest.mark.parametrize(
    "id_usuario",
    [
        None,
        True,
        False,
        0,
        -1,
        "1",
    ],
)
def test_cambiar_contrasenia_rechaza_id_invalido(
    controlador,
    id_usuario,
):
    with pytest.raises(
        ValueError,
        match="id de usuario",
    ):
        controlador.cambiar_contrasenia(
            id_usuario,
            "ClaveActual123!",
            "NuevaClave123!",
        )


@pytest.mark.parametrize(
    "contrasenia_actual",
    [
        None,
        "",
        10,
    ],
)
def test_cambiar_contrasenia_rechaza_actual_invalida(
    controlador,
    contrasenia_actual,
):
    with pytest.raises(
        ValueError,
        match="contraseña actual",
    ):
        controlador.cambiar_contrasenia(
            1,
            contrasenia_actual,
            "NuevaClave123!",
        )


@pytest.mark.parametrize(
    "nueva_contrasenia",
    [
        None,
        "",
        10,
    ],
)
def test_cambiar_contrasenia_rechaza_nueva_vacia(
    controlador,
    nueva_contrasenia,
):
    with pytest.raises(
        ValueError,
        match="nueva contraseña",
    ):
        controlador.cambiar_contrasenia(
            1,
            "ClaveActual123!",
            nueva_contrasenia,
        )


def test_cambiar_contrasenia_rechaza_nueva_debil(
    controlador,
):
    with patch(
        "src.controladores.control_clientes."
        "GestorSeguridad.validar_fortaleza_contrasena",
        return_value=False,
    ):
        with pytest.raises(
            ValueError,
            match="muy débil",
        ):
            controlador.cambiar_contrasenia(
                1,
                "ClaveActual123!",
                "debil",
            )


def test_cambiar_contrasenia_exitoso(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.actualizar_contrasenia.return_value = True

    with patch(
        "src.controladores.control_clientes."
        "GestorSeguridad.validar_fortaleza_contrasena",
        return_value=True,
    ):
        resultado = controlador.cambiar_contrasenia(
            1,
            "ClaveActual123!",
            "NuevaClave123!",
        )

    assert resultado is True

    mock_cliente_dao.actualizar_contrasenia.assert_called_once_with(
        1,
        "ClaveActual123!",
        "NuevaClave123!",
    )


@pytest.mark.parametrize(
    "id_usuario",
    [
        None,
        True,
        False,
        0,
        -1,
        "5",
    ],
)
def test_eliminar_cliente_rechaza_id_invalido(
    controlador,
    id_usuario,
):
    with pytest.raises(
        ValueError,
        match="id de usuario",
    ):
        controlador.eliminar_cliente(id_usuario)


def test_eliminar_cliente_y_auditoria(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.eliminar_por_id.return_value = True

    resultado = controlador.eliminar_cliente(5)

    assert resultado is True

    mock_cliente_dao.eliminar_por_id.assert_called_once_with(
        5
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "ID_5" in contenido_log
    assert "ELIMINACION_CLIENTE" in contenido_log


@pytest.mark.parametrize(
    "metodo",
    [
        "consultar_progreso",
        "generar_progreso_mensual",
        "calcular_diferencia_peso",
    ],
)
@pytest.mark.parametrize(
    "id_cliente",
    [
        None,
        True,
        False,
        0,
        -1,
        "1",
    ],
)
def test_metodos_progreso_rechazan_id_invalido(
    controlador,
    metodo,
    id_cliente,
):
    with pytest.raises(
        ValueError,
        match="id de cliente",
    ):
        getattr(controlador, metodo)(id_cliente)


@pytest.mark.parametrize(
    "metodo,nombre_dao",
    [
        (
            "consultar_progreso",
            "obtener_progreso",
        ),
        (
            "generar_progreso_mensual",
            "generar_progreso_mensual",
        ),
        (
            "calcular_diferencia_peso",
            "calcular_diferencia_peso",
        ),
    ],
)
def test_metodos_progreso_rechazan_dao_sin_metodo(
    tmp_path,
    metodo,
    nombre_dao,
):
    dao_sin_metodo = SimpleNamespace()

    controlador = ControlClientes(
        cliente_dao=dao_sin_metodo,
        ruta_log=str(tmp_path / "registro.txt"),
    )

    with pytest.raises(
        RuntimeError,
        match=nombre_dao,
    ):
        getattr(controlador, metodo)(1)


def test_consultar_progreso_exitoso_y_auditoria(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.obtener_progreso.return_value = {
        "peso_actual": 70,
        "peso_objetivo": 65,
    }

    with patch(
        "src.controladores.control_clientes.log_consulta_progreso",
    ) as mock_log_consulta:
        resultado = controlador.consultar_progreso(10)

    assert resultado == {
        "peso_actual": 70,
        "peso_objetivo": 65,
    }

    mock_cliente_dao.obtener_progreso.assert_called_once_with(
        10
    )

    mock_log_consulta.assert_called_once_with(
        "CLIENTE_10"
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "CONSULTA_PROGRESO" in contenido_log


def test_generar_progreso_mensual_exitoso_y_auditoria(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.generar_progreso_mensual.return_value = {
        "mes": "2026-10",
        "cumplimiento": 80,
    }

    with patch(
        "src.controladores.control_clientes.log_generar_progreso",
    ) as mock_log_progreso:
        resultado = controlador.generar_progreso_mensual(10)

    assert resultado == {
        "mes": "2026-10",
        "cumplimiento": 80,
    }

    mock_cliente_dao.generar_progreso_mensual.assert_called_once_with(
        10
    )

    mock_log_progreso.assert_called_once_with(
        "CLIENTE_10"
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "GENERAR_PROGRESO" in contenido_log


def test_calcular_diferencia_peso_exitoso_y_auditoria(
    controlador,
    mock_cliente_dao,
):
    mock_cliente_dao.calcular_diferencia_peso.return_value = 5.5

    with patch(
        "src.controladores.control_clientes."
        "log_calculo_diferencia_peso",
    ) as mock_log_diferencia:
        resultado = controlador.calcular_diferencia_peso(10)

    assert resultado == 5.5

    mock_cliente_dao.calcular_diferencia_peso.assert_called_once_with(
        10
    )

    mock_log_diferencia.assert_called_once_with(
        "CLIENTE_10",
        5.5,
    )

    contenido_log = controlador.ruta_log.read_text(
        encoding="utf-8"
    )

    assert "CALCULO_DIFERENCIA_PESO" in contenido_log
    assert "DIF: 5.5" in contenido_log


@pytest.mark.parametrize(
    "valor",
    [
        None,
        True,
        False,
        0,
        -1,
        "1",
        1.5,
    ],
)
def test_validar_id_usuario_rechaza_valores_invalidos(
    valor,
):
    with pytest.raises(
        ValueError,
        match="id de usuario",
    ):
        ControlClientes._validar_id_usuario(valor)


@pytest.mark.parametrize(
    "valor",
    [
        None,
        True,
        False,
        0,
        -1,
        "1",
        1.5,
    ],
)
def test_validar_id_cliente_rechaza_valores_invalidos(
    valor,
):
    with pytest.raises(
        ValueError,
        match="id de cliente",
    ):
        ControlClientes._validar_id_cliente(valor)


def test_validar_ids_validos_no_generan_error():
    assert ControlClientes._validar_id_usuario(1) is None
    assert ControlClientes._validar_id_cliente(1) is None

def test_validar_datos_registro_rechaza_genero_vacio():
    """
    Verifica la validación interna cuando el género está vacío.
    """
    with pytest.raises(
        ValueError,
        match="género es obligatorio",
    ):
        ControlClientes._validar_datos_registro(
            nombre="Carlos",
            apellido="Pérez",
            correo_electronico="carlos@example.com",
            contrasenia_plana="Password123",
            edad=28,
            genero="",
            peso=75,
            altura=1.78,
            objetivo="Ganar resistencia",
            peso_objetivo=70,
        )


def test_validar_datos_registro_usa_peso_como_meta_por_defecto():
    """
    Verifica que peso_objetivo tome el peso actual cuando llega None.
    """
    resultado = ControlClientes._validar_datos_registro(
        nombre="Carlos",
        apellido="Pérez",
        correo_electronico="carlos@example.com",
        contrasenia_plana="Password123",
        edad=28,
        genero="HOMBRE",
        peso=75,
        altura=1.78,
        objetivo="Ganar resistencia",
        peso_objetivo=None,
    )

    assert resultado is None