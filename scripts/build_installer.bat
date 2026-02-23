@echo off
setlocal
cd /d "%~dp0.."

echo.
echo ==============================
echo Generando installer.iss...
echo ==============================
python scripts\gen_installer_iss.py
if errorlevel 1 (
    echo ERROR generando installer.iss
    pause
    exit /b 1
)

echo.
echo ==============================
echo Compilando con Inno Setup...
echo ==============================
iscc scripts\installer.iss
REM Si no está en PATH:
REM "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" scripts\installer.iss

if errorlevel 1 (
    echo ERROR compilando instalador
    pause
    exit /b 1
)

REM ==============================
REM Firma automática (opcional)
REM ==============================
if exist "scripts\sign_win.bat" (
    echo.
    echo ==============================
    echo Firmando instalador...
    echo ==============================
    call scripts\sign_win.bat
    if errorlevel 1 (
        echo ERROR: Fallo en firma digital.
        pause
        exit /b 1
    )
) else (
    echo WARN: scripts\sign_win.bat no existe. Saltando firma.
)

echo.
echo ==============================
echo Generando docs\latest.json (sha256)...
echo ==============================
python scripts\gen_latest_json.py
if errorlevel 1 (
    echo ERROR generando latest.json
    pause
    exit /b 1
)

echo.
echo ==============================
echo INSTALADOR GENERADO (Y FIRMADO SI APLICA)
echo Salida: dist\
echo Manifiesto: docs\latest.json
echo ==============================
pause
endlocal