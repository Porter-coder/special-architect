#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Runs headless tests until the system is working or max retries reached.

.DESCRIPTION
    This script continuously runs headless tests to verify the real-time workbench
    system works end-to-end. It will retry until tests pass or max attempts reached.

.PARAMETER MaxRetries
    Maximum number of test runs (default: 10)

.PARAMETER DelaySeconds
    Seconds to wait between test runs (default: 5)

.EXAMPLE
    .\run-headless-tests.ps1 -MaxRetries 5 -DelaySeconds 10
#>

param(
    [int]$MaxAttempts = 10,
    [int]$WaitSeconds = 5
)

$ErrorActionPreference = "Stop"

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "White" = [ConsoleColor]::White
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
    }

    if ($colorMap.ContainsKey($Color)) {
        Write-Host $Message -ForegroundColor $colorMap[$Color]
    } else {
        Write-Host $Message
    }
}

function Test-NodeModules {
    $nodeModulesPath = Join-Path $PSScriptRoot ".." "node_modules"

    if (-not (Test-Path $nodeModulesPath)) {
        Write-ColoredOutput "Installing dependencies..." "Yellow"
        try {
            Push-Location (Join-Path $PSScriptRoot "..")
            & npm install
            Pop-Location
        } catch {
            Write-ColoredOutput "Failed to install dependencies: $_" "Red"
            return $false
        }
    }

    return $true
}

function Run-HeadlessTest {
    param([int]$AttemptNumber)

    Write-ColoredOutput "`n🔄 Attempt $AttemptNumber/$MaxRetries" "Cyan"
    Write-ColoredOutput "Running headless tests..." "White"

    try {
        Push-Location (Join-Path $PSScriptRoot "..")

        # Run the headless test script
        $process = Start-Process -FilePath "node" -ArgumentList "scripts/headless-test.js" -NoNewWindow -Wait -PassThru

        if ($process.ExitCode -eq 0) {
            Write-ColoredOutput "✅ Tests passed on attempt $AttemptNumber!" "Green"
            return $true
        } else {
            Write-ColoredOutput "❌ Tests failed on attempt $AttemptNumber" "Red"
            return $false
        }
    } catch {
        Write-ColoredOutput "❌ Test execution failed: $_" "Red"
        return $false
    } finally {
        Pop-Location
    }
}

function Main {
    Write-ColoredOutput "🚀 Starting headless test runner" "Green"
    Write-ColoredOutput "Max retries: $MaxRetries, Delay: $DelaySeconds seconds" "White"
    Write-ColoredOutput "=" * 50 "Cyan"

    # Check if dependencies are installed
    if (-not (Test-NodeModules)) {
        Write-ColoredOutput "❌ Failed to setup dependencies. Exiting." "Red"
        exit 1
    }

    # Run tests until they pass or max retries reached
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        $success = Run-HeadlessTest -AttemptNumber $attempt

        if ($success) {
            Write-ColoredOutput "`n🎉 System is working! All tests passed." "Green"
            Write-ColoredOutput "Ready for deployment." "Green"
            exit 0
        }

        if ($attempt -lt $MaxAttempts) {
            Write-ColoredOutput "⏳ Waiting $DelaySeconds seconds before next attempt..." "Yellow"
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    Write-ColoredOutput "`n💥 All $MaxRetries attempts failed. System needs manual intervention." "Red"
    Write-ColoredOutput "Check the logs above for specific error details." "Red"
    exit 1
}

# Run the main function
try {
    Main
} catch {
    Write-ColoredOutput "💥 Script execution failed: $_" "Red"
    exit 1
}
