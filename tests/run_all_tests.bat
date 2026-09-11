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

echo [0/7] Limpiando datos de prueba anteriores...
echo -----------------------------------------------------------------------------
python tests/integracion/limpiar_datos_prueba.py
echo.

echo [1/6] Ejecutando pruebas unitarias e integracion...
echo -----------------------------------------------------------------------------
python -m pytest tests/ -v --durations=10
if %errorlevel% equ 0 (
    echo [OK] Pruebas unitarias completadas
    set /a tests_exitosos+=1
) else (
    echo [ERROR] Fallo en pruebas unitarias
)
set /a total_tests+=1
echo.

echo [2/6] Generando reporte de cobertura...
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

echo [3/6] Stress test PostgreSQL...
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

echo [4/6] Stress test SQLite...
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

echo [5/6] Pruebas de integracion...
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

echo [6/6] Abriendo reporte de cobertura...
echo -----------------------------------------------------------------------------
if exist "htmlcov\index.html" (
    start htmlcov\index.html
    echo [OK] Reporte HTML abierto
    set /a tests_exitosos+=1
) else (
    echo [WARNING] No se encontro el reporte HTML
)
set /a total_tests+=1
echo.

echo ============================================================================
echo RESUMEN: %tests_exitosos%/%total_tests% pruebas completadas exitosamente
echo ============================================================================
echo.
echo Para ver resultados detallados, revisa:
echo   - Reporte HTML: htmlcov\index.html
echo   - Documentacion: tests/RUN_TESTS.md
echo.
pause