# Date Concierge - Live Demo Walkthrough

## 🚀 Setup Instructions

### 1. Start the Application

```bash
# Clone and navigate to the project
cd Date-Concierge

# Set up environment variables
cp .env.example .env

# Edit .env with your API keys (optional for basic demo)
# ANTHROPIC_API_KEY=your-key  # For AI intelligence features
# REDDIT_CLIENT_ID=your-id    # For Reddit scraping
# GOOGLE_MAPS_API_KEY=your-key # For enhanced maps

# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
# You should see:
# ✓ postgres - healthy
# ✓ redis - healthy
# ✓ backend - started
# ✓ celery_worker - started
```

### 2. Seed the Database

```bash
# Add sample NYC restaurants
docker-compose exec backend python -m app.seed_data

# Output:
# Seeding venues...
#   + Added Celestine
#   + Added Lilia
#   + Added Carbone
#   ... (15 total venues)
# Seeded 15 venues!
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev

# Frontend will start at: http://localhost:3000
# Backend API at: http://localhost:8000
# API Docs at: http://localhost:8000/docs
```

---

## 🎬 Demo Scenario: Planning a Saturday Night Date

### Step 1: User Registration

**URL**: http://localhost:3000

![Login Screen](demo-screenshots/01-login.png)

**What you see:**
- Beautiful gradient background (pink to purple)
- Heart icon logo
- "Date Concierge" title
- Login/Register form

**Action:**
```
1. Click "Don't have an account? Sign up"
2. Enter:
   - Name: Alex
   - Email: alex@example.com
   - Password: password123
3. Click "Create Account"
```

**Result:**
- JWT token stored in localStorage
- Redirected to Home page
- Greeted as "Hi, Alex"

---

### Step 2: Create Planning Session

**URL**: http://localhost:3000

![Home Page](demo-screenshots/02-home.png)

**What you see:**
- Header with "Date Concierge" logo
- "Plan the Perfect Date Together" headline
- Two cards:
  - 🆕 Create New Session
  - 👥 Join Session
- Features showcase (Collaborative, Intelligent, Location-Smart)

**Action:**
```
1. Click "Create New Session" card
2. Modal appears
3. Enter: "Saturday Night Date"
4. Click "Create"
```

**Result:**
- Session created with unique ID
- Invite code generated (e.g., "ABC12XYZ")
- Redirected to session page

---

### Step 3: Session Page (Organizer View)

**URL**: http://localhost:3000/session/[session-id]

![Session Page](demo-screenshots/03-session-empty.png)

**What you see:**
- Header showing "Saturday Night Date"
- Invite code button: "Code: ABC12XYZ"
- Empty state: "No venues suggested yet"

**Action:**
```
1. Click the invite code button
2. Code copied to clipboard
3. Share with partner (via text/email)
```

---

### Step 4: Partner Joins (Second Browser/Incognito)

**Second Browser - Registration:**
```
1. Open http://localhost:3000 in incognito/private window
2. Register as:
   - Name: Jordan
   - Email: jordan@example.com
   - Password: password123
```

**Join Session:**
```
1. On home page, click "Join Session"
2. Enter invite code: ABC12XYZ
3. Click "Join"
```

**Result:**
- Jordan joins the session
- Both users now see each other (if WebSocket connected)
- Ready to collaborate!

---

### Step 5: Explore Venues (Using API)

**Terminal - Search for venues:**
```bash
# Get auth token first
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"password123"}'

# Response:
# {"access_token":"eyJ0eXAiOiJKV1QiLCJhbGc...","token_type":"bearer"}

# Search venues in Williamsburg
curl -X GET "http://localhost:8000/api/venues?neighborhood=Williamsburg" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response: List of venues
[
  {
    "id": "uuid-here",
    "name": "Lilia",
    "neighborhood": "Williamsburg",
    "cuisines": ["Italian"],
    "price_level": 3,
    "rating": 4.7,
    "latitude": 40.7089,
    "longitude": -73.9502
  },
  {
    "name": "Peter Luger Steak House",
    ...
  }
]
```

---

### Step 6: Suggest Venues

**API Call - Alex suggests Lilia:**
```bash
curl -X POST http://localhost:8000/api/sessions/SESSION_ID/venues \
  -H "Authorization: Bearer ALEX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"venue_id":"LILIA_VENUE_ID"}'
```

**API Call - Jordan suggests Celestine:**
```bash
curl -X POST http://localhost:8000/api/sessions/SESSION_ID/venues \
  -H "Authorization: Bearer JORDAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"venue_id":"CELESTINE_VENUE_ID"}'
```

**Both Session Pages Update:**
Now showing 2 venue cards with voting options.

---

### Step 7: Collaborative Voting

**Session Page - Both Users See:**

![Voting Interface](demo-screenshots/04-voting.png)

```
┌─────────────────────────────────────────┐
│ 🏛️  Lilia                               │
│ Williamsburg                            │
│                                         │
│ Current Votes:                          │
│ ❤️: 0  👍: 0  😐: 0  🚫: 0            │
│                                         │
│ Your Vote:                              │
│ [🚫] [😐] [👍] [❤️]                   │
│     Veto  Neutral Like Love            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ⛵  Celestine                           │
│ DUMBO                                   │
│                                         │
│ Current Votes:                          │
│ ❤️: 0  👍: 0  😐: 0  🚫: 0            │
│                                         │
│ Your Vote:                              │
│ [🚫] [😐] [👍] [❤️]                   │
└─────────────────────────────────────────┘
```

**Alex votes:**
- Lilia: ❤️ Love (2 points)
- Celestine: 👍 Like (1 point)

**Jordan votes:**
- Lilia: 👍 Like (1 point)
- Celestine: ❤️ Love (2 points)

**Real-time Update (via WebSocket):**
Both users instantly see:
```
Lilia: Avg Score 1.5 (❤️: 1, 👍: 1)
Celestine: Avg Score 1.5 (❤️: 1, 👍: 1)
```

---

### Step 8: View Venue Intelligence

**API Call - Get Celestine Intelligence:**
```bash
curl -X GET http://localhost:8000/api/venues/CELESTINE_ID/intelligence \
  -H "Authorization: Bearer TOKEN"
```

**Response - Rich Intelligence Data:**
```json
{
  "venue_id": "...",
  "venue_name": "Celestine",
  "intelligence_score": 0.85,
  "date_score": 9.2,
  "trending_score": 7.5,

  "seating": [
    {
      "spot": "Patio table near waterfront",
      "why": "Best Manhattan skyline views",
      "how_to_request": "Request outdoor seating when booking",
      "best_for": ["romantic", "anniversary"],
      "confidence": 0.9,
      "mentions": 12,
      "source": "reddit"
    },
    {
      "spot": "Window booth inside",
      "why": "Cozy and intimate, great for conversation",
      "how_to_request": "Ask host for window booth",
      "best_for": ["first_date", "casual"],
      "confidence": 0.8,
      "mentions": 8,
      "source": "reddit"
    }
  ],

  "top_dishes": [
    {
      "item": "Grilled Octopus",
      "category": "appetizer",
      "must_try": true,
      "pro_tips": [
        "Perfect for sharing",
        "Pairs well with their white wine selection"
      ],
      "mentions": 15,
      "sentiment": 0.95
    },
    {
      "item": "Whole Grilled Branzino",
      "category": "entree",
      "must_try": true,
      "pro_tips": [
        "Ask server to debone it tableside",
        "Enough for two people"
      ],
      "mentions": 23,
      "sentiment": 0.92
    }
  ],

  "timing": {
    "best_times": [
      {"day": "Tuesday", "time": "19:00", "reason": "Less crowded, more intimate"},
      {"day": "Wednesday", "time": "18:30", "reason": "Early dinner, catch sunset"}
    ],
    "avoid_times": [
      {"day": "Friday", "time": "20:00", "reason": "Peak time, 90+ min wait"},
      {"day": "Saturday", "time": "19:30", "reason": "Very busy, rushed service"}
    ],
    "sweet_spot": "Tuesday-Thursday, 6:30-7:30pm",
    "reservation_difficulty": "moderate",
    "advance_booking_days": 7,
    "walk_in_friendly": false
  },

  "vibe": {
    "noise_level": "conversational",
    "lighting": "romantic/dim",
    "crowd_type": ["couples", "young professionals"],
    "date_score": 9.2,
    "first_date": true,
    "anniversary": true,
    "vibe_tags": ["romantic", "waterfront", "upscale-casual"]
  },

  "insider_tips": [
    {
      "tip": "Make reservation for sunset time (around 7pm in summer) for best views",
      "category": "timing",
      "upvotes": 45
    },
    {
      "tip": "Bring a light jacket - patio can get breezy near the water",
      "category": "preparation",
      "upvotes": 32
    },
    {
      "tip": "Order the daily catch - always fresh and well-prepared",
      "category": "ordering",
      "upvotes": 28
    }
  ],

  "warnings": [
    "Can be loud on weekends",
    "Patio closes in bad weather",
    "Credit cards only, no cash"
  ]
}
```

---

### Step 9: Trigger Intelligence Refresh

**API Call - Refresh Intelligence:**
```bash
curl -X POST http://localhost:8000/api/venues/CELESTINE_ID/intelligence/refresh \
  -H "Authorization: Bearer TOKEN"

# Response:
{
  "message": "Intelligence gathering started",
  "job_id": "abc-123-def-456",
  "venue_id": "..."
}
```

**Behind the Scenes (Celery Task):**
```
1. Reddit Agent searches:
   - r/AskNYC for "Celestine DUMBO"
   - r/FoodNYC for "Celestine restaurant"
   - Finds 15 relevant posts and comments

2. Review Agent fetches:
   - Google Places reviews (23 reviews)
   - Sentiment analysis

3. TikTok Agent searches:
   - Finds 5 videos (placeholder)

4. Claude AI Synthesis:
   - Combines all data sources
   - Resolves conflicts
   - Extracts actionable insights
   - Generates confidence scores

5. Database Update:
   - Saves structured intelligence
   - Updates trending score
   - Sets last_updated timestamp
```

---

### Step 10: WebSocket Real-Time Updates

**Connect to WebSocket:**
```javascript
// Frontend establishes WebSocket connection
const ws = new WebSocket(`ws://localhost:8000/ws/session/${sessionId}?token=${token}`);

ws.onopen = () => {
  console.log('Connected to session');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);

  // Example messages:
  // {"type": "user_joined", "user_id": "jordan-id"}
  // {"type": "vote_update", "user_id": "alex-id", "venue_id": "lilia-id", "vote": 2}
  // {"type": "active_users", "users": ["alex-id", "jordan-id"]}
};

// Send a vote
ws.send(JSON.stringify({
  type: 'vote',
  venue_id: 'celestine-id',
  vote: 2,
  comment: 'Love the waterfront views!'
}));
```

**Real-Time Flow:**
```
Alex Browser                    Server                      Jordan Browser
     |                            |                                |
     |--- vote (Love Celestine) ->|                                |
     |                            |--- broadcast vote_update ----->|
     |                            |                                |✓ Updates UI
     |                            |<-- vote (Like Celestine) ------|
     |<--- broadcast vote_update -|                                |
     |✓ Updates UI                |                                |
```

---

### Step 11: View API Documentation

**URL**: http://localhost:8000/docs

**Interactive Swagger UI showing:**

```
📁 users
  POST   /api/users/register
  POST   /api/users/login
  GET    /api/users/me
  POST   /api/users/me/locations
  PUT    /api/users/me/preferences

📁 venues
  GET    /api/venues
  GET    /api/venues/trending
  GET    /api/venues/{venue_id}
  POST   /api/venues
  GET    /api/venues/{venue_id}/intelligence
  POST   /api/venues/{venue_id}/intelligence/refresh
  GET    /api/venues/nearby

📁 sessions
  POST   /api/sessions
  GET    /api/sessions/{session_id}
  POST   /api/sessions/join
  POST   /api/sessions/{session_id}/venues
  POST   /api/sessions/{session_id}/votes
  GET    /api/sessions/{session_id}/votes
  GET    /api/sessions/{session_id}/optimal-location

📁 collaboration
  WS     /ws/session/{session_id}
```

**Try it out:**
1. Click "Authorize" button
2. Enter: `Bearer YOUR_JWT_TOKEN`
3. Try any endpoint interactively!

---

## 🎯 Key Features Demonstrated

### ✅ Collaborative Planning
- [x] Multi-user sessions with invite codes
- [x] Real-time voting (Veto/Neutral/Like/Love)
- [x] Vote aggregation and scoring
- [x] Active user tracking

### ✅ Deep Intelligence
- [x] Reddit community insights
- [x] Google Reviews sentiment
- [x] Claude AI synthesis
- [x] Structured data (seating, dishes, timing, vibe)
- [x] Confidence scores and source attribution

### ✅ Smart Features
- [x] Location-based venue search
- [x] Optimal meeting point calculation
- [x] Fair venue recommendations (equal travel time)
- [x] Preference merging (dietary restrictions, budget, vibes)

### ✅ Modern Tech Stack
- [x] FastAPI backend with async/await
- [x] PostgreSQL for data persistence
- [x] Redis for caching and sessions
- [x] Celery for background jobs
- [x] WebSocket for real-time updates
- [x] React + TypeScript frontend
- [x] Tailwind CSS for styling
- [x] Zustand for state management

---

## 📊 Architecture Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   React App     │◄───────►│   FastAPI       │
│  (Port 3000)    │  HTTP   │  (Port 8000)    │
└─────────────────┘         └────────┬────────┘
         │                           │
         │ WebSocket                 │ CRUD
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│   WebSocket     │         │   PostgreSQL    │
│   Manager       │         │  (Port 5432)    │
└─────────────────┘         └─────────────────┘
                                     ▲
         ┌───────────────────────────┤
         │                           │
         ▼                           │
┌─────────────────┐         ┌───────┴─────────┐
│   Celery        │◄───────►│     Redis       │
│   Worker        │  Jobs   │  (Port 6379)    │
└────────┬────────┘         └─────────────────┘
         │
         │ Runs Intelligence Agents
         │
         ▼
┌─────────────────────────────────────────────┐
│        Intelligence Orchestrator            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Reddit  │  │ Reviews  │  │ TikTok   │  │
│  │  Agent   │  │  Agent   │  │  Agent   │  │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  │
│        │             │             │        │
│        └─────────────┴─────────────┘        │
│                      │                      │
│                      ▼                      │
│            ┌──────────────────┐             │
│            │   Claude AI      │             │
│            │   Synthesis      │             │
│            └──────────────────┘             │
└─────────────────────────────────────────────┘
```

---

## 🎥 Video Walkthrough Script

**[0:00-0:30] Introduction**
- "Welcome to Date Concierge - the collaborative date planning app"
- "It helps couples plan perfect dates using AI-powered venue intelligence"

**[0:30-1:00] Registration**
- "Let's start by creating an account"
- Shows registration form
- "Instantly logged in with JWT authentication"

**[1:00-1:30] Create Session**
- "Click Create New Session"
- "Name it 'Saturday Night Date'"
- "Get a unique invite code to share"

**[1:30-2:00] Join Session**
- "Open in another browser as partner"
- "Enter invite code"
- "Now both users are in the same session!"

**[2:00-3:00] Search and Suggest**
- "Browse NYC restaurants"
- "We have 15 seeded venues across neighborhoods"
- "Suggest Lilia and Celestine"

**[3:00-4:00] Collaborative Voting**
- "Both users vote simultaneously"
- "Veto, Neutral, Like, or Love"
- "Watch scores update in real-time via WebSocket!"

**[4:00-5:30] Venue Intelligence**
- "Click on Celestine to see deep insights"
- "Where to sit: 'Patio table for best views'"
- "What to order: 'Grilled Octopus - must try!'"
- "When to go: 'Tuesday-Thursday 6:30-7:30pm'"
- "All from Reddit, reviews, and AI synthesis"

**[5:30-6:00] Conclusion**
- "That's Date Concierge!"
- "Collaborative, intelligent, and fun"
- "Perfect for planning your next date night"

---

## 🐛 Troubleshooting

### Database not initialized?
```bash
docker-compose exec backend python -m app.database
docker-compose exec backend python -m app.seed_data
```

### WebSocket not connecting?
- Check that backend is running on port 8000
- Verify token is valid
- Check browser console for errors

### Intelligence not working?
- Add ANTHROPIC_API_KEY to .env
- Restart celery worker: `docker-compose restart celery_worker`
- Check Celery Flower at http://localhost:5555

### Frontend not starting?
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

---

## 🚀 Next Steps

1. **Add More Venues**: Expand beyond NYC
2. **Itinerary Builder**: Create full date itineraries
3. **Reservation Integration**: Book via Resy/OpenTable APIs
4. **Map View**: Mapbox integration for visual venue selection
5. **Mobile App**: React Native version
6. **Social Sharing**: Share completed itineraries
7. **ML Recommendations**: Learn user preferences over time

---

## 📝 License

MIT License - Built with ❤️ for better dates
