@echo off
setlocal
set "current_path=%~dp0"
cd /d "%current_path%"
call env\Scripts\activate
pip install -r req.txt
python -m src.main
call deactivate