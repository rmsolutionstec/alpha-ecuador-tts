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

    # En este entorno PyInstaller puede recoger ICU desde herramientas ajenas (por ejemplo,
    # Poppler). PySide6 no distribuye esas DLL y Qt usa las bibliotecas del sistema Windows;
    # dejarlas junto al ejecutable causa un conflicto al cargar Qt6Core.
    $internalDir = Join-Path $projectRoot "dist\AlphaStudioTTSLatino\_internal"
    foreach ($foreignIcuDll in @("icuuc.dll", "icudt78.dll")) {
        $foreignIcuPath = Join-Path $internalDir $foreignIcuDll
        if (Test-Path -LiteralPath $foreignIcuPath) {
            Remove-Item -LiteralPath $foreignIcuPath -Force
        }
    }

    Write-Host "Ejecutable generado en dist\AlphaStudioTTSLatino"
} finally {
    Pop-Location
}
