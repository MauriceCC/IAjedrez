@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno Python. Sigue los pasos de README.md.
  pause
  exit /b 1
)
echo IAjedrez - demostracion IHC
echo Abre http://127.0.0.1:8765 en tu navegador.
echo Deja esta ventana abierta durante la demostracion.
echo Para detener el servidor, pulsa Ctrl+C.
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8765
pause
