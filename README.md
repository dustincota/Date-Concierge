# Date Concierge

A collaborative date planning application that helps 2+ people plan perfect date experiences together. Features deep venue intelligence scraped from social media, reviews, and community recommendations.

## Key Features

### 🤝 Collaborative Planning
- Multi-user sessions with real-time collaboration
- Shared voting on venue options
- Location-aware recommendations that are fair to all participants
- Automatic preference merging (dietary restrictions, budgets, vibes)

### 🧠 Deep Venue Intelligence
- **Where to Sit**: Specific seating recommendations from real users
- **What to Order**: Must-try dishes and what to avoid
- **When to Go**: Best times, reservation difficulty, wait times
- **How to Get There**: Transit, driving, parking, and rideshare tips
- **Vibe Check**: Noise level, lighting, crowd type, date suitability

### 📊 Data Sources
- Reddit discussions (r/AskNYC, r/FoodNYC, etc.)
- TikTok videos and trending spots
- Google Reviews, Resy, OpenTable
- Instagram mentions
- Synthesized by Claude AI for actionable insights

### 🗺️ Smart Location Features
- Finds optimal meeting points between participants
- Filters venues by travel time fairness
- Multi-modal routing (transit, walking, driving)
- Weather-aware planning

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery
- **AI**: Anthropic Claude API
- **Scraping**: Playwright, BeautifulSoup, asyncpraw

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand/Redux Toolkit
- **Maps**: Mapbox GL JS
- **Real-time**: WebSockets

## Getting Started

### Prerequisites
- Docker and Docker Compose
- (Optional) API keys for enhanced features:
  - Anthropic API key (for intelligence extraction)
  - Reddit API credentials (for Reddit intelligence)
  - Google Maps API key (for enhanced routing)
  - Mapbox access token (for frontend maps)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Date-Concierge
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Celery Flower (monitoring): http://localhost:5555

### Environment Variables

Required variables (see `.env.example`):

```bash
# Required for intelligence features
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional but recommended
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MAPBOX_ACCESS_TOKEN=your-mapbox-token
```

## API Documentation

### Authentication

**Register**
```http
POST /api/users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Login**
```http
POST /api/users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Planning Sessions

**Create Session**
```http
POST /api/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Saturday Night Date",
  "target_date": "2026-02-14",
  "participant_emails": ["partner@example.com"]
}
```

**Join Session**
```http
POST /api/sessions/join
Authorization: Bearer <token>
Content-Type: application/json

{
  "invite_code": "ABC12345",
  "location_id": "<user-location-id>",
  "preferences": {
    "budget_min": 2,
    "budget_max": 3,
    "cuisines_loved": ["Italian", "Japanese"],
    "dietary_restrictions": ["vegetarian"],
    "vibes": ["romantic", "cozy"]
  }
}
```

**Vote on Venue**
```http
POST /api/sessions/{session_id}/votes
Authorization: Bearer <token>
Content-Type: application/json

{
  "venue_id": "<venue-id>",
  "vote": 2,
  "comment": "Perfect for a date night!"
}
```

Vote values:
- `-1`: Veto (absolutely not)
- `0`: Neutral
- `1`: Like
- `2`: Love

**Get Optimal Meeting Point**
```http
GET /api/sessions/{session_id}/optimal-location
Authorization: Bearer <token>
```

### Venue Intelligence

**Get Venue Intelligence**
```http
GET /api/venues/{venue_id}/intelligence
Authorization: Bearer <token>
```

Response includes:
- Seating recommendations with confidence scores
- Must-order dishes with pro tips
- Timing insights (best/worst times)
- Commute information
- Vibe check (noise, lighting, crowd)
- Insider tips
- Trending score

**Trigger Intelligence Refresh**
```http
POST /api/venues/{venue_id}/intelligence/refresh
Authorization: Bearer <token>
```

## Architecture

### Database Models

- **Users**: Authentication and profile
- **User Locations**: Multiple locations per user (home, work, etc.)
- **User Preferences**: Default date preferences
- **Planning Sessions**: Collaborative planning sessions
- **Session Participants**: Many-to-many session membership
- **Venues**: Restaurant/venue data
- **Venue Intelligence**: AI-extracted insights
- **Venue Votes**: User votes on venues
- **Itineraries**: Final date plans
- **Reservations**: Restaurant bookings

### Intelligence Pipeline

1. **Trigger**: Manual refresh or scheduled job
2. **Agents Run in Parallel**:
   - Reddit Agent: Scrapes discussions
   - TikTok Agent: Finds viral videos
   - Review Agent: Scrapes Google/Yelp/Resy
3. **Claude AI Synthesis**: Extracts structured insights
4. **Storage**: Cached in database
5. **Serving**: Real-time via API

### Real-time Collaboration

WebSocket endpoint: `/ws/session/{session_id}`

Events:
- `user_joined`: Participant joins
- `user_left`: Participant leaves
- `vote_update`: Vote cast/changed
- `new_suggestion`: Venue suggested
- `new_comment`: Comment added

## Development

### Running Locally (without Docker)

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Database**:
```bash
# Install PostgreSQL and create database
createdb date_concierge

# Run migrations
alembic upgrade head
```

**Celery Worker**:
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Project Structure

```
date-concierge/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # DB connection
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── weather.py       # Weather API
│   │   │   ├── geocoding.py     # Location services
│   │   │   ├── travel.py        # Travel time
│   │   │   └── location_optimizer.py
│   │   ├── agents/              # Intelligence agents
│   │   │   ├── reddit_agent.py
│   │   │   ├── tiktok_agent.py
│   │   │   ├── review_agent.py
│   │   │   └── orchestrator.py
│   │   └── tasks/               # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── collaborative/   # Session UI
│   │   │   ├── intelligence/    # Venue intelligence
│   │   │   └── common/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── stores/
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Database models
- [x] User authentication
- [x] Weather service
- [x] Geocoding and travel services
- [x] Location optimization

### Phase 2: Collaborative Planning ✅
- [x] Session creation and management
- [x] Participant preferences merging
- [x] Venue voting system
- [ ] Real-time WebSocket collaboration

### Phase 3: Intelligence Agents (In Progress)
- [ ] Reddit agent
- [ ] Review scraping
- [ ] TikTok agent
- [ ] Claude AI synthesis
- [ ] Background job scheduling

### Phase 4: Frontend
- [ ] React app setup
- [ ] Session UI components
- [ ] Intelligence display
- [ ] Mapbox integration
- [ ] Real-time updates

### Phase 5: Polish
- [ ] Reservation integration
- [ ] Itinerary export/sharing
- [ ] Push notifications
- [ ] Mobile responsiveness

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details

## Support

For questions or issues, please open a GitHub issue or contact the maintainers.

---

Built with ❤️ for better dates
