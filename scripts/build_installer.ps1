$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$buildScript = Join-Path $PSScriptRoot "build_windows.ps1"
$installerScript = Join-Path $projectRoot "installer\AlphaStudioTTSLatino.iss"
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if (-not $iscc) {
    $knownIsccPaths = @(
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )
    $isccPath = $knownIsccPaths | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($isccPath) {
        $iscc = [pscustomobject]@{ Source = $isccPath }
    }
}

if (-not $iscc) {
    throw "No se encontró Inno Setup. Instálalo y vuelve a ejecutar este script."
}

& $buildScript
& $iscc.Source $installerScript
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo crear el instalador de Windows."
}

Write-Host "Instalador generado en dist\installer\AlphaStudioTTSLatino-Setup.exe"
