@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m src.uvm.main %*
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -m src.uvm.main %*
    ) else (
        py -3 -m src.uvm.main %*
    )
)
exit /b %errorlevel%
