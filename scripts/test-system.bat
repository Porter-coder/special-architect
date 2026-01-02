@echo off
echo 🚀 Testing Real-Time Workbench System
echo =====================================

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

echo 🚀 Starting development server...
start /B npm run dev
timeout /t 10 /nobreak >nul

echo 🔍 Testing API endpoints...
curl -s http://localhost:3000/api/health >nul
if %errorlevel% neq 0 (
    echo ❌ Health check failed
    taskkill /im node.exe /f >nul 2>&1
    exit /b 1
)

echo ✅ Health check passed

echo 📝 Testing API endpoints...
curl -s -X POST http://localhost:3000/api/generate -H "Content-Type: application/json" -d "{\"prompt\":\"test\"}" >nul
if %errorlevel% neq 0 (
    echo ❌ API generate endpoint failed
    taskkill /im node.exe /f >nul 2>&1
    exit /b 1
)

echo ✅ API endpoints working

echo 🛑 Stopping server...
taskkill /im node.exe /f >nul 2>&1

echo 🎉 All tests passed! System is ready.
echo Ready for deployment.
pause
