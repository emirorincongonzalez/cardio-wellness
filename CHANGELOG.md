# Changelog

Todos los cambios importantes en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] - 2026-09-13

### Agregado
- Sistema completo de gestión de rutinas Cardio-Wellness (backend)
- CRUD de clientes, rutinas, ejercicios y sesiones
- Autenticación de usuarios con hash de contraseñas
- Sistema de backups automáticos
- 279 pruebas unitarias y de integración
- Documentación técnica completa por capa
- Scripts de utilidad (backup, seed, debug, mantenimiento)

### Cambiado
- Migración de SQLite a PostgreSQL (opcional)
- Mejora en validaciones de datos
- Optimización de consultas a base de datos

### Corregido
- Errores de integridad referencial en asignación de rutinas
- Problemas de concurrencia en escrituras simultáneas
- Validaciones de edad y IMC en clientes

### Seguridad
- Hash de contraseñas con SHA-256
- Validación de permisos por tipo de usuario
- Protección contra inyección SQL con parámetros

---

## [0.2.0] - 2026-09-10

### Agregado
- Módulo de progreso de clientes
- Reportes de sesiones completadas

### Corregido
- Errores en cálculo de calorías
- Problemas de persistencia en SQLite

---

## [0.1.0] - 2026-09-01

### Agregado
- Estructura base del proyecto
- Modelos de dominio
- Conexión a base de datos
- Primeras pruebas unitarias