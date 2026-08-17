import os

import psycopg2
from dotenv import load_dotenv


class ConexionBD:
    """
    Administra la conexión con PostgreSQL usando las variables del archivo .env.
    """

    @staticmethod
    def obtener_conexion():
        load_dotenv()

        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )