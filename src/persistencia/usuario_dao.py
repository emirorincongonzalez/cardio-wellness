from typing import Optional

from psycopg2 import IntegrityError

from src.modelos.administrador import Administrador
from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class UsuarioDAO:
    """
    DAO para usuarios, clientes y administradores.
    """

    def __init__(self) -> None:
        self._conexion = (
            ConexionBD.obtener_instancia()
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

    @staticmethod
    def _obtener_tipo_usuario(
        valor,
    ) -> str:
        """
        Convierte un enum o texto a un tipo normalizado.
        """
        valor = getattr(
            valor,
            "value",
            valor,
        )

        tipo = str(valor).strip().lower()

        if "." in tipo:
            tipo = tipo.split(".")[-1]

        if tipo == "admin":
            return "administrador"

        return tipo

    @staticmethod
    def _validar_usuario(
        usuario,
    ) -> None:
        """
        Valida los datos básicos de un usuario.
        """
        if usuario is None:
            raise ValueError(
                "El usuario no puede ser nulo."
            )

        if not isinstance(
            getattr(usuario, "nombre", None),
            str,
        ) or not usuario.nombre.strip():
            raise ValueError(
                "El nombre no puede estar vacío."
            )

        if not isinstance(
            getattr(usuario, "apellido", None),
            str,
        ) or not usuario.apellido.strip():
            raise ValueError(
                "El apellido no puede estar vacío."
            )

        if not isinstance(
            getattr(usuario, "edad", None),
            int,
        ) or isinstance(usuario.edad, bool):
            raise ValueError(
                "La edad debe ser un entero."
            )

        if usuario.edad <= 0:
            raise ValueError(
                "La edad debe ser positiva."
            )

    def guardar(
        self,
        usuario,
        contrasenia_plana: str,
    ):
        """
        Guarda un usuario.

        La contraseña recibida es plana únicamente durante
        este método. Antes de enviarla a PostgreSQL se
        convierte siempre en un hash bcrypt.
        """
        self._validar_usuario(usuario)

        if (
            not isinstance(contrasenia_plana, str)
            or not contrasenia_plana
        ):
            raise ValueError(
                "La contraseña debe ser una cadena "
                "no vacía."
            )

        correo_limpio = (
            self._normalizar_correo(
                usuario.correo_electronico
            )
        )

        contrasenia_hash = (
            GestorSeguridad.generar_hash(
                contrasenia_plana
            )
        )

        tipo_usuario = (
            self._obtener_tipo_usuario(
                getattr(
                    usuario,
                    "tipo_usuario",
                    None,
                )
            )
        )

        if tipo_usuario not in {
            "cliente",
            "administrador",
        }:
            raise ValueError(
                "El tipo de usuario no es válido."
            )

        sql_usuario = """
            INSERT INTO usuarios (
                nombre,
                apellido,
                correo_electronico,
                contrasenia_hash,
                edad,
                tipo_usuario
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id_usuario,
                fecha_registro
        """

        parametros_usuario = (
            usuario.nombre.strip(),
            usuario.apellido.strip(),
            correo_limpio,
            contrasenia_hash,
            usuario.edad,
            tipo_usuario,
        )

        try:
            resultado = (
                self._conexion.ejecutar_consulta(
                    sql_usuario,
                    parametros_usuario,
                )
            )

            if not resultado:
                raise RuntimeError(
                    "No se pudo guardar el usuario."
                )

            usuario.id_usuario = (
                resultado[0]["id_usuario"]
            )

            usuario.fecha_registro = (
                resultado[0]["fecha_registro"]
            )

            # Mantiene el hash en el objeto sin guardar
            # nunca la contraseña plana.
            if hasattr(usuario, "contrasenia_hash"):
                usuario.contrasenia_hash = (
                    contrasenia_hash
                )

            if isinstance(usuario, Cliente):
                sql_cliente = """
                    INSERT INTO clientes (
                        id_usuario,
                        peso,
                        altura,
                        objetivo
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING fecha_ingreso
                """

                parametros_cliente = (
                    usuario.id_usuario,
                    usuario.peso,
                    usuario.altura,
                    usuario.objetivo,
                )

                resultado_cliente = (
                    self._conexion.ejecutar_consulta(
                        sql_cliente,
                        parametros_cliente,
                    )
                )

                if resultado_cliente:
                    usuario.fecha_ingreso = (
                        resultado_cliente[0][
                            "fecha_ingreso"
                        ]
                    )

            self._conexion._conexion.commit()

            return usuario

        except IntegrityError as error:
            self._conexion._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            if error.pgcode == "23503":
                raise ValueError(
                    "La información relacionada "
                    "no existe."
                ) from error

            raise RuntimeError(
                "Error de integridad al guardar "
                f"el usuario: {error}"
            ) from error

        except Exception:
            self._conexion._conexion.rollback()
            raise

    def buscar_por_correo(
        self,
        correo: str,
    ) -> Optional[object]:
        """
        Busca un usuario por correo.
        """
        correo_limpio = (
            self._normalizar_correo(correo)
        )

        sql = """
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
            LEFT JOIN clientes AS c
                ON u.id_usuario = c.id_usuario
            WHERE LOWER(u.correo_electronico) = %s
            LIMIT 1
        """

        resultado = (
            self._conexion.ejecutar_consulta(
                sql,
                (correo_limpio,),
            )
        )

        if not resultado:
            return None

        fila = resultado[0]

        tipo_usuario = (
            self._obtener_tipo_usuario(
                fila["tipo_usuario"]
            )
        )

        if tipo_usuario == "cliente":
            return Cliente(
                id_usuario=fila["id_usuario"],
                nombre=fila["nombre"],
                apellido=fila["apellido"],
                correo_electronico=(
                    fila["correo_electronico"]
                ),
                contrasenia_hash=(
                    fila["contrasenia_hash"]
                ),
                edad=fila["edad"],
                fecha_registro=(
                    fila["fecha_registro"]
                ),
                peso=(
                    float(fila["peso"])
                    if fila["peso"] is not None
                    else None
                ),
                altura=(
                    float(fila["altura"])
                    if fila["altura"] is not None
                    else None
                ),
                objetivo=fila["objetivo"],
                fecha_ingreso=(
                    fila["fecha_ingreso"]
                ),
            )

        if tipo_usuario == "administrador":
            return Administrador(
                id_usuario=fila["id_usuario"],
                nombre=fila["nombre"],
                apellido=fila["apellido"],
                correo_electronico=(
                    fila["correo_electronico"]
                ),
                contrasenia_hash=(
                    fila["contrasenia_hash"]
                ),
                edad=fila["edad"],
                fecha_registro=(
                    fila["fecha_registro"]
                ),
            )

        raise ValueError(
            "Tipo de usuario desconocido: "
            f"{tipo_usuario}"
        )

    def iniciar_sesion(
        self,
        correo: str,
        contrasenia: str,
    ) -> Optional[object]:
        """
        Busca el usuario y verifica la contraseña.
        """
        if not isinstance(correo, str):
            return None

        if not isinstance(contrasenia, str):
            return None

        if not contrasenia:
            return None

        try:
            usuario = self.buscar_por_correo(
                correo
            )
        except (
            ValueError,
            RuntimeError,
        ):
            return None

        if usuario is None:
            return None

        hash_guardado = getattr(
            usuario,
            "contrasenia_hash",
            None,
        )

        if not isinstance(hash_guardado, str):
            return None

        if not hash_guardado.startswith(
            ("$2a$", "$2b$", "$2y$")
        ):
            return None

        if len(hash_guardado) != 60:
            return None

        return (
            usuario
            if GestorSeguridad.verificar_contrasenia(
                contrasenia,
                hash_guardado,
            )
            else None
        )

    def actualizar(
        self,
        usuario,
    ):
        """
        Actualiza los datos básicos de un usuario.
        """
        if getattr(
            usuario,
            "id_usuario",
            None,
        ) is None:
            raise ValueError(
                "El usuario debe tener un ID."
            )

        self._validar_usuario(usuario)

        correo_limpio = (
            self._normalizar_correo(
                usuario.correo_electronico
            )
        )

        tipo_usuario = (
            self._obtener_tipo_usuario(
                usuario.tipo_usuario
            )
        )

        if tipo_usuario not in {
            "cliente",
            "administrador",
        }:
            raise ValueError(
                "El tipo de usuario no es válido."
            )

        sql = """
            UPDATE usuarios
            SET
                nombre = %s,
                apellido = %s,
                correo_electronico = %s,
                edad = %s,
                tipo_usuario = %s
            WHERE id_usuario = %s
        """

        parametros = (
            usuario.nombre.strip(),
            usuario.apellido.strip(),
            correo_limpio,
            usuario.edad,
            tipo_usuario,
            usuario.id_usuario,
        )

        try:
            actualizado = (
                self._conexion.ejecutar_actualizacion(
                    sql,
                    parametros,
                )
            )

            if not actualizado:
                raise ValueError(
                    "No se encontró el usuario."
                )

            self._conexion._conexion.commit()

            return usuario

        except IntegrityError as error:
            self._conexion._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            raise ValueError(
                "Error de integridad al actualizar "
                f"el usuario: {error}"
            ) from error

        except ValueError:
            self._conexion._conexion.rollback()
            raise

        except Exception as error:
            self._conexion._conexion.rollback()

            raise ValueError(
                "Error al actualizar el usuario: "
                f"{error}"
            ) from error

    def cambiar_contrasenia(
        self,
        id_usuario: int,
        contrasenia_nueva: str,
    ) -> bool:
        """
        Cambia la contraseña generando siempre un hash.
        """
        if (
            not isinstance(id_usuario, int)
            or isinstance(id_usuario, bool)
            or id_usuario <= 0
        ):
            raise ValueError(
                "El ID debe ser un entero positivo."
            )

        if (
            not isinstance(contrasenia_nueva, str)
            or not contrasenia_nueva
        ):
            raise ValueError(
                "La contraseña no puede estar vacía."
            )

        nuevo_hash = (
            GestorSeguridad.generar_hash(
                contrasenia_nueva
            )
        )

        sql = """
            UPDATE usuarios
            SET contrasenia_hash = %s
            WHERE id_usuario = %s
        """

        try:
            actualizado = (
                self._conexion.ejecutar_actualizacion(
                    sql,
                    (
                        nuevo_hash,
                        id_usuario,
                    ),
                )
            )

            self._conexion._conexion.commit()

            return bool(actualizado)

        except Exception:
            self._conexion._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_usuario: int,
    ) -> bool:
        """
        Elimina un usuario por ID.
        """
        if isinstance(id_usuario, bool):
            raise ValueError(
                "El ID debe ser un entero positivo."
            )

        if not isinstance(id_usuario, int):
            raise ValueError(
                "El ID debe ser un entero positivo."
            )

        if id_usuario <= 0:
            raise ValueError(
                "El ID debe ser un entero positivo."
            )

        sql = """
            DELETE FROM usuarios
            WHERE id_usuario = %s
        """

        try:
            eliminado = (
                self._conexion.ejecutar_actualizacion(
                    sql,
                    (id_usuario,),
                )
            )

            self._conexion._conexion.commit()

            return bool(eliminado)

        except Exception:
            self._conexion._conexion.rollback()
            raise