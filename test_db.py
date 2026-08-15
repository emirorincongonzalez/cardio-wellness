import os
import sys
from decimal import Decimal

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def imprimir_configuracion():
    print("⚙️ Configuración cargada:")

    claves = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    for clave in claves:
        valor = os.getenv(clave)

        if clave == "DB_PASSWORD":
            valor = "<configurada>" if valor else "<no configurada>"

        print(f"   {clave}: {valor}")

    print()


def obtener_configuracion():
    claves_requeridas = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    faltantes = [
        clave
        for clave in claves_requeridas
        if not os.getenv(clave)
    ]

    if faltantes:
        raise RuntimeError(
            "Faltan variables en el archivo .env: "
            + ", ".join(faltantes)
        )

    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "options": "-c lc_messages=C",
    }


def mostrar_datos_conexion(cursor):
    cursor.execute(
        """
        SELECT
            current_database(),
            current_user,
            version();
        """
    )

    base_datos, usuario, version = cursor.fetchone()

    print("✅ CONEXIÓN EXITOSA")
    print(f"📁 Base de datos: {base_datos}")
    print(f"👤 Usuario: {usuario}")
    print(f"🗄️ Servidor: {version}")
    print()


def mostrar_tablas(cursor):
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
    )

    tablas = cursor.fetchall()

    print(f"📋 Tablas encontradas: {len(tablas)}")

    for tabla in tablas:
        print(f"   - {tabla[0]}")

    print()


def mostrar_vistas(cursor):
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
    )

    vistas = cursor.fetchall()

    print(f"👁️ Vistas encontradas: {len(vistas)}")

    for vista in vistas:
        print(f"   - {vista[0]}")

    print()


def consultar_usuarios(cursor):
    cursor.execute(
        """
        SELECT
            id_usuario,
            nombre,
            apellido,
            correo_electronico,
            tipo_usuario
        FROM usuarios
        ORDER BY id_usuario;
        """
    )

    usuarios = cursor.fetchall()

    print(f"👥 Usuarios registrados: {len(usuarios)}")

    if not usuarios:
        print("   No hay usuarios registrados.")
    else:
        for usuario in usuarios:
            print(f"   {usuario}")

    print()


def consultar_clientes(cursor):
    cursor.execute(
        """
        SELECT
            id_usuario,
            nombre,
            apellido,
            correo_electronico,
            edad,
            peso,
            altura,
            objetivo
        FROM vw_clientes_completo
        ORDER BY id_usuario;
        """
    )

    clientes = cursor.fetchall()

    print(f"🏃 Clientes registrados: {len(clientes)}")

    if not clientes:
        print("   No hay clientes registrados.")
    else:
        for cliente in clientes:
            print(f"   {cliente}")

    print()


def insertar_datos_prueba(cursor):
    correo_prueba = "cliente.prueba@example.com"

    cursor.execute(
        """
        SELECT id_usuario
        FROM usuarios
        WHERE correo_electronico = %s;
        """,
        (correo_prueba,),
    )

    usuario_existente = cursor.fetchone()

    if usuario_existente:
        print("ℹ️ El usuario de prueba ya existe.")
        print()
        return usuario_existente[0], False

    cursor.execute(
        """
        INSERT INTO usuarios (
            nombre,
            apellido,
            correo_electronico,
            "contraseña_hash",
            edad,
            tipo_usuario
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_usuario;
        """,
        (
            "Carlos",
            "Pérez",
            correo_prueba,
            "hash_de_prueba",
            28,
            "cliente",
        ),
    )

    id_usuario = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO clientes (
            id_usuario,
            peso,
            altura,
            objetivo
        )
        VALUES (%s, %s, %s, %s);
        """,
        (
            id_usuario,
            Decimal("82.50"),
            Decimal("1.75"),
            "Bajar de peso",
        ),
    )

    print("✅ Datos de prueba insertados.")
    print(f"   ID del usuario: {id_usuario}")
    print()

    return id_usuario, True


def main():
    print("=" * 60)
    print("PRUEBAS DE CONEXIÓN PYTHON - POSTGRESQL")
    print("=" * 60)
    print()

    try:
        configuracion = obtener_configuracion()

        imprimir_configuracion()

        conexion = psycopg2.connect(**configuracion)

        try:
            with conexion.cursor() as cursor:
                mostrar_datos_conexion(cursor)
                mostrar_tablas(cursor)
                mostrar_vistas(cursor)
                consultar_usuarios(cursor)
                consultar_clientes(cursor)

                _, datos_insertados = insertar_datos_prueba(cursor)

                if datos_insertados:
                    print("🔎 Verificando el cliente insertado:")
                    consultar_clientes(cursor)

                    print("↩️ Revirtiendo datos de prueba...")
                    conexion.rollback()
                    print("✅ Datos de prueba eliminados mediante rollback.")
                    print()
                else:
                    conexion.rollback()

        finally:
            conexion.close()
            print("🔒 Conexión cerrada.")

    except psycopg2.OperationalError as error:
        print("❌ No se pudo conectar con PostgreSQL.")
        print(f"Detalle: {error}")
        sys.exit(1)

    except psycopg2.Error as error:
        print("❌ Error de PostgreSQL.")
        print(f"Detalle: {error}")
        sys.exit(1)

    except Exception as error:
        print("❌ Error en la prueba.")
        print(f"Detalle: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()