@echo off
title Shirt Studio
cd /d "%~dp0"
echo Starting Shirt Studio at http://127.0.0.1:8765/ ... (close this window to stop)
uv run -q --with pillow --with numpy --with scipy tools\server.py
pause
