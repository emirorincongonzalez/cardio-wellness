from unittest.mock import Mock
import pytest

from src.controladores.control_rutinas import ControlRutinas, _instanciar_rutina
from src.modelos.rutina import Rutina


@pytest.fixture
def mock_rutina_dao():
    return Mock()


@pytest.fixture
def mock_asignacion_dao():
    return Mock()


@pytest.fixture
def controlador(mock_rutina_dao, mock_asignacion_dao, tmp_path):
    log_file = tmp_path / "logs" / "LOG_CARDIO.txt"
    return ControlRutinas(
        rutina_dao=mock_rutina_dao,
        asignacion_dao=mock_asignacion_dao,
        ruta_log=str(log_file),
    )


def test_crear_rutina_exitoso_y_auditoria(controlador, mock_rutina_dao):
    mock_rutina_dao.guardar.side_effect = lambda r: r

    rutina = controlador.crear_rutina(
        nombre="Fuerza Básica",
        descripcion="Rutina para principiantes",
        nivel_dificultad="BASICO",
        duracion_estimada=45,
        creado_por=10,
    )

    assert isinstance(rutina, Rutina)
    mock_rutina_dao.guardar.assert_called_once()

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "10, CREACION_RUTINA" in contenido_log


@pytest.mark.parametrize(
    "nombre, descripcion, nivel, duracion, creado_por",
    [
        ("", "Desc", "Facil", 30, 1),
        ("   ", "Desc", "Facil", 30, 1),
        ("Rutina", "", "Facil", 30, 1),
        ("Rutina", "Desc", "", 30, 1),
        ("Rutina", "Desc", "Facil", 0, 1),
        ("Rutina", "Desc", "Facil", -10, 1),
        ("Rutina", "Desc", "Facil", "30", 1),
        ("Rutina", "Desc", "Facil", 30, -5),
        ("Rutina", "Desc", "Facil", 30, 0),
        ("Rutina", "Desc", "Facil", 30, "1"),
    ],
)
def test_crear_rutina_validaciones_incorrectas(
    controlador, nombre, descripcion, nivel, duracion, creado_por
):
    with pytest.raises(ValueError):
        controlador.crear_rutina(
            nombre=nombre,
            descripcion=descripcion,
            nivel_dificultad=nivel,
            duracion_estimada=duracion,
            creado_por=creado_por,
        )


def test_buscar_por_id_y_alias(controlador, mock_rutina_dao):
    mock_rutina_dao.buscar_por_id.return_value = "rutina_mock"

    assert controlador.buscar_por_id(1) == "rutina_mock"
    assert controlador.obtener_por_id(1) == "rutina_mock"
    assert mock_rutina_dao.buscar_por_id.call_count == 2

    with pytest.raises(ValueError):
        controlador.buscar_por_id(-1)


def test_listar_y_alias(controlador, mock_rutina_dao):
    mock_rutina_dao.listar.return_value = ["r1", "r2"]

    assert len(controlador.listar()) == 2
    assert len(controlador.listar_rutinas()) == 2
    assert mock_rutina_dao.listar.call_count == 2


def test_actualizar_rutina(controlador, mock_rutina_dao):
    rutina = _instanciar_rutina(
        id_rutina=1,
        nombre="Nombre nuevo",
        descripcion="Desc",
        nivel_dificultad="INTERMEDIO",
        duracion_estimada=40,
    )
    mock_rutina_dao.actualizar.return_value = rutina

    resultado = controlador.actualizar_rutina(rutina)
    assert resultado == rutina
    mock_rutina_dao.actualizar.assert_called_once_with(rutina)

    with pytest.raises(TypeError):
        controlador.actualizar_rutina("no_es_objeto_rutina")


def test_eliminar_rutina_y_auditoria(controlador, mock_rutina_dao):
    mock_rutina_dao.eliminar_por_id.return_value = True

    res = controlador.eliminar_rutina(4, usuario_accion=1)

    assert res is True
    mock_rutina_dao.eliminar_por_id.assert_called_once_with(4)

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "1, ELIMINACION_RUTINA" in contenido_log


def test_agregar_y_eliminar_ejercicio_auditoria(controlador, mock_rutina_dao):
    mock_rutina_dao.agregar_ejercicio.return_value = True
    mock_rutina_dao.eliminar_ejercicio.return_value = True

    controlador.agregar_ejercicio_a_rutina(1, 10, usuario_accion=1)
    controlador.eliminar_ejercicio_de_rutina(1, 10, usuario_accion=1)

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "1, AGREGAR_EJERCICIO_A_RUTINA" in contenido_log
    assert "1, ELIMINAR_EJERCICIO_DE_RUTINA" in contenido_log


def test_asignar_rutina_con_rutina_activa_previa(controlador, mock_asignacion_dao):
    mock_activa = Mock()
    mock_activa.id_asignacion = 55
    mock_asignacion_dao.obtener_activa_por_cliente.return_value = mock_activa
    mock_asignacion_dao.asignar.return_value = {"id_asignacion": 56, "activa": True}

    cliente_mock = Mock()
    cliente_mock.id_usuario = 3
    rutina_mock = Mock()
    rutina_mock.id_rutina = 9

    res = controlador.asignar_rutina(cliente_mock, rutina_mock, asignado_por=1)

    mock_asignacion_dao.obtener_activa_por_cliente.assert_called_once_with(3)
    mock_asignacion_dao.finalizar_asignacion.assert_called_once_with(55)
    mock_asignacion_dao.asignar.assert_called_once_with(
        id_cliente=3,
        id_rutina=9,
        asignado_por=1,
        observaciones="",
    )
    assert res == {"id_asignacion": 56, "activa": True}

    contenido_log = controlador.ruta_log.read_text(encoding="utf-8")
    assert "1, ASIGNACION_RUTINA" in contenido_log


def test_asignar_rutina_sin_rutina_activa_previa_y_usando_ids(
    controlador, mock_asignacion_dao
):
    mock_asignacion_dao.obtener_activa_por_cliente.return_value = None
    mock_asignacion_dao.asignar.return_value = {"id_asignacion": 70, "activa": True}

    res = controlador.asignar_rutina(cliente=7, rutina=12, asignado_por=2)

    mock_asignacion_dao.obtener_activa_por_cliente.assert_called_once_with(7)
    mock_asignacion_dao.finalizar_asignacion.assert_not_called()
    mock_asignacion_dao.asignar.assert_called_once_with(
        id_cliente=7,
        id_rutina=12,
        asignado_por=2,
        observaciones="",
    )
    assert res == {"id_asignacion": 70, "activa": True}