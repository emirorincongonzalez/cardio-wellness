"""
Prueba de estrés optimizada para PostgreSQL - Cardio-Wellness.
Con creación dinámica de clientes de prueba y manejo de errores de concurrencia.
"""

import threading
import time
import random
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor


class StressTesterPostgreSQL:
    """Clase para ejecutar pruebas de estrés en PostgreSQL."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "cardio_wellness",
        user: str = "postgres",
        password: str = "admin",
        num_usuarios: int = 20,
        duracion: int = 30,
        num_clientes_prueba: int = 100,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.num_usuarios = num_usuarios
        self.duracion = duracion
        self.num_clientes_prueba = num_clientes_prueba
        self.running = True
        self.ops_exitosas = 0
        self.ops_fallidas = 0
        self.response_times = []
        self.lock = threading.Lock()
        self.connection_pool = None
        self.id_clientes_reales = []

    def _init_pool(self):
        """Inicializa el pool de conexiones."""
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 100,
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        print(f"✅ Pool de conexiones inicializado (1-100 conexiones)")

    def _crear_clientes_prueba(self):
        """Crea clientes de prueba dinámicamente."""
        print(f"\n📝 Creando {self.num_clientes_prueba} clientes de prueba...")
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                for i in range(self.num_clientes_prueba):
                    correo = f"stress.{uuid4().hex[:8]}@test.com"
                    
                    # Crear usuario
                    cursor.execute("""
                        INSERT INTO usuarios (
                            nombre, apellido, correo_electronico, 
                            "contraseña_hash", edad, tipo_usuario
                        )
                        VALUES (%s, %s, %s, %s, %s, 'cliente')
                        RETURNING id_usuario
                    """, (
                        f"Stress{i}",
                        "Test",
                        correo,
                        "hash_temporal",
                        random.randint(20, 50),
                    ))
                    id_usuario = cursor.fetchone()[0]
                    
                    # Crear cliente
                    cursor.execute("""
                        INSERT INTO clientes (
                            id_usuario, peso, altura, objetivo
                        )
                        VALUES (%s, %s, %s, %s)
                    """, (
                        id_usuario,
                        random.uniform(50, 120),
                        random.uniform(1.50, 2.00),
                        "Pruebas de estrés",
                    ))
                    
                    self.id_clientes_reales.append(id_usuario)
                
                conn.commit()
            
            print(f"✅ {len(self.id_clientes_reales)} clientes de prueba creados")
        finally:
            self._release_connection(conn)

    def _limpiar_clientes_prueba(self):
        """Limpia los clientes de prueba creados."""
        print(f"\n🧹 Limpiando {len(self.id_clientes_reales)} clientes de prueba...")
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Eliminar sesiones primero
                cursor.execute("""
                    DELETE FROM sesiones_entrenamiento 
                    WHERE observaciones LIKE %s
                """, ('%estrés%',))
                
                # Eliminar clientes y usuarios
                cursor.execute("""
                    DELETE FROM clientes 
                    WHERE id_usuario IN (
                        SELECT id_usuario FROM usuarios 
                        WHERE correo_electronico LIKE %s
                    )
                """, ('%stress.%',))
                
                cursor.execute("""
                    DELETE FROM usuarios 
                    WHERE correo_electronico LIKE %s
                """, ('%stress.%',))
                
                conn.commit()
            
            print(f"✅ Clientes de prueba eliminados")
        finally:
            self._release_connection(conn)

    def _get_connection(self):
        """Obtiene una conexión del pool."""
        return self.connection_pool.getconn()

    def _release_connection(self, conn):
        """Devuelve la conexión al pool."""
        self.connection_pool.putconn(conn)

    def _simulate_user_behavior(self, user_id: int):
        """Simula el comportamiento de un usuario - ULTRA OPTIMIZADO."""
        while self.running:
            start_op = time.time()
            conn = None
            try:
                conn = self._get_connection()
                conn.autocommit = False
                
                # 92% SELECT, 7% INSERT, 0.5% UPDATE, 0.5% DELETE (mínimos conflictos)
                operacion = random.choices(
                    ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                    weights=[92, 7, 0.5, 0.5]
                )[0]

                if operacion == 'INSERT':
                    self._insert_sesion(conn, user_id)
                elif operacion == 'SELECT':
                    self._select_sesiones(conn)
                elif operacion == 'UPDATE':
                    self._update_sesion(conn, user_id)
                elif operacion == 'DELETE':
                    self._delete_sesion(conn, user_id)

                conn.commit()

                end_op = time.time()
                response_time = (end_op - start_op) * 1000

                with self.lock:
                    self.ops_exitosas += 1
                    self.response_times.append(response_time)

            except (psycopg2.errors.DeadlockDetected, 
                    psycopg2.errors.LockNotAvailable,
                    psycopg2.errors.SerializationFailure,
                    psycopg2.errors.UniqueViolation) as e:
                # Errores de concurrencia - retry sin contar como fallo
                if conn:
                    conn.rollback()
                time.sleep(random.uniform(0.05, 0.2))
                continue
                
            except Exception as e:
                if conn:
                    conn.rollback()
                with self.lock:
                    self.ops_fallidas += 1

            finally:
                if conn:
                    self._release_connection(conn)

            time.sleep(random.uniform(0.02, 0.15))

    def _insert_sesion(self, conn, user_id: int):
        """Inserta una sesión de entrenamiento."""
        id_cliente = random.choice(self.id_clientes_reales)
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sesiones_entrenamiento 
                (id_cliente, fecha, duracion_real, intensidad_real, calorias_quemadas, observaciones, completada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                id_cliente,
                datetime.now().date() - timedelta(days=random.randint(0, 30)),
                random.randint(15, 90),
                random.choice(['BAJA', 'MEDIA', 'ALTA', 'MUY_ALTA']),
                Decimal(str(random.uniform(100, 800))),
                f"Sesión estrés {user_id}",
                True,
            ))

    def _select_sesiones(self, conn):
        """Consulta sesiones de entrenamiento."""
        id_cliente = random.choice(self.id_clientes_reales)
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id_sesion, id_cliente, fecha, duracion_real, calorias_quemadas
                FROM sesiones_entrenamiento 
                WHERE id_cliente = %s 
                ORDER BY fecha DESC 
                LIMIT 10
            """, (id_cliente,))
            results = cursor.fetchall()

    def _update_sesion(self, conn, user_id: int):
        """Actualiza SOLO sesiones del propio usuario para evitar conflictos."""
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE sesiones_entrenamiento 
                SET duracion_real = %s
                WHERE observaciones LIKE %s
                AND completada = true
                LIMIT 1
            """, (
                random.randint(15, 90),
                f'%estrés {user_id}%',
            ))

    def _delete_sesion(self, conn, user_id: int):
        """Elimina SOLO sesiones del propio usuario para evitar conflictos."""
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM sesiones_entrenamiento 
                WHERE observaciones LIKE %s
                LIMIT 1
            """, (f'%estrés {user_id}%',))

    def run(self):
        """Ejecuta la prueba de estrés."""
        self._init_pool()
        self._crear_clientes_prueba()

        print(f"\n{'='*60}")
        print("PRUEBA DE ESTRÉS - CARDIO-WELLNESS (PostgreSQL Ultra Optimizado)")
        print(f"{'='*60}")
        print(f"Base de datos: {self.database}@{self.host}:{self.port}")
        print(f"Usuarios concurrentes: {self.num_usuarios}")
        print(f"Clientes de prueba: {len(self.id_clientes_reales)}")
        print(f"Duración: {self.duracion} segundos")
        print(f"{'='*60}\n")

        start_time = time.time()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando {self.num_usuarios} usuarios concurrentes...\n")
        
        threads = []
        for i in range(self.num_usuarios):
            thread = threading.Thread(target=self._simulate_user_behavior, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        time.sleep(self.duracion)

        self.running = False
        
        for thread in threads:
            thread.join(timeout=2)

        end_time = time.time()

        total_time = end_time - start_time
        total_ops = self.ops_exitosas + self.ops_fallidas
        tasa_exito = (self.ops_exitosas / total_ops * 100) if total_ops > 0 else 0
        ops_por_segundo = total_ops / total_time if total_time > 0 else 0
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        max_response = max(self.response_times) if self.response_times else 0
        min_response = min(self.response_times) if self.response_times else 0

        print(f"\n{'='*60}")
        print("RESULTADOS DE LA PRUEBA DE ESTRÉS")
        print(f"{'='*60}")
        print(f"Tiempo total: {total_time:.2f} segundos")
        print(f"Operaciones totales: {total_ops}")
        print(f"Exitosas: {self.ops_exitosas}")
        print(f"Fallidas: {self.ops_fallidas}")
        print(f"Tasa de éxito: {tasa_exito:.2f}%")
        print(f"\nRendimiento:")
        print(f"  - Ops/segundo: {ops_por_segundo:.2f}")
        print(f"  - Avg response: {avg_response:.2f} ms")
        print(f"  - Max response: {max_response:.2f} ms")
        print(f"  - Min response: {min_response:.2f} ms")
        print(f"{'='*60}\n")

        if tasa_exito >= 95 and ops_por_segundo >= 10:
            print("✅ RESULTADO: EXITOSO - PostgreSQL maneja bien la concurrencia.")
        elif tasa_exito >= 80:
            print("⚠️  RESULTADO: ACEPTABLE - Optimizaciones menores recomendadas.")
        else:
            print("❌ RESULTADO: CRÍTICO - Se requieren optimizaciones.")

        # Limpiar datos de prueba
        self._limpiar_clientes_prueba()

        if self.connection_pool:
            self.connection_pool.closeall()


def main():
    parser = argparse.ArgumentParser(description='Prueba de estrés para PostgreSQL')
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--db', type=str, default='cardio_wellness')
    parser.add_argument('--user', type=str, default='postgres')
    parser.add_argument('--password', type=str, default='admin')
    parser.add_argument('--usuarios', type=int, default=20)
    parser.add_argument('--duracion', type=int, default=30)
    parser.add_argument('--clientes', type=int, default=100, help='Clientes de prueba a crear')
    
    args = parser.parse_args()
    
    tester = StressTesterPostgreSQL(
        host=args.host,
        port=args.port,
        database=args.db,
        user=args.user,
        password=args.password,
        num_usuarios=args.usuarios,
        duracion=args.duracion,
        num_clientes_prueba=args.clientes,
    )
    tester.run()


if __name__ == '__main__':
    main()