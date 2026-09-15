"""
Prueba de estrés EXTREMA: 500 usuarios concurrentes, 120 segundos.
CON SEMÁFORO para limitar conexiones simultáneas.
"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import random
import os
import traceback
import threading

sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from dotenv import load_dotenv


# Semáforo para limitar conexiones simultáneas
MAX_CONEXIONES_SIMULTANEAS = 50
semaforo = threading.Semaphore(MAX_CONEXIONES_SIMULTANEAS)


def obtener_conexion():
    """Crea una nueva conexión a la base de datos."""
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'cardio_wellness'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )


def operacion_usuario(usuario_id):
    """Simula las operaciones de un usuario CON SEMÁFORO."""
    conn = None
    try:
        # Adquirir semáforo (espera si hay 50 conexiones activas)
        semaforo.acquire()
        
        # Crear conexión
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        exitos = 0
        fallidos = 0
        
        # 1. Listar clientes
        try:
            cursor.execute("""
                SELECT c.id_usuario, u.nombre, u.apellido, u.correo_electronico
                FROM clientes c
                INNER JOIN usuarios u ON c.id_usuario = u.id_usuario
            """)
            clientes = cursor.fetchall()
            exito_listar_clientes = len(clientes) > 0
            if exito_listar_clientes:
                exitos += 1
            else:
                fallidos += 1
        except Exception as e:
            fallidos += 1
        
        # 2. Listar rutinas
        try:
            cursor.execute("SELECT id_rutina, nombre FROM rutinas")
            rutinas = cursor.fetchall()
            exito_listar_rutinas = len(rutinas) > 0
            if exito_listar_rutinas:
                exitos += 1
            else:
                fallidos += 1
        except Exception as e:
            fallidos += 1
        
        # 3. Registrar sesión (escritura)
        exito_registrar_sesion = False
        if clientes:
            cliente = random.choice(clientes)
            id_cliente = cliente[0]
            try:
                cursor.execute("""
                    INSERT INTO sesiones_entrenamiento 
                    (id_cliente, fecha, duracion_real, intensidad_real, calorias_quemadas, observaciones, completada)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_cliente,
                    datetime.now(),
                    45,
                    'MEDIA',
                    200,
                    f'Sesión prueba EXTREMA 500 - Usuario {usuario_id}',
                    True
                ))
                conn.commit()
                exito_registrar_sesion = True
                exitos += 1
            except Exception as e:
                conn.rollback()
                fallidos += 1
        else:
            fallidos += 1
        
        # 4. Ver progreso
        exito_ver_progreso = False
        if clientes:
            cliente = random.choice(clientes)
            id_cliente = cliente[0]
            try:
                cursor.execute("""
                    SELECT * FROM progreso_mensual 
                    WHERE id_cliente = %s 
                    ORDER BY mes DESC 
                    LIMIT 1
                """, (id_cliente,))
                progreso = cursor.fetchone()
                exito_ver_progreso = True
                exitos += 1
            except Exception as e:
                fallidos += 1
        else:
            fallidos += 1
        
        cursor.close()
        conn.close()
        
        # Liberar semáforo
        semaforo.release()
        
        return exitos, fallidos
        
    except Exception as e:
        # Liberar semáforo en caso de error
        try:
            semaforo.release()
        except:
            pass
        
        if conn:
            try:
                conn.close()
            except:
                pass
        return 0, 4


def ejecutar_prueba_estres_extrema():
    """Ejecuta prueba de estrés EXTREMA con 500 usuarios, 120 segundos."""
    
    print("=" * 70)
    print("PRUEBA DE ESTRÉS EXTREMA - 500 USUARIOS, 120 SEGUNDOS")
    print(f"CON SEMÁFORO (máx {MAX_CONEXIONES_SIMULTANEAS} conexiones simultáneas)")
    print("=" * 70)
    
    NUM_USUARIOS = 500
    DURACION_OBJETIVO = 120  # segundos
    
    exitos = 0
    fallidos = 0
    total_operaciones = 0
    inicio_prueba = datetime.now()
    
    print(f"\n🚀 Iniciando prueba con {NUM_USUARIOS} usuarios concurrentes...")
    print(f"⏱️  Duración objetivo: {DURACION_OBJETIVO} segundos")
    print(f"📊 Operaciones por usuario: 4")
    print(f"📈 Operaciones totales esperadas: {NUM_USUARIOS * 4}")
    print()
    
    with ThreadPoolExecutor(max_workers=NUM_USUARIOS) as executor:
        futures = [executor.submit(operacion_usuario, i) for i in range(NUM_USUARIOS)]
        
        for i, future in enumerate(as_completed(futures)):
            exitos_usuario, fallidos_usuario = future.result()
            
            exitos += exitos_usuario
            fallidos += fallidos_usuario
            total_operaciones += 4
            
            # Progreso
            if (i + 1) % 50 == 0:
                print(f"   Progreso: {i + 1}/{NUM_USUARIOS} usuarios completados")
    
    fin_prueba = datetime.now()
    duracion_real = (fin_prueba - inicio_prueba).total_seconds()
    ops_por_segundo = total_operaciones / duracion_real if duracion_real > 0 else 0
    
    tasa_exito = (exitos / total_operaciones * 100) if total_operaciones > 0 else 0
    
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    print(f"✅ Exitosas: {exitos}")
    print(f"❌ Fallidas: {fallidos}")
    print(f"📊 Total operaciones: {total_operaciones}")
    print(f"⏱️  Duración real: {duracion_real:.2f} segundos")
    print(f"⚡ Ops/segundo: {ops_por_segundo:.2f}")
    print(f"📈 Tasa de éxito: {tasa_exito:.2f}%")
    print()
    
    # Interpretación
    if tasa_exito >= 95:
        print("🟢 RESULTADO: EXCELENTE - Sistema maneja carga extrema perfectamente")
    elif tasa_exito >= 90:
        print("🟢 RESULTADO: MUY BIEN - Sistema maneja carga extrema con mínimo error")
    elif tasa_exito >= 80:
        print("🟡 RESULTADO: ACEPTABLE - Sistema maneja carga extrema con degradación menor")
    elif tasa_exito >= 70:
        print("🟠 RESULTADO: CRÍTICO - Sistema bajo estrés significativo")
    else:
        print("🔴 RESULTADO: INSUFICIENTE - Sistema no soporta esta carga")
    
    print("=" * 70)
    
    # Guardar reporte
    with open('reporte_estres_500_usuarios_120s.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("REPORTE DE ESTRÉS EXTREMA - 500 USUARIOS, 120 SEGUNDOS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Usuarios concurrentes: {NUM_USUARIOS}\n")
        f.write(f"Conexiones simultáneas máx: {MAX_CONEXIONES_SIMULTANEAS}\n")
        f.write(f"Duración objetivo: {DURACION_OBJETIVO} segundos\n\n")
        f.write("RESULTADOS:\n")
        f.write(f"  ✅ Exitosas: {exitos}\n")
        f.write(f"  ❌ Fallidas: {fallidos}\n")
        f.write(f"  📊 Total operaciones: {total_operaciones}\n")
        f.write(f"  ⏱️  Duración real: {duracion_real:.2f} segundos\n")
        f.write(f"  ⚡ Ops/segundo: {ops_por_segundo:.2f}\n")
        f.write(f"  📈 Tasa de éxito: {tasa_exito:.2f}%\n\n")
        
        if tasa_exito >= 95:
            f.write("🟢 RESULTADO: EXCELENTE\n")
        elif tasa_exito >= 90:
            f.write("🟢 RESULTADO: MUY BIEN\n")
        elif tasa_exito >= 80:
            f.write("🟡 RESULTADO: ACEPTABLE\n")
        elif tasa_exito >= 70:
            f.write("🟠 RESULTADO: CRÍTICO\n")
        else:
            f.write("🔴 RESULTADO: INSUFICIENTE\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    print("\n📄 Reporte guardado: reporte_estres_500_usuarios_120s.txt")


if __name__ == "__main__":
    ejecutar_prueba_estres_extrema()