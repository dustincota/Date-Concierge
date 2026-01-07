# 🔌 Port Configuration

## Current Ports

Your Date Concierge app now runs on these ports:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## Quick Start

```bash
./quick_start.sh
```

Then visit: **http://localhost:5173**

## Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Frontend will start on port **5173** automatically.

## Why These Ports?

- **5173**: Vite's default development port (avoids conflict with your port 3000)
- **8080**: Common alternative to 8000 (avoids conflict with your port 8000)

## Change Ports Again?

If you need different ports, edit these files:

### Backend Port (currently 8080):
- `backend/app/config.py` - line 20: `PORT: int = 8080`
- `docker-compose.yml` - line 56: `"8080:8080"`
- `quick_start.sh` - line 108: `port=8080`

### Frontend Port (currently 5173):
- `frontend/vite.config.ts` - line 14: `port: 5173`
- Also update API proxy target in same file

### API Base URL:
- `frontend/src/utils/api.ts` - line 4: `http://localhost:8080/api`

## Docker Compose

If using Docker, ports are already configured:
```bash
docker compose up -d
```

Services:
- PostgreSQL: 5432
- Redis: 6379
- Backend: **8080**
- Celery Flower: 5555

## Troubleshooting

### Port still in use?

**Find and kill process:**
```bash
# Mac/Linux
lsof -ti:8080 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Vite auto-picks different port?

If port 5173 is taken, Vite will suggest 5174, 5175, etc.
Just use whatever port it suggests!

### CORS errors?

Make sure `backend/app/config.py` includes your frontend port:
```python
CORS_ORIGINS: list = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

## Testing

After starting both servers:

```bash
# Test backend
curl http://localhost:8080/health

# Test frontend (open in browser)
open http://localhost:5173
```

## All Access Points

Once running, you can access:

| Service | URL |
|---------|-----|
| Frontend App | http://localhost:5173 |
| Backend API | http://localhost:8080 |
| API Docs (Swagger) | http://localhost:8080/docs |
| API Docs (ReDoc) | http://localhost:8080/redoc |
| Health Check | http://localhost:8080/health |

Happy dating! 💕
