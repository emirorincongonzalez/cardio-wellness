import pytest

from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.enums import Intensidad
from src.persistencia.ejercicio_dao import EjercicioDAO


def crear_ejercicio(
    nombre="Ejercicio DAO nuevo",
    duracion=30,
    intensidad="MEDIA",
    calorias=180.0,
):
    return EjercicioCardio(
        nombre=nombre,
        descripcion="Descripción del ejercicio",
        tipo="Aeróbico",
        duracion_minutos=duracion,
        intensidad=intensidad,
        calorias_estimadas=calorias,
    )


def eliminar_ejercicio_seguro(dao, ejercicio):
    if (
        ejercicio is not None
        and ejercicio.id_ejercicio is not None
    ):
        try:
            dao.eliminar_por_id(ejercicio.id_ejercicio)
        except ValueError:
            pass


def test_ejercicio_dao_buscar_por_id():
    dao = EjercicioDAO()
    ejercicio_guardado = None

    try:
        ejercicio_guardado = dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio buscar por id"
            )
        )

        ejercicio_encontrado = dao.buscar_por_id(
            ejercicio_guardado.id_ejercicio
        )

        assert ejercicio_encontrado is not None
        assert ejercicio_encontrado.id_ejercicio == (
            ejercicio_guardado.id_ejercicio
        )
        assert ejercicio_encontrado.nombre == (
            "Ejercicio buscar por id"
        )
        assert ejercicio_encontrado.descripcion == (
            "Descripción del ejercicio"
        )
        assert ejercicio_encontrado.tipo == "Aeróbico"
        assert ejercicio_encontrado.duracion_minutos == 30
        assert ejercicio_encontrado.intensidad == (
            Intensidad.MEDIA
        )
        assert ejercicio_encontrado.intensidad.value == "MEDIA"
        assert float(
            ejercicio_encontrado.calorias_estimadas
        ) == 180.0

    finally:
        eliminar_ejercicio_seguro(
            dao,
            ejercicio_guardado,
        )


def test_ejercicio_dao_buscar_por_id_inexistente():
    dao = EjercicioDAO()

    ejercicio_encontrado = dao.buscar_por_id(999999999)

    assert ejercicio_encontrado is None


def test_ejercicio_dao_listar():
    dao = EjercicioDAO()
    ejercicio_guardado = None

    try:
        ejercicio_guardado = dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio para listar"
            )
        )

        ejercicios = dao.listar()

        ejercicio_encontrado = next(
            (
                ejercicio
                for ejercicio in ejercicios
                if ejercicio.id_ejercicio
                == ejercicio_guardado.id_ejercicio
            ),
            None,
        )

        assert ejercicio_encontrado is not None
        assert ejercicio_encontrado.nombre == (
            "Ejercicio para listar"
        )

    finally:
        eliminar_ejercicio_seguro(
            dao,
            ejercicio_guardado,
        )


def test_ejercicio_dao_listar_ejercicios():
    dao = EjercicioDAO()
    ejercicio_guardado = None

    try:
        ejercicio_guardado = dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio listar alias"
            )
        )

        ejercicios = dao.listar_ejercicios()

        ejercicio_encontrado = next(
            (
                ejercicio
                for ejercicio in ejercicios
                if ejercicio.id_ejercicio
                == ejercicio_guardado.id_ejercicio
            ),
            None,
        )

        assert ejercicio_encontrado is not None

    finally:
        eliminar_ejercicio_seguro(
            dao,
            ejercicio_guardado,
        )


def test_ejercicio_dao_actualizar():
    dao = EjercicioDAO()
    ejercicio_guardado = None

    try:
        ejercicio_guardado = dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio antes de actualizar"
            )
        )

        ejercicio_guardado.nombre = (
            "Ejercicio actualizado"
        )
        ejercicio_guardado.descripcion = (
            "Descripción actualizada"
        )
        ejercicio_guardado.tipo = "HIIT"
        ejercicio_guardado.duracion_minutos = 45
        ejercicio_guardado.intensidad = (
            Intensidad.ALTA
        )
        ejercicio_guardado.calorias_estimadas = 300.0

        ejercicio_actualizado = dao.actualizar(
            ejercicio_guardado
        )

        assert ejercicio_actualizado is not None
        assert ejercicio_actualizado.id_ejercicio == (
            ejercicio_guardado.id_ejercicio
        )

        ejercicio_encontrado = dao.buscar_por_id(
            ejercicio_guardado.id_ejercicio
        )

        assert ejercicio_encontrado is not None
        assert ejercicio_encontrado.nombre == (
            "Ejercicio actualizado"
        )
        assert ejercicio_encontrado.descripcion == (
            "Descripción actualizada"
        )
        assert ejercicio_encontrado.tipo == "HIIT"
        assert ejercicio_encontrado.duracion_minutos == 45
        assert ejercicio_encontrado.intensidad == (
            Intensidad.ALTA
        )
        assert ejercicio_encontrado.intensidad.value == "ALTA"
        assert float(
            ejercicio_encontrado.calorias_estimadas
        ) == 300.0

    finally:
        eliminar_ejercicio_seguro(
            dao,
            ejercicio_guardado,
        )


def test_ejercicio_dao_actualizar_sin_id():
    dao = EjercicioDAO()

    ejercicio = crear_ejercicio(
        nombre="Ejercicio sin id"
    )

    with pytest.raises(
        ValueError,
        match="debe tener un id",
    ):
        dao.actualizar(ejercicio)


def test_ejercicio_dao_actualizar_inexistente():
    dao = EjercicioDAO()

    ejercicio = crear_ejercicio(
        nombre="Ejercicio inexistente"
    )
    ejercicio.id_ejercicio = 999999999

    with pytest.raises(
        ValueError,
        match="No se encontró el ejercicio",
    ):
        dao.actualizar(ejercicio)


def test_ejercicio_dao_eliminar_retorna_true():
    dao = EjercicioDAO()
    ejercicio_guardado = None

    try:
        ejercicio_guardado = dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio eliminar true"
            )
        )

        resultado = dao.eliminar_por_id(
            ejercicio_guardado.id_ejercicio
        )

        assert resultado is True

        ejercicio_guardado = None

    finally:
        eliminar_ejercicio_seguro(
            dao,
            ejercicio_guardado,
        )


def test_ejercicio_dao_eliminar_retorna_false():
    dao = EjercicioDAO()

    resultado = dao.eliminar_por_id(999999999)

    assert resultado is False


def test_ejercicio_dao_rechaza_creador_inexistente():
    dao = EjercicioDAO()
    ejercicio_guardado = None

    try:
        ejercicio = crear_ejercicio(
            nombre="Ejercicio creador inválido"
        )
        ejercicio.creado_por = 999999999

        with pytest.raises(
            ValueError,
            match="El creador del ejercicio no existe",
        ):
            dao.guardar(ejercicio)

    finally:
        eliminar_ejercicio_seguro(
            dao,
            ejercicio_guardado,
        )