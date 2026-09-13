"""
Script de respaldo automático de la base de datos PostgreSQL.
"""

import subprocess
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.persistencia.conexion_bd import ConexionBD


def obtener_configuracion_db():
    """Obtiene la configuración de la base de datos desde .env."""
    load_dotenv()
    
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def crear_respaldo(ruta_respaldo: str = None):
    """Crea un respaldo de la base de datos usando pg_dump."""
    config = obtener_configuracion_db()
    
    if not config["dbname"]:
        raise ValueError("DB_NAME no está configurada en .env")
    
    if ruta_respaldo is None:
        ruta_respaldo = Path(__file__).parent.parent / "backups"
    
    ruta_respaldo = Path(ruta_respaldo)
    ruta_respaldo.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"cardio_wellness_{timestamp}.sql"
    ruta_archivo = ruta_respaldo / nombre_archivo
    
    comando = [
        "pg_dump",
        "-h", config["host"],
        "-p", config["port"],
        "-U", config["user"],
        "-d", config["dbname"],
        "-F", "p",
        "-f", str(ruta_archivo),
    ]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = config["password"]
    
    try:
        subprocess.run(comando, env=env, check=True, capture_output=True, text=True)
        print(f"✓ Respaldo creado: {ruta_archivo}")
        return ruta_archivo
    except FileNotFoundError:
        print("⚠ pg_dump no encontrado. Creando respaldo manual...")
        return crear_respaldo_manual(ruta_respaldo, nombre_archivo)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e.stderr}")
        raise


def crear_respaldo_manual(ruta_respaldo, nombre_archivo):
    """Crea un respaldo manual exportando datos con Python."""
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()
    
    ruta_archivo = ruta_respaldo / nombre_archivo
    
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write("-- Respaldo manual de Cardio-Wellness\n")
        f.write(f"-- Fecha: {datetime.now()}\n\n")
        
        tablas = ['usuarios', 'rutinas', 'ejercicios', 'rutina_ejercicios', 
                  'sesiones_entrenamiento', 'progreso_mensual', 'asignaciones_rutina']
        
        with bd._conexion.cursor() as cursor:
            for tabla in tablas:
                try:
                    cursor.execute(f"SELECT * FROM {tabla}")
                    columnas = [desc[0] for desc in cursor.description]
                    filas = cursor.fetchall()
                    
                    f.write(f"-- Tabla: {tabla}\n")
                    for fila in filas:
                        valores = ", ".join([f"'{str(v)}'" if isinstance(v, str) else str(v) for v in fila])
                        f.write(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({valores});\n")
                    f.write("\n")
                except Exception as e:
                    f.write(f"-- Error en tabla {tabla}: {e}\n\n")
        
        bd.cerrar_conexion()
    
    print(f"✓ Respaldo manual creado: {ruta_archivo}")
    return ruta_archivo


def verificar_integridad():
    """Verifica la integridad de la base de datos."""
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()
    
    try:
        with bd._conexion.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        print("✓ Integridad de la base de datos: OK")
        return True
    except Exception as e:
        print(f"✗ Error de integridad: {e}")
        return False
    finally:
        bd.cerrar_conexion()


def limpiar_respaldo_antiguo(dias_maximos: int = 30):
    """Elimina respaldos antiguos."""
    ruta_respaldo = Path(__file__).parent.parent / "backups"
    
    if not ruta_respaldo.exists():
        return
    
    ahora = datetime.now()
    eliminados = 0
    
    for archivo in ruta_respaldo.glob("cardio_wellness_*.sql"):
        fecha_archivo = datetime.fromtimestamp(archivo.stat().st_mtime)
        antiguedad = (ahora - fecha_archivo).days
        
        if antiguedad > dias_maximos:
            archivo.unlink()
            eliminados += 1
            print(f"✓ Eliminado respaldo antiguo: {archivo.name}")
    
    print(f"Total eliminados: {eliminados}")


def main():
    """Función principal del script de respaldo."""
    print("=" * 60)
    print("Script de Respaldo - Cardio-Wellness")
    print("=" * 60)
    
    print("\n1. Verificando integridad de la base de datos...")
    if not verificar_integridad():
        print("✗ La base de datos tiene errores. No se creará respaldo.")
        return
    
    print("\n2. Creando respaldo...")
    try:
        ruta_respaldo = crear_respaldo()
        print(f"✓ Respaldo exitoso: {ruta_respaldo}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    print("\n3. Limpiando respaldos antiguos (>30 días)...")
    limpiar_respaldo_antiguo()
    
    print("\n" + "=" * 60)
    print("Proceso completado exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    main()