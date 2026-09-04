"""
Prueba de estrés para la base de datos SQLite de Cardio-Wellness.
Simula múltiples usuarios concurrentes realizando operaciones CRUD.
"""

import sqlite3
import threading
import time
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta


class StressTester:
    """Clase para ejecutar pruebas de estrés en la base de datos."""

    def __init__(self, db_path: str, num_usuarios: int = 50, duracion: int = 60):
        self.db_path = Path(db_path)
        self.num_usuarios = num_usuarios
        self.duracion = duracion
        self.running = True
        self.ops_exitosas = 0
        self.ops_fallidas = 0
        self.response_times = []
        self.lock = threading.Lock()

    def _prepare_database(self):
        """Crea el directorio y la tabla antes de iniciar los hilos."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sesiones_entrenamiento (
                id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                id_rutina INTEGER,
                fecha_sesion TEXT NOT NULL,
                duracion_real INTEGER NOT NULL,
                intensidad_real TEXT NOT NULL,
                calorias_quemadas REAL NOT NULL,
                observaciones TEXT
            )
        """)

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión SQLite con configuración optimizada."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            isolation_level=None,
        )
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        conn.row_factory = sqlite3.Row
        return conn

    def _simulate_user_behavior(self, user_id: int):
        """Simula el comportamiento de un usuario realizando operaciones."""
        while self.running:
            start_op = time.time()
            try:
                conn = self._get_connection()
                operacion = random.choice(['INSERT', 'SELECT', 'UPDATE', 'DELETE'])

                if operacion == 'INSERT':
                    self._insert_sesion(conn, user_id)
                elif operacion == 'SELECT':
                    self._select_sesiones(conn)
                elif operacion == 'UPDATE':
                    self._update_sesion(conn, user_id)
                elif operacion == 'DELETE':
                    self._delete_sesion(conn, user_id)

                conn.close()

                end_op = time.time()
                response_time = (end_op - start_op) * 1000

                with self.lock:
                    self.ops_exitosas += 1
                    self.response_times.append(response_time)

            except Exception as e:
                with self.lock:
                    self.ops_fallidas += 1
                print(f"Error usuario {user_id}: {e}")

            time.sleep(random.uniform(0.1, 0.5))

    def _insert_sesion(self, conn: sqlite3.Connection, user_id: int):
        """Inserta una sesión de entrenamiento."""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sesiones_entrenamiento 
            (id_cliente, id_rutina, fecha_sesion, duracion_real, intensidad_real, calorias_quemadas, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            random.randint(1, 100),
            random.randint(1, 20),
            datetime.now().isoformat(),
            random.randint(15, 90),
            random.choice(['Baja', 'Media', 'Alta', 'Muy Alta']),
            random.uniform(100, 800),
            f"Sesión prueba usuario {user_id}"
        ))
        conn.commit()

    def _select_sesiones(self, conn: sqlite3.Connection):
        """Consulta sesiones de entrenamiento."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sesiones_entrenamiento 
            WHERE id_cliente = ? 
            ORDER BY fecha_sesion DESC 
            LIMIT 10
        """, (random.randint(1, 100),))
        results = cursor.fetchall()

    def _update_sesion(self, conn: sqlite3.Connection, user_id: int):
        """Actualiza una sesión existente usando subquery compatible."""
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sesiones_entrenamiento 
            SET duracion_real = ?, intensidad_real = ?, calorias_quemadas = ?
            WHERE id_sesion = (
                SELECT id_sesion FROM sesiones_entrenamiento 
                WHERE id_cliente = ? 
                LIMIT 1
            )
        """, (
            random.randint(15, 90),
            random.choice(['Baja', 'Media', 'Alta', 'Muy Alta']),
            random.uniform(100, 800),
            random.randint(1, 100)
        ))
        conn.commit()

    def _delete_sesion(self, conn: sqlite3.Connection, user_id: int):
        """Elimina sesiones usando subquery compatible."""
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM sesiones_entrenamiento 
            WHERE id_sesion = (
                SELECT id_sesion FROM sesiones_entrenamiento 
                WHERE id_cliente = ? 
                LIMIT 1
            )
        """, (random.randint(1, 100),))
        conn.commit()

    def run(self):
        """Ejecuta la prueba de estrés con múltiples usuarios concurrentes."""
        self._prepare_database()

        print(f"\n{'='*60}")
        print("PRUEBA DE ESTRÉS - CARDIO-WELLNESS")
        print(f"{'='*60}")
        print(f"Base de datos: {self.db_path}")
        print(f"Usuarios concurrentes: {self.num_usuarios}")
        print(f"Duración: {self.duracion} segundos")
        print(f"{'='*60}\n")

        start_time = time.time()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando {self.num_usuarios} usuarios concurrentes...\n")
        for i in range(self.num_usuarios):
            thread = threading.Thread(target=self._simulate_user_behavior, args=(i+1,))
            thread.daemon = True
            thread.start()

        time.sleep(self.duracion)

        self.running = False
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
        print(f"Tiempo total de ejecución: {total_time:.2f} segundos")
        print(f"Operaciones totales: {total_ops}")
        print(f"Operaciones exitosas: {self.ops_exitosas}")
        print(f"Operaciones fallidas: {self.ops_fallidas}")
        print(f"Tasa de éxito: {tasa_exito:.2f}%")
        print(f"\nRendimiento:")
        print(f"  - Operaciones por segundo: {ops_por_segundo:.2f}")
        print(f"  - Tiempo promedio de respuesta: {avg_response:.2f} ms")
        print(f"  - Tiempo máximo de respuesta: {max_response:.2f} ms")
        print(f"  - Tiempo mínimo de respuesta: {min_response:.2f} ms")
        print(f"{'='*60}\n")

        if tasa_exito >= 95 and ops_por_segundo >= 10:
            print("✅ RESULTADO: EXITOSO - La base de datos maneja bien la concurrencia.")
        elif tasa_exito >= 80:
            print("⚠️  RESULTADO: ACEPTABLE - Se recomiendan optimizaciones menores.")
        else:
            print("❌ RESULTADO: CRÍTICO - Se requieren optimizaciones urgentes de la base de datos.")


def main():
    parser = argparse.ArgumentParser(description='Prueba de estrés para SQLite')
    parser.add_argument('--usuarios', type=int, default=50, help='Número de usuarios concurrentes')
    parser.add_argument('--duracion', type=int, default=60, help='Duración de la prueba en segundos')
    parser.add_argument('--db', type=str, default='database/cardio.db', help='Ruta a la base de datos')
    
    args = parser.parse_args()
    
    if not args.db.startswith('database/'):
        print(f"\n⚠️  ADVERTENCIA: La base de datos '{args.db}' no existe.")
        print("   Se creará una base de datos temporal para la prueba.\n")
    
    tester = StressTester(
        db_path=args.db,
        num_usuarios=args.usuarios,
        duracion=args.duracion
    )
    tester.run()


if __name__ == '__main__':
    main()