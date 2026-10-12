@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (python -c "import sys" >nul 2>nul && set "PY=python")
if not defined PY (
  echo Khong tim thay Python. Cai Python 3.8+ tai https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^), roi bam dup lai file nay.
  echo Python was not found. Install Python 3.8+ from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^), then double-click this file again.
  pause
  exit /b 1
)
rem Mo bang dieu khien trong trinh duyet; cua so nho chay nen se tu tat khi dong trang.
rem Opens the control panel in the browser; the small background window closes itself when the page is closed.
start "Workspace panel" /min %PY% tools\app.py
