# Pruebas de Integración - Cardio-Wellness

Estas pruebas verifican el comportamiento completo del sistema sin interfaz gráfica, llamando directamente a los controladores y verificando los resultados en la base de datos.

## Casos de Prueba

### 1. Registro completo de un cliente
- Crea un cliente con datos válidos
- Verifica que se crea el usuario con contraseña hasheada
- Verifica que se crea el registro en clientes
- Verifica que se puede consultar el cliente

### 2. Inicio de sesión (correcto e incorrecto)
- Intentar login con credenciales correctas
- Intentar login con contraseña incorrecta
- Intentar login con correo inexistente
- Verificar que se registran los intentos en el log

### 3. Asignación de una rutina a un cliente
- Crear una rutina de prueba
- Asignar rutina al cliente
- Verificar que la rutina anterior se finaliza (si existe)
- Verificar que la nueva rutina está activa

### 4. Registro de sesión de entrenamiento y cálculo de progreso mensual
- Registrar una sesión de entrenamiento
- Verificar que la sesión se guarda correctamente
- Calcular progreso mensual
- Verificar que el progreso se actualiza

### 5. Verificación del archivo LOG_CARDIO.txt
- Verificar que el archivo LOG_CARDIO.txt existe
- Verificar que se están registrando las operaciones
- Verificar formato de los logs

## Ejecución

```bash
# Desde la raíz del proyecto
python tests/integracion/test_integracion_completa.py
```

## Requisitos

- Base de datos PostgreSQL configurada y con el esquema creado
- Controladores implementados y funcionando
- Gestor de seguridad operativo
- Sistema de logging configurado

## Salida

Las pruebas generan:
- Salida en consola con resultados de cada prueba (✅/❌)
- Archivo `resumen_pruebas_integracion.txt` con el detalle completo
- Registro en `LOG_CARDIO.txt` de todas las operaciones

## Datos de Prueba

Las pruebas crean automáticamente:
- 1 cliente de prueba (test.integracion@wellness.com)
- 1 rutina de prueba (Rutina Test Integración)
- 1 sesión de entrenamiento
- 1 registro de progreso mensual

**Nota:** Los datos se crean con prefijos "Test" para fácil identificación y eliminación posterior.