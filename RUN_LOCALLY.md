# 🚀 Run Date Concierge Locally (No Docker Needed!)

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ ([Download](https://nodejs.org/))
- Git

### Option 1: Automated Setup (Recommended)

```bash
# Clone and run
git clone <your-repo-url>
cd Date-Concierge
./quick_start.sh
```

This will:
1. ✓ Install all dependencies
2. ✓ Setup SQLite database (simpler than PostgreSQL)
3. ✓ Seed 15 NYC restaurants
4. ✓ Start backend API
5. ✓ Start frontend dev server
6. ✓ Open http://localhost:3000

### Option 2: Manual Setup

#### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Initialize database and seed data
python3 -c "
from app.database import init_db
from app.seed_data import seed_venues
from app.database import SessionLocal

init_db()
db = SessionLocal()
seed_venues(db)
db.close()
print('✓ Database ready!')
"

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

#### Step 2: Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will run at: **http://localhost:3000**

---

## 🎯 First Use

1. **Open** http://localhost:3000
2. **Register** a new account
3. **Create** a planning session
4. **Try it!** Vote on venues

---

## 📱 What You'll See

### 1. Login Screen
Beautiful pink gradient with heart logo:
- Sign in or create account
- JWT authentication
- Instant login

### 2. Home Dashboard
Two main options:
- **Create New Session**: Start planning
- **Join Session**: Enter invite code

### 3. Session Page
Collaborative planning interface:
- See suggested venues
- Vote with emoji reactions (🚫 😐 👍 ❤️)
- Real-time score updates
- Invite code sharing

### 4. Venue Intelligence (If Available)
Deep insights including:
- Where to sit
- What to order
- When to go
- Getting there
- Vibe check

---

## 🧪 Quick Test

Try this in your browser console after starting:

```javascript
// Register user
fetch('http://localhost:8000/api/users/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'test123',
    name: 'Test User'
  })
})
.then(r => r.json())
.then(data => console.log('✓ Registered:', data));

// Login
fetch('http://localhost:8000/api/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'test123'
  })
})
.then(r => r.json())
.then(data => console.log('✓ Token:', data.access_token));
```

---

## 🐛 Troubleshooting

### Backend won't start?

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
# Or use different port:
uvicorn app.main:app --reload --port 8001
```

**Database errors:**
```bash
# Delete and recreate database
rm date_concierge.db
python3 -c "from app.database import init_db; init_db()"
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start?

**Dependencies issue:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Port already in use:**
```bash
# Vite will automatically suggest another port
# Or kill process:
lsof -ti:3000 | xargs kill -9  # Mac/Linux
```

### Can't login?

- Check backend is running: http://localhost:8000/health
- Check API docs: http://localhost:8000/docs
- Open browser console for errors
- Verify CORS is enabled in backend

---

## ⚡ Features Available Locally

### ✅ Working Out of the Box
- User registration and authentication
- Session creation and joining
- Venue browsing (15 seeded NYC restaurants)
- Collaborative voting
- Real-time score updates
- Session management

### 🔧 Requires API Keys (Optional)
Add to `.env` for these features:

```bash
# For AI intelligence extraction
ANTHROPIC_API_KEY=your-key-here

# For Reddit scraping
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-secret

# For enhanced maps
GOOGLE_MAPS_API_KEY=your-key-here
```

Without API keys:
- ✓ All core features work
- ✗ Venue intelligence gathering disabled
- ✗ Reddit insights unavailable
- ✗ Limited maps features

---

## 🌐 Deploy Online

Want to show it to others? Deploy for free:

### Option 1: Vercel (Frontend) + Railway (Backend)

**Frontend (Vercel):**
```bash
cd frontend
npm install -g vercel
vercel

# Follow prompts, set environment variable:
# VITE_API_URL=https://your-backend.railway.app/api
```

**Backend (Railway):**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Add PostgreSQL database
5. Set environment variables
6. Deploy!

### Option 2: Render (All-in-One)

1. Go to [render.com](https://render.com)
2. New → Web Service (Backend)
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. New → Static Site (Frontend)
   - Build: `npm install && npm run build`
   - Publish: `dist`

### Option 3: Heroku

```bash
# Install Heroku CLI
brew install heroku  # Mac

# Login
heroku login

# Deploy backend
cd backend
heroku create your-app-backend
git push heroku main

# Deploy frontend
cd ../frontend
heroku create your-app-frontend
git push heroku main
```

---

## 📊 Database Options

### SQLite (Default - Easiest)
```python
# In app/config.py
DATABASE_URL = "sqlite:///./date_concierge.db"
```
✅ No setup required
✅ Perfect for development
✅ Single file database
❌ Not for production

### PostgreSQL (Production)
```bash
# Install PostgreSQL
brew install postgresql  # Mac
sudo apt install postgresql  # Linux

# Create database
createdb date_concierge

# Update .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/date_concierge
```

### Use Docker Compose (Original Setup)
```bash
docker compose up -d
# Everything configured automatically!
```

---

## 🎨 Customize

### Change Theme Colors
Edit `frontend/tailwind.config.js`:
```javascript
colors: {
  primary: {
    600: '#your-color-here',
  }
}
```

### Add More Venues
Edit `backend/app/seed_data.py` and add your favorite restaurants!

### Modify Features
- Backend: `backend/app/routers/`
- Frontend: `frontend/src/pages/`

---

## 📝 Available Scripts

### Backend
```bash
# Start server
python -m uvicorn app.main:app --reload

# Seed database
python -m app.seed_data

# Run tests (if you add them)
pytest

# Format code
black app/
```

### Frontend
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

---

## 🎯 Next Steps

1. **Explore the app**: Register, create session, vote!
2. **Check API docs**: http://localhost:8000/docs
3. **Read the demo**: See `DEMO.md` for full walkthrough
4. **Add intelligence**: Get Anthropic API key for venue insights
5. **Deploy**: Share with friends!

---

## 💡 Tips

- **Use incognito mode** to test with multiple users
- **Check browser console** for real-time WebSocket messages
- **Try the API** interactively at /docs
- **Read the code** - it's well-commented!

---

## 🆘 Still Having Issues?

1. Check the logs:
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)

2. Verify services:
   - Backend: `curl http://localhost:8000/health`
   - Frontend: Open http://localhost:3000

3. Check versions:
   - Python: `python3 --version` (need 3.11+)
   - Node: `node --version` (need 18+)

4. Start fresh:
   ```bash
   rm -rf backend/venv backend/*.db
   rm -rf frontend/node_modules
   ./quick_start.sh
   ```

---

**Ready?** Run `./quick_start.sh` and visit http://localhost:3000! 🚀
