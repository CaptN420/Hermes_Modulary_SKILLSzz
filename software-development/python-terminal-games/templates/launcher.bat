@echo off
chcp 65001 >nul
title GAME TITLE
cd /d "%~dp0"
mode con: cols=84 lines=34 >nul 2>nul
color 0F
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if not errorlevel 1 goto use_python

echo.
echo  Python 3 was not found on this PC.
echo  Install it from https://www.python.org/downloads/ then run this file again.
echo.
pause
exit /b 1

:use_py
py -3 main.py
goto done

:use_python
python main.py
goto done

:done
if errorlevel 1 (
  echo.
  echo  The game stopped with an error. Read the message above.
  pause
)
exit /b 0
