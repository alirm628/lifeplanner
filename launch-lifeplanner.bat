@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch-lifeplanner.ps1"
if errorlevel 1 (
  echo.
  echo Launch failed. Check output above.
  pause
)

endlocal
