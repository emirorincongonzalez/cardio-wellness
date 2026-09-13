# Plan de Pruebas de Usabilidad - Cardio-Wellness

## Objetivo

Validar que los usuarios finales (entrenadores y administrativos del gimnasio) puedan completar las tareas críticas del sistema sin asistencia, con una tasa de éxito ≥80% y un NPS ≥40.

---

## Fase Alpha (Interna)

### Participantes
- 3-5 entrenadores internos del gimnasio
- Duración: 2 semanas

### Tareas a Evaluar

#### Tarea 1: Registrar nuevo cliente
1. Iniciar sesión como administrador
2. Navegar a "Gestión de Clientes"
3. Click en "Nuevo Cliente"
4. Completar formulario (nombre, apellido, correo, edad, peso, altura, objetivo)
5. Guardar cliente

**Criterios de éxito:**
- Completa la tarea sin errores
- Tiempo esperado: <2 minutos
- No requiere asistencia

#### Tarea 2: Asignar rutina a cliente
1. Buscar cliente por nombre
2. Seleccionar "Asignar Rutina"
3. Elegir rutina de la lista
4. Confirmar asignación

**Criterios de éxito:**
- Completa la tarea sin errores
- Tiempo esperado: <1 minuto

#### Tarea 3: Registrar sesión de entrenamiento
1. Iniciar sesión como cliente
2. Navegar a "Mis Rutinas"
3. Seleccionar rutina activa
4. Click en "Registrar Sesión"
5. Completar datos (fecha, duración, intensidad, calorías)
6. Guardar sesión

**Criterios de éxito:**
- Completa la tarea sin errores
- Tiempo esperado: <2 minutos

### Métricas

| Métrica | Objetivo | Resultado Esperado |
|---------|----------|-------------------|
| Tasa de completitud | ≥80% | 4-5 de 5 usuarios completan todas las tareas |
| Tiempo promedio por tarea | <2 minutos | Promedio <120 segundos |
| Errores de usuario | ≤2 por usuario | Máximo 2 errores por participante |
| Satisfacción (1-5) | ≥4 | Promedio ≥4.0 |

---

## Fase Beta (Piloto)

### Participantes
- 10-15 entrenadores y administrativos
- Duración: 4 semanas

### Métricas

| Métrica | Objetivo | Método de Medición |
|---------|----------|-------------------|
| NPS (Net Promoter Score) | ≥40 | Encuesta final: "¿Recomendarías este sistema?" (0-10) |
| Satisfacción por módulo | ≥4.0/5 | Encuesta por módulo (1-5) |
| Incidencias reportadas | ≤5 críticas | Sistema de tickets |
| Solicitudes de mejora | - | Lista de feature requests |

### Cuestionario NPS

**Pregunta principal:**
> "En una escala del 0 al 10, ¿qué tan probable es que recomiendes Cardio-Wellness a un colega?"

- **Promotores (9-10):** Usuarios leales
- **Neutros (7-8):** Satisfechos pero no entusiastas
- **Detractores (0-6):** Insatisfechos

**Cálculo:**


**Objetivo:** NPS ≥ 40

---

## Fase Post-lanzamiento

### Métricas Continuas

| Métrica | Frecuencia | Herramienta |
|---------|------------|-------------|
| Tickets de soporte | Semanal | Email/WhatsApp |
| Frecuencia de uso | Semanal | Logs del sistema |
| Retención de usuarios | Mensual | Reporte de usuarios activos |
| Feedback cualitativo | Continuo | Encuestas informales |

---

## Criterios de Aceptación

El sistema se considera **usable** cuando:

- ✅ 80% de usuarios completa tareas críticas sin asistencia
- ✅ NPS mínimo de 40 en fase Beta
- ✅ No más de 5 defectos críticos reportados durante la Beta
- ✅ Tiempo promedio por tarea <2 minutos

---

## Protocolo de Ejecución

### Para cada participante:

1. **Briefing (5 min)**
   - Explicar objetivo de la prueba
   - Aclarar que se evalúa el sistema, no al usuario
   - Obtener consentimiento

2. **Ejecución de tareas (15-20 min)**
   - Observar sin intervenir (salvo errores críticos)
   - Registrar tiempos y errores
   - Tomar notas de comentarios del usuario

3. **Encuesta post-prueba (5 min)**
   - Cuestionario de satisfacción (1-5)
   - Preguntas abiertas de feedback

4. **Análisis (post-sesión)**
   - Calcular métricas
   - Identificar patrones de error
   - Priorizar mejoras

---

## Plantilla de Registro

### Participante: _______________
**Fecha:** _______________  
**Rol:** _______________  

| Tarea | Completada (✓/✗) | Tiempo (seg) | Errores | Comentarios |
|-------|------------------|--------------|---------|-------------|
| Registrar cliente | | | | |
| Asignar rutina | | | | |
| Registrar sesión | | | | |

**Satisfacción general (1-5):** _____  
**Comentarios adicionales:**  
_________________________________  
_________________________________

---

## Cronograma Propuesto

| Semana | Actividad |
|--------|-----------|
| 1-2 | Fase Alpha (3-5 usuarios) |
| 3-6 | Fase Beta (10-15 usuarios) |
| 7+ | Post-lanzamiento (continuo) |

---

## Notas

- Las pruebas de usabilidad están **pendientes de ejecución** con usuarios reales
- Este documento describe el **protocolo** que se seguirá cuando se ejecute
- Para fines académicos, se considera **cumplido** con la documentación del plan