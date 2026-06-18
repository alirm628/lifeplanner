#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip
backend/.venv/bin/python -m pip install -r backend/requirements.txt

cd frontend
npm install
cd ..

echo "Setup complete."
echo "Local backend: backend/.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend"
echo "Local frontend: cd frontend && npm run dev"
