# Checklist de Despliegue en Producción

## Pre-Despliegue

- [ ] Backup de la base de datos realizado
- [ ] Tests unitarios pasan (100%)
- [ ] Tests de integración pasan
- [ ] Documentación actualizada (README, CHANGELOG)
- [ ] Variables de entorno configuradas (.env)
- [ ] Permisos de archivos verificados
- [ ] Espacio en disco suficiente (>1 GB libre)

## Despliegue

- [ ] Código actualizado desde main (`git pull`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Migraciones aplicadas (si corresponde)
- [ ] Servicio reiniciado
- [ ] Logs verificados (sin errores)

## Post-Despliegue

- [ ] Login funcional
- [ ] CRUD de clientes operativo
- [ ] CRUD de rutinas operativo
- [ ] Registro de sesiones funcional
- [ ] Backups automáticos configurados
- [ ] Monitoreo activado

## Rollback (si es necesario)

- [ ] Backup anterior identificado
- [ ] Código revertido (`git revert` o `git checkout`)
- [ ] Base de datos restaurada
- [ ] Servicios reiniciados
- [ ] Usuarios notificados

---

**Fecha de despliegue**: _______________  
**Responsable**: _______________  
**Versión**: _______________  
**Estado**: ✅ Exitoso / ❌ Fallido