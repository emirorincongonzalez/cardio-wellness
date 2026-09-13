import os
from typing import Any, Dict, List, Optional

import psycopg2
from dotenv import load_dotenv


class ConexionBD:
    """
    Administra la conexión con PostgreSQL usando las variables del archivo .env.
    Implementa el patrón Singleton para garantizar una única conexión.
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
            
            # Configurar modo WAL para mejor concurrencia (si es SQLite)
            # Para PostgreSQL, configurar parámetros de rendimiento
            with self._conexion.cursor() as cursor:
                # Configurar timezone
                cursor.execute("SET TIME ZONE 'UTC'")
            
            print("Conexión a la base de datos establecida.")
        except psycopg2.OperationalError as error:
            raise RuntimeError(
                f"Error al conectar a la base de datos: {error}"
            ) from error

    def cerrar_conexion(self) -> None:
        """Cierra la conexión activa, si existe."""
        if self._conexion is not None and not self._conexion.closed:
            self._conexion.close()
            self._conexion = None
            print("Conexión a la base de datos cerrada.")

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
                self._conexion.commit()
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            self._conexion.rollback() # Revertir cambios en caso de error
            raise RuntimeError(f"Error al ejecutar la actualizacion: {e}")

    def __enter__(self):
        """Permite usar ConexionBD dentro de un bloque with."""
        self.abrir_conexion()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al finalizar un bloque with."""
        self.cerrar_conexion()

    def verificar_integridad(self) -> bool:
        """
        Verifica la integridad de la conexión a la base de datos.
        
        Returns:
            bool: True si la conexión es válida
        """
        try:
            if self._conexion is None or self._conexion.closed:
                return False
            
            # Ejecutar consulta simple para verificar conexión
            with self._conexion.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return True
        except Exception:
            return False

    def obtener_configuracion(self) -> Dict[str, str]:
        """
        Obtiene la configuración actual de la conexión.
        
        Returns:
            Dict: Configuración de la base de datos (sin password)
        """
        return {
            "host": self._config.get("host", "localhost"),
            "port": self._config.get("port", "5432"),
            "dbname": self._config.get("dbname", ""),
            "user": self._config.get("user", ""),
        }