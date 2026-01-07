#!/bin/bash

# Date Concierge - Quick API Demo Script
# This demonstrates the core features via API calls

set -e

API_URL="http://localhost:8000/api"
echo "🎬 Date Concierge API Demo"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Register User 1 (Alex)
echo -e "${BLUE}Step 1: Registering Alex...${NC}"
ALEX_RESPONSE=$(curl -s -X POST "$API_URL/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alex@demo.com",
    "password": "demo123",
    "name": "Alex"
  }')

ALEX_TOKEN=$(echo $ALEX_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}✓ Alex registered and logged in${NC}"
echo "Token: ${ALEX_TOKEN:0:20}..."
echo ""

# Step 2: Register User 2 (Jordan)
echo -e "${BLUE}Step 2: Registering Jordan...${NC}"
JORDAN_RESPONSE=$(curl -s -X POST "$API_URL/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jordan@demo.com",
    "password": "demo123",
    "name": "Jordan"
  }')

JORDAN_TOKEN=$(echo $JORDAN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}✓ Jordan registered and logged in${NC}"
echo "Token: ${JORDAN_TOKEN:0:20}..."
echo ""

# Step 3: Create Planning Session
echo -e "${BLUE}Step 3: Alex creates a planning session...${NC}"
SESSION_RESPONSE=$(curl -s -X POST "$API_URL/sessions" \
  -H "Authorization: Bearer $ALEX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Saturday Night Date",
    "target_date": "2026-02-14"
  }')

SESSION_ID=$(echo $SESSION_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
INVITE_CODE=$(echo $SESSION_RESPONSE | grep -o '"invite_code":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}✓ Session created${NC}"
echo "Session ID: $SESSION_ID"
echo "Invite Code: $INVITE_CODE"
echo ""

# Step 4: Jordan joins session
echo -e "${BLUE}Step 4: Jordan joins with invite code...${NC}"
curl -s -X POST "$API_URL/sessions/join" \
  -H "Authorization: Bearer $JORDAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"invite_code\": \"$INVITE_CODE\"
  }" > /dev/null

echo -e "${GREEN}✓ Jordan joined the session${NC}"
echo ""

# Step 5: Search for venues
echo -e "${BLUE}Step 5: Searching for venues in Williamsburg...${NC}"
VENUES=$(curl -s -X GET "$API_URL/venues?neighborhood=Williamsburg" \
  -H "Authorization: Bearer $ALEX_TOKEN")

VENUE_1_ID=$(echo $VENUES | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
VENUE_1_NAME=$(echo $VENUES | grep -o '"name":"[^"]*' | head -1 | cut -d'"' -f4)
echo -e "${GREEN}✓ Found venues${NC}"
echo "First venue: $VENUE_1_NAME (ID: $VENUE_1_ID)"
echo ""

# Step 6: Suggest venue
echo -e "${BLUE}Step 6: Alex suggests $VENUE_1_NAME...${NC}"
curl -s -X POST "$API_URL/sessions/$SESSION_ID/venues" \
  -H "Authorization: Bearer $ALEX_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"venue_id\": \"$VENUE_1_ID\"
  }" > /dev/null

echo -e "${GREEN}✓ Venue suggested${NC}"
echo ""

# Step 7: Vote on venue
echo -e "${BLUE}Step 7: Collaborative voting...${NC}"

# Alex votes Love (2)
curl -s -X POST "$API_URL/sessions/$SESSION_ID/votes" \
  -H "Authorization: Bearer $ALEX_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"venue_id\": \"$VENUE_1_ID\",
    \"vote\": 2,
    \"comment\": \"Perfect for a romantic dinner!\"
  }" > /dev/null

echo -e "${GREEN}✓ Alex voted: ❤️ Love${NC}"

# Jordan votes Like (1)
curl -s -X POST "$API_URL/sessions/$SESSION_ID/votes" \
  -H "Authorization: Bearer $JORDAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"venue_id\": \"$VENUE_1_ID\",
    \"vote\": 1,
    \"comment\": \"Sounds good to me!\"
  }" > /dev/null

echo -e "${GREEN}✓ Jordan voted: 👍 Like${NC}"
echo ""

# Step 8: Get vote results
echo -e "${BLUE}Step 8: Getting vote results...${NC}"
VOTES=$(curl -s -X GET "$API_URL/sessions/$SESSION_ID/votes" \
  -H "Authorization: Bearer $ALEX_TOKEN")

echo "$VOTES" | python3 -m json.tool 2>/dev/null || echo "$VOTES"
echo ""

# Step 9: Get venue intelligence (if available)
echo -e "${BLUE}Step 9: Checking for venue intelligence...${NC}"
INTEL=$(curl -s -X GET "$API_URL/venues/$VENUE_1_ID/intelligence" \
  -H "Authorization: Bearer $ALEX_TOKEN" 2>/dev/null)

if echo "$INTEL" | grep -q "intelligence_score"; then
  echo -e "${GREEN}✓ Intelligence data available!${NC}"
  echo "$INTEL" | python3 -m json.tool 2>/dev/null || echo "$INTEL"
else
  echo -e "${YELLOW}⚠ No intelligence data yet. Trigger refresh:${NC}"
  echo "curl -X POST $API_URL/venues/$VENUE_1_ID/intelligence/refresh \\"
  echo "  -H \"Authorization: Bearer $ALEX_TOKEN\""
fi
echo ""

# Summary
echo -e "${GREEN}=========================="
echo "✅ Demo Complete!"
echo "==========================${NC}"
echo ""
echo "What we did:"
echo "  1. ✓ Registered 2 users (Alex & Jordan)"
echo "  2. ✓ Created a planning session"
echo "  3. ✓ Jordan joined via invite code"
echo "  4. ✓ Searched for venues"
echo "  5. ✓ Suggested a venue"
echo "  6. ✓ Both users voted"
echo "  7. ✓ Got collaborative results"
echo ""
echo "Next steps:"
echo "  - Open http://localhost:3000 in your browser"
echo "  - Login as alex@demo.com or jordan@demo.com (password: demo123)"
echo "  - See the session at http://localhost:3000/session/$SESSION_ID"
echo "  - View API docs at http://localhost:8000/docs"
echo ""
echo "Session Details:"
echo "  ID: $SESSION_ID"
echo "  Invite Code: $INVITE_CODE"
echo "  Suggested Venue: $VENUE_1_NAME"
echo ""
