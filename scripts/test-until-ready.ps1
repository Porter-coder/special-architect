# Test system until it's ready
param(
    [int]$MaxAttempts = 5,
    [int]$WaitSeconds = 10
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = "White"
}

function Test-System {
    Write-ColorOutput "🔍 Testing system..." "Cyan"

    Push-Location "$PSScriptRoot\..\frontend\src"

    try {
        # Install dependencies
        Write-ColorOutput "📦 Installing dependencies..." "Yellow"
        & npm install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

        # Build
        Write-ColorOutput "🏗️ Building application..." "Yellow"
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw "build failed" }

        # Run unit tests
        Write-ColorOutput "🧪 Running unit tests..." "Yellow"
        & npm test
        if ($LASTEXITCODE -ne 0) { throw "unit tests failed" }

        # Start server
        Write-ColorOutput "🚀 Starting server..." "Yellow"
        $serverProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow -PassThru

        # Wait for server to start
        Start-Sleep -Seconds 15

        # Test health endpoint
        Write-ColorOutput "🏥 Testing health check..." "Yellow"
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -TimeoutSec 10
            if ($response.StatusCode -ne 200) { throw "Health check failed" }
        } catch {
            throw "Health check failed: $_"
        }

        # Test API endpoint
        Write-ColorOutput "🔗 Testing API endpoint..." "Yellow"
        try {
            $body = @{ prompt = "Create a simple Python hello world" } | ConvertTo-Json
            $response = Invoke-WebRequest -Uri "http://localhost:3000/api/generate" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
            if ($response.StatusCode -ne 200) { throw "API test failed" }
        } catch {
            throw "API test failed: $_"
        }

        # Stop server
        Write-ColorOutput "🛑 Stopping server..." "Yellow"
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue

        return $true
    }
    catch {
        # Stop server if running
        Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        throw
    }
    finally {
        Pop-Location
    }
}

# Main loop
for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    Write-ColorOutput "`n🔄 Attempt $attempt/$MaxAttempts" "Magenta"

    try {
        $success = Test-System
        if ($success) {
            Write-ColorOutput "`n🎉 SUCCESS! System is working and ready for deployment." "Green"
            exit 0
        }
    }
    catch {
        Write-ColorOutput "❌ Attempt $attempt failed: $_" "Red"

        if ($attempt -lt $MaxAttempts) {
            Write-ColorOutput "⏳ Waiting $WaitSeconds seconds before retry..." "Yellow"
            Start-Sleep -Seconds $WaitSeconds
        }
    }
}

Write-ColorOutput "`n💥 All $MaxAttempts attempts failed. Manual intervention required." "Red"
exit 1
