param(
  [switch]$UseDocker
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.env')) {
  Copy-Item '.env.example' '.env'
  Write-Host 'Created .env from .env.example'
}

Write-Host 'Setting up backend venv and dependencies...'
py -3.12 -m venv backend\.venv
& backend\.venv\Scripts\python.exe -m pip install --upgrade pip
& backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

Write-Host 'Setting up frontend dependencies...'
Push-Location frontend
npm install
Pop-Location

if ($UseDocker) {
  Write-Host 'Starting with Docker Compose...'
  docker compose up -d --build
} else {
  Write-Host 'Setup complete. Run backend and frontend locally:'
  Write-Host '1) backend: .\\backend\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
  Write-Host '2) frontend: cd frontend; npm run dev'
}
