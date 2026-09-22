from datetime import date
from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class ClienteDAO:
    """
    DAO para la entidad Cliente.

    La contraseña debe llegar ya convertida a hash bcrypt
    dentro de cliente.contrasenia_hash.
    """

    def __init__(self) -> None:
        self._bd = ConexionBD.obtener_instancia()

    @staticmethod
    def _validar_hash(
        hash_guardado: str,
    ) -> None:
        """
        Valida que el valor sea un hash bcrypt.
        """
        if (
            not isinstance(hash_guardado, str)
            or not hash_guardado
        ):
            raise ValueError(
                "El hash de la contraseña no puede "
                "estar vacío."
            )

        if not hash_guardado.startswith(
            ("$2a$", "$2b$", "$2y$")
        ):
            raise ValueError(
                "La contraseña debe estar almacenada "
                "como hash bcrypt."
            )

        if len(hash_guardado) != 60:
            raise ValueError(
                "El hash bcrypt debe tener 60 "
                "caracteres."
            )

    @staticmethod
    def _normalizar_correo(
        correo: str,
    ) -> str:
        """
        Limpia y normaliza un correo electrónico.
        """
        if not isinstance(correo, str):
            raise ValueError(
                "El correo debe ser una cadena."
            )

        correo_limpio = correo.strip().lower()

        if not correo_limpio:
            raise ValueError(
                "El correo no puede estar vacío."
            )

        return correo_limpio

    def guardar(
        self,
        cliente: Cliente,
    ) -> Cliente:
        """
        Guarda un cliente nuevo.

        El hash bcrypt debe haber sido generado
        previamente por ControlClientes.
        """
        if not isinstance(cliente, Cliente):
            raise TypeError(
                "Debe proporcionar una instancia de Cliente."
            )

        hash_guardado = cliente.contrasenia_hash

        self._validar_hash(hash_guardado)

        correo_limpio = (
            self._normalizar_correo(
                cliente.correo_electronico
            )
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta_usuario = """
                    INSERT INTO usuarios (
                        nombre,
                        apellido,
                        correo_electronico,
                        contrasenia_hash,
                        edad,
                        tipo_usuario
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING
                        id_usuario,
                        fecha_registro
                """

                cursor.execute(
                    consulta_usuario,
                    (
                        cliente.nombre.strip(),
                        cliente.apellido.strip(),
                        correo_limpio,
                        hash_guardado,
                        cliente.edad,
                        "cliente",
                    ),
                )

                usuario_resultado = (
                    cursor.fetchone()
                )

                if usuario_resultado is None:
                    raise RuntimeError(
                        "No se pudo obtener el usuario "
                        "creado."
                    )

                cliente.id_usuario = (
                    usuario_resultado[0]
                )

                cliente.fecha_registro = (
                    usuario_resultado[1]
                )

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
                        cliente.objetivo.strip(),
                    ),
                )

                cliente_resultado = (
                    cursor.fetchone()
                )

                if cliente_resultado is None:
                    raise RuntimeError(
                        "No se pudieron obtener los "
                        "datos del cliente creado."
                    )

                cliente.fecha_ingreso = (
                    cliente_resultado[0]
                )

            self._bd._conexion.commit()

            return cliente

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            if error.pgcode == "23503":
                raise ValueError(
                    "No existe una referencia relacionada."
                ) from error

            raise RuntimeError(
                "Error de integridad al guardar "
                f"el cliente: {error}"
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(
        self,
        id_usuario: int,
    ) -> Optional[Cliente]:
        """
        Busca un cliente por su ID de usuario.
        """
        self._validar_id(id_usuario)
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u.contrasenia_hash,
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios AS u
                    JOIN clientes AS c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.id_usuario = %s
                      AND LOWER(
                          CAST(u.tipo_usuario AS TEXT)
                      ) = 'cliente'
                """

                cursor.execute(
                    consulta,
                    (id_usuario,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_cliente_desde_fila(fila)

        except Exception:
            raise

    def buscar_por_correo(
        self,
        correo: str,
    ) -> Optional[Cliente]:
        """
        Busca un cliente por correo.
        """
        correo_limpio = (
            self._normalizar_correo(correo)
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u.contrasenia_hash,
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios AS u
                    JOIN clientes AS c
                        ON u.id_usuario = c.id_usuario
                    WHERE LOWER(
                        u.correo_electronico
                    ) = %s
                      AND LOWER(
                          CAST(u.tipo_usuario AS TEXT)
                      ) = 'cliente'
                    LIMIT 1
                """

                cursor.execute(
                    consulta,
                    (correo_limpio,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_cliente_desde_fila(fila)

        except Exception:
            raise

    def listar(self) -> List[Cliente]:
        """
        Lista todos los clientes.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u.contrasenia_hash,
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios AS u
                    JOIN clientes AS c
                        ON u.id_usuario = c.id_usuario
                    WHERE LOWER(
                        CAST(u.tipo_usuario AS TEXT)
                    ) = 'cliente'
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

    def actualizar(
        self,
        cliente: Cliente,
    ) -> Cliente:
        """
        Actualiza los datos de un cliente.
        """
        if not isinstance(cliente, Cliente):
            raise TypeError(
                "Debe proporcionar una instancia de Cliente."
            )

        self._validar_id(cliente.id_usuario)
        correo_limpio = (
            self._normalizar_correo(
                cliente.correo_electronico
            )
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta_usuario = """
                    UPDATE usuarios
                    SET
                        nombre = %s,
                        apellido = %s,
                        correo_electronico = %s,
                        edad = %s
                    WHERE id_usuario = %s
                      AND LOWER(
                          CAST(tipo_usuario AS TEXT)
                      ) = 'cliente'
                """

                cursor.execute(
                    consulta_usuario,
                    (
                        cliente.nombre.strip(),
                        cliente.apellido.strip(),
                        correo_limpio,
                        cliente.edad,
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontró el cliente."
                    )

                consulta_cliente = """
                    UPDATE clientes
                    SET
                        peso = %s,
                        altura = %s,
                        objetivo = %s
                    WHERE id_usuario = %s
                """

                cursor.execute(
                    consulta_cliente,
                    (
                        cliente.peso,
                        cliente.altura,
                        cliente.objetivo.strip(),
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontraron los datos "
                        "del cliente."
                    )

            self._bd._conexion.commit()

            return cliente

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            raise RuntimeError(
                "Error de integridad al actualizar "
                f"el cliente: {error}"
            ) from error

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
        Cambia la contraseña verificando la actual.
        """
        self._validar_id(id_usuario)

        if (
            not isinstance(
                contrasenia_actual,
                str,
            )
            or not contrasenia_actual
        ):
            raise ValueError(
                "La contraseña actual es obligatoria."
            )

        if (
            not isinstance(
                nueva_contrasenia,
                str,
            )
            or not nueva_contrasenia
        ):
            raise ValueError(
                "La nueva contraseña no puede estar "
                "vacía."
            )

        if not GestorSeguridad.validar_fortaleza_contrasena(
            nueva_contrasenia
        ):
            raise ValueError(
                "La nueva contraseña es muy débil."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT contrasenia_hash
                    FROM usuarios
                    WHERE id_usuario = %s
                      AND LOWER(
                          CAST(tipo_usuario AS TEXT)
                      ) = 'cliente'
                    """,
                    (id_usuario,),
                )

                fila = cursor.fetchone()

                if fila is None:
                    return False

                hash_guardado = fila[0]

                if not GestorSeguridad.verificar_contrasenia(
                    contrasenia_actual,
                    hash_guardado,
                ):
                    return False

                nuevo_hash = (
                    GestorSeguridad.generar_hash(
                        nueva_contrasenia
                    )
                )

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET contrasenia_hash = %s
                    WHERE id_usuario = %s
                      AND LOWER(
                          CAST(tipo_usuario AS TEXT)
                      ) = 'cliente'
                    """,
                    (
                        nuevo_hash,
                        id_usuario,
                    ),
                )

                actualizado = cursor.rowcount > 0

            self._bd._conexion.commit()

            return actualizado

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_usuario: int,
    ) -> bool:
        """
        Elimina un cliente por ID.
        """
        self._validar_id(id_usuario)
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = %s
                      AND LOWER(
                          CAST(tipo_usuario AS TEXT)
                      ) = 'cliente'
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
    def _crear_cliente_desde_fila(
        fila: Tuple,
    ) -> Cliente:
        """
        Convierte una fila de PostgreSQL en Cliente.
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

        cliente._fecha_ingreso = (
            fila[11]
            if fila[11] is not None
            else date.today()
        )

        return cliente

    @staticmethod
    def _validar_id(
        id_usuario: int,
    ) -> None:
        """
        Valida un ID de usuario.
        """
        if (
            not isinstance(id_usuario, int)
            or isinstance(id_usuario, bool)
            or id_usuario <= 0
        ):
            raise ValueError(
                "El ID de usuario debe ser un entero "
                "positivo."
            )