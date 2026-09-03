import os
from typing import Any, Dict, List, Optional

import psycopg2
from dotenv import load_dotenv


class ConexionBD:
    """
    Administra la conexión con PostgreSQL usando las variables del archivo .env.
    """

    #==Clase Singleton que administra la conexion a la base de datos.==
    _instancia: Optional['ConexionBD'] = None
    _conexion = None

    def __new__(cls) -> 'ConexionBD':
        #==Controla la creacion de la instancia (patron Singleton)==
        if cls._instancia is None:
            cls._instancia = super(ConexionBD, cls).__new__(cls)
        return cls._instancia

    def __init__(self) -> None:
        #==Inicializa la configuracion(solo una vez).==
        if not hasattr(self, '_inicializado'):
            load_dotenv() #Carga las variables de entorno una sola vez.
            self._config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'dbname': os.getenv('DB_NAME'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
            }
            self._validar_configuracion()
            self._inicializado = True

    def _validar_configuracion(self) -> None:
        #==Valida que todas las variables de entorno necesarias estén presentes.==
        obligatorias = ['dbname', 'user', 'password']
        faltantes = [key for key in obligatorias if not self._config.get(key)]
        if faltantes:
            raise EnvironmentError(
                f"Faltan variables de entorno: {', '.join(faltantes)}"
                "Asegurate de tener un archivo .env con DB_NAME, DB_USER, DB_PASSWORD."
            )

    @staticmethod
    def obtener_instancia() -> 'ConexionBD':
        #==Devuelve la unica instancia de la clase (Singleton)==
        return ConexionBD()

    def abrir_conexion(self) -> None:
        #==Establece la conexion con la base de datos==#
        #==Si ya esta abierta, no hace nada.==

        if self._conexion is not None and not self._conexion.closed:
            return  # Conexion ya abierta

        try:
            self._conexion = psycopg2.connect(**self._config)
            print("Conexion a la base de datos establecida.")
        except psycopg2.OperationalError as e:
            raise RuntimeError(f"Error al conectar a la base de datos: {e}")

    def cerrar_conexion(self) -> None:
        #==Cierra la conexion con la base de datos si esta abierta.==
        if self._conexion is not None and not self._conexion.closed:
            self._conexion.close()
            self._conexion = None 
            print("Conexion a la base de datos cerrada.")

    def _obtener_cursor(self):
        #==Obtiene un cursor de la conexion (abre la conexion si es necesario)==
        if self._conexion is None or self._conexion.closed:
            self.abrir_conexion()
        return self._conexion.cursor()

    def ejecutar_consulta(self, sql: str, parametros: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y devuelve los resultados como una lista de diccionarios.
        
        Args:
            sql (str): La consulta SQL con placeholders %s.
            parametros (tuple, optional): Parametros para la consulta.

        Returns:
            List[Dict[str, Any]]: Lista de resultados como diccionarios (columna: valor).
        """
        try:
            with self._obtener_cursor() as cursor:
                cursor.execute(sql, parametros or ())
                columnas = [desc[0] for desc in cursor.description]
                filas = cursor.fetchall()
                return [dict(zip(columnas, fila)) for fila in filas]
        except psycopg2.Error as e:
            raise RuntimeError(f"Error al ejecutar la consulta: {e}")

    def ejecutar_actualizacion(self, sql: str, parametros: Optional[tuple] = None) -> bool:
        """
        Ejecuta una sentencia INSERT, UPDATE, o DELTE.

        args:
            sql (str): La sentencia SQL con placeholders %s.
            parametros (tuple, optional): Parametros para la sentencia.

        Returns:
            bool: True si la operacion afecto al menos una fila.
        """
        try:
            with self._obtener_cursor() as cursor:
                cursor.execute(sql, parametros or ())
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            self._conexion.rollback() # Revertir cambios en caso de error
            raise RuntimeError(f"Error al ejecutar la actualizacion: {e}")

    def __enter__(self):
        #==Permite usar la clase con el contexto 'with'==#
        self.abrir_conexion()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #==Cierra la conexion al salir del contexto==#
        self.cerrar_conexion()

#====