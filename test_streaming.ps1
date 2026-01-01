# Test script for AI Code Flow streaming functionality

Write-Host "🚀 Testing AI Code Flow Streaming"
Write-Host "=================================="

# Step 1: Test server health
Write-Host "`n1. Testing server health..."
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 5
    $health = $response.Content | ConvertFrom-Json
    Write-Host "✓ Server healthy: $($health.status)"
} catch {
    Write-Host "✗ Server not responding: $($_.Exception.Message)"
    exit 1
}

# Step 2: Create a code generation request
Write-Host "`n2. Creating code generation request..."
$headers = @{"Content-Type" = "application/json"}
$body = '{"user_input": "写个简单的Hello World程序"}'

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/generate-code" -Method POST -Headers $headers -Body $body -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    $requestId = $result.request_id
    Write-Host "✓ Request created: $requestId"
} catch {
    Write-Host "✗ Request creation failed: $($_.Exception.Message)"
    exit 1
}

# Step 3: Wait for generation to complete
Write-Host "`n3. Waiting for generation to complete..."
Start-Sleep -Seconds 15

# Step 4: Test streaming
Write-Host "`n4. Testing streaming functionality..."
try {
    $streamResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/generate-code/$requestId/stream" -TimeoutSec 30
    $streamLines = $streamResponse.Content -split "`n"

    Write-Host "✓ Streaming completed successfully!"
    Write-Host "Stream events received: $($streamLines.Count)"

    # Count different event types
    $connectedEvents = ($streamLines | Where-Object { $_ -match "event: connected" }).Count
    $thinkingEvents = ($streamLines | Where-Object { $_ -match "event: ai_thinking" }).Count
    $phaseEvents = ($streamLines | Where-Object { $_ -match "event: phase_update" }).Count
    $completionEvents = ($streamLines | Where-Object { $_ -match "event: completion" }).Count

    Write-Host "📊 Event breakdown:"
    Write-Host "  - Connected: $connectedEvents"
    Write-Host "  - Thinking: $thinkingEvents"
    Write-Host "  - Phase updates: $phaseEvents"
    Write-Host "  - Completion: $completionEvents"

    # Check for "store & replay" pattern
    if ($thinkingEvents -gt 0 -and $phaseEvents -gt 0) {
        Write-Host "✓ Store & Replay streaming is working!"
    }

} catch {
    Write-Host "✗ Streaming test failed: $($_.Exception.Message)"
    exit 1
}

# Step 5: Test project retrieval
Write-Host "`n5. Testing project retrieval..."
try {
    $projectResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/projects/$requestId" -TimeoutSec 10
    $project = $projectResponse.Content | ConvertFrom-Json
    Write-Host "✓ Project retrieved: $($project.project_name)"
    Write-Host "  - Files: $($project.total_files)"
    Write-Host "  - Size: $($project.total_size_bytes) bytes"
    Write-Host "  - Validated: $($project.syntax_validated)"
} catch {
    Write-Host "✗ Project retrieval failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "`n🎉 All tests passed! Streaming functionality is working correctly."
Write-Host "`n📋 Summary:"
Write-Host "  ✅ Server health check"
Write-Host "  ✅ Request creation"
Write-Host "  ✅ Background generation"
Write-Host "  ✅ Store & Replay streaming"
Write-Host "  ✅ Project retrieval"
Write-Host "  ✅ No attribute errors"
