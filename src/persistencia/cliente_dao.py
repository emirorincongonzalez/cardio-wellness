from typing import List, Optional, Tuple
from datetime import date

from psycopg2 import IntegrityError

from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class ClienteDAO:
    def __init__(self) -> None:
        """Inicializa el DAO con la conexión Singleton."""
        self._bd = ConexionBD.obtener_instancia()

    def guardar(self, cliente: Cliente) -> Cliente:
        """
        Guarda un nuevo cliente en la base de datos.

        Inserta los datos generales en usuarios y los datos específicos
        en clientes. Actualiza el objeto con los IDs y fechas generados.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                contrasenia_hash = cliente.contrasenia_hash

                consulta_usuario = """
                    INSERT INTO usuarios (
                        nombre,
                        apellido,
                        correo_electronico,
                        "contraseña_hash",
                        edad,
                        tipo_usuario
                    )
                    VALUES (%s, %s, %s, %s, %s, 'cliente')
                    RETURNING id_usuario, fecha_registro
                """

                cursor.execute(
                    consulta_usuario,
                    (
                        cliente.nombre,
                        cliente.apellido,
                        cliente.correo_electronico,
                        contrasenia_hash,
                        cliente.edad,
                    ),
                )

                usuario_resultado = cursor.fetchone()

                if usuario_resultado is None:
                    raise RuntimeError(
                        "No se pudo obtener el usuario creado."
                    )

                cliente.id_usuario = usuario_resultado[0]
                cliente.fecha_registro = usuario_resultado[1]

                consulta_cliente = """
                    INSERT INTO clientes (
                        id_usuario,
                        peso,
                        altura,
                        objetivo
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING fecha_ingreso
                """

                cursor.execute(
                    consulta_cliente,
                    (
                        cliente.id_usuario,
                        cliente.peso,
                        cliente.altura,
                        cliente.objetivo,
                    ),
                )

                cliente_resultado = cursor.fetchone()

                if cliente_resultado is None:
                    raise RuntimeError(
                        "No se pudieron obtener los datos del cliente creado."
                    )

                cliente.fecha_ingreso = cliente_resultado[0]

            self._bd._conexion.commit()
            return cliente

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            raise

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(self, id_usuario: int) -> Optional[Cliente]:
        """Busca un cliente por su ID de usuario."""
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u."contraseña_hash",
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios u
                    JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.id_usuario = %s
                      AND u.tipo_usuario = 'cliente'
                """

                cursor.execute(consulta, (id_usuario,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return self._crear_cliente_desde_fila(fila)

        except Exception:
            raise

    def buscar_por_correo(self, correo: str) -> Optional[Cliente]:
        """Busca un cliente por su correo electrónico."""
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u."contraseña_hash",
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios u
                    JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.correo_electronico = %s
                      AND u.tipo_usuario = 'cliente'
                """

                cursor.execute(consulta, (correo,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return self._crear_cliente_desde_fila(fila)

        except Exception:
            raise

    def listar(self) -> List[Cliente]:
        """Lista todos los clientes del sistema."""
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u."contraseña_hash",
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios u
                    JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.tipo_usuario = 'cliente'
                    ORDER BY u.id_usuario
                """

                cursor.execute(consulta)
                filas = cursor.fetchall()

                return [
                    self._crear_cliente_desde_fila(fila)
                    for fila in filas
                ]

        except Exception:
            raise

    def actualizar(self, cliente: Cliente) -> Cliente:
        """
        Actualiza los datos de un cliente existente.

        Requiere que el cliente tenga un ID de usuario.
        """
        if cliente.id_usuario is None:
            raise ValueError(
                "El cliente debe tener un id para actualizarse."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta_usuario = """
                    UPDATE usuarios
                    SET nombre = %s,
                        apellido = %s,
                        correo_electronico = %s,
                        edad = %s
                    WHERE id_usuario = %s
                      AND tipo_usuario = 'cliente'
                """

                cursor.execute(
                    consulta_usuario,
                    (
                        cliente.nombre,
                        cliente.apellido,
                        cliente.correo_electronico,
                        cliente.edad,
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError("No se encontró el cliente.")

                consulta_cliente = """
                    UPDATE clientes
                    SET peso = %s,
                        altura = %s,
                        objetivo = %s
                    WHERE id_usuario = %s
                """

                cursor.execute(
                    consulta_cliente,
                    (
                        cliente.peso,
                        cliente.altura,
                        cliente.objetivo,
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontraron los datos del cliente."
                    )

            self._bd._conexion.commit()
            return cliente

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            raise

        except Exception:
            self._bd._conexion.rollback()
            raise

    def actualizar_contrasenia(
        self,
        id_usuario: int,
        contrasenia_actual: str,
        nueva_contrasenia: str,
    ) -> bool:
        """
        Cambia la contraseña de un cliente después de verificar la actual.

        Retorna True si se actualizó correctamente. Retorna False si:
        - El cliente no existe.
        - La contraseña actual es incorrecta.
        """
        if not nueva_contrasenia:
            raise ValueError(
                "La nueva contraseña no puede estar vacía."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT "contraseña_hash"
                    FROM usuarios
                    WHERE id_usuario = %s
                      AND tipo_usuario = 'cliente'
                    """,
                    (id_usuario,),
                )

                fila = cursor.fetchone()

                if fila is None:
                    return False

                hash_guardado = fila[0]

                contrasenia_valida = (
                    GestorSeguridad.verificar_contrasenia(
                        contrasenia_actual,
                        hash_guardado,
                    )
                )

                if not contrasenia_valida:
                    return False

                nuevo_hash = GestorSeguridad.generar_hash(
                    nueva_contrasenia
                )

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET "contraseña_hash" = %s
                    WHERE id_usuario = %s
                      AND tipo_usuario = 'cliente'
                    """,
                    (nuevo_hash, id_usuario),
                )

                if cursor.rowcount == 0:
                    return False

            self._bd._conexion.commit()
            return True

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(self, id_usuario: int) -> bool:
        """
        Elimina un cliente y su usuario asociado por su ID.

        Retorna True si se eliminó y False si no existía.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = %s
                      AND tipo_usuario = 'cliente'
                    """,
                    (id_usuario,),
                )

                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_cliente_desde_fila(fila: Tuple) -> Cliente:
        """
        Crea un objeto Cliente a partir de una fila de la base de datos.

        Orden esperado de la fila:

        0. id_usuario
        1. nombre
        2. apellido
        3. correo_electronico
        4. contraseña_hash
        5. edad
        6. tipo_usuario (NO SE USA)
        7. fecha_registro
        8. peso
        9. altura
        10. objetivo
        11. fecha_ingreso
        """
        cliente = Cliente(
            id_usuario=fila[0],
            nombre=fila[1],
            apellido=fila[2],
            correo_electronico=fila[3],
            contrasenia_hash=fila[4],
            edad=fila[5],
            peso=fila[8],
            altura=fila[9],
            objetivo=fila[10],
            fecha_registro=fila[7],
        )
        # Setear fecha_ingreso como propiedad (no como parámetro del constructor)
        cliente._fecha_ingreso = fila[11] if fila[11] is not None else date.today()
        return cliente