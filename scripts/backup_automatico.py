"""
Backup automático programado para Cardio-Wellness.
Ejecutar diariamente vía Task Scheduler (Windows) o cron (Linux/Mac).
"""

import sys
from pathlib import Path
from datetime import datetime
import os

# Agregar root al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import psycopg2


def crear_backup():
    """Crea un backup de la base de datos exportando todas las tablas."""
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Obtener credenciales
        db_name = os.getenv('DB_NAME', 'cardio_wellness')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        
        # Crear directorio de backups si no existe
        backup_dir = Path(__file__).parent.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"cardio_wellness_auto_{timestamp}.sql"
        
        print(f"Creando backup: {backup_file.name}")
        
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        # Abrir archivo para escribir
        with open(backup_file, 'w', encoding='utf-8') as f:
            cursor = conn.cursor()
            
            # Escribir header
            f.write("--\n")
            f.write(f"-- Backup de Cardio-Wellness\n")
            f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Base de datos: {db_name}\n")
            f.write("--\n\n")
            
            # Lista de tablas a exportar
            tablas = [
                'usuarios', 'clientes', 'rutinas', 'ejercicios',
                'rutinas_ejercicios', 'asignaciones_rutina',
                'sesiones_entrenamiento', 'progreso_mensual'
            ]
            
            for tabla in tablas:
                try:
                    # Verificar si la tabla existe
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, (tabla,))
                    
                    if not cursor.fetchone()[0]:
                        f.write(f"-- Tabla {tabla} no existe, saltando...\n\n")
                        continue
                    
                    # Obtener columnas
                    cursor.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (tabla,))
                    columnas_info = cursor.fetchall()
                    columnas = [col[0] for col in columnas_info]
                    
                    if not columnas:
                        continue
                    
                    # Escribir comentarios
                    f.write(f"\n--\n-- Datos de la tabla {tabla}\n--\n\n")
                    
                    # Obtener todos los registros
                    cursor.execute(f"SELECT * FROM {tabla}")
                    registros = cursor.fetchall()
                    
                    for registro in registros:
                        valores = []
                        for val in registro:
                            if val is None:
                                valores.append('NULL')
                            elif isinstance(val, str):
                                # Escapar comillas simples
                                escaped = val.replace("'", "''")
                                valores.append(f"'{escaped}'")
                            elif isinstance(val, datetime):
                                valores.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                            elif isinstance(val, bool):
                                valores.append('TRUE' if val else 'FALSE')
                            else:
                                valores.append(str(val))
                        
                        f.write(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({', '.join(valores)});\n")
                
                except Exception as e:
                    f.write(f"-- Error exportando tabla {tabla}: {e}\n\n")
                    print(f"   ⚠️  Advertencia: Error en tabla {tabla}: {e}")
        
        conn.close()
        
        # Mantener solo los últimos 7 backups
        backups = sorted(backup_dir.glob("cardio_wellness_auto_*.sql"))
        if len(backups) > 7:
            for backup_viejo in backups[:-7]:
                backup_viejo.unlink()
                print(f"Eliminado backup antiguo: {backup_viejo.name}")
        
        print(f"✓ Backup automático creado: {backup_file.name}")
        print(f"   Tamaño: {backup_file.stat().st_size / 1024:.2f} KB")
        return True
        
    except Exception as e:
        print(f"✗ Error en backup automático: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    exit(0 if crear_backup() else 1)