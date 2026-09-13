# Resultados de Pruebas de Carga - Cardio-Wellness

## Configuración

- **Base de datos:** PostgreSQL 14+
- **Conexiones:** Pool de conexiones múltiples
- **Escenario:** CRUD concurrente (lecturas y escrituras)

## Resultados

### Escenario: Carga Alta (50 usuarios concurrentes)

| Métrica | Valor |
|---------|-------|
| Usuarios | 50 |
| Duración | 60 segundos |
| Tasa de éxito | 95.88% |
| Operaciones fallidas | 84 |
| Ops/segundo | 33.94 |
| **Resultado** | ✅ **Exitoso** |

### Escenario: Carga Media (100 usuarios concurrentes)

| Métrica | Valor |
|---------|-------|
| Usuarios | 100 |
| Duración | 60 segundos |
| Tasa de éxito | 84.18% |
| Operaciones fallidas | 329 |
| Ops/segundo | 34.62 |
| **Resultado** | ✅ **Aceptable** |

### Escenario: Carga Sostenida (50 usuarios, 120s)

| Métrica | Valor |
|---------|-------|
| Usuarios | 50 |
| Duración | 120 segundos |
| Tasa de éxito | 94.40% |
| Operaciones fallidas | 211 |
| Ops/segundo | 31.42 |
| **Resultado** | ✅ **Aceptable** |

### Escenario: Estrés Extremo (200 usuarios)

| Métrica | Valor |
|---------|-------|
| Usuarios | 200 |
| Duración | 60 segundos |
| Tasa de éxito | 73.61% |
| Operaciones fallidas | 771 |
| Ops/segundo | 48.62 |
| **Resultado** | ⚠️ **Crítico** |

## Interpretación

- ✅ El sistema soporta **95.88% de éxito con 50 usuarios concurrentes**
- ⚠️ Con 100+ usuarios, aumentan los bloqueos por escrituras simultáneas
- 💡 **Recomendación:** Para producción con alta concurrencia, implementar:
  - Cola de escrituras
  - Reintentos con espera exponencial
  - Pool de conexiones optimizado

## Conclusiones

El sistema es **adecuado para gimnasios pequeños y medianos** (≤50 usuarios concurrentes). Para gimnasios grandes, se recomienda optimización adicional.

---

**Fecha de prueba:** 2026-09-13  
**Responsable:** Equipo de desarrollo  
**Versión del sistema:** 1.0.0