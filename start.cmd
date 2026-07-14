@echo off
title BloxyMe
pip install -r requirements.txt >nul 2>&1
python server.py
pause