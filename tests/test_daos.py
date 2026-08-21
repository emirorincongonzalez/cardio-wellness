from src.modelos.cliente import Cliente
from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.enums import Intensidad, NivelRutina
from src.modelos.rutina import Rutina
from src.persistencia.cliente_dao import ClienteDAO
from src.persistencia.ejercicio_dao import EjercicioDAO
from src.persistencia.rutina_dao import RutinaDAO
from src.persistencia.usuario_dao import UsuarioDAO


def test_usuario_dao():
    correo = "usuario.dao.prueba@example.com"
    dao = UsuarioDAO()

    usuario = Cliente(
        nombre="Usuario",
        apellido="Prueba",
        correo_electronico=correo,
        contrasenia_hash="Clave123",
        edad=30,
        peso=70.0,
        altura=1.70,
        objetivo="Mantener condición",
    )

    usuario_guardado = None

    try:
        usuario_guardado = dao.guardar(usuario)

        assert usuario_guardado.id_usuario is not None
        assert usuario_guardado.fecha_registro is not None

        usuario_encontrado = dao.buscar_por_correo(correo)

        assert usuario_encontrado is not None
        assert usuario_encontrado.correo_electronico == correo
        assert usuario_encontrado.nombre == "Usuario"
        assert usuario_encontrado.tipo_usuario == "cliente"

        sesion_correcta = dao.iniciar_sesion(
            correo,
            "Clave123",
        )

        assert sesion_correcta is not None
        assert sesion_correcta.correo_electronico == correo

        sesion_incorrecta = dao.iniciar_sesion(
            correo,
            "Incorrecta",
        )

        assert sesion_incorrecta is None

    finally:
        if usuario_guardado is not None:
            dao.eliminar_por_id(usuario_guardado.id_usuario)


def test_cliente_dao():
    correo = "cliente.dao.prueba@example.com"
    dao = ClienteDAO()

    cliente = Cliente(
        nombre="Carlos",
        apellido="Perez",
        correo_electronico=correo,
        contrasenia_hash="Clave123",
        edad=28,
        peso=82.5,
        altura=1.75,
        objetivo="Bajar de peso",
    )

    cliente_guardado = None

    try:
        cliente_guardado = dao.guardar(cliente)

        assert cliente_guardado.id_usuario is not None
        assert cliente_guardado.fecha_registro is not None
        assert cliente_guardado.fecha_ingreso is not None

        cliente_encontrado = dao.buscar_por_id(
            cliente_guardado.id_usuario
        )

        assert cliente_encontrado is not None
        assert cliente_encontrado.nombre == "Carlos"
        assert cliente_encontrado.correo_electronico == correo
        assert cliente_encontrado.tipo_usuario == "cliente"
        assert float(cliente_encontrado.peso) == 82.5
        assert float(cliente_encontrado.altura) == 1.75
        assert cliente_encontrado.objetivo == "Bajar de peso"
        assert cliente_encontrado.fecha_ingreso is not None

        clientes = dao.listar()

        assert any(
            cliente_item.id_usuario == cliente_guardado.id_usuario
            for cliente_item in clientes
        )

    finally:
        if cliente_guardado is not None:
            dao.eliminar_por_id(cliente_guardado.id_usuario)


def test_rutina_dao():
    dao = RutinaDAO()

    rutina = Rutina(
        nombre="Rutina DAO",
        descripcion="Rutina de prueba",
        objetivo="Mejorar resistencia",
        nivel="BASICO",
        duracion_semanas=4,
    )

    rutina_guardada = None

    try:
        rutina_guardada = dao.guardar(rutina)

        assert rutina_guardada.id_rutina is not None
        assert rutina_guardada.fecha_creacion is not None
        assert rutina_guardada.nivel == NivelRutina.BASICO
        assert rutina_guardada.nivel.value == "BASICO"

        rutina_encontrada = dao.buscar_por_id(
            rutina_guardada.id_rutina
        )

        assert rutina_encontrada is not None
        assert rutina_encontrada.nombre == "Rutina DAO"
        assert rutina_encontrada.descripcion == "Rutina de prueba"
        assert rutina_encontrada.objetivo == "Mejorar resistencia"
        assert rutina_encontrada.nivel == NivelRutina.BASICO
        assert rutina_encontrada.nivel.value == "BASICO"
        assert rutina_encontrada.duracion_semanas == 4

        rutinas = dao.listar()

        assert any(
            rutina_item.id_rutina == rutina_guardada.id_rutina
            for rutina_item in rutinas
        )

    finally:
        if rutina_guardada is not None:
            dao.eliminar_por_id(rutina_guardada.id_rutina)


def test_ejercicio_dao():
    dao = EjercicioDAO()

    ejercicio = EjercicioCardio(
        nombre="Ejercicio DAO",
        descripcion="Ejercicio de prueba",
        tipo="Aeróbico",
        duracion_minutos=30,
        intensidad="MEDIA",
        calorias_estimadas=180.0,
    )

    ejercicio_guardado = None

    try:
        ejercicio_guardado = dao.guardar(ejercicio)

        assert ejercicio_guardado.id_ejercicio is not None
        assert ejercicio_guardado.intensidad == Intensidad.MEDIA
        assert ejercicio_guardado.intensidad.value == "MEDIA"

        ejercicios = dao.listar_ejercicios()

        ejercicio_encontrado = next(
            (
                ejercicio_item
                for ejercicio_item in ejercicios
                if ejercicio_item.id_ejercicio
                == ejercicio_guardado.id_ejercicio
            ),
            None,
        )

        assert ejercicio_encontrado is not None
        assert ejercicio_encontrado.nombre == "Ejercicio DAO"
        assert ejercicio_encontrado.descripcion == "Ejercicio de prueba"
        assert ejercicio_encontrado.tipo == "Aeróbico"
        assert ejercicio_encontrado.duracion_minutos == 30
        assert ejercicio_encontrado.intensidad == Intensidad.MEDIA
        assert ejercicio_encontrado.intensidad.value == "MEDIA"
        assert float(ejercicio_encontrado.calorias_estimadas) == 180.0
        assert ejercicio_encontrado.calcular_calorias() == 180.0

    finally:
        if ejercicio_guardado is not None:
            dao.eliminar_por_id(ejercicio_guardado.id_ejercicio)