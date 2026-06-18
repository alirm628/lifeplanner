# Raspberry Pi 5 Deployment Guide (Debian/Ubuntu/Raspberry Pi OS)

## Prerequisites

- Raspberry Pi 5 (64-bit OS recommended)
- Docker Engine + Docker Compose plugin
- Git

## 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
docker --version
docker compose version
```

## 2. Clone Project

```bash
git clone <your-repo-url> lifeplanner
cd lifeplanner
```

## 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` values:
- `SECRET_KEY`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `TZ`
- optional custom ports

## 4. Start

```bash
docker compose up -d --build
```

Access app at:
- `http://<pi-ip-address>`

## 5. Persistence

SQLite data is stored in Docker volume:
- `lifeplanner_data`

No code changes are required between Windows and Raspberry Pi.

## 6. Reverse Proxy / HTTPS Later

Current compose includes Nginx HTTP reverse proxy.
To add HTTPS later:
- add certificate volumes
- add TLS server block in `nginx/default.conf`
- expose `443`

## 7. Resource Notes

- Keep only required services running.
- For low-memory environments, add compose resource limits.
- Scheduler is lightweight heuristic and suitable for Pi-class CPU.

## 8. Updating

```bash
git pull
docker compose up -d --build
```

## 9. Backup/Restore

Use app Settings page backup/export and import/restore.
