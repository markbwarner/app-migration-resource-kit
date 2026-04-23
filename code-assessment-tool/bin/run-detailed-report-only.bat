@echo off
setlocal

if "%~1"=="" (
  echo Usage: %~nx0 ^<input-directory^> [custom-patterns-json] [output-directory]
  exit /b 1
)

set "INPUT_DIR=%~f1"
if not exist "%INPUT_DIR%" (
  echo Input directory does not exist: %INPUT_DIR%
  exit /b 1
)

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
for %%I in ("%INPUT_DIR%") do set "SCAN_NAME=%%~nxI"

if "%~2"=="" (
  set "CUSTOM_PATTERNS=%REPO_ROOT%\custom-patterns.example.json"
) else (
  set "CUSTOM_PATTERNS=%~f2"
)

if "%~3"=="" (
  set "OUTPUT_DIR=%REPO_ROOT%\reports"
) else (
  set "OUTPUT_DIR=%~f3"
)

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"

set "FULL_JSON=%OUTPUT_DIR%\%SCAN_NAME%_pii-impact-report_%STAMP%.json"
set "FILE_REPORTS_JSON=%OUTPUT_DIR%\%SCAN_NAME%_pii-file-reports_%STAMP%.json"
set "FILE_REPORTS_CSV=%OUTPUT_DIR%\%SCAN_NAME%_pii-file-reports_%STAMP%.csv"

python "%REPO_ROOT%\app.py" "%INPUT_DIR%" ^
  --custom-patterns "%CUSTOM_PATTERNS%" ^
  --json-out "%FULL_JSON%" ^
  --json-file-reports-out "%FILE_REPORTS_JSON%" ^
  --csv-file-reports-out "%FILE_REPORTS_CSV%" ^
  --include-file-reports

endlocal
