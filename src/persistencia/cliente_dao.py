from decimal import Decimal
from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import (
    GestorSeguridad,
)


class ClienteDAO:
    """
    DAO para la entidad Cliente.

    La contraseña debe llegar convertida a hash bcrypt
    dentro de cliente.contrasenia_hash.
    """

    def __init__(self) -> None:
        self._bd = (
            ConexionBD.obtener_instancia()
        )

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
                (
                    "El hash de la contraseña no puede "
                    "estar vacío."
                )
            )

        if not hash_guardado.startswith(
            (
                "$2a$",
                "$2b$",
                "$2y$",
            )
        ):
            raise ValueError(
                (
                    "La contraseña debe estar almacenada "
                    "como hash bcrypt."
                )
            )

        if len(hash_guardado) != 60:
            raise ValueError(
                (
                    "El hash bcrypt debe tener 60 "
                    "caracteres."
                )
            )

    @staticmethod
    def _normalizar_correo(
        correo: str,
    ) -> str:
        """
        Limpia y normaliza un correo.
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

    @staticmethod
    def _normalizar_genero(
        genero: str,
    ) -> str:
        """
        Normaliza y valida el género.
        """
        if not isinstance(genero, str):
            raise ValueError(
                "El género debe ser texto."
            )

        genero_limpio = genero.strip().upper()

        opciones_validas = {
            "HOMBRE",
            "MUJER",
            "OTRO",
            "PREFIERO NO DECIRLO",
        }

        if genero_limpio not in opciones_validas:
            raise ValueError(
                (
                    "El género debe ser HOMBRE, MUJER, "
                    "OTRO o PREFIERO NO DECIRLO."
                )
            )

        return genero_limpio

    def guardar(
        self,
        cliente: Cliente,
    ) -> Cliente:
        """
        Guarda un cliente nuevo.
        """
        if not isinstance(cliente, Cliente):
            raise TypeError(
                (
                    "Debe proporcionar una instancia "
                    "de Cliente."
                )
            )

        self._validar_hash(
            cliente.contrasenia_hash
        )

        correo_limpio = (
            self._normalizar_correo(
                cliente.correo_electronico
            )
        )

        genero_limpio = (
            self._normalizar_genero(
                cliente.genero
            )
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
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
                    """,
                    (
                        cliente.nombre.strip(),
                        cliente.apellido.strip(),
                        correo_limpio,
                        cliente.contrasenia_hash,
                        cliente.edad,
                        "cliente",
                    ),
                )

                usuario_resultado = (
                    cursor.fetchone()
                )

                if usuario_resultado is None:
                    raise RuntimeError(
                        (
                            "No se pudo obtener el usuario "
                            "creado."
                        )
                    )

                cliente.id_usuario = (
                    usuario_resultado[0]
                )

                cliente.fecha_registro = (
                    usuario_resultado[1]
                )

                cursor.execute(
                    """
                    INSERT INTO clientes (
                        id_usuario,
                        peso,
                        peso_objetivo,
                        altura,
                        objetivo,
                        genero
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING fecha_ingreso
                    """,
                    (
                        cliente.id_usuario,
                        cliente.peso,
                        cliente.peso_objetivo,
                        cliente.altura,
                        cliente.objetivo.strip(),
                        genero_limpio,
                    ),
                )

                cliente_resultado = (
                    cursor.fetchone()
                )

                if cliente_resultado is None:
                    raise RuntimeError(
                        (
                            "No se pudieron obtener los "
                            "datos del cliente creado."
                        )
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
                (
                    "Error de integridad al guardar "
                    f"el cliente: {error}"
                )
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
                cursor.execute(
                    """
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
                        c.peso_objetivo,
                        c.altura,
                        c.objetivo,
                        c.genero,
                        c.fecha_ingreso
                    FROM usuarios AS u
                    JOIN clientes AS c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.id_usuario = %s
                      AND LOWER(
                          CAST(u.tipo_usuario AS TEXT)
                      ) = 'cliente'
                    """,
                    (id_usuario,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_cliente_desde_fila(
                fila
            )

        except Exception:
            self._bd._conexion.rollback()
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
                cursor.execute(
                    """
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
                        c.peso_objetivo,
                        c.altura,
                        c.objetivo,
                        c.genero,
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
                    """,
                    (correo_limpio,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_cliente_desde_fila(
                fila
            )

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar(self) -> List[Cliente]:
        """
        Lista todos los clientes.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
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
                        c.peso_objetivo,
                        c.altura,
                        c.objetivo,
                        c.genero,
                        c.fecha_ingreso
                    FROM usuarios AS u
                    JOIN clientes AS c
                        ON u.id_usuario = c.id_usuario
                    WHERE LOWER(
                        CAST(u.tipo_usuario AS TEXT)
                    ) = 'cliente'
                    ORDER BY u.id_usuario
                    """
                )

                filas = cursor.fetchall()

            return [
                self._crear_cliente_desde_fila(
                    fila
                )
                for fila in filas
            ]

        except Exception:
            self._bd._conexion.rollback()
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
                (
                    "Debe proporcionar una instancia "
                    "de Cliente."
                )
            )

        self._validar_id(
            cliente.id_usuario
        )

        correo_limpio = (
            self._normalizar_correo(
                cliente.correo_electronico
            )
        )

        genero_limpio = (
            self._normalizar_genero(
                cliente.genero
            )
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
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
                    """,
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

                cursor.execute(
                    """
                    UPDATE clientes
                    SET
                        peso = %s,
                        peso_objetivo = %s,
                        altura = %s,
                        objetivo = %s,
                        genero = %s
                    WHERE id_usuario = %s
                    """,
                    (
                        cliente.peso,
                        cliente.peso_objetivo,
                        cliente.altura,
                        cliente.objetivo.strip(),
                        genero_limpio,
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        (
                            "No se encontraron los datos "
                            "del cliente."
                        )
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
                (
                    "Error de integridad al actualizar "
                    f"el cliente: {error}"
                )
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def actualizar_peso(
        self,
        id_usuario: int,
        nuevo_peso,
    ) -> bool:
        """
        Actualiza solamente el peso actual.
        """
        self._validar_id(id_usuario)

        if (
            nuevo_peso is None
            or nuevo_peso <= 0
        ):
            raise ValueError(
                (
                    "El nuevo peso debe ser "
                    "mayor que cero."
                )
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE clientes
                    SET peso = %s
                    WHERE id_usuario = %s
                    """,
                    (
                        nuevo_peso,
                        id_usuario,
                    ),
                )

                actualizado = (
                    cursor.rowcount > 0
                )

            self._bd._conexion.commit()

            return actualizado

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
                (
                    "La contraseña actual es "
                    "obligatoria."
                )
            )

        if (
            not isinstance(
                nueva_contrasenia,
                str,
            )
            or not nueva_contrasenia
        ):
            raise ValueError(
                (
                    "La nueva contraseña no puede "
                    "estar vacía."
                )
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

                actualizado = (
                    cursor.rowcount > 0
                )

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

                eliminado = (
                    cursor.rowcount > 0
                )

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

        Orden esperado:
        0  id_usuario
        1  nombre
        2  apellido
        3  correo_electronico
        4  contrasenia_hash
        5  edad
        6  tipo_usuario
        7  fecha_registro
        8  peso
        9  peso_objetivo
        10 altura
        11 objetivo
        12 genero
        13 fecha_ingreso
        """
        peso_objetivo = fila[9]

        if peso_objetivo is None:
            peso_objetivo = fila[8]

        genero = fila[12]

        if genero is None or not str(genero).strip():
            genero = "PREFIERO NO DECIRLO"

        return Cliente(
            id_usuario=fila[0],
            nombre=fila[1],
            apellido=fila[2],
            correo_electronico=fila[3],
            contrasenia_hash=fila[4],
            edad=fila[5],
            genero=str(genero),
            peso=fila[8],
            peso_objetivo=peso_objetivo,
            altura=fila[10],
            objetivo=fila[11],
            fecha_registro=fila[7],
            fecha_ingreso=fila[13],
        )

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
                (
                    "El ID de usuario debe ser un "
                    "entero positivo."
                )
            )