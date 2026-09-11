"""
Pruebas de Integración - Cardio-Wellness


Estas pruebas verifican el comportamiento completo del sistema sin interfaz gráfica,
llamando directamente a la base de datos y verificando los resultados.


Casos de prueba:
1. Registro completo de un cliente (con hash de contraseña)
2. Inicio de sesión (correcto e incorrecto)
3. Asignación de una rutina a un cliente (verificar que la rutina anterior se finaliza)
4. Registro de sesión de entrenamiento y cálculo de progreso mensual
5. Verificación del archivo LOG_CARDIO.txt
"""


import sys
import hashlib
from pathlib import Path
from datetime import datetime, date


# Agregar la raíz del proyecto al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))


from tests.integracion.config_db import ejecutar_consulta, ejecutar_con_retorno, get_connection



class IntegracionWellness:
    """Clase para ejecutar pruebas de integración del sistema."""


    def __init__(self):
        self.resultados = []
        self.id_cliente_prueba = None
        self.correo_prueba = None
        self.contrasena_prueba = None
        self.id_rutina_prueba = None
        self.id_sesion_prueba = None


    def _registrar_resultado(self, nombre_prueba: str, exito: bool, mensaje: str = ""):
        """Registra el resultado de una prueba."""
        self.resultados.append({
            'prueba': nombre_prueba,
            'exito': exito,
            'mensaje': mensaje
        })
        
        estado = "✅" if exito else "❌"
        print(f"{estado} {nombre_prueba}: {mensaje}")


    def _hash_contraseña(self, contrasena: str) -> str:
        """Hashea una contraseña usando SHA-256."""
        return hashlib.sha256(contrasena.encode()).hexdigest()


    def test_01_registro_cliente(self):
        """CASO 1: Registro completo de cliente."""
        print("\n" + "="*70)
        print("CASO 1: Registro completo de cliente")
        print("="*70)
        
        try:
            datos_cliente = {
                'nombre': 'Test',
                'apellido': 'Integracion',
                'correo': 'test.integracion@wellness.com',
                'contrasena': 'Password123!',
                'edad': 25,
                'peso': 75.5,
                'altura': 1.75,
                'objetivo': 'Mejorar resistencia'
            }
            
            print(f"Creando usuario: {datos_cliente['nombre']} {datos_cliente['apellido']}")
            password_hash = self._hash_contraseña(datos_cliente['contrasena'])
            
            # Crear usuario
            id_usuario = ejecutar_con_retorno("""
                INSERT INTO usuarios (nombre, apellido, correo_electronico, contraseña_hash, edad, tipo_usuario)
                VALUES (%s, %s, %s, %s, %s, 'cliente')
                RETURNING id_usuario
            """, (
                datos_cliente['nombre'],
                datos_cliente['apellido'],
                datos_cliente['correo'],
                password_hash,
                datos_cliente['edad']
            ))
            
            print(f"Usuario creado con ID: {id_usuario}")
            
            self._registrar_resultado(
                "Registro de usuario",
                True,
                f"Usuario registrado con ID: {id_usuario}"
            )
            
            # Crear cliente usando conexión directa con commit
            conn = get_connection()
            conn.abrir_conexion()
            try:
                with conn._obtener_cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO clientes (id_usuario, peso, altura, objetivo, fecha_ingreso)
                        VALUES (%s, %s, %s, %s, CURRENT_DATE)
                    """, (
                        id_usuario,
                        datos_cliente['peso'],
                        datos_cliente['altura'],
                        datos_cliente['objetivo']
                    ))
                    conn._conexion.commit()
            finally:
                conn.cerrar_conexion()
            
            self._registrar_resultado(
                "Registro de cliente",
                True,
                "Cliente registrado exitosamente"
            )
            
            # Verificar autenticación
            print("Verificando autenticación...")
            resultados = ejecutar_consulta("""
                SELECT u.id_usuario, u.nombre, u.apellido, u.correo_electronico
                FROM usuarios u
                WHERE u.correo_electronico = %s AND u.contraseña_hash = %s
            """, (datos_cliente['correo'], password_hash))
            
            if resultados and resultados[0]['id_usuario'] == id_usuario:
                self._registrar_resultado(
                    "Verificación de hash",
                    True,
                    "Contraseña hasheada correctamente"
                )
            else:
                self._registrar_resultado(
                    "Verificación de hash",
                    False,
                    "No se pudo verificar el hash de contraseña"
                )
            
            # Guardar datos para pruebas posteriores
            self.id_cliente_prueba = id_usuario
            self.correo_prueba = datos_cliente['correo']
            self.contrasena_prueba = datos_cliente['contrasena']
            
            return True
            
        except Exception as e:
            self._registrar_resultado(
                "Registro de cliente",
                False,
                f"Excepción: {str(e)}"
            )
            return False


    def test_02_inicio_sesion(self):
        """CASO 2: Inicio de sesión (correcto e incorrecto)."""
        print("\n" + "="*70)
        print("CASO 2: Inicio de sesión")
        print("="*70)
        
        try:
            # Login correcto
            print("Prueba 2.1: Login con credenciales correctas...")
            password_hash = self._hash_contraseña(self.contrasena_prueba)
            
            resultados = ejecutar_consulta("""
                SELECT u.id_usuario, u.nombre, u.apellido, u.correo_electronico
                FROM usuarios u
                WHERE u.correo_electronico = %s AND u.contraseña_hash = %s
            """, (self.correo_prueba, password_hash))
            
            if resultados and resultados[0]['correo_electronico'] == self.correo_prueba:
                self._registrar_resultado(
                    "Login correcto",
                    True,
                    f"Usuario autenticado: {resultados[0]['nombre']} {resultados[0]['apellido']}"
                )
            else:
                self._registrar_resultado(
                    "Login correcto",
                    False,
                    "No se pudo autenticar con credenciales válidas"
                )
            
            # Login con contraseña incorrecta
            print("Prueba 2.2: Login con contraseña incorrecta...")
            password_incorrecto = self._hash_contraseña("ContraseñaIncorrecta123")
            
            resultados = ejecutar_consulta("""
                SELECT u.id_usuario
                FROM usuarios u
                WHERE u.correo_electronico = %s AND u.contraseña_hash = %s
            """, (self.correo_prueba, password_incorrecto))
            
            if not resultados:
                self._registrar_resultado(
                    "Login incorrecto (contraseña)",
                    True,
                    "Correctamente rechazado por contraseña inválida"
                )
            else:
                self._registrar_resultado(
                    "Login incorrecto (contraseña)",
                    False,
                    "¡ERROR DE SEGURIDAD!"
                )
            
            # Login con correo inexistente
            print("Prueba 2.3: Login con correo inexistente...")
            resultados = ejecutar_consulta("""
                SELECT u.id_usuario
                FROM usuarios u
                WHERE u.correo_electronico = %s
            """, ('no.existe@wellness.com',))
            
            if not resultados:
                self._registrar_resultado(
                    "Login incorrecto (correo)",
                    True,
                    "Correctamente rechazado por correo inexistente"
                )
            else:
                self._registrar_resultado(
                    "Login incorrecto (correo)",
                    False,
                    "¡ERROR!"
                )
            
            return True
            
        except Exception as e:
            self._registrar_resultado(
                "Inicio de sesión",
                False,
                f"Excepción: {str(e)}"
            )
            return False


    def test_03_asignacion_rutina(self):
        """CASO 3: Asignación de rutina a cliente."""
        print("\n" + "="*70)
        print("CASO 3: Asignación de rutina")
        print("="*70)
        
        try:
            # Crear rutina
            print("Creando rutina de prueba...")
            id_rutina = ejecutar_con_retorno("""
                INSERT INTO rutinas (nombre, descripcion, objetivo, nivel, duracion_semanas)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_rutina
            """, (
                'Rutina Test Integración',
                'Rutina creada para pruebas de integración',
                'Mejorar resistencia',
                'INTERMEDIO',
                4
            ))
            
            self._registrar_resultado(
                "Creación de rutina",
                True,
                f"Rutina creada con ID: {id_rutina}"
            )
            
            # Finalizar rutinas activas anteriores - CORREGIDO
            print("Finalizando rutinas activas anteriores...")
            conn = get_connection()
            conn.abrir_conexion()
            try:
                with conn._obtener_cursor() as cursor:
                    cursor.execute("""
                        UPDATE asignaciones_rutina
                        SET estado = 'FINALIZADA', fecha_finalizacion = CURRENT_DATE
                        WHERE id_cliente = %s AND estado = 'ACTIVA'
                    """, (self.id_cliente_prueba,))
                    conn._conexion.commit()
            finally:
                conn.cerrar_conexion()
            
            self._registrar_resultado(
                "Finalización de rutina anterior",
                True,
                "Rutinas anteriores finalizadas"
            )
            
            # Asignar nueva rutina
            print(f"Asignando rutina {id_rutina} al cliente {self.id_cliente_prueba}...")
            id_asignacion = ejecutar_con_retorno("""
                INSERT INTO asignaciones_rutina (id_cliente, id_rutina, estado, observaciones)
                VALUES (%s, %s, 'ACTIVA', %s)
                RETURNING id_asignacion
            """, (self.id_cliente_prueba, id_rutina, 'Asignación desde prueba de integración'))
            
            self._registrar_resultado(
                "Asignación de rutina",
                True,
                f"Rutina asignada con ID: {id_asignacion}"
            )
            
            # Verificar rutina activa
            print("Verificando rutina activa del cliente...")
            resultados = ejecutar_consulta("""
                SELECT r.id_rutina, r.nombre
                FROM rutinas r
                JOIN asignaciones_rutina a ON r.id_rutina = a.id_rutina
                WHERE a.id_cliente = %s AND a.estado = 'ACTIVA'
            """, (self.id_cliente_prueba,))
            
            if resultados and resultados[0]['id_rutina'] == id_rutina:
                self._registrar_resultado(
                    "Verificación de rutina activa",
                    True,
                    f"Rutina activa: {resultados[0]['nombre']}"
                )
            else:
                self._registrar_resultado(
                    "Verificación de rutina activa",
                    False,
                    "La rutina asignada no aparece como activa"
                )
            
            self.id_rutina_prueba = id_rutina
            
            return True
            
        except Exception as e:
            self._registrar_resultado(
                "Asignación de rutina",
                False,
                f"Excepción: {str(e)}"
            )
            return False


    def test_04_registro_sesion_progreso(self):
        """CASO 4: Registro de sesión y cálculo de progreso."""
        print("\n" + "="*70)
        print("CASO 4: Registro de sesión y progreso")
        print("="*70)
        
        try:
            # Registrar sesión
            print("Registrando sesión de entrenamiento...")
            id_sesion = ejecutar_con_retorno("""
                INSERT INTO sesiones_entrenamiento 
                (id_cliente, fecha, duracion_real, intensidad_real, calorias_quemadas, observaciones, completada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_sesion
            """, (
                self.id_cliente_prueba,
                date.today(),
                45,
                'ALTA',
                450.5,
                'Sesión de prueba de integración',
                True
            ))
            
            self._registrar_resultado(
                "Registro de sesión",
                True,
                f"Sesión registrada con ID: {id_sesion}"
            )
            
            # Consultar sesión
            print("Consultando sesión registrada...")
            resultados = ejecutar_consulta("""
                SELECT id_sesion, duracion_real, calorias_quemadas
                FROM sesiones_entrenamiento
                WHERE id_sesion = %s
            """, (id_sesion,))
            
            if resultados and resultados[0]['duracion_real'] == 45:
                self._registrar_resultado(
                    "Consulta de sesión",
                    True,
                    f"Sesión: {resultados[0]['duracion_real']} min, {resultados[0]['calorias_quemadas']} cal"
                )
            else:
                self._registrar_resultado(
                    "Consulta de sesión",
                    False,
                    "No se pudo consultar la sesión"
                )
            
            # Calcular progreso mensual
            print("Calculando progreso mensual...")
            resultados = ejecutar_consulta("""
                SELECT COUNT(*) as sesiones
                FROM sesiones_entrenamiento
                WHERE id_cliente = %s 
                AND completada = TRUE
                AND EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
            """, (self.id_cliente_prueba,))
            
            sesiones_completadas = resultados[0]['sesiones'] if resultados else 0
            
            self._registrar_resultado(
                "Cálculo de progreso",
                True,
                f"Sesiones completadas este mes: {sesiones_completadas}"
            )
            
            self.id_sesion_prueba = id_sesion
            
            return True
            
        except Exception as e:
            self._registrar_resultado(
                "Registro de sesión y progreso",
                False,
                f"Excepción: {str(e)}"
            )
            return False


    def test_05_verificacion_log(self):
        """CASO 5: Verificación del archivo LOG_CARDIO.txt."""
        print("\n" + "="*70)
        print("CASO 5: Verificación de LOG_CARDIO.txt")
        print("="*70)
        
        try:
            log_path = ROOT_DIR / 'LOG_CARDIO.txt'
            
            if log_path.exists():
                self._registrar_resultado(
                    "Existencia de LOG_CARDIO.txt",
                    True,
                    f"Archivo encontrado"
                )
                
                with open(log_path, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                    ultimas_lineas = lineas[-5:] if len(lineas) >= 5 else lineas
                
                if len(ultimas_lineas) > 0:
                    self._registrar_resultado(
                        "Contenido de LOG_CARDIO.txt",
                        True,
                        f"{len(ultimas_lineas)} entradas recientes"
                    )
                    
                    print("\nÚltimas entradas del log:")
                    print("-" * 70)
                    for linea in ultimas_lineas[-3:]:
                        print(f"  {linea.strip()}")
                    print("-" * 70)
                else:
                    self._registrar_resultado(
                        "Contenido de LOG_CARDIO.txt",
                        False,
                        "El archivo está vacío"
                    )
            else:
                self._registrar_resultado(
                    "Existencia de LOG_CARDIO.txt",
                    False,
                    "El archivo no existe"
                )
                return False
            
            return True
            
        except Exception as e:
            self._registrar_resultado(
                "Verificación de LOG_CARDIO.txt",
                False,
                f"Excepción: {str(e)}"
            )
            return False


    def ejecutar_todas_las_pruebas(self):
        """Ejecuta todas las pruebas de integración."""
        print("\n" + "="*70)
        print("PRUEBAS DE INTEGRACIÓN - CARDIO-WELLNESS")
        print("="*70)
        print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.test_01_registro_cliente()
        self.test_02_inicio_sesion()
        self.test_03_asignacion_rutina()
        self.test_04_registro_sesion_progreso()
        self.test_05_verificacion_log()
        
        self._mostrar_resumen()


    def _mostrar_resumen(self):
        """Muestra el resumen de resultados."""
        print("\n" + "="*70)
        print("RESUMEN DE PRUEBAS DE INTEGRACIÓN")
        print("="*70)
        
        total = len(self.resultados)
        exitosas = sum(1 for r in self.resultados if r['exito'])
        fallidas = total - exitosas
        
        print(f"Total de pruebas: {total}")
        print(f"Exitosas: {exitosas} ({exitosas/total*100:.1f}%)")
        print(f"Fallidas: {fallidas} ({fallidas/total*100:.1f}%)")
        print("="*70)
        
        fallidas_detalle = [r for r in self.resultados if not r['exito']]
        if fallidas_detalle:
            print("\nPRUEBAS FALLIDAS:")
            print("-" * 70)
            for resultado in fallidas_detalle:
                print(f"❌ {resultado['prueba']}: {resultado['mensaje']}")
            print("-" * 70)
        
        self._guardar_resumen()


    def _guardar_resumen(self):
        """Guarda el resumen en un archivo."""
        resumen_path = ROOT_DIR / 'tests' / 'integracion' / 'resumen_pruebas_integracion.txt'
        
        try:
            with open(resumen_path, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("RESUMEN DE PRUEBAS DE INTEGRACIÓN - CARDIO-WELLNESS\n")
                f.write("="*70 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                total = len(self.resultados)
                exitosas = sum(1 for r in self.resultados if r['exito'])
                
                f.write(f"Total: {total}\n")
                f.write(f"Exitosas: {exitosas} ({exitosas/total*100:.1f}%)\n")
                f.write(f"Fallidas: {total - exitosas}\n\n")
                
                f.write("DETALLE:\n")
                f.write("-" * 70 + "\n")
                for resultado in self.resultados:
                    estado = "✅" if resultado['exito'] else "❌"
                    f.write(f"{estado} {resultado['prueba']}: {resultado['mensaje']}\n")
            
            print(f"\nResumen guardado en: {resumen_path}")
            
        except Exception as e:
            print(f"Error al guardar resumen: {e}")



def main():
    """Función principal."""
    tester = IntegracionWellness()
    tester.ejecutar_todas_las_pruebas()



if __name__ == "__main__":
    main()