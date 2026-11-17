@echo off
REM overnight-runner 启动脚本（Windows，由 install.sh 生成）
setlocal
set "DIR=%~dp0"
set "PYTHONPATH=%DIR%;%PYTHONPATH%"
"python3" -m overnight_runner %*
