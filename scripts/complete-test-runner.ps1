# Complete Test Runner - Runs all tests until they pass
param(
    [int]$MaxAttempts = 5,
    [int]$ServerStartWait = 15,
    [int]$TestInterval = 3
)

$ErrorActionPreference = "Stop"

function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = "White"
}

function Start-DevServer {
    Write-ColoredOutput "🚀 Starting Next.js development server..." "Yellow"

    $serverProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow -PassThru -WorkingDirectory "$PSScriptRoot\..\frontend\src"

    # Wait for server to start
    Write-ColoredOutput "⏳ Waiting $ServerStartWait seconds for server to start..." "Yellow"
    Start-Sleep -Seconds $ServerStartWait

    # Check if server is still running
    $serverRunning = Get-Process -Id $serverProcess.Id -ErrorAction SilentlyContinue
    if (-not $serverRunning) {
        throw "Server failed to start"
    }

    return $serverProcess
}

function Stop-DevServer {
    param([System.Diagnostics.Process]$ServerProcess)

    if ($ServerProcess) {
        Write-ColoredOutput "🛑 Stopping development server..." "Yellow"
        Stop-Process -Id $ServerProcess.Id -Force -ErrorAction SilentlyContinue

        # Wait a moment for cleanup
        Start-Sleep -Seconds 2
    }
}

function Run-HeadlessTest {
    param([int]$AttemptNumber)

    Write-ColoredOutput "`n🔄 Test Attempt $AttemptNumber/$MaxAttempts" "Cyan"

    try {
        Push-Location "$PSScriptRoot\..\frontend"

        # Run the headless test
        $testProcess = Start-Process -FilePath "node" -ArgumentList "src/scripts/headless-test.js" -NoNewWindow -Wait -PassThru -WorkingDirectory "$PSScriptRoot\..\frontend"

        if ($testProcess.ExitCode -eq 0) {
            Write-ColoredOutput "✅ All tests passed on attempt $AttemptNumber!" "Green"
            return $true
        } else {
            Write-ColoredOutput "❌ Tests failed on attempt $AttemptNumber (Exit code: $($testProcess.ExitCode))" "Red"
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Test execution failed: $_" "Red"
        return $false
    }
    finally {
        Pop-Location
    }
}

function Main {
    Write-ColoredOutput "🎯 Complete Test Runner - Real-Time Workbench" "Green"
    Write-ColoredOutput "=" * 50 "Cyan"
    Write-ColoredOutput "This script will:" "White"
    Write-ColoredOutput "1. Start the Next.js dev server" "White"
    Write-ColoredOutput "2. Run headless tests repeatedly until all pass" "White"
    Write-ColoredOutput "3. Stop the server when done" "White"
    Write-ColoredOutput "" "White"

    $serverProcess = $null

    try {
        # Start the dev server
        $serverProcess = Start-DevServer

        # Run tests until they pass or max attempts reached
        for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
            $success = Run-HeadlessTest -AttemptNumber $attempt

            if ($success) {
                Write-ColoredOutput "`n🎉 SUCCESS! All tests passed after $attempt attempts." "Green"
                Write-ColoredOutput "The Real-Time Workbench system is fully functional! 🚀" "Green"
                return 0
            }

            if ($attempt -lt $MaxAttempts) {
                Write-ColoredOutput "⏳ Waiting $TestInterval seconds before next attempt..." "Yellow"
                Start-Sleep -Seconds $TestInterval
            }
        }

        Write-ColoredOutput "`n💥 FAILURE! All $MaxAttempts attempts failed." "Red"
        Write-ColoredOutput "The system needs manual intervention." "Red"
        return 1

    }
    catch {
        Write-ColoredOutput "💥 Script failed: $_" "Red"
        return 1
    }
    finally {
        # Always stop the server
        if ($serverProcess) {
            Stop-DevServer -ServerProcess $serverProcess
        }
    }
}

# Run the main function
try {
    $exitCode = Main
    exit $exitCode
}
catch {
    Write-ColoredOutput "💥 Unexpected error: $_" "Red"
    exit 1
}
