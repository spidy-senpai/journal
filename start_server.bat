@echo off
echo ========================================
echo   Starting Journal Webapp Server
echo ========================================
echo.
echo Server will be accessible at:
echo   - Local:   http://localhost:5000
echo   - Network: http://10.123.216.105:5000
echo.
echo Share this link with your friend:
echo   http://10.123.216.105:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
python app.py

pause
