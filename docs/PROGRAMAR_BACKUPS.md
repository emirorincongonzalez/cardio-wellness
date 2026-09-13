# Cómo Programar Backups Automáticos

## Windows (Task Scheduler)

1. Abrir **Task Scheduler**
2. Click en **Create Basic Task**
3. Nombre: `Cardio-Wellness Backup Diario`
4. Trigger: **Daily** a las 2:00 AM
5. Action: **Start a program**
6. Program/script: `python`
7. Add arguments: `scripts/backup_automatico.py`
8. Start in: `C:\Users\PC\Documents\Pruebas\cardio-wellness`
9. Finish

## Linux/Mac (cron)

Editar crontab:
```bash
crontab -e
```

Agregar línea:
```bash
0 2 * * * /usr/bin/python3 /ruta/cardio-wellness/scripts/backup_automatico.py >> /var/log/cardio_backup.log 2>&1
```

## Verificar

```bash
# Windows
schtasks /query /tn "Cardio-Wellness Backup Diario"

# Linux
tail -f /var/log/cardio_backup.log
```