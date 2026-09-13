"""
Script para insertar datos de ejemplo - Versión corregida.
"""

import sys
from pathlib import Path
import bcrypt

# Agregar el root del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persistencia.conexion_bd import ConexionBD


def ver_estructura_tablas(bd):
    """Verifica la estructura de las tablas."""
    print("=== Verificando estructura de tablas ===\n")
    
    with bd._conexion.cursor() as cursor:
        # Columnas de rutinas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'rutinas' 
            ORDER BY ordinal_position
        """)
        print("Columnas de 'rutinas':")
        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]}")
        
        # Columnas de ejercicios
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ejercicios' 
            ORDER BY ordinal_position
        """)
        print("\nColumnas de 'ejercicios':")
        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]}")
        
        # Columnas de rutina_ejercicios
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'rutina_ejercicios' 
            ORDER BY ordinal_position
        """)
        print("\nColumnas de 'rutina_ejercicios':")
        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]}")


def crear_administrador_si_no_existe(bd):
    """Crea un usuario administrador en la BD."""
    print("\n1. Verificando/creando administrador...")
    
    with bd._conexion.cursor() as cursor:
        cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE correo_electronico = %s", ("admin@cardio.com",))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"✓ Usuario encontrado: {resultado[1]} (ID: {resultado[0]})")
            return resultado[0]
        
        contrasenia_plana = "Admin123"
        contrasena_hash = bcrypt.hashpw(contrasenia_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, correo_electronico, contraseña_hash, tipo_usuario, edad)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_usuario
        """, ("Admin", "Sistema", "admin@cardio.com", contrasena_hash, "cliente", 30))
        
        admin_id = cursor.fetchone()[0]
        bd._conexion.commit()
        print(f"✓ Usuario creado (ID: {admin_id})")
        return admin_id


def crear_rutinas_ejemplo():
    """Crea rutinas de ejemplo en la base de datos."""
    print("=" * 60)
    print("Creando rutinas de ejemplo...")
    print("=" * 60)
    
    bd = ConexionBD.obtener_instancia()
    bd.abrir_conexion()
    
    # Ver estructura primero
    ver_estructura_tablas(bd)
    
    # Paso 1: Crear administrador
    id_creador = crear_administrador_si_no_existe(bd)
    
    # Paso 2: Crear rutinas y ejercicios directamente en BD
    print("\n2. Creando rutinas y ejercicios...")
    
    with bd._conexion.cursor() as cursor:
        # Rutina 1: Cardio Básico (ajustar columnas según estructura real)
        cursor.execute("""
            INSERT INTO rutinas (nombre, descripcion, objetivo, nivel, duracion_semanas, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_rutina
        """, ("Cardio Básico", "Rutina de cardio para principiantes", "Perder peso", "BASICO", 4, id_creador))
        
        rutina_cardio_id = cursor.fetchone()[0]
        print(f"✓ Rutina creada: Cardio Básico (ID: {rutina_cardio_id})")
        
        # Ejercicios para Cardio Básico
        ejercicios_cardio = [
            ("Cinta caminando", "Caminata moderada", "Cardio", 10, "BAJA", 50.0),
            ("Elíptica", "Ejercicio de baja impacto", "Cardio", 10, "BAJA", 60.0),
            ("Sentadillas", "Sentadillas sin peso", "Fuerza", 10, "BAJA", 40.0),
        ]
        
        orden = 1
        for nombre, desc, tipo, duracion, intensidad, calorias in ejercicios_cardio:
            cursor.execute("""
                INSERT INTO ejercicios (nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_ejercicio
            """, (nombre, desc, tipo, duracion, intensidad, calorias, id_creador))
            
            ejercicio_id = cursor.fetchone()[0]
            print(f"  - Ejercicio creado: {nombre} (ID: {ejercicio_id})")
            
            cursor.execute("""
                INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
                VALUES (%s, %s, %s)
            """, (rutina_cardio_id, ejercicio_id, orden))
            
            orden += 1
        
        print(f"✓ Ejercicios agregados a: Cardio Básico")
        
        # Rutina 2: Fuerza Intermedio
        cursor.execute("""
            INSERT INTO rutinas (nombre, descripcion, objetivo, nivel, duracion_semanas, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_rutina
        """, ("Fuerza Intermedio", "Rutina de fuerza para nivel intermedio", "Ganar masa muscular", "INTERMEDIO", 6, id_creador))
        
        rutina_fuerza_id = cursor.fetchone()[0]
        print(f"✓ Rutina creada: Fuerza Intermedio (ID: {rutina_fuerza_id})")
        
        # Ejercicios para Fuerza Intermedio
        ejercicios_fuerza = [
            ("Press de banca", "Press de banca con barra", "Fuerza", 15, "MEDIA", 80.0),
            ("Peso muerto", "Peso muerto rumano", "Fuerza", 15, "MEDIA", 90.0),
            ("Dominadas", "Dominadas asistidas", "Fuerza", 15, "MEDIA", 70.0),
        ]
        
        orden = 1
        for nombre, desc, tipo, duracion, intensidad, calorias in ejercicios_fuerza:
            cursor.execute("""
                INSERT INTO ejercicios (nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_ejercicio
            """, (nombre, desc, tipo, duracion, intensidad, calorias, id_creador))
            
            ejercicio_id = cursor.fetchone()[0]
            print(f"  - Ejercicio creado: {nombre} (ID: {ejercicio_id})")
            
            cursor.execute("""
                INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
                VALUES (%s, %s, %s)
            """, (rutina_fuerza_id, ejercicio_id, orden))
            
            orden += 1
        
        print(f"✓ Ejercicios agregados a: Fuerza Intermedio")
        
        bd._conexion.commit()
    
    print("\n" + "=" * 60)
    print("Proceso completado exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    try:
        crear_rutinas_ejemplo()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            bd = ConexionBD.obtener_instancia()
            bd.cerrar_conexion()
        except Exception:
            pass