@echo off
setlocal EnableExtensions
rem Johnny AI Skill one-click installer wrapper (release v0.4.1).
rem Every exit holds the console open first: this file is meant to be
rem double-clicked from Explorer, where an unpaused exit closes the window
rem before the user can read why the bundle was refused.
set "BUNDLE_NAME=johnny-ai-skill-0.4.1.zip"
set "APPROVED_DIGEST=f67047f4780a63c08383fd3fce4af85d5dfb5cb9bbd857f8b99d6c4a8b90b464"

set "BUNDLE_PATH=%~dp0%BUNDLE_NAME%"

if not exist "%BUNDLE_PATH%" (
    echo {"status":"BLOCKED","code":"BUNDLE_NOT_FOUND"}
    echo Expected the approved bundle beside this file: %BUNDLE_NAME%
    pause
    exit /b 2
)

set "EXTRACT_STAGE=%TEMP%\johnny-install-wrapper-%RANDOM%-%RANDOM%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; $bundle = '%BUNDLE_PATH%'; $approved = '%APPROVED_DIGEST%'; $stage = '%EXTRACT_STAGE%'; if (-not (Test-Path -LiteralPath $bundle -PathType Leaf)) { Write-Output '{\"status\":\"BLOCKED\",\"code\":\"BUNDLE_NOT_FOUND\"}'; exit 2 }; $hash = (Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLowerInvariant(); if ($hash -ne $approved) { Write-Output '{\"status\":\"BLOCKED\",\"code\":\"DIGEST_MISMATCH\"}'; Write-Output ('approved ' + $approved); Write-Output ('actual   ' + $hash); exit 2 }; Add-Type -AssemblyName System.IO.Compression.FileSystem; New-Item -ItemType Directory -Path $stage -Force | Out-Null; $archive = [System.IO.Compression.ZipFile]::OpenRead($bundle); try { $entry = $archive.Entries | Where-Object { $_.FullName -eq 'install.ps1' }; if ($null -eq $entry) { Write-Output '{\"status\":\"BLOCKED\",\"code\":\"INSTALL_SCRIPT_MISSING\"}'; exit 2 }; $target = Join-Path $stage 'install.ps1'; [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $target, $true); } finally { $archive.Dispose(); }"
if errorlevel 1 (
    if exist "%EXTRACT_STAGE%" rmdir /s /q "%EXTRACT_STAGE%" 2>nul
    pause
    exit /b 2
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%EXTRACT_STAGE%\install.ps1" -BundleZip "%BUNDLE_PATH%"
set "PS_EXIT=%ERRORLEVEL%"
if exist "%EXTRACT_STAGE%" rmdir /s /q "%EXTRACT_STAGE%" 2>nul
echo install.ps1 exit code: %PS_EXIT%
pause
exit /b %PS_EXIT%
