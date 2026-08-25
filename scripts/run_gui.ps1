$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    throw "No existe .venv. Crea el entorno e instala requirements.txt antes de continuar."
}

Push-Location -LiteralPath $projectRoot
try {
    & $pythonExecutable "gui.py"
} finally {
    Pop-Location
}
