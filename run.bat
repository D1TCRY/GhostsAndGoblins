@echo off
setlocal
set "current_path=%~dp0"
cd /d "%current_path%"
call env\Scripts\activate
pip install -r req.txt
python src\main.py
call deactivate