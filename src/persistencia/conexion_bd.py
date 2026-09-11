import os
from typing import Any, Dict, List, Optional

import psycopg2
from dotenv import load_dotenv


class ConexionBD:
    """
    Administra la conexión con PostgreSQL usando las variables del archivo .env.
    """

    _instancia: Optional["ConexionBD"] = None
    _conexion = None

    def __new__(cls) -> "ConexionBD":
        """Controla la creación de la instancia mediante el patrón Singleton."""
        if cls._instancia is None:
            cls._instancia = super(ConexionBD, cls).__new__(cls)
        return cls._instancia

    def __init__(self) -> None:
        """Inicializa la configuración una única vez."""
        if not hasattr(self, "_inicializado"):
            load_dotenv()

            self._config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": os.getenv("DB_PORT", "5432"),
                "dbname": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
            }

            self._validar_configuracion()
            self._inicializado = True

    def _validar_configuracion(self) -> None:
        """Valida que existan las variables necesarias para PostgreSQL."""
        obligatorias = ["dbname", "user", "password"]
        faltantes = [
            clave for clave in obligatorias
            if not self._config.get(clave)
        ]

        if faltantes:
            raise EnvironmentError(
                f"Faltan variables de entorno: {', '.join(faltantes)}. "
                "Asegúrate de tener un archivo .env con "
                "DB_NAME, DB_USER y DB_PASSWORD."
            )

    @staticmethod
    def obtener_instancia() -> "ConexionBD":
        """Devuelve la única instancia de ConexionBD."""
        return ConexionBD()

    def abrir_conexion(self) -> None:
        """Abre la conexión con PostgreSQL si aún no está abierta."""
        if self._conexion is not None and not self._conexion.closed:
            return

        try:
            self._conexion = psycopg2.connect(**self._config)
            print("Conexion a la base de datos establecida.")
        except psycopg2.OperationalError as error:
            raise RuntimeError(
                f"Error al conectar a la base de datos: {error}"
            ) from error

    def cerrar_conexion(self) -> None:
        """Cierra la conexión activa, si existe."""
        if self._conexion is not None and not self._conexion.closed:
            self._conexion.close()
            self._conexion = None
            print("Conexion a la base de datos cerrada.")

    def _obtener_cursor(self):
        """Obtiene un cursor y abre la conexión si es necesario."""
        if self._conexion is None or self._conexion.closed:
            self.abrir_conexion()

        return self._conexion.cursor()

    def ejecutar_consulta(
        self,
        sql: str,
        parametros: Optional[tuple] = None,
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta que devuelve filas, incluyendo INSERT con RETURNING.

        Devuelve una lista de diccionarios, uno por cada fila obtenida.
        """
        try:
            with self._obtener_cursor() as cursor:
                cursor.execute(sql, parametros or ())

                if cursor.description is None:
                    self._conexion.commit()
                    return []

                columnas = [descripcion[0] for descripcion in cursor.description]
                filas = cursor.fetchall()
                self._conexion.commit()

                return [
                    dict(zip(columnas, fila))
                    for fila in filas
                ]

        except psycopg2.IntegrityError:
            self._conexion.rollback()
            raise

        except psycopg2.Error as error:
            self._conexion.rollback()
            raise RuntimeError(
                f"Error al ejecutar la consulta: {error}"
            ) from error

    def ejecutar_actualizacion(
        self,
        sql: str,
        parametros: Optional[tuple] = None,
    ) -> bool:
        """
        Ejecuta INSERT, UPDATE o DELETE sin requerir filas de retorno.

        Retorna True cuando la operación afecta al menos una fila.
        """
        try:
            with self._obtener_cursor() as cursor:
                cursor.execute(sql, parametros or ())
                filas_afectadas = cursor.rowcount
                self._conexion.commit()
                return filas_afectadas > 0

        except psycopg2.IntegrityError:
            self._conexion.rollback()
            raise

        except psycopg2.Error as error:
            self._conexion.rollback()
            raise RuntimeError(
                f"Error al ejecutar la actualización: {error}"
            ) from error

    def __enter__(self):
        """Permite usar ConexionBD dentro de un bloque with."""
        self.abrir_conexion()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al finalizar un bloque with."""
        self.cerrar_conexion()