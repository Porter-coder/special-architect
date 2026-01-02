# Trinity Generation Test - Proof of Life
param(
    [int]$WaitSeconds = 30
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
    Write-ColoredOutput "⏳ Waiting for server to start..." "Yellow"
    Start-Sleep -Seconds 10

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
        Start-Sleep -Seconds 2
    }
}

function Invoke-Generation {
    param([string]$Prompt, [int]$GenerationNumber)

    Write-ColoredOutput "`n🔄 Starting Generation $GenerationNumber..." "Cyan"
    Write-ColoredOutput "Prompt: $Prompt" "Gray"

    try {
        $body = @{
            prompt = $Prompt
            application_type = "python"
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/generate" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30

        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            $projectId = $data.project_id
            Write-ColoredOutput "✅ Generation $GenerationNumber started - Project ID: $projectId" "Green"
            return $projectId
        } else {
            throw "HTTP $($response.StatusCode)"
        }
    }
    catch {
        Write-ColoredOutput "❌ Generation $GenerationNumber failed: $_" "Red"
        return $null
    }
}

function Wait-For-Generation {
    param([string]$ProjectId, [int]$GenerationNumber, [int]$TimeoutSeconds = 120)

    Write-ColoredOutput "⏳ Waiting for Generation $GenerationNumber to complete..." "Yellow"

    $startTime = Get-Date
    $completed = $false

    while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
        try {
            # Check if project directory exists and has files
            $projectDir = Join-Path "$PSScriptRoot\..\projects" $ProjectId
            if (Test-Path $projectDir) {
                $mainPyPath = Join-Path $projectDir "main.py"
                if (Test-Path $mainPyPath) {
                    $content = Get-Content $mainPyPath -Raw
                    if ($content -and $content.Trim().Length -gt 0) {
                        Write-ColoredOutput "✅ Generation $GenerationNumber completed successfully!" "Green"
                        Write-ColoredOutput "📁 Project directory: $projectDir" "Gray"
                        Write-ColoredOutput "📄 main.py size: $($content.Length) characters" "Gray"
                        return $true
                    }
                }
            }
        }
        catch {
            # Ignore errors, continue checking
        }

        Start-Sleep -Seconds 2
    }

    Write-ColoredOutput "❌ Generation $GenerationNumber timed out after $TimeoutSeconds seconds" "Red"
    return $false
}

function Main {
    Write-ColoredOutput "🧪 TRINITY GENERATION TEST - PROOF OF LIFE" "Green"
    Write-ColoredOutput "==================================================" "Cyan"
    Write-ColoredOutput "This script will perform 3 code generations and verify files are created." "White"
    Write-ColoredOutput "" "White"

    $serverProcess = $null
    $projectIds = @()

    try {
        # Start the dev server
        $serverProcess = Start-DevServer

        # Define the three prompts
        $prompts = @(
            "Create a Python snake game using pygame with collision detection and scoring",
            "Create a Python calculator application with GUI using tkinter",
            "Create a Python weather app that fetches data from an API and displays it"
        )

        # Perform the three generations
        for ($i = 0; $i -lt $prompts.Length; $i++) {
            $projectId = Invoke-Generation -Prompt $prompts[$i] -GenerationNumber ($i + 1)
            if ($projectId) {
                $projectIds += $projectId
                $success = Wait-For-Generation -ProjectId $projectId -GenerationNumber ($i + 1)
                if (-not $success) {
                    throw "Generation $($i + 1) failed to complete"
                }
            } else {
                throw "Generation $($i + 1) failed to start"
            }
        }

        # Verify all projects exist
        Write-ColoredOutput "`n🔍 VERIFICATION PHASE" "Magenta"
        Write-ColoredOutput "==============================" "Cyan"

        $allValid = $true
        foreach ($projectId in $projectIds) {
            $projectDir = Join-Path "$PSScriptRoot\..\projects" $projectId
            $mainPyPath = Join-Path $projectDir "main.py"

            if (Test-Path $projectDir) {
                Write-ColoredOutput "✅ Project directory exists: $projectDir" "Green"

                if (Test-Path $mainPyPath) {
                    $content = Get-Content $mainPyPath -Raw
                    if ($content -and $content.Trim().Length -gt 0) {
                        Write-ColoredOutput "✅ main.py exists with content ($($content.Length) chars)" "Green"
                    } else {
                        Write-ColoredOutput "❌ main.py is empty or missing content" "Red"
                        $allValid = $false
                    }
                } else {
                    Write-ColoredOutput "❌ main.py does not exist" "Red"
                    $allValid = $false
                }
            } else {
                Write-ColoredOutput "❌ Project directory does not exist: $projectDir" "Red"
                $allValid = $false
            }
        }

        # Show final directory structure
        Write-ColoredOutput "`n📂 FINAL PROJECTS DIRECTORY STRUCTURE" "Magenta"
        Write-ColoredOutput "========================================" "Cyan"

        Get-ChildItem "$PSScriptRoot\..\projects" -Recurse | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
            $relativePath = $_.FullName.Replace("$PSScriptRoot\..\projects", "projects")
            $size = if ($_.Length -gt 1024) { "$([math]::Round($_.Length / 1024, 1)) KB" } else { "$($_.Length) bytes" }
            Write-ColoredOutput "📄 $relativePath ($size)" "White"
        }

        if ($allValid) {
            Write-ColoredOutput "`n🎉 TRINITY TEST PASSED! All generations completed successfully." "Green"
            Write-ColoredOutput "The Real-Time Workbench is fully operational! 🚀" "Green"
            return 0
        } else {
            Write-ColoredOutput "`n💥 TRINITY TEST FAILED! Some generations did not complete properly." "Red"
            return 1
        }

    }
    catch {
        Write-ColoredOutput "💥 Test failed: $_" "Red"
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
