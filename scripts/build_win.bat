@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ==============================
echo        RE:mind Build
echo ==============================

REM Ir a la raiz del proyecto (desde scripts\)
cd /d "%~dp0.."
echo Working directory: %cd%

set "VENV_DIR=.venv"
set "APP_NAME=remind"
set "ENTRY_POINT=src\remind\app.py"
set "ICON_PATH=assets\app.ico"

REM Validaciones
if not exist "%ENTRY_POINT%" (
  echo ERROR: No existe "%ENTRY_POINT%" en %cd%
  pause
  exit /b 1
)

if not exist "%ICON_PATH%" (
  echo ERROR: No existe "%ICON_PATH%"
  pause
  exit /b 1
)

REM 1) Crear venv si no existe (usa 'py -3.12' si existe, sino 'python')
REM Recomendacion: PyInstaller es mas estable con 3.11/3.12.
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3.12 -m venv "%VENV_DIR%" 2>nul
  if errorlevel 1 (
    echo py -3.12 no disponible. Probando con python...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
      echo ERROR: No se pudo crear el venv.
      pause
      exit /b 1
    )
  )
)

REM 2) Forzar uso del python del venv (NO el python global)
set "VENV_PY=%CD%\%VENV_DIR%\Scripts\python.exe"
if not exist "%VENV_PY%" (
  echo ERROR: No se encuentra python del venv: %VENV_PY%
  pause
  exit /b 1
)

echo Using venv python: %VENV_PY%

REM 3) Instalar deps
if exist "requirements.txt" (
  echo Installing requirements...
  "%VENV_PY%" -m pip install --upgrade pip
  "%VENV_PY%" -m pip install -r requirements.txt
) else (
  echo WARNING: requirements.txt no encontrado. Continuando...
)

REM 4) Asegurar PyInstaller en el venv
"%VENV_PY%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
  echo Installing PyInstaller...
  "%VENV_PY%" -m pip install pyinstaller
  if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller en el venv.
    pause
    exit /b 1
  )
)

REM 5) Limpiar builds anteriores
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

echo.
echo Building executable...

REM 6) Build (SIEMPRE con python del venv)
"%VENV_PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name "%APP_NAME%" ^
  --icon "%ICON_PATH%" ^
  --add-data "assets;assets" ^
  --add-data "src\remind\i18n;remind\i18n" ^
  "%ENTRY_POINT%"

if errorlevel 1 (
  echo.
  echo ERROR: PyInstaller fallo.
  pause
  exit /b 1
)

echo.
echo ==============================
echo Build finished.
echo Output: dist\%APP_NAME%\
echo ==============================
pause

endlocal