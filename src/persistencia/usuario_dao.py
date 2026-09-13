from typing import Optional


from psycopg2 import IntegrityError

from src.modelos.administrador import Administrador
from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad




class UsuarioDAO:


    def __init__(self) -> None:
        """Inicializa el DAO con la instancia Singleton de ConexionBD."""
        self._conexion = ConexionBD.obtener_instancia()


    def guardar(self, usuario, contrasenia_plana: str):
        """
        Guarda un nuevo usuario en la base de datos.


        Args:
            usuario: Instancia del usuario a guardar.
            contrasenia_plana (str): Contraseña en texto plano del usuario.


        Returns:
            Usuario: Instancia del usuario con el ID asignado y fecha de registro.


        Raises:
            ValueError: Si el correo ya está registrado.
            RuntimeError: Si ocurre un error inesperado durante la operación.
        """
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            raise ValueError("La contraseña debe ser una cadena no vacía.")

        # Generar hash de la contraseña
        contrasenia_hash = GestorSeguridad.generar_hash(contrasenia_plana)

        # Insertar en usuarios
        sql_usuario = """
            INSERT INTO usuarios (
                nombre,
                apellido,
                correo_electronico,
                "contraseña_hash",
                edad,
                tipo_usuario
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_usuario, fecha_registro
        """
        parametros_usuario = (
            usuario.nombre,
            usuario.apellido,
            usuario.correo_electronico,
            contrasenia_hash,
            usuario.edad,
            usuario.tipo_usuario
        )


        try:
            # Insertar usuario (con commit manual porque ejecutar_consulta no hace commit)
            resultado = self._conexion.ejecutar_consulta(sql_usuario, parametros_usuario)
            if not resultado:
                raise RuntimeError("No se pudo guardar el usuario.")
            usuario.id_usuario = resultado[0]['id_usuario']
            usuario.fecha_registro = resultado[0]['fecha_registro']

            # Hacer commit manual después de la inserción
            self._conexion._conexion.commit()

            # Si es cliente, insertar en clientes
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
                    usuario.objetivo
                )
                resultado_cliente = self._conexion.ejecutar_consulta(sql_cliente, parametros_cliente)
                if resultado_cliente:
                    usuario.fecha_ingreso = resultado_cliente[0]['fecha_ingreso']
                self._conexion._conexion.commit()  # Commit de la segunda inserción


            return usuario


        except IntegrityError as e:
            self._conexion._conexion.rollback()
            if e.pgcode == "23505":  # Violación de restricción única
                raise ValueError("El correo ya está registrado.") from e
            raise RuntimeError(f"Error de integridad al guardar el usuario: {e}") from e

        except Exception as e:
            self._conexion._conexion.rollback()
            raise RuntimeError(f"Error inesperado al guardar el usuario: {e}") from e

    def buscar_por_correo(self, correo: str):
        """
        Busca un usuario por su correo electrónico.


        Args:
            correo (str): Correo electrónico del usuario a buscar.


        Returns:
            Usuario: Instancia del usuario encontrado, o None si no se encuentra.
        """
        sql = """
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
            LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
            WHERE u.correo_electronico = %s
        """
        resultado = self._conexion.ejecutar_consulta(sql, (correo,))
        if not resultado:
            return None


        fila = resultado[0]
        tipo_usuario = fila['tipo_usuario'].strip().lower()


        if tipo_usuario == "cliente":
            return Cliente(
                id_usuario=fila['id_usuario'],
                nombre=fila['nombre'],
                apellido=fila['apellido'],
                correo_electronico=fila['correo_electronico'],
                contrasenia_hash=fila['contraseña_hash'],
                edad=fila['edad'],
                fecha_registro=fila['fecha_registro'],
                peso=float(fila['peso']) if fila['peso'] else None,
                altura=float(fila['altura']) if fila['altura'] else None,
                objetivo=fila['objetivo'],
                fecha_ingreso=fila['fecha_ingreso']
            )
        elif tipo_usuario == "administrador":
            return Administrador(
                id_usuario=fila['id_usuario'],
                nombre=fila['nombre'],
                apellido=fila['apellido'],
                correo_electronico=fila['correo_electronico'],
                contrasenia_hash=fila['contraseña_hash'],
                edad=fila['edad'],
                fecha_registro=fila['fecha_registro']
            )
        else:
            raise ValueError(f"Tipo de usuario desconocido: {tipo_usuario}")

    def iniciar_sesion(self, correo: str, contrasenia: str):
        """
        Verifica las credenciales de un usuario.


        Args:
            correo (str): Correo electrónico del usuario.
            contrasenia (str): Contraseña en texto plano del usuario.


        Returns:
            Usuario: Instancia del usuario si las credenciales son válidas, o None si no.
        """
        usuario = self.buscar_por_correo(correo)


        if usuario is None:
            return None


        if GestorSeguridad.verificar_contrasenia(contrasenia, usuario.contrasenia_hash):
            return usuario
        return None


    def actualizar(self, usuario):
        """
        Actualiza los datos de un usuario.


        Args:
            usuario: Instancia de Usuario con id_usuario.


        Returns:
            Usuario: Instancia del usuario actualizado.


        Raises:
            ValueError: Si el usuario no tiene un id_usuario o si el correo ya está registrado.
        """
        if usuario.id_usuario is None:
            raise ValueError("El usuario debe tener un id para actualizarse.")


        sql = """
            UPDATE usuarios
            SET nombre = %s,
                apellido = %s,
                correo_electronico = %s,
                edad = %s,
                tipo_usuario = %s
            WHERE id_usuario = %s
        """
        parametros = (
            usuario.nombre,
            usuario.apellido,
            usuario.correo_electronico,
            usuario.edad,
            usuario.tipo_usuario,
            usuario.id_usuario
        )


        try:
            actualizado = self._conexion.ejecutar_actualizacion(sql, parametros)
            if not actualizado:
                raise ValueError("No se encontró usuario con el ID proporcionado.")
            return usuario
        except IntegrityError as e:
            self._conexion._conexion.rollback()
            if e.pgcode == "23505":
                raise ValueError("El correo ya está registrado.") from e
            raise RuntimeError(f"Error de integridad al actualizar el usuario: {e}") from e
        except Exception as e:
            self._conexion._conexion.rollback()
            raise RuntimeError(f"Error inesperado al actualizar el usuario: {e}") from e

    def eliminar_por_id(self, id_usuario: int) -> bool:
        """
        Elimina un usuario de la base de datos por su ID.


        Args:
            id_usuario (int): ID del usuario a eliminar.


        Returns:
            bool: True si el usuario fue eliminado, False en caso contrario.
        """
        sql = "DELETE FROM usuarios WHERE id_usuario = %s"
        return self._conexion.ejecutar_actualizacion(sql, (id_usuario,))
