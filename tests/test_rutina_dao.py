import pytest

from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.enums import NivelRutina
from src.modelos.rutina import Rutina
from src.persistencia.ejercicio_dao import EjercicioDAO
from src.persistencia.rutina_dao import RutinaDAO


def crear_rutina(
    nombre="Rutina actualización",
    nivel="BASICO",
):
    return Rutina(
        nombre=nombre,
        descripcion="Descripción inicial",
        objetivo="Mejorar resistencia",
        nivel=nivel,
        duracion_semanas=4,
    )


def crear_ejercicio(
    nombre="Ejercicio rutina",
    duracion=30,
):
    return EjercicioCardio(
        nombre=nombre,
        descripcion="Ejercicio para prueba de rutina",
        tipo="Aeróbico",
        duracion_minutos=duracion,
        intensidad="MEDIA",
        calorias_estimadas=180.0,
    )


def eliminar_rutina_seguro(dao, rutina):
    if rutina is not None and rutina.id_rutina is not None:
        try:
            dao.eliminar_por_id(rutina.id_rutina)
        except ValueError:
            pass


def eliminar_ejercicio_seguro(dao, ejercicio):
    if (
        ejercicio is not None
        and ejercicio.id_ejercicio is not None
    ):
        dao.eliminar_por_id(ejercicio.id_ejercicio)


def test_rutina_dao_actualizar():
    dao = RutinaDAO()
    rutina_guardada = None

    try:
        rutina_guardada = dao.guardar(
            crear_rutina()
        )

        rutina_guardada.nombre = "Rutina actualizada"
        rutina_guardada.descripcion = (
            "Descripción actualizada"
        )
        rutina_guardada.objetivo = "Bajar de peso"
        rutina_guardada.nivel = NivelRutina.INTERMEDIO
        rutina_guardada.duracion_semanas = 8

        rutina_actualizada = dao.actualizar(
            rutina_guardada
        )

        assert rutina_actualizada is not None
        assert rutina_actualizada.id_rutina == (
            rutina_guardada.id_rutina
        )

        rutina_encontrada = dao.buscar_por_id(
            rutina_guardada.id_rutina
        )

        assert rutina_encontrada is not None
        assert rutina_encontrada.nombre == (
            "Rutina actualizada"
        )
        assert rutina_encontrada.descripcion == (
            "Descripción actualizada"
        )
        assert rutina_encontrada.objetivo == "Bajar de peso"
        assert rutina_encontrada.nivel == (
            NivelRutina.INTERMEDIO
        )
        assert rutina_encontrada.duracion_semanas == 8

    finally:
        eliminar_rutina_seguro(dao, rutina_guardada)


def test_rutina_dao_actualizar_sin_id():
    dao = RutinaDAO()

    rutina = crear_rutina()

    with pytest.raises(
        ValueError,
        match="debe tener un id",
    ):
        dao.actualizar(rutina)


def test_rutina_dao_actualizar_inexistente():
    dao = RutinaDAO()

    rutina = crear_rutina()
    rutina.id_rutina = 999999999

    with pytest.raises(
        ValueError,
        match="No se encontró la rutina",
    ):
        dao.actualizar(rutina)


def test_rutina_dao_eliminar_retorna_true():
    dao = RutinaDAO()
    rutina_guardada = None

    try:
        rutina_guardada = dao.guardar(
            crear_rutina(
                nombre="Rutina para eliminar"
            )
        )

        resultado = dao.eliminar_por_id(
            rutina_guardada.id_rutina
        )

        assert resultado is True

        rutina_guardada = None

    finally:
        eliminar_rutina_seguro(dao, rutina_guardada)


def test_rutina_dao_eliminar_retorna_false():
    dao = RutinaDAO()

    resultado = dao.eliminar_por_id(999999999)

    assert resultado is False


def test_rutina_dao_agregar_ejercicio():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    rutina_guardada = None
    ejercicio_guardado = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina con ejercicio"
            )
        )

        ejercicio_guardado = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Caminata para rutina"
            )
        )

        resultado = rutina_dao.agregar_ejercicio(
            rutina_guardada.id_rutina,
            ejercicio_guardado.id_ejercicio,
            1,
        )

        assert resultado is True

        ejercicios = rutina_dao.listar_ejercicios(
            rutina_guardada.id_rutina
        )

        assert len(ejercicios) == 1
        assert ejercicios[0].id_ejercicio == (
            ejercicio_guardado.id_ejercicio
        )
        assert ejercicios[0].nombre == (
            "Caminata para rutina"
        )

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            ejercicio_guardado,
        )


def test_rutina_dao_agregar_varios_ejercicios_en_orden():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    rutina_guardada = None
    primer_ejercicio = None
    segundo_ejercicio = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina ordenada"
            )
        )

        primer_ejercicio = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Primer ejercicio",
                duracion=20,
            )
        )

        segundo_ejercicio = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Segundo ejercicio",
                duracion=40,
            )
        )

        rutina_dao.agregar_ejercicio(
            rutina_guardada.id_rutina,
            segundo_ejercicio.id_ejercicio,
            2,
        )

        rutina_dao.agregar_ejercicio(
            rutina_guardada.id_rutina,
            primer_ejercicio.id_ejercicio,
            1,
        )

        ejercicios = rutina_dao.listar_ejercicios(
            rutina_guardada.id_rutina
        )

        assert len(ejercicios) == 2
        assert ejercicios[0].id_ejercicio == (
            primer_ejercicio.id_ejercicio
        )
        assert ejercicios[1].id_ejercicio == (
            segundo_ejercicio.id_ejercicio
        )

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            primer_ejercicio,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            segundo_ejercicio,
        )


def test_rutina_dao_agregar_ejercicio_duplicado():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    rutina_guardada = None
    ejercicio_guardado = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina duplicada"
            )
        )

        ejercicio_guardado = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio duplicado"
            )
        )

        rutina_dao.agregar_ejercicio(
            rutina_guardada.id_rutina,
            ejercicio_guardado.id_ejercicio,
            1,
        )

        with pytest.raises(
            ValueError,
            match="ya pertenece a la rutina",
        ):
            rutina_dao.agregar_ejercicio(
                rutina_guardada.id_rutina,
                ejercicio_guardado.id_ejercicio,
                2,
            )

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            ejercicio_guardado,
        )


def test_rutina_dao_rechaza_orden_cero():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    rutina_guardada = None
    ejercicio_guardado = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina orden inválido"
            )
        )

        ejercicio_guardado = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio orden inválido"
            )
        )

        with pytest.raises(
            ValueError,
            match="mayor que cero",
        ):
            rutina_dao.agregar_ejercicio(
                rutina_guardada.id_rutina,
                ejercicio_guardado.id_ejercicio,
                0,
            )

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            ejercicio_guardado,
        )


def test_rutina_dao_eliminar_ejercicio_retorna_true():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    rutina_guardada = None
    ejercicio_guardado = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina eliminar ejercicio"
            )
        )

        ejercicio_guardado = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio para eliminar"
            )
        )

        rutina_dao.agregar_ejercicio(
            rutina_guardada.id_rutina,
            ejercicio_guardado.id_ejercicio,
            1,
        )

        resultado = rutina_dao.eliminar_ejercicio(
            rutina_guardada.id_rutina,
            ejercicio_guardado.id_ejercicio,
        )

        assert resultado is True

        ejercicios = rutina_dao.listar_ejercicios(
            rutina_guardada.id_rutina
        )

        assert ejercicios == []

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            ejercicio_guardado,
        )


def test_rutina_dao_eliminar_ejercicio_retorna_false():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    rutina_guardada = None
    ejercicio_guardado = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina sin asociación"
            )
        )

        ejercicio_guardado = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio no asociado"
            )
        )

        resultado = rutina_dao.eliminar_ejercicio(
            rutina_guardada.id_rutina,
            ejercicio_guardado.id_ejercicio,
        )

        assert resultado is False

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            ejercicio_guardado,
        )


def test_rutina_dao_rechaza_rutina_inexistente_al_agregar():
    rutina_dao = RutinaDAO()
    ejercicio_dao = EjercicioDAO()

    ejercicio_guardado = None

    try:
        ejercicio_guardado = ejercicio_dao.guardar(
            crear_ejercicio(
                nombre="Ejercicio rutina inexistente"
            )
        )

        with pytest.raises(
            ValueError,
            match="La rutina o el ejercicio no existe",
        ):
            rutina_dao.agregar_ejercicio(
                999999999,
                ejercicio_guardado.id_ejercicio,
                1,
            )

    finally:
        eliminar_ejercicio_seguro(
            ejercicio_dao,
            ejercicio_guardado,
        )


def test_rutina_dao_rechaza_ejercicio_inexistente_al_agregar():
    rutina_dao = RutinaDAO()

    rutina_guardada = None

    try:
        rutina_guardada = rutina_dao.guardar(
            crear_rutina(
                nombre="Rutina ejercicio inexistente"
            )
        )

        with pytest.raises(
            ValueError,
            match="La rutina o el ejercicio no existe",
        ):
            rutina_dao.agregar_ejercicio(
                rutina_guardada.id_rutina,
                999999999,
                1,
            )

    finally:
        eliminar_rutina_seguro(
            rutina_dao,
            rutina_guardada,
        )