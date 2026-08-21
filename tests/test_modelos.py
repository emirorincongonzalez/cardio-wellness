import pytest
from datetime import date
from decimal import Decimal

from src.modelos.cliente import Cliente
from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.enums import Intensidad, NivelRutina
from src.modelos.rutina import Rutina
from src.modelos.usuario import Usuario


def crear_cliente():
    return Cliente(
        nombre="Ana",
        apellido="Perez",
        correo_electronico="ana@example.com",
        contrasenia_hash="Clave123",
        edad=30,
        peso=70.0,
        altura=1.70,
        objetivo="Mejorar salud",
    )


def crear_rutina():
    return Rutina(
        nombre="Rutina de prueba",
        descripcion="Descripción de prueba",
        objetivo="Mejorar resistencia",
        nivel="BASICO",
        duracion_semanas=4,
    )


def crear_ejercicio(
    nombre="Caminata",
    duracion=30,
    intensidad="MEDIA",
    calorias=180.0,
):
    return EjercicioCardio(
        nombre=nombre,
        descripcion="Ejercicio de prueba",
        tipo="Aeróbico",
        duracion_minutos=duracion,
        intensidad=intensidad,
        calorias_estimadas=calorias,
    )


# =========================
# Pruebas de Usuario
# =========================

def test_usuario_es_abstracto():
    with pytest.raises(TypeError):
        Usuario(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
        )


def test_usuario_rechaza_nombre_vacio():
    with pytest.raises(ValueError):
        Cliente(
            nombre="",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=70,
            altura=1.70,
            objetivo="Mejorar salud",
        )


def test_usuario_rechaza_apellido_vacio():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=70,
            altura=1.70,
            objetivo="Mejorar salud",
        )


def test_usuario_rechaza_edad_cero():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=0,
            peso=70,
            altura=1.70,
            objetivo="Mejorar salud",
        )


def test_usuario_rechaza_edad_negativa():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=-1,
            peso=70,
            altura=1.70,
            objetivo="Mejorar salud",
        )


def test_usuario_obtiene_nombre_completo():
    cliente = crear_cliente()

    assert cliente.obtener_nombre_completo() == "Ana Perez"


# =========================
# Pruebas de Cliente
# =========================

def test_cliente_fuerza_tipo_cliente():
    cliente = crear_cliente()

    assert cliente.tipo_usuario == "cliente"
    assert cliente.obtener_tipo_usuario() == "cliente"


def test_cliente_fecha_ingreso_por_defecto():
    cliente = crear_cliente()

    assert cliente.fecha_ingreso == date.today()


def test_cliente_rechaza_peso_cero():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=0,
            altura=1.70,
            objetivo="Mejorar salud",
        )


def test_cliente_rechaza_peso_negativo():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=-10,
            altura=1.70,
            objetivo="Mejorar salud",
        )


def test_cliente_rechaza_altura_cero():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=70,
            altura=0,
            objetivo="Mejorar salud",
        )


def test_cliente_rechaza_altura_negativa():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=70,
            altura=-1.70,
            objetivo="Mejorar salud",
        )


def test_cliente_rechaza_objetivo_vacio():
    with pytest.raises(ValueError):
        Cliente(
            nombre="Ana",
            apellido="Perez",
            correo_electronico="ana@example.com",
            contrasenia_hash="Clave123",
            edad=30,
            peso=70,
            altura=1.70,
            objetivo="",
        )


def test_cliente_acepta_decimal():
    cliente = Cliente(
        nombre="Ana",
        apellido="Perez",
        correo_electronico="ana@example.com",
        contrasenia_hash="Clave123",
        edad=30,
        peso=Decimal("70.50"),
        altura=Decimal("1.70"),
        objetivo="Mejorar salud",
    )

    assert cliente.peso == Decimal("70.50")
    assert cliente.altura == Decimal("1.70")


# =========================
# Pruebas de Rutina
# =========================

def test_rutina_convierte_nivel_a_enum():
    rutina = crear_rutina()

    assert rutina.nivel == NivelRutina.BASICO
    assert rutina.nivel.value == "BASICO"


def test_rutina_acepta_miembro_del_enum():
    rutina = Rutina(
        nombre="Rutina avanzada",
        descripcion="Descripción",
        objetivo="Mejorar fuerza",
        nivel=NivelRutina.AVANZADO,
        duracion_semanas=8,
    )

    assert rutina.nivel is NivelRutina.AVANZADO


def test_rutina_fecha_creacion_por_defecto():
    rutina = crear_rutina()

    assert rutina.fecha_creacion == date.today()


def test_rutina_rechaza_nombre_vacio():
    with pytest.raises(ValueError):
        Rutina(
            nombre="",
            descripcion="Descripción",
            objetivo="Objetivo",
            nivel="BASICO",
            duracion_semanas=4,
        )


def test_rutina_rechaza_descripcion_vacia():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="",
            objetivo="Objetivo",
            nivel="BASICO",
            duracion_semanas=4,
        )


def test_rutina_rechaza_objetivo_vacio():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="Descripción",
            objetivo="",
            nivel="BASICO",
            duracion_semanas=4,
        )


def test_rutina_rechaza_duracion_cero():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="Descripción",
            objetivo="Objetivo",
            nivel="BASICO",
            duracion_semanas=0,
        )


def test_rutina_rechaza_duracion_negativa():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="Descripción",
            objetivo="Objetivo",
            nivel="BASICO",
            duracion_semanas=-1,
        )


def test_rutina_rechaza_duracion_decimal():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="Descripción",
            objetivo="Objetivo",
            nivel="BASICO",
            duracion_semanas=4.5,
        )


def test_rutina_rechaza_nivel_invalido():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="Descripción",
            objetivo="Objetivo",
            nivel="EXPERTO",
            duracion_semanas=4,
        )


def test_rutina_acepta_creado_por():
    rutina = Rutina(
        nombre="Rutina",
        descripcion="Descripción",
        objetivo="Objetivo",
        nivel="BASICO",
        duracion_semanas=4,
        creado_por=15,
    )

    assert rutina.creado_por == 15


def test_rutina_rechaza_creado_por_cero():
    with pytest.raises(ValueError):
        Rutina(
            nombre="Rutina",
            descripcion="Descripción",
            objetivo="Objetivo",
            nivel="BASICO",
            duracion_semanas=4,
            creado_por=0,
        )


def test_rutina_agrega_ejercicio():
    rutina = crear_rutina()
    ejercicio = crear_ejercicio()

    rutina.agregar_ejercicio(ejercicio)

    assert ejercicio in rutina.ejercicios
    assert len(rutina.ejercicios) == 1


def test_rutina_agrega_ejercicio_con_id():
    rutina = crear_rutina()

    ejercicio = EjercicioCardio(
        nombre="Caminata",
        descripcion="Caminata de prueba",
        tipo="Aeróbico",
        duracion_minutos=30,
        intensidad="MEDIA",
        calorias_estimadas=180.0,
        id_ejercicio=10,
    )

    rutina.agregar_ejercicio(ejercicio)

    assert rutina.id_ejercicios == (10,)


def test_rutina_rechaza_ejercicio_none():
    rutina = crear_rutina()

    with pytest.raises(TypeError):
        rutina.agregar_ejercicio(None)


def test_rutina_rechaza_objeto_invalido():
    rutina = crear_rutina()

    with pytest.raises(TypeError):
        rutina.agregar_ejercicio("No es un ejercicio")


def test_rutina_rechaza_ejercicio_duplicado():
    rutina = crear_rutina()
    ejercicio = crear_ejercicio()

    rutina.agregar_ejercicio(ejercicio)

    with pytest.raises(ValueError):
        rutina.agregar_ejercicio(ejercicio)


def test_rutina_elimina_ejercicio():
    rutina = crear_rutina()
    ejercicio = crear_ejercicio()

    rutina.agregar_ejercicio(ejercicio)
    rutina.eliminar_ejercicio(ejercicio)

    assert ejercicio not in rutina.ejercicios
    assert rutina.calcular_duracion_total() == 0


def test_rutina_rechaza_eliminar_ejercicio_inexistente():
    rutina = crear_rutina()
    ejercicio = crear_ejercicio()

    with pytest.raises(ValueError):
        rutina.eliminar_ejercicio(ejercicio)


def test_rutina_calcula_duracion_total():
    rutina = crear_rutina()

    rutina.agregar_ejercicio(
        crear_ejercicio(
            nombre="Caminata",
            duracion=30,
        )
    )

    rutina.agregar_ejercicio(
        crear_ejercicio(
            nombre="Bicicleta",
            duracion=20,
        )
    )

    rutina.agregar_ejercicio(
        crear_ejercicio(
            nombre="Natación",
            duracion=45,
        )
    )

    assert rutina.calcular_duracion_total() == 95


# =========================
# Pruebas de EjercicioCardio
# =========================

def test_ejercicio_convierte_intensidad_a_enum():
    ejercicio = crear_ejercicio(intensidad="MEDIA")

    assert ejercicio.intensidad == Intensidad.MEDIA
    assert ejercicio.intensidad.value == "MEDIA"


def test_ejercicio_acepta_miembro_del_enum():
    ejercicio = crear_ejercicio(
        intensidad=Intensidad.ALTA
    )

    assert ejercicio.intensidad is Intensidad.ALTA


def test_ejercicio_rechaza_nombre_vacio():
    with pytest.raises(ValueError):
        EjercicioCardio(
            nombre="",
            descripcion="Descripción",
            tipo="Aeróbico",
            duracion_minutos=30,
            intensidad="MEDIA",
            calorias_estimadas=180.0,
        )


def test_ejercicio_rechaza_descripcion_vacia():
    with pytest.raises(ValueError):
        EjercicioCardio(
            nombre="Caminata",
            descripcion="",
            tipo="Aeróbico",
            duracion_minutos=30,
            intensidad="MEDIA",
            calorias_estimadas=180.0,
        )


def test_ejercicio_rechaza_tipo_vacio():
    with pytest.raises(ValueError):
        EjercicioCardio(
            nombre="Caminata",
            descripcion="Descripción",
            tipo="",
            duracion_minutos=30,
            intensidad="MEDIA",
            calorias_estimadas=180.0,
        )


def test_ejercicio_rechaza_duracion_cero():
    with pytest.raises(ValueError):
        crear_ejercicio(duracion=0)


def test_ejercicio_rechaza_duracion_negativa():
    with pytest.raises(ValueError):
        crear_ejercicio(duracion=-5)


def test_ejercicio_rechaza_intensidad_invalida():
    with pytest.raises(ValueError):
        crear_ejercicio(intensidad="EXTREMA")


def test_ejercicio_rechaza_calorias_negativas():
    with pytest.raises(ValueError):
        crear_ejercicio(calorias=-1)


def test_ejercicio_acepta_calorias_cero():
    ejercicio = crear_ejercicio(calorias=0)

    assert ejercicio.calorias_estimadas == 0


def test_ejercicio_acepta_decimal():
    ejercicio = EjercicioCardio(
        nombre="Caminata",
        descripcion="Descripción",
        tipo="Aeróbico",
        duracion_minutos=Decimal("30.00"),
        intensidad=Intensidad.BAJA,
        calorias_estimadas=Decimal("150.50"),
    )

    assert ejercicio.duracion_minutos == Decimal("30.00")
    assert ejercicio.calorias_estimadas == Decimal("150.50")


def test_ejercicio_calcula_calorias():
    ejercicio = crear_ejercicio(calorias=180.0)

    assert ejercicio.calcular_calorias() == 180.0


def test_ejercicio_calcula_calorias_decimal():
    ejercicio = EjercicioCardio(
        nombre="Caminata",
        descripcion="Descripción",
        tipo="Aeróbico",
        duracion_minutos=30,
        intensidad="MEDIA",
        calorias_estimadas=Decimal("180.50"),
    )

    assert ejercicio.calcular_calorias() == 180.50


def test_ejercicio_acepta_creado_por():
    ejercicio = crear_ejercicio()

    ejercicio.creado_por = 20

    assert ejercicio.creado_por == 20


def test_ejercicio_rechaza_creado_por_cero():
    with pytest.raises(ValueError):
        EjercicioCardio(
            nombre="Caminata",
            descripcion="Descripción",
            tipo="Aeróbico",
            duracion_minutos=30,
            intensidad="MEDIA",
            calorias_estimadas=180.0,
            creado_por=0,
        )