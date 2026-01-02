@echo off
echo 🚀 Running headless tests until all pass...
echo ============================================

cd frontend\src

echo 📦 Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo 🏗️ Building the application...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Build failed
    exit /b 1
)

echo 🧪 Running unit tests...
call npm test
if %errorlevel% neq 0 (
    echo ❌ Unit tests failed
    exit /b 1
)

echo 🔄 Starting dev server...
start /B npm run dev
timeout /t 15 /nobreak >nul

echo 🎯 Running headless tests until success...
powershell -ExecutionPolicy Bypass -File scripts/run-headless-tests.ps1 -MaxAttempts 5 -WaitSeconds 10

if %errorlevel% equ 0 (
    echo ✅ All tests passed! System is ready.
    goto :cleanup
) else (
    echo ❌ Tests failed after all attempts
    goto :cleanup
)

:cleanup
echo 🛑 Stopping dev server...
taskkill /im node.exe /f >nul 2>&1
echo Done.
pause
