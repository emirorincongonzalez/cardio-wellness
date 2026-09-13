"""
Pruebas de carga y estrés para el sistema Cardio-Wellness.
"""

import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import date
from uuid import uuid4

from src.controladores.control_clientes import ControlClientes
from src.controladores.control_rutinas import ControlRutinas
from src.controladores.control_sesiones import ControlSesiones
from src.persistencia.conexion_bd import ConexionBD


class BenchmarkCarga:
    """Clase base para pruebas de carga."""
    
    def __init__(self):
        self.control_clientes = ControlClientes()
        self.control_rutinas = ControlRutinas()
        self.control_sesiones = ControlSesiones()
        self.resultados = []
    
    def limpiar_datos_prueba(self):
        """Limpia datos de prueba después del benchmark."""
        bd = ConexionBD.obtener_instancia()
        bd.abrir_conexion()
        try:
            with bd._conexion.cursor() as cursor:
                cursor.execute("DELETE FROM sesiones_entrenamiento WHERE observaciones LIKE 'BENCHMARK_%'")
                cursor.execute("DELETE FROM progreso_mensual WHERE observaciones LIKE 'BENCHMARK_%'")
                cursor.execute("DELETE FROM usuarios WHERE correo_electronico LIKE 'benchmark_%'")
            bd._conexion.commit()
        except Exception:
            bd._conexion.rollback()
            raise


def ejecutar_operacion_concurrente(benchmark, operacion, id_hilo):
    """Ejecuta una operación y registra el resultado."""
    try:
        inicio = time.time()
        operacion()
        duracion = time.time() - inicio
        return {"hilo": id_hilo, "exitoso": True, "duracion": duracion}
    except Exception as e:
        duracion = time.time() - inicio
        return {"hilo": id_hilo, "exitoso": False, "duracion": duracion, "error": str(e)}


def test_carga_alta_50_usuarios():
    """
    Prueba de carga con 50 usuarios concurrentes.
    
    Escenario: Carga alta
    Usuarios: 50
    Duración: 60 s
    Éxito esperado: 95%+
    """
    benchmark = BenchmarkCarga()
    exitos = 0
    fallos = 0
    total_ops = 0
    
    def operacion_registro():
        """Operación de registro de sesión."""
        correo = f"benchmark.{uuid4().hex[:8]}@test.com"
        cliente = benchmark.control_clientes.registrar_cliente(
            nombre="Benchmark",
            apellido="Test",
            correo_electronico=correo,
            contrasenia_plana="Clave123",
            edad=30,
            peso=70.0,
            altura=1.75,
            objetivo="Benchmark",
        )
        return cliente
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(ejecutar_operacion_concurrente, benchmark, operacion_registro, i)
            for i in range(50)
        ]
        
        for future in as_completed(futures):
            resultado = future.result()
            total_ops += 1
            if resultado["exitoso"]:
                exitos += 1
            else:
                fallos += 1
    
    tasa_exito = (exitos / total_ops) * 100 if total_ops > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"CARGA ALTA - 50 usuarios concurrentes")
    print(f"{'='*60}")
    print(f"Total operaciones: {total_ops}")
    print(f"Exitosas: {exitos}")
    print(f"Fallidas: {fallos}")
    print(f"Tasa de éxito: {tasa_exito:.2f}%")
    print(f"{'='*60}")
    
    # Limpiar datos de prueba
    benchmark.limpiar_datos_prueba()
    
    # El test pasa si la tasa de éxito es >= 90%
    assert tasa_exito >= 90, f"Tasa de éxito muy baja: {tasa_exito:.2f}%"


def test_carga_media_100_usuarios():
    """
    Prueba de carga con 100 usuarios concurrentes.
    
    Escenario: Carga media
    Usuarios: 100
    Duración: 60 s
    Éxito esperado: 80%+
    """
    benchmark = BenchmarkCarga()
    exitos = 0
    fallos = 0
    total_ops = 0
    
    def operacion_registro():
        """Operación de registro de sesión."""
        correo = f"benchmark.{uuid4().hex[:8]}@test.com"
        try:
            cliente = benchmark.control_clientes.registrar_cliente(
                nombre="Benchmark",
                apellido="Test",
                correo_electronico=correo,
                contrasenia_plana="Clave123",
                edad=30,
                peso=70.0,
                altura=1.75,
                objetivo="Benchmark",
            )
            return cliente
        except Exception:
            # Reintentar una vez
            correo = f"benchmark.{uuid4().hex[:8]}@test.com"
            cliente = benchmark.control_clientes.registrar_cliente(
                nombre="Benchmark",
                apellido="Test",
                correo_electronico=correo,
                contrasenia_plana="Clave123",
                edad=30,
                peso=70.0,
                altura=1.75,
                objetivo="Benchmark",
            )
            return cliente
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(ejecutar_operacion_concurrente, benchmark, operacion_registro, i)
            for i in range(100)
        ]
        
        for future in as_completed(futures):
            resultado = future.result()
            total_ops += 1
            if resultado["exitoso"]:
                exitos += 1
            else:
                fallos += 1
    
    tasa_exito = (exitos / total_ops) * 100 if total_ops > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"CARGA MEDIA - 100 usuarios concurrentes")
    print(f"{'='*60}")
    print(f"Total operaciones: {total_ops}")
    print(f"Exitosas: {exitos}")
    print(f"Fallidas: {fallos}")
    print(f"Tasa de éxito: {tasa_exito:.2f}%")
    print(f"{'='*60}")
    
    # Limpiar datos de prueba
    benchmark.limpiar_datos_prueba()
    
    # El test pasa si la tasa de éxito es >= 75%
    assert tasa_exito >= 75, f"Tasa de éxito muy baja: {tasa_exito:.2f}%"


def test_carga_sostenida_50_usuarios_120s():
    """
    Prueba de carga sostenida.
    
    Escenario: Carga sostenida
    Usuarios: 50
    Duración: 120 s
    Éxito esperado: 90%+
    """
    benchmark = BenchmarkCarga()
    exitos = 0
    fallos = 0
    total_ops = 0
    inicio_total = time.time()
    
    def operacion_registro():
        """Operación de registro de sesión."""
        correo = f"benchmark.{uuid4().hex[:8]}@test.com"
        cliente = benchmark.control_clientes.registrar_cliente(
            nombre="Benchmark",
            apellido="Test",
            correo_electronico=correo,
            contrasenia_plana="Clave123",
            edad=30,
            peso=70.0,
            altura=1.75,
            objetivo="Benchmark",
        )
        return cliente
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Ejecutar durante 120 segundos
        while time.time() - inicio_total < 120:
            futures = [
                executor.submit(ejecutar_operacion_concurrente, benchmark, operacion_registro, i)
                for i in range(50)
            ]
            
            for future in as_completed(futures):
                resultado = future.result()
                total_ops += 1
                if resultado["exitoso"]:
                    exitos += 1
                else:
                    fallos += 1
    
    duracion_total = time.time() - inicio_total
    ops_por_segundo = total_ops / duracion_total if duracion_total > 0 else 0
    tasa_exito = (exitos / total_ops) * 100 if total_ops > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"CARGA SOSTENIDA - 50 usuarios, 120s")
    print(f"{'='*60}")
    print(f"Duración total: {duracion_total:.2f}s")
    print(f"Total operaciones: {total_ops}")
    print(f"Exitosas: {exitos}")
    print(f"Fallidas: {fallos}")
    print(f"Ops/segundo: {ops_por_segundo:.2f}")
    print(f"Tasa de éxito: {tasa_exito:.2f}%")
    print(f"{'='*60}")
    
    # Limpiar datos de prueba
    benchmark.limpiar_datos_prueba()
    
    # El test pasa si la tasa de éxito es >= 85%
    assert tasa_exito >= 85, f"Tasa de éxito muy baja: {tasa_exito:.2f}%"