@echo off
setlocal enableextensions

REM ==============================
REM CONFIG (AJUSTA)
REM ==============================
set "PFX_PATH=D:\certs\codesign.pfx"
set "PFX_PASS=TU_PASSWORD"
set "TIMESTAMP_URL=http://timestamp.digicert.com"

REM Ruta signtool (si no está en PATH, pon ruta completa)
set "SIGNTOOL=signtool"

REM ==============================
REM HELPERS
REM ==============================
if not exist "%PFX_PATH%" (
  echo [SIGN] ERROR: No existe el certificado PFX en: %PFX_PATH%
  exit /b 2
)

REM ==============================
REM 1) Firmar EXE (modo carpeta)
REM ==============================
if exist "dist\remind\remind.exe" (
  echo [SIGN] Firmando dist\remind\remind.exe ...
  %SIGNTOOL% sign /f "%PFX_PATH%" /p "%PFX_PASS%" /fd sha256 /tr "%TIMESTAMP_URL%" /td sha256 "dist\remind\remind.exe"
  if errorlevel 1 (
    echo [SIGN] ERROR firmando EXE.
    exit /b 3
  )
) else (
  echo [SIGN] WARN: No existe dist\remind\remind.exe (saltando firma EXE)
)

REM ==============================
REM 2) Firmar instalador (si existe)
REM ==============================
set "FOUND_INSTALLER="
for %%F in ("dist_installer\REmind_Setup_*.exe") do (
  if exist "%%~fF" (
    set "FOUND_INSTALLER=1"
    echo [SIGN] Firmando instalador %%~nxF ...
    %SIGNTOOL% sign /f "%PFX_PATH%" /p "%PFX_PASS%" /fd sha256 /tr "%TIMESTAMP_URL%" /td sha256 "%%~fF"
    if errorlevel 1 (
      echo [SIGN] ERROR firmando instalador: %%~nxF
      exit /b 4
    )
  )
)

if not defined FOUND_INSTALLER (
  echo [SIGN] WARN: No se encontró instalador en dist_installer\REmind_Setup_*.exe
)

echo [SIGN] OK: Firma completada.
exit /b 0