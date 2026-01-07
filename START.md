# 🚀 START THE APP IN 3 STEPS

## For Your Local Machine

### Step 1: Install Requirements
```bash
# Need Python 3.11+ and Node.js 18+
python3 --version  # Check you have Python
node --version     # Check you have Node.js
```

Don't have them?
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

### Step 2: Run Setup
```bash
cd Date-Concierge
./quick_start.sh
```

### Step 3: Open Browser
```
http://localhost:3000
```

**That's it!** 🎉

---

## What Happens Next?

1. **Register** an account (any email works locally)
2. **Create** a planning session
3. **Browse** 15 seeded NYC restaurants
4. **Vote** on venues you like

---

## Want to Test Collaboration?

Open another browser (or incognito window):
1. Register as second user
2. Click "Join Session"
3. Enter invite code from first user
4. Vote together in real-time!

---

## Didn't Work?

### Quick Fixes:

**"Command not found: python3"**
- Try `python` instead
- Or install Python from python.org

**"Port 8000 in use"**
```bash
# Kill it and retry
kill -9 $(lsof -ti:8000)
```

**"Port 3000 in use"**
- Vite will suggest port 3001
- Just use that instead

**Still stuck?**
- Read: `RUN_LOCALLY.md` (detailed guide)
- Or use: `docker compose up -d` (if you have Docker)

---

## 🎬 Want to See It Without Running?

Check out:
- **DEMO_VISUAL.md** - See UI mockups
- **DEMO.md** - Complete walkthrough
- **README.md** - Full documentation

---

## 🌐 Deploy Online (Free Options)

### Vercel (Easiest for Frontend)
```bash
cd frontend
npm install -g vercel
vercel
```

### Railway (Easiest for Backend)
1. Go to railway.app
2. New Project → Deploy from GitHub
3. Done!

### Render (Free Tier)
1. Go to render.com
2. New Web Service
3. Connect GitHub
4. Auto-deploys!

---

**Questions?** Open an issue or check the docs!

🚀 **Ready?** → `./quick_start.sh`
