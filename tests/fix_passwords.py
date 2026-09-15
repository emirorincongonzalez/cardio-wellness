import os

# Diccionario de reemplazos de contraseñas débiles -> fuertes
password_replacements = {
    '"123456"': '"Test123!"',
    '"password"': '"Test123!"',
    '"test123"': '"Test123!"',
    "'123456'": "'Test123!'",
    "'password'": "'Test123!'",
    "'test123'": "'Test123!'",
    '"test"': '"Test123!"',
    "'test'": "'Test123!'",
    '"admin123"': '"Admin123!"',
    "'admin123'": "'Admin123!'",
}

# Archivos de tests a corregir
test_files = [
    'tests/test_cliente_dao.py',
    'tests/test_control_autenticacion.py',
    'tests/test_daos.py',
    'tests/test_gestor_seguridad.py',
    'tests/test_usuario_dao.py',
    'tests/test_asignacion_rutina_dao.py',
    'tests/test_asignacion_rutina_dao_excepciones.py',
    'tests/test_progreso_mensual_dao.py',
    'tests/test_progreso_mensual_dao_excepciones.py',
    'tests/test_rutina_dao_excepciones.py',
    'tests/test_sesion_entrenamiento_dao.py',
    'tests/test_sesion_entrenamiento_dao_excepciones.py',
]

total_replacements = 0

for test_file in test_files:
    if not os.path.exists(test_file):
        print(f"⚠️  Archivo no encontrado: {test_file}")
        continue
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for weak, strong in password_replacements.items():
        if weak in content:
            content = content.replace(weak, strong)
    
    if content != original_content:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {test_file}: Actualizado")
    else:
        print(f"ℹ️  {test_file}: Sin cambios")

print(f"\n✅ Corrección completada")