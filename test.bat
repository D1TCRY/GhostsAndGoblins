@echo off
setlocal

set "current_path=%~dp0"
cd /d "%current_path%"

set "VENV_PY=%current_path%env\Scripts\python.exe"

REM: Using the virtual environment
"%VENV_PY%" -c "import sys; print(sys.executable); print(sys.prefix)"

REM: Install requirements
"%VENV_PY%" -m pip install -r req.txt

cls

REM: Run tests
"%VENV_PY%" -m unittest discover -s tests -p "test_*.py"

PAUSE
