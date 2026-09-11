# 🧪 Comandos de Pruebas - Cardio-Wellness

Este archivo contiene todos los comandos útiles para ejecutar pruebas en el proyecto Cardio-Wellness.

---

## 📋 Tabla de Contenido

1. [Pruebas Unitarias e Integración](#1-pruebas-unitarias-e-integración-pytest)
2. [Cobertura de Código](#2-cobertura-de-código)
3. [Stress Tests](#3-stress-tests-pruebas-de-estréscarga)
4. [Pruebas de Integración End-to-End](#4-pruebas-de-integración-end-to-end)
5. [Utilidades](#5-utilidades)
6. [Cheat Sheet](#6-comandos-rápidos-cheat-sheet)

---

## 1. Pruebas Unitarias e Integración (pytest)

### Ejecutar TODOS los tests
```bash
python -m pytest tests/ -v
```

### Con detalles de duración
```bash
python -m pytest tests/ -v --durations=10
```

### Test específico
```bash
python -m pytest tests/test_cliente_dao.py -v
python -m pytest tests/test_sesion_entrenamiento_dao.py -v
python -m pytest tests/test_modelos.py -v
```

---

## 2. Cobertura de Código

### Reporte en terminal
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Reporte HTML (recomendado)
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Abrir reporte HTML (Windows)
```bash
start htmlcov\index.html
```

### Cobertura completa
```bash
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
```

---

## 3. Stress Tests (Pruebas de Estrés/Carga)

### PostgreSQL (configuración recomendada)
```bash
python tests/stress_test_postgresql.py --usuarios 30 --duracion 40 --clientes 100
```

### PostgreSQL (rápido)
```bash
python tests/stress_test_postgresql.py --usuarios 20 --duracion 30 --clientes 50
```

### PostgreSQL (extremo)
```bash
python tests/stress_test_postgresql.py --usuarios 50 --duracion 60 --clientes 200
```

### SQLite
```bash
python tests/stress_test_sqlite.py --usuarios 20 --duracion 30
```

### SQLite (rápido)
```bash
python tests/stress_test_sqlite.py --usuarios 10 --duracion 15
```

---

## 4. Pruebas de Integración (End-to-End)

### Ejecutar pruebas completas
```bash
python tests/integracion/test_integracion_completa.py
```

### Limpiar datos de prueba
```bash
python tests/integracion/limpiar_datos_prueba.py
```

---

## 5. Utilidades

### Limpiar caché de pytest
```bash
pytest --cache-clear
```

### Guardar resultados en archivo
```bash
python -m pytest tests/ -v > resultados_tests.txt
```

### Ejecutar solo tests fallidos
```bash
python -m pytest tests/ --lf
```

---

## 6. Comandos Rápidos (Cheat Sheet)

| Acción | Comando |
|--------|---------|
| Todos los tests | `python -m pytest tests/ -v` |
| Cobertura HTML | `python -m pytest tests/ --cov=src --cov-report=html` |
| Stress PostgreSQL | `python tests/stress_test_postgresql.py --usuarios 30 --duracion 40 --clientes 100` |
| Stress SQLite | `python tests/stress_test_sqlite.py --usuarios 20 --duracion 30` |
| Integración | `python tests/integracion/test_integracion_completa.py` |
| Limpiar datos | `python tests/integracion/limpiar_datos_prueba.py` |
| Ver cobertura | `start htmlcov\index.html` |

---

## 📊 Estado Actual de Pruebas

| Tipo | Cantidad | Resultado |
|------|----------|-----------|
| Unitarias | 210 | ✅ 210/210 |
| Integración | 15 | ✅ 15/15 |
| Stress SQLite | - | ✅ 99.56% |
| Stress PostgreSQL | - | ✅ 97.47% |
| Cobertura | - | 📊 79% |

---

**Última actualización**: 2026-09-11