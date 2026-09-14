# Diagramas UML - Cardio-Wellness


### Componentes Implementados

| Componente | Ubicación en Código |
|------------|---------------------|
| Interfaz de Usuario (GUI) | `src/vistas/` |
| Lógica de Negocio (Core) | `src/modelos/` |
| Acceso a Datos (DAO) | `src/dao/` |
| Generador de Reportes | `src/servicios/` |


### Nota sobre la Base de Datos

El diagrama original especifica SQLite embebido, pero la implementación final utiliza **PostgreSQL 17** para mayor robustez en entornos multiusuario.

## Relación con el Código

- **GUI → Core:** Las ventanas importan modelos y controladores
- **Core → DAO:** Los modelos usan DAOs para persistencia
- **DAO → BD:** Los DAOs ejecutan SQL en PostgreSQL
- **Reportes:** Servicio especializado que exporta a PDF/Excel