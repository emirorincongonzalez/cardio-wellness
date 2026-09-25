## Instalación en Windows

### Requisitos

- Git
- Python
- PostgreSQL para Windows

Durante la instalación de PostgreSQL, recuerda la contraseña que asignes al usuario `postgres`.

### Configuración

Clona el repositorio:

```powershell
git clone URL_DEL_REPOSITORIO
cd cardio-wellness
```

Crea y activa el entorno virtual:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Configura la base de datos:

```powershell
.\scripts\setup_database.ps1
```

El script solicitará la contraseña local del usuario PostgreSQL `postgres`, creará la base de datos `cardio_wellness` si no existe, restaurará el respaldo incluido en el repositorio y generará/configurará el archivo `.env`.

Ejecuta las pruebas:

```powershell
python -m pytest
```