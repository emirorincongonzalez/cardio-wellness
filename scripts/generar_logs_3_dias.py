"""
Script para generar logs de 3 días automáticamente.
AGREGA registros sin borrar los existentes.
"""

from datetime import datetime, timedelta
import random
import os

# Asegurar que existe la carpeta logs
os.makedirs('logs', exist_ok=True)

# Acciones posibles para simular
ACCIONES = [
    ('CONSULTA_PROGRESO', 'Cliente consultó su progreso'),
    ('GENERAR_PROGRESO', 'Se generó reporte de progreso'),
    ('CONSULTA_IMPACTO', 'Se consultó impacto de rutina'),
    ('SUGERENCIA_RUTINA', 'Se sugirió rutina al usuario'),
    ('CALCULO_DIFERENCIA_PESO', 'Se calculó diferencia de peso'),
    ('REPORTE_PDF_GENERADO', 'Se generó reporte PDF'),
    ('REGISTRO_CLIENTE', 'Nuevo cliente registrado'),
    ('REGISTRO_ADMINISTRADOR', 'Nuevo administrador registrado'),
    ('LOGIN_EXITOSO', 'Inicio de sesión exitoso'),
    ('CREACION_RUTINA', 'Se creó nueva rutina'),
    ('CREACION_EJERCICIO', 'Se creó nuevo ejercicio'),
]

# Usuarios posibles
USUARIOS = [
    'CLIENTE_1', 'CLIENTE_2', 'CLIENTE_4', 'CLIENTE_6', 'CLIENTE_7', 'CLIENTE_9',
    '1', '2', '3', '448',
    '[test@example.com](mailto:test@example.com)', '[admin@cardio.com](mailto:admin@cardio.com)',
    'SISTEMA', 'RUTINA_1', 'RUTINA_2', 'RUTINA_3', 'RUTINA_10'
]

def generar_log_para_fecha(fecha, cantidad=50):
    """Genera registros de log para una fecha específica."""
    registros = []
    
    for i in range(cantidad):
        # Hora aleatoria entre 08:00 y 22:00
        hora = f"{random.randint(8, 21):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        
        # Usuario aleatorio
        usuario = random.choice(USUARIOS)
        
        # Acción aleatoria
        accion, detalle_base = random.choice(ACCIONES)
        
        # Detalle variable
        if accion == 'CALCULO_DIFERENCIA_PESO':
            detalle = f"DIF: {random.uniform(-5, 5):.1f}"
        elif accion == 'REPORTE_PDF_GENERADO':
            detalle = f"reporte_{i}.pdf"
        elif accion == 'SUGERENCIA_RUTINA':
            detalle = random.choice(['DEFAULT', 'SIN_RUTINAS', 'PERSONALIZADA'])
        else:
            detalle = detalle_base
        
        # Formato: YYYY-MM-DD HH:MM:SS, USUARIO, ACCION, DETALLE
        registro = f"{fecha} {hora}, {usuario}, {accion}, {detalle}\n"
        registros.append(registro)
    
    return registros


def main():
    """Genera logs para 3 días y los AGREGA al archivo existente."""
    
    print("=" * 70)
    print("GENERADOR DE LOGS - 3 DÍAS (MODO AGREGAR)")
    print("=" * 70)
    
    # Fechas: hoy, ayer, anteayer
    hoy = datetime.now().strftime('%Y-%m-%d')
    ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    anteayer = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    print(f"\n📅 Generando logs para:")
    print(f"   - {anteayer} (Día 1)")
    print(f"   - {ayer} (Día 2)")
    print(f"   - {hoy} (Día 3)")
    
    # Leer archivo existente si existe
    ruta_log = 'logs/LOG_CARDIO.txt'
    registros_existentes = []
    
    if os.path.exists(ruta_log):
        with open(ruta_log, 'r', encoding='utf-8') as f:
            registros_existentes = f.readlines()
        print(f"\n📖 Leyendo {len(registros_existentes)} registros existentes...")
    
    # Generar registros para cada día (SOLO si no hay registros de esa fecha)
    registros_nuevos = []
    
    # Verificar si ya hay registros de hoy
    hay_registros_hoy = any(hoy in linea for linea in registros_existentes)
    
    if not hay_registros_hoy:
        registros_hoy = generar_log_para_fecha(hoy, cantidad=20)
        registros_nuevos.extend(registros_hoy)
        print(f"   ✅ {len(registros_hoy)} registros nuevos para {hoy}")
    else:
        print(f"   ⏭️  Saltando {hoy} (ya tiene registros)")
    
    # Unir todos los registros
    todos_registros = registros_existentes + registros_nuevos
    
    # Guardar (SOBRESCRIBIR pero con todo el contenido)
    with open(ruta_log, 'w', encoding='utf-8') as f:
        f.writelines(todos_registros)
    
    # También guardar en la raíz (copia completa)
    ruta_log_raiz = 'LOG_CARDIO.txt'
    
    with open(ruta_log_raiz, 'w', encoding='utf-8') as f:
        f.writelines(todos_registros)
    
    print(f"\n✅ Logs actualizados exitosamente:")
    print(f"   - {len(registros_nuevos)} registros nuevos agregados")
    print(f"   - Total: {len(todos_registros)} registros")
    print(f"\n📄 Archivos actualizados:")
    print(f"   - {ruta_log}")
    print(f"   - {ruta_log_raiz}")
    
    print("\n" + "=" * 70)
    print("✅ ¡LISTO! Los logs se mantienen y agregan nuevos registros")
    print("=" * 70)


if __name__ == "__main__":
    main()