"""
Tests para cubrir excepciones y casos edge en RutinaDAO.
"""

import pytest
from uuid import uuid4

from src.modelos.enums import Intensidad, NivelRutina
from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.rutina import Rutina
from src.persistencia.rutina_dao import RutinaDAO
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


@pytest.fixture
def dao():
    return RutinaDAO()


@pytest.fixture
def datos_prueba():
    """Crea administrador, ejercicio para pruebas."""
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()

    correo = f"test.rutina.{uuid4().hex}@example.com"
    contrasenia_hash = GestorSeguridad.generar_hash("Clave123!")

    try:
        with bd._conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre, apellido, correo_electronico, "contraseña_hash", edad, tipo_usuario
                )
                VALUES (%s, %s, %s, %s, %s, 'administrador')
                RETURNING id_usuario
                """,
                ("Test", "Rutina", correo, contrasenia_hash, 30),
            )
            id_admin = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO ejercicios (
                    nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_ejercicio
                """,
                ("Ejercicio Test", "Para pruebas", "cardio", 30, "MEDIA", 200.0, id_admin),
            )
            id_ejercicio = cursor.fetchone()[0]

        bd._conexion.commit()
        yield {"id_admin": id_admin, "id_ejercicio": id_ejercicio}

    except Exception:
        bd._conexion.rollback()
        raise

    finally:
        try:
            with bd._conexion.cursor() as cursor:
                cursor.execute("DELETE FROM rutina_ejercicios WHERE id_rutina IN (SELECT id_rutina FROM rutinas WHERE creado_por = %s)", (id_admin,))
                cursor.execute("DELETE FROM rutinas WHERE creado_por = %s", (id_admin,))
                cursor.execute("DELETE FROM ejercicios WHERE id_ejercicio = %s", (id_ejercicio,))
                cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_admin,))
            bd._conexion.commit()
        except Exception:
            bd._conexion.rollback()


def test_dao_guardar_con_creador_inexistente(dao):
    """Prueba que guarda con creador inexistente lanza ValueError."""
    rutina = Rutina(
        id_rutina=None,
        nombre="Rutina Test",
        descripcion="Para pruebas",
        objetivo="Pruebas excepciones",
        nivel=NivelRutina.INTERMEDIO,
        duracion_semanas=4,
        creado_por=999999,  # Creador inexistente
    )

    with pytest.raises(ValueError, match="El creador de la rutina no existe"):
        dao.guardar(rutina)


def test_dao_buscar_por_id_inexistente(dao):
    """Prueba que buscar ID inexistente retorna None."""
    resultado = dao.buscar_por_id(999999)
    assert resultado is None


def test_dao_actualizar_sin_id(dao, datos_prueba):
    """Prueba que actualizar sin ID lanza ValueError."""
    rutina = Rutina(
        id_rutina=None,  # Sin ID
        nombre="Rutina Test",
        descripcion="Para pruebas",
        objetivo="Pruebas excepciones",
        nivel=NivelRutina.INTERMEDIO,
        duracion_semanas=4,
        creado_por=datos_prueba["id_admin"],
    )

    with pytest.raises(ValueError, match="La rutina debe tener un id"):
        dao.actualizar(rutina)


def test_dao_actualizar_id_inexistente(dao):
    """Prueba que actualizar ID inexistente lanza ValueError."""
    rutina = Rutina(
        id_rutina=999999,  # ID inexistente
        nombre="Rutina Test",
        descripcion="Para pruebas",
        objetivo="Pruebas excepciones",
        nivel=NivelRutina.INTERMEDIO,
        duracion_semanas=4,
        creado_por=1,
    )

    with pytest.raises(ValueError, match="No se encontró la rutina"):
        dao.actualizar(rutina)


def test_dao_agregar_ejercicio_orden_invalido(dao, datos_prueba):
    """Prueba que agregar ejercicio con orden <= 0 lanza ValueError."""
    with pytest.raises(ValueError, match="El orden del ejercicio debe ser mayor que cero"):
        dao.agregar_ejercicio(1, datos_prueba["id_ejercicio"], 0)

    with pytest.raises(ValueError, match="El orden del ejercicio debe ser mayor que cero"):
        dao.agregar_ejercicio(1, datos_prueba["id_ejercicio"], -1)


def test_dao_agregar_ejercicio_rutina_inexistente(dao, datos_prueba):
    """Prueba que agregar ejercicio a rutina inexistente lanza ValueError."""
    with pytest.raises(ValueError, match="La rutina o el ejercicio no existe"):
        dao.agregar_ejercicio(999999, datos_prueba["id_ejercicio"], 1)


def test_dao_agregar_ejercicio_duplicado(dao, datos_prueba):
    """Prueba que agregar ejercicio duplicado lanza ValueError."""
    # Crear rutina
    rutina = Rutina(
        id_rutina=None,
        nombre="Rutina Test",
        descripcion="Para pruebas",
        objetivo="Pruebas excepciones",
        nivel=NivelRutina.INTERMEDIO,
        duracion_semanas=4,
        creado_por=datos_prueba["id_admin"],
    )
    rutina = dao.guardar(rutina)

    # Agregar ejercicio
    dao.agregar_ejercicio(rutina.id_rutina, datos_prueba["id_ejercicio"], 1)

    # Intentar agregar mismo ejercicio de nuevo
    with pytest.raises(ValueError, match="El ejercicio ya pertenece a la rutina"):
        dao.agregar_ejercicio(rutina.id_rutina, datos_prueba["id_ejercicio"], 2)


def test_dao_eliminar_ejercicio_no_existe(dao, datos_prueba):
    """Prueba que eliminar ejercicio no asociado retorna False."""
    resultado = dao.eliminar_ejercicio(999999, datos_prueba["id_ejercicio"])
    assert resultado is False


def test_dao_listar_ejercicios_rutina_vacia(dao, datos_prueba):
    """Prueba que listar ejercicios de rutina sin ejercicios retorna lista vacía."""
    rutina = Rutina(
        id_rutina=None,
        nombre="Rutina Test",
        descripcion="Para pruebas",
        objetivo="Pruebas excepciones",
        nivel=NivelRutina.INTERMEDIO,
        duracion_semanas=4,
        creado_por=datos_prueba["id_admin"],
    )
    rutina = dao.guardar(rutina)

    resultado = dao.listar_ejercicios(rutina.id_rutina)
    assert isinstance(resultado, list)
    assert len(resultado) == 0


def test_dao_eliminar_id_inexistente(dao):
    """Prueba que eliminar ID inexistente retorna False."""
    resultado = dao.eliminar_por_id(999999)
    assert resultado is False
