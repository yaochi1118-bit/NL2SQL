@echo off
REM Start the DDL-to-SQL web application

cd /d "%~dp0"
echo Building frontend...
call npm run build
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

cd /d "%~dp0.."
echo Starting backend server...
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
