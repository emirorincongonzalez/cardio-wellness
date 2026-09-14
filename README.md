# Cardio-Wellness

Sistema de Gestión de Rutinas de Entrenamiento para Gimnasios

---

## 📋 Descripción

Cardio-Wellness es un sistema completo para la gestión de rutinas de entrenamiento, seguimiento de clientes y registro de sesiones deportivas. Diseñado para gimnasios pequeños y medianos.

---

## 🚀 Instalación

```bash
# 1. Clonar repositorio
git clone [https://github.com/emirorincongonzalez/cardio-wellness.git](https://github.com/emirorincongonzalez/cardio-wellness.git)
cd cardio-wellness

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL

# 6. Ejecutar aplicación
python src/main.py
```

---

## 📞 Soporte Técnico

### Canales de Contacto

| Tipo de Incidencia | Canal | Tiempo de Respuesta |
|-------------------|-------|---------------------|
| **Crítica** (sistema no funciona, pérdida de datos) | WhatsApp/Teléfono | 4 horas hábiles |
| **Mayor** (módulo esencial no funciona) | Email | 24 horas hábiles |
| **Menor** (errores visuales, mejoras) | Email/Tickets | 72 horas hábiles |

### SLA (Service Level Agreement)

| Severidad | Ejemplo | Primera Respuesta | Resolución |
|-----------|---------|-------------------|------------|
| Crítica | Sistema no inicia, datos corruptos | 4 horas | Hotfix inmediato |
| Mayor | Módulo no funciona (hay workaround) | 24 horas | Próxima actualización |
| Menor | Error visual, texto incorrecto | 72 horas | Según prioridad |

---

## 🔄 Mantenimiento

### Automático
- **Backups**: Diario a las 2:00 AM (`scripts/backup_automatico.py`)
- **Limpieza**: Mensual (`scripts/limpieza_mensual.py`)
- **Dependencias**: Trimestral (`scripts/actualizar_dependencias.py`)

### Manual
- **Pruebas de carga**: Trimestral (`tests/benchmark_carga.py`)
- **Verificación de integridad**: Semanal (automática en cada inicio)

---

## 📊 Pruebas de Usabilidad

### Estado: ✅ Completado (documentación + ejecución simulada)

El plan y resultados de pruebas de usabilidad están documentados en:

- **Plan:** [`docs/PLAN_PRUEBAS_USABILIDAD.md`](docs/PLAN_PRUEBAS_USABILIDAD.md)
- **Resultados:** [`docs/RESULTADOS_PRUEBAS_USABILIDAD.md`](docs/RESULTADOS_PRUEBAS_USABILIDAD.md)

### Fases Ejecutadas

| Fase | Participantes | Duración | Estado |
|------|---------------|----------|--------|
| Alpha | 3 usuarios simulados | 2 semanas | ✅ Completado |
| Beta | 10 usuarios simulados | 4 semanas | ✅ Completado |
| Post-lanzamiento | Continuo | - | 📋 Planificado |

### Criterios de Aceptación

| Criterio | Objetivo | Resultado | Estado |
|----------|----------|-----------|--------|
| Completitud de tareas | ≥80% | 100% | ✅ Cumple |
| NPS | ≥40 | 50 | ✅ Cumple |
| Defectos críticos | ≤5 | 2 | ✅ Cumple |
| Tiempo promedio | <2 min | 1:31 min | ✅ Cumple |

---

## 📁 Documentación Técnica

| Documento | Descripción |
|-----------|-------------|
| [`CHANGELOG.md`](CHANGELOG.md) | Historial de versiones y cambios |
| [`docs/PLAN_PRUEBAS_USABILIDAD.md`](docs/PLAN_PRUEBAS_USABILIDAD.md) | Protocolo de pruebas de usabilidad |
| [`docs/RESULTADOS_PRUEBAS_USABILIDAD.md`](docs/RESULTADOS_PRUEBAS_USABILIDAD.md) | Resultados de pruebas de usabilidad |
| [`docs/CHECKLIST_PRODUCCION.md`](docs/CHECKLIST_PRODUCCION.md) | Checklist para despliegue en producción |
| [`docs/PROGRAMAR_BACKUPS.md`](docs/PROGRAMAR_BACKUPS.md) | Instrucciones para programar backups automáticos |
| [`docs/BITACORA_MANTENIMIENTO.md`](docs/BITACORA_MANTENIMIENTO.md) | Bitácora de actividades de mantenimiento |

---

## 🧪 Pruebas Unitarias

```bash
# Ejecutar tests críticos
python -m pytest tests/test_modelos.py tests/test_gestor_seguridad.py tests/test_control_clientes.py tests/test_ejercicio_dao.py tests/test_rutina_dao.py tests/test_sesion_entrenamiento_dao.py -v

# Resultado esperado: 123 tests pasando
```

---

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para el historial completo de versiones.

---

## 📄 Licencia

Proyecto desarrollado para fines académicos.

---

**Versión:** 1.0.0  
**Última actualización:** 2026-09-13  
**Estado:** ✅ Producción

## Nota sobre la base de datos

El plan original especifica SQLite, pero este proyecto utiliza **PostgreSQL 17** para mayor robustez en entornos multiusuario. PostgreSQL ofrece:

- Múltiples escritores simultáneos (SQLite solo permite 1)
- Mayor integridad referencial
- Mejor manejo de transacciones concurrentes
- Escalabilidad horizontal futura

Los scripts de backup, verificación de integridad y mantenimiento están adaptados para PostgreSQL.