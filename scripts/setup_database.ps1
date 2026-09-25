$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

$DatabaseName = "cardio_wellness"
$DatabaseUser = "postgres"
$DatabaseHost = "localhost"
$DatabasePort = "5432"

$SqlFile = Join-Path `
    $ProjectRoot `
    "database\cardio_wellness.sql"

$EnvExampleFile = Join-Path `
    $ProjectRoot `
    ".env.example"

$EnvFile = Join-Path `
    $ProjectRoot `
    ".env"

$PostgreSqlRoot = Join-Path `
    $env:ProgramFiles `
    "PostgreSQL"

$PsqlExe = Get-ChildItem `
    -Path $PostgreSqlRoot `
    -Filter "psql.exe" `
    -Recurse `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Directory.Name -eq "bin" -and
        (
            Test-Path (
                Join-Path `
                    $_.Directory.FullName `
                    "createdb.exe"
            )
        )
    } |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if ($null -eq $PsqlExe) {
    throw @"
No se encontró una instalación válida de PostgreSQL.

Se esperaba encontrar psql.exe y createdb.exe en una ruta como:

C:\Program Files\PostgreSQL\18\bin\

Instala PostgreSQL para Windows y vuelve a ejecutar:

.\scripts\setup_database.ps1
"@
}

$PsqlPath = $PsqlExe.FullName

$CreateDbPath = Join-Path `
    $PsqlExe.Directory.FullName `
    "createdb.exe"

Write-Host ""
Write-Host "Herramientas PostgreSQL seleccionadas:" `
    -ForegroundColor Green

Write-Host "psql:      $PsqlPath"
Write-Host "createdb:  $CreateDbPath"

if (-not (Test-Path $SqlFile)) {
    throw "No se encontró el respaldo SQL en: $SqlFile"
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Configuración automática de Cardio Wellness" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PostgreSQL encontrado en:"
Write-Host $PsqlExe.Directory.FullName
Write-Host ""

$SecurePassword = Read-Host `
    "Contraseña local del usuario PostgreSQL '$DatabaseUser'" `
    -AsSecureString

$PasswordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR(
    $SecurePassword
)

try {
    $PlainPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
        $PasswordPointer
    )

    $env:PGPASSWORD = $PlainPassword

    $DatabaseExists = & $PsqlPath `
        -h $DatabaseHost `
        -p $DatabasePort `
        -U $DatabaseUser `
        -d postgres `
        -tAc "SELECT 1 FROM pg_database WHERE datname = '$DatabaseName';"

    if ($LASTEXITCODE -ne 0) {
        throw "No fue posible conectarse a PostgreSQL."
    }

    if ($DatabaseExists.Trim() -ne "1") {
        Write-Host ""
        Write-Host "Creando base de datos '$DatabaseName'..." `
            -ForegroundColor Yellow

        & $CreateDbPath `
            -h $DatabaseHost `
            -p $DatabasePort `
            -U $DatabaseUser `
            $DatabaseName

        if ($LASTEXITCODE -ne 0) {
            throw "No fue posible crear la base de datos."
        }

        Write-Host "Base de datos creada correctamente." `
            -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "La base '$DatabaseName' ya existe." `
            -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Restaurando database\cardio_wellness.sql..." `
        -ForegroundColor Yellow

    & $PsqlPath `
        -h $DatabaseHost `
        -p $DatabasePort `
        -U $DatabaseUser `
        -d $DatabaseName `
        -f $SqlFile

    if ($LASTEXITCODE -ne 0) {
        throw "La restauración del respaldo SQL falló."
    }

    if (-not (Test-Path $EnvFile)) {
        if (-not (Test-Path $EnvExampleFile)) {
            throw "No existe .env.example."
        }

        Copy-Item `
            -Path $EnvExampleFile `
            -Destination $EnvFile

        Write-Host ""
        Write-Host ".env creado desde .env.example." `
            -ForegroundColor Green
    }

    $EnvContent = Get-Content `
        -Path $EnvFile `
        -Raw

    if ($EnvContent -match "(?m)^DB_PASSWORD=") {
        $EnvContent = $EnvContent -replace `
            "(?m)^DB_PASSWORD=.*$", `
            "DB_PASSWORD=$PlainPassword"
    }
    else {
        $EnvContent += "`r`nDB_PASSWORD=$PlainPassword`r`n"
    }

    if ($EnvContent -match "(?m)^DB_HOST=") {
        $EnvContent = $EnvContent -replace `
            "(?m)^DB_HOST=.*$", `
            "DB_HOST=$DatabaseHost"
    }

    if ($EnvContent -match "(?m)^DB_PORT=") {
        $EnvContent = $EnvContent -replace `
            "(?m)^DB_PORT=.*$", `
            "DB_PORT=$DatabasePort"
    }

    if ($EnvContent -match "(?m)^DB_NAME=") {
        $EnvContent = $EnvContent -replace `
            "(?m)^DB_NAME=.*$", `
            "DB_NAME=$DatabaseName"
    }

    if ($EnvContent -match "(?m)^DB_USER=") {
        $EnvContent = $EnvContent -replace `
            "(?m)^DB_USER=.*$", `
            "DB_USER=$DatabaseUser"
    }

    Set-Content `
        -Path $EnvFile `
        -Value $EnvContent `
        -Encoding utf8

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host " Base de datos configurada correctamente." -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ya puedes ejecutar el proyecto."
}
finally {
    if ($PasswordPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR(
            $PasswordPointer
        )
    }

    Remove-Item `
        Env:PGPASSWORD `
        -ErrorAction SilentlyContinue
}