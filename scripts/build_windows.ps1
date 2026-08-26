$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $projectRoot ".venv\Scripts\python.exe"
$dictionaryPath = Join-Path $projectRoot "studio_tts_latino\data\pronunciation_es_mx.json"
$qtRuntimeHook = Join-Path $projectRoot "scripts\pyinstaller_pyside6_runtime.py"

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    throw "No existe .venv. Crea el entorno e instala requirements.txt antes de continuar."
}

if (-not (Test-Path -LiteralPath $dictionaryPath)) {
    throw "No se encontro el diccionario de pronunciacion incluido en la aplicacion."
}

if (-not (Test-Path -LiteralPath $qtRuntimeHook)) {
    throw "No se encontro el hook de runtime de PySide6."
}

Push-Location -LiteralPath $projectRoot
try {
    & $pythonExecutable -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --name "AlphaStudioTTSLatino" `
        --runtime-hook $qtRuntimeHook `
        --add-data "$dictionaryPath;studio_tts_latino/data" `
        "gui.py"

    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo crear el ejecutable. Instala PyInstaller con pip install '.[build]'."
    }

    Write-Host "Ejecutable generado en dist\AlphaStudioTTSLatino"
} finally {
    Pop-Location
}
