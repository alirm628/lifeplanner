param(
  [switch]$SkipSetup
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

function Test-PortListening {
  param([int]$Port)
  $conn = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
  return $null -ne $conn
}

function Wait-Url {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [int]$TimeoutSeconds = 60
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
      return $true
    } catch {
      Start-Sleep -Milliseconds 750
    }
  }

  return $false
}

if (-not $SkipSetup) {
  Write-Host 'Running setup...' -ForegroundColor Cyan
  & "$repoRoot\scripts\setup.ps1"
}

$backendRunning = Test-PortListening -Port 8000
$frontendRunning = Test-PortListening -Port 5173

if (-not $backendRunning) {
  Write-Host 'Starting backend on :8000...' -ForegroundColor Cyan
  $backendCommand = "Set-Location '$repoRoot\\backend'; .\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
  Start-Process powershell -ArgumentList @('-NoProfile', '-WindowStyle', 'Hidden', '-Command', $backendCommand) -WindowStyle Hidden | Out-Null
} else {
  Write-Host 'Backend already running on :8000' -ForegroundColor Yellow
}

if (-not $frontendRunning) {
  Write-Host 'Starting frontend on :5173...' -ForegroundColor Cyan
  $frontendCommand = "Set-Location '$repoRoot\\frontend'; npm run dev"
  Start-Process powershell -ArgumentList @('-NoProfile', '-WindowStyle', 'Hidden', '-Command', $frontendCommand) -WindowStyle Hidden | Out-Null
} else {
  Write-Host 'Frontend already running on :5173' -ForegroundColor Yellow
}

Write-Host 'Waiting for services to be ready...' -ForegroundColor Cyan
$backendReady = Wait-Url -Url 'http://localhost:8000/healthz' -TimeoutSeconds 60
$frontendReady = Wait-Url -Url 'http://localhost:5173' -TimeoutSeconds 60

if (-not $backendReady) {
  throw 'Backend did not become ready in time (http://localhost:8000/healthz).'
}

if (-not $frontendReady) {
  throw 'Frontend did not become ready in time (http://localhost:5173).'
}

Write-Host 'Opening LifePlanner in your browser...' -ForegroundColor Green
Start-Process 'http://localhost:5173'

Write-Host 'LifePlanner is running.' -ForegroundColor Green
Write-Host 'Backend:  http://localhost:8000/healthz'
Write-Host 'Frontend: http://localhost:5173'
