# Windows 11 Deployment Guide

## Prerequisites

- Windows 11
- Python 3.12 (`py -3.12`)
- Node.js 20+
- npm 10+
- (Optional) Docker Desktop for Compose deployment

## Local Development

1. Open PowerShell in repository root.
2. Initialize:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`
3. Create environment file if missing:
   - `Copy-Item .env.example .env`
4. Start backend:
   - `cd backend`
   - `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
5. Start frontend in a second shell:
   - `cd frontend`
   - `npm run dev`
6. Visit:
   - [http://localhost:5173](http://localhost:5173)

## Default Credentials

Values come from `.env`:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

Defaults:
- `admin@local.dev`
- `admin1234`

## Compose Deployment (Windows)

1. Install Docker Desktop.
2. Ensure Docker is running.
3. Run from repo root:
   - `docker compose up -d --build`
4. Open:
   - [http://localhost](http://localhost)

## Updating

- Pull/update files.
- Rebuild containers:
  - `docker compose up -d --build`

## Backup

Use Settings page -> One-click Backup, or call:
- `GET /api/v1/backup/export`
