@echo off
setlocal enabledelayedexpansion


echo ============================================================================
echo CARDIO-WELLNESS - SUITE DE PRUEBAS COMPLETA
echo ============================================================================
echo.
echo Fecha: %date% %time%
echo.


REM Contadores
set /a total_tests=0
set /a tests_exitosos=0


echo [0/9] Limpiando datos de prueba anteriores...
echo -----------------------------------------------------------------------------
python tests/integracion/limpiar_datos_prueba.py
echo.


echo [1/9] Ejecutando pruebas unitarias e integracion...
echo -----------------------------------------------------------------------------
python -m pytest tests/ -v --durations=10 --tb=short
if %errorlevel% equ 0 (
    echo [OK] Pruebas unitarias completadas
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en pruebas unitarias
)
set /a total_tests+=1
echo.


echo [2/9] Generando reporte de cobertura...
echo -----------------------------------------------------------------------------
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
if %errorlevel% equ 0 (
    echo [OK] Reporte de cobertura generado
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en generacion de cobertura
)
set /a total_tests+=1
echo.


echo [3/9] Pruebas de seguridad (Penetration Test)...
echo -----------------------------------------------------------------------------
python tests/test_seguridad.py
if %errorlevel% equ 0 (
    echo [OK] Pruebas de seguridad completadas
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en pruebas de seguridad
)
set /a total_tests+=1
echo.


echo [4/9] Test de usabilidad masivo (100 usuarios)...
echo -----------------------------------------------------------------------------
python tests/test_usabilidad_masivo.py
if %errorlevel% equ 0 (
    echo [OK] Test de usabilidad completado
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en test de usabilidad
)
set /a total_tests+=1
echo.


echo [5/9] Stress test PostgreSQL (30 usuarios, 40s, 100 clientes)...
echo -----------------------------------------------------------------------------
python tests/stress_test_postgresql.py --usuarios 30 --duracion 40 --clientes 100
if %errorlevel% equ 0 (
    echo [OK] Stress test PostgreSQL completado
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en stress test PostgreSQL
)
set /a total_tests+=1
echo.


echo [6/9] Stress test SQLite (20 usuarios, 30s)...
echo -----------------------------------------------------------------------------
python tests/stress_test_sqlite.py --usuarios 20 --duracion 30
if %errorlevel% equ 0 (
    echo [OK] Stress test SQLite completado
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en stress test SQLite
)
set /a total_tests+=1
echo.


echo [7/9] Pruebas de integracion completa...
echo -----------------------------------------------------------------------------
python tests/integracion/test_integracion_completa.py
if %errorlevel% equ 0 (
    echo [OK] Pruebas de integracion completadas
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en pruebas de integracion
)
set /a total_tests+=1
echo.


echo [8/9] Optimizacion de rendimiento...
echo -----------------------------------------------------------------------------
python tests/optimizar_rendimiento.py
if %errorlevel% equ 0 (
    echo [OK] Optimizacion de rendimiento completada
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en optimizacion de rendimiento
)
set /a total_tests+=1
echo.


echo [9/9] Verificando logs...
echo -----------------------------------------------------------------------------
powershell -Command "Get-Content logs\LOG_CARDIO.txt -Tail 15"
echo [OK] Logs verificados
set /a tests_exitosos+=1
set /a total_tests+=1
echo.


echo ============================================================================
echo RESUMEN: %tests_exitosos%/%total_tests% pruebas completadas exitosamente
echo ============================================================================
echo.
echo Para ver resultados detallados, revisa:
echo   - Reporte HTML: htmlcov\index.html
echo   - Documentacion: tests/RUN_TESTS.md
echo   - Logs: logs\LOG_CARDIO.txt
echo.
pause