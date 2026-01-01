# Deployment Guide

Complete deployment instructions for AI Code Flow in production environments.

## Prerequisites

### System Requirements

- **Operating System**: Windows Server 2019+ or Windows 10/11
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB free space (for logs and generated projects)
- **Network**: Stable internet connection (10Mbps+)

### Software Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11.x | Backend runtime |
| Node.js | 20.x LTS | Frontend build |
| PowerShell | 5.1+ | Automation scripts |
| IIS/Apache | Latest | Reverse proxy (optional) |
| SSL Certificate | Valid | HTTPS support |

### API Keys Required

- **MiniMax API Key**: Primary AI provider
- **OpenAI API Key**: Fallback AI provider

## Production Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Reverse Proxy  │
│   (Optional)    │────│   (IIS/Apache)  │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   AI Code Flow  │    │   AI Providers  │
│   Backend       │◄──►│   (MiniMax)     │
│   (FastAPI)     │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   File Storage  │
│   (Next.js)     │    │   (Local/Cloud) │
└─────────────────┘    └─────────────────┘
```

## Deployment Options

### Option 1: Standalone Deployment (Recommended)

Single server deployment with all components.

### Option 2: Distributed Deployment

Separate servers for backend and frontend.

### Option 3: Cloud Deployment

Azure/AWS/GCP with managed services.

## Installation Steps

### 1. Server Preparation

```powershell
# Update Windows
Install-WindowsUpdate -AcceptAll -AutoReboot

# Install required Windows features
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer

# Configure firewall
New-NetFirewallRule -DisplayName "AI Code Flow HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "AI Code Flow HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

### 2. Python Environment Setup

```powershell
# Download and install Python 3.11
# From: https://www.python.org/downloads/

# Verify installation
python --version  # Should show Python 3.11.x

# Install virtual environment support
python -m pip install --upgrade pip
python -m pip install virtualenv
```

### 3. Application Deployment

```powershell
# Create application directory
New-Item -ItemType Directory -Path "C:\AI-Code-Flow" -Force
Set-Location "C:\AI-Code-Flow"

# Clone repository
git clone <repository-url> .
git checkout main  # or production branch

# Backend setup
Set-Location backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt --only-binary=all
```

### 4. Configuration

Create production configuration:

```powershell
# Create config directory
New-Item -ItemType Directory -Path "C:\AI-Code-Flow\config" -Force

# Create production config
@"
{
  "minimax": {
    "api_key": "$env:MINIMAX_API_KEY",
    "base_url": "https://api.minimax.chat/v1"
  },
  "openai": {
    "api_key": "$env:OPENAI_API_KEY",
    "base_url": "https://api.openai.com/v1"
  },
  "generation": {
    "model": "MiniMax-M2.1",
    "max_tokens": 4000,
    "temperature": 0.1,
    "timeout": 60
  },
  "system": {
    "max_concurrent_users": 5,
    "log_level": "INFO",
    "projects_dir": "C:\\AI-Code-Flow\\projects",
    "logs_dir": "C:\\AI-Code-Flow\\logs"
  },
  "security": {
    "cors_origins": ["https://yourdomain.com"],
    "rate_limit_per_minute": 10,
    "max_request_size_mb": 10
  }
}
"@ | Out-File -FilePath "C:\AI-Code-Flow\backend\config.json" -Encoding UTF8
```

### 5. Frontend Build

```powershell
Set-Location "C:\AI-Code-Flow\frontend"
npm ci --only=production
npm run build

# Verify build
Test-Path "C:\AI-Code-Flow\frontend\.next" -PathType Container
```

## Service Configuration

### Windows Service Setup

Create Windows service for backend:

```powershell
# Create service script
@"
# AI Code Flow Backend Service
Set-Location "C:\AI-Code-Flow\backend"
.venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
"@ | Out-File -FilePath "C:\AI-Code-Flow\scripts\run-backend.ps1" -Encoding UTF8

# Register as Windows service using NSSM
# Download NSSM from https://nssm.cc/
nssm install "AICodeFlow" "powershell.exe" "-ExecutionPolicy Bypass -File C:\AI-Code-Flow\scripts\run-backend.ps1"
nssm set "AICodeFlow" Description "AI Code Flow Backend Service"
nssm start "AICodeFlow"
```

### IIS Reverse Proxy Setup (Optional)

Configure IIS for frontend hosting:

```xml
<!-- web.config -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="React Routes" stopProcessing="true">
                    <match url=".*" />
                    <conditions logicalGrouping="MatchAll">
                        <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
                        <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
                    </conditions>
                    <action type="Rewrite" url="/index.html" />
                </rule>
            </rules>
        </rewrite>
        <staticContent>
            <mimeMap fileExtension=".json" mimeType="application/json" />
        </staticContent>
    </system.webServer>
</configuration>
```

## Environment Variables

Set required environment variables:

```powershell
# API Keys (secure storage recommended)
[Environment]::SetEnvironmentVariable("MINIMAX_API_KEY", "your-minimax-key", "Machine")
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-openai-key", "Machine")

# Application settings
[Environment]::SetEnvironmentVariable("ENVIRONMENT", "production", "Machine")
[Environment]::SetEnvironmentVariable("LOG_LEVEL", "INFO", "Machine")
```

## SSL/TLS Configuration

### Using Windows Certificate Store

```powershell
# Import SSL certificate
Import-PfxCertificate -FilePath "C:\certs\certificate.pfx" -CertStoreLocation Cert:\LocalMachine\My

# Configure IIS for HTTPS
# Use IIS Manager to bind certificate to site
```

### Let's Encrypt (Automated)

```powershell
# Install Win-ACME
# Download from https://www.win-acme.com/
wacs.exe --target manual --host yourdomain.com
```

## Monitoring Setup

### Application Monitoring

```powershell
# Create monitoring script
@"
# Health check monitoring
$healthUrl = "http://localhost:8000/api/health"
$maxRetries = 3

for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 30
        $health = $response.Content | ConvertFrom-Json

        if ($health.status -eq "healthy") {
            Write-Host "✓ Service is healthy"
            exit 0
        } else {
            Write-Warning "⚠ Service status: $($health.status)"
        }
    } catch {
        Write-Warning "✗ Health check failed (attempt $i/$maxRetries): $($_.Exception.Message)"
        if ($i -lt $maxRetries) {
            Start-Sleep -Seconds 5
        }
    }
}

Write-Error "❌ Service is unhealthy"
exit 1
"@ | Out-File -FilePath "C:\AI-Code-Flow\scripts\health-check.ps1" -Encoding UTF8
```

### Windows Performance Monitoring

```powershell
# Configure Windows Performance Counters
# Monitor CPU, Memory, Disk I/O, Network

# Setup scheduled task for monitoring
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\AI-Code-Flow\scripts\health-check.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "AICodeFlowHealthCheck" -Action $action -Trigger $trigger -User "SYSTEM"
```

## Backup Strategy

### Automated Backups

```powershell
# Create backup script
@"
# AI Code Flow Backup Script
param(
    [string]$BackupPath = "D:\Backups\AI-Code-Flow"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $BackupPath $timestamp

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force

# Backup application files
Copy-Item "C:\AI-Code-Flow\*" $backupDir -Recurse -Exclude @("logs", "projects", ".venv", "node_modules")

# Backup configuration (secure)
Copy-Item "C:\AI-Code-Flow\backend\config.json" $backupDir

# Backup projects (compressed)
Compress-Archive -Path "C:\AI-Code-Flow\projects\*" -DestinationPath "$backupDir\projects.zip"

# Backup logs (last 7 days)
$logFiles = Get-ChildItem "C:\AI-Code-Flow\logs\*" -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
Compress-Archive -Path $logFiles.FullName -DestinationPath "$backupDir\logs.zip"

# Cleanup old backups (keep last 30)
$oldBackups = Get-ChildItem $BackupPath |
    Where-Object { $_.PSIsContainer -and $_.Name -match "^\\d{8}_\\d{6}$" } |
    Sort-Object Name -Descending |
    Select-Object -Skip 30

foreach ($oldBackup in $oldBackups) {
    Remove-Item $oldBackup.FullName -Recurse -Force
    Write-Host "Cleaned up old backup: $($oldBackup.Name)"
}

Write-Host "Backup completed: $backupDir"
"@ | Out-File -FilePath "C:\AI-Code-Flow\scripts\backup.ps1" -Encoding UTF8

# Schedule daily backups
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\AI-Code-Flow\scripts\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
Register-ScheduledTask -TaskName "AICodeFlowBackup" -Action $action -Trigger $trigger -User "SYSTEM"
```

## Scaling Considerations

### Vertical Scaling

```powershell
# Increase worker processes
# Edit service configuration to use more workers
# Monitor resource usage and adjust accordingly
```

### Horizontal Scaling

```powershell
# Load balancer configuration
# Session affinity for streaming connections
# Shared storage for generated projects
```

### Performance Tuning

```powershell
# Database optimization (if added later)
# Cache configuration
# Connection pooling
# Memory limits
```

## Security Hardening

### Network Security

```powershell
# Configure Windows Firewall
New-NetFirewallRule -DisplayName "AI Code Flow Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Domain,Private

# Disable unused services
Stop-Service -Name "Telnet"
Set-Service -Name "Telnet" -StartupType Disabled
```

### Application Security

```powershell
# Input validation (already implemented)
# Rate limiting (configured)
# Error handling (no stack traces in production)
# Secure headers (add to reverse proxy)
```

## Troubleshooting

### Common Production Issues

**High Memory Usage:**
```powershell
# Monitor memory usage
Get-Process -Name python | Select-Object Name, WS, CPU

# Restart service if needed
Restart-Service AICodeFlow
```

**Slow Response Times:**
```powershell
# Check AI provider connectivity
Test-NetConnection -ComputerName api.minimax.chat -Port 443

# Monitor concurrent requests
Invoke-WebRequest -Uri "http://localhost:8000/api/health" | ConvertFrom-Json
```

**Disk Space Issues:**
```powershell
# Check disk usage
Get-PSDrive C | Select-Object Used, Free

# Clean up old logs
Get-ChildItem "C:\AI-Code-Flow\logs\*" -File |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item
```

## Maintenance Procedures

### Regular Tasks

- **Daily**: Monitor health checks and logs
- **Weekly**: Review performance metrics and backups
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system backup and restore testing

### Emergency Procedures

1. **Service Down**: Check Windows services and restart
2. **High Load**: Scale up resources or implement rate limiting
3. **Data Loss**: Restore from backups
4. **Security Incident**: Isolate affected systems and investigate

## Support and Monitoring

### External Monitoring

```powershell
# Setup external monitoring (e.g., DataDog, New Relic)
# Configure alerts for:
# - Service downtime
# - High error rates
# - Performance degradation
# - Disk space warnings
```

### Contact Information

- **Technical Support**: tech-support@company.com
- **Emergency**: emergency@company.com
- **Documentation**: https://docs.company.com/ai-code-flow

---

**Last Updated**: 2026-01-01
**Version**: 1.0.0
