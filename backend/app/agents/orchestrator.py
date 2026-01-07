"""
Intelligence orchestrator - coordinates all agents to build complete venue intelligence.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import anthropic

from app.agents.reddit_agent import RedditAgent
from app.agents.review_agent import ReviewAgent
from app.agents.tiktok_agent import TikTokAgent
from app.models.venue import Venue
from app.config import settings


class IntelligenceOrchestrator:
    """
    Coordinates all intelligence agents to gather and synthesize venue data.
    """

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.agents = {
            "reddit": RedditAgent(),
            "reviews": ReviewAgent(),
            "tiktok": TikTokAgent(),
        }

        self.llm_client = None
        if settings.ANTHROPIC_API_KEY:
            self.llm_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def gather_intelligence(self, venue: Venue) -> Dict[str, Any]:
        """
        Run all agents in parallel to gather venue intelligence,
        then synthesize into unified intelligence package.

        Args:
            venue: Venue model instance

        Returns:
            Complete intelligence data ready for database storage
        """
        location = f"{venue.neighborhood}, {venue.city}" if venue.neighborhood else venue.city

        # Run all agents concurrently
        tasks = []
        for name, agent in self.agents.items():
            tasks.append(agent.run(venue.name, location))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        combined_data = {}
        for name, result in zip(self.agents.keys(), results):
            if not isinstance(result, Exception) and result.get("success"):
                combined_data[name] = result

        # Synthesize into final intelligence
        intelligence = await self._synthesize_intelligence(venue, combined_data)

        return intelligence

    async def _synthesize_intelligence(
        self, venue: Venue, source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Claude to synthesize all source data into unified, actionable intelligence.

        Args:
            venue: Venue model instance
            source_data: Dictionary of data from each agent

        Returns:
            Unified intelligence dictionary
        """
        if not self.llm_client:
            # Return basic structure without AI synthesis
            return self._basic_synthesis(source_data)

        # Prepare source data for Claude
        reddit_insights = source_data.get("reddit", {}).get("insights", {})
        review_insights = source_data.get("reviews", {}).get("insights", {})
        tiktok_insights = source_data.get("tiktok", {}).get("insights", {})

        prompt = f"""You are synthesizing venue intelligence for "{venue.name}" in {venue.neighborhood}.

Data from multiple sources:

REDDIT INSIGHTS:
{self._format_json(reddit_insights)}

REVIEW INSIGHTS:
{self._format_json(review_insights)}

TIKTOK INSIGHTS:
{self._format_json(tiktok_insights)}

Create a unified intelligence report with:

1. **SEATING RECOMMENDATIONS** (ranked by confidence):
   - Specific spots with how to request them
   - Best for what occasion

2. **MUST-ORDER DISHES**:
   - With pro tips and pairings
   - What to avoid

3. **TIMING INSIGHTS**:
   - Best times to visit
   - Reservation difficulty
   - Typical wait times

4. **COMMUTE TIPS**:
   - Transit directions
   - Parking situation
   - Rideshare tips

5. **VIBE CHECK**:
   - Noise level, lighting, crowd type
   - Date suitability scores
   - Dress code

6. **INSIDER TIPS** (top 5):
   - Actionable, specific tips

7. **WARNINGS**:
   - Important things to know

8. **TRENDING SCORE** (0-10):
   - How hot/viral is this place

Resolve conflicts between sources by:
- Prioritizing recency
- Weighing consensus (multiple sources agreeing)
- Favoring specific details over vague mentions

Return as JSON matching this exact structure:

{{
  "seating_recommendations": [
    {{
      "spot": "string",
      "why": "string",
      "how_to_request": "string",
      "best_for": ["first_date", "anniversary"],
      "source": "reddit",
      "mentions": 3,
      "confidence": 0.8
    }}
  ],
  "dish_recommendations": [
    {{
      "item": "string",
      "category": "entree",
      "must_try": true,
      "pro_tips": ["tip1"],
      "pairings": ["wine"],
      "mentions": 5,
      "sentiment": 0.9,
      "sources": [{{"platform": "reddit", "mentions": 3}}]
    }}
  ],
  "timing_insights": {{
    "best_times": [{{"day": "Tuesday", "time": "19:00", "reason": "quiet"}}],
    "avoid_times": [{{"day": "Friday", "time": "20:00", "reason": "2hr wait"}}],
    "sweet_spot": "Tuesday-Thursday, 7-8pm",
    "reservation_difficulty": "hard",
    "advance_booking_days": 14,
    "walk_in_friendly": false
  }},
  "commute_insights": {{
    "nearest_subway": "F/G at Bergen St",
    "subway_walk_minutes": 5,
    "parking_situation": "street parking difficult",
    "rideshare_dropoff": "corner of Smith and Pacific"
  }},
  "vibe_check": {{
    "noise_level": "conversational",
    "lighting": "dim/romantic",
    "music": "soft background",
    "crowd_type": ["young professionals", "couples"],
    "age_range": "25-40",
    "dress_code": "smart casual",
    "date_score": 9.0,
    "first_date": true,
    "anniversary": true,
    "vibe_tags": ["romantic", "intimate", "upscale"]
  }},
  "insider_tips": [
    {{
      "tip": "specific actionable tip",
      "category": "ordering",
      "source": "reddit",
      "upvotes": 15
    }}
  ],
  "warnings": ["cash only", "loud music after 9pm"],
  "trending_score": 7.5,
  "intelligence_score": 0.85,
  "date_score": 9.0
}}

Be specific and actionable. Only include data that actually appears in the sources."""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON from response
            import json
            import re

            response_text = response.content[0].text
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)

            intelligence_data = json.loads(response_text)

            # Add metadata
            intelligence_data.update({
                "last_updated": datetime.utcnow(),
                "reddit_data": source_data.get("reddit", {}).get("raw_data", []),
                "google_reviews_summary": source_data.get("reviews", {}).get("insights", {}),
                "tiktok_data": source_data.get("tiktok", {}).get("raw_data", []),
            })

            return intelligence_data

        except Exception as e:
            print(f"Error synthesizing intelligence: {e}")
            return self._basic_synthesis(source_data)

    def _basic_synthesis(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic synthesis without AI when Claude API is unavailable.

        Args:
            source_data: Raw source data

        Returns:
            Basic intelligence structure
        """
        reddit_insights = source_data.get("reddit", {}).get("insights", {})
        review_insights = source_data.get("reviews", {}).get("insights", {})

        return {
            "seating_recommendations": reddit_insights.get("seating", []),
            "dish_recommendations": reddit_insights.get("dishes", []),
            "timing_insights": reddit_insights.get("timing", {}),
            "commute_insights": {},
            "vibe_check": reddit_insights.get("vibe", {}),
            "insider_tips": reddit_insights.get("tips", []),
            "warnings": reddit_insights.get("warnings", []),
            "trending_score": 5.0,
            "intelligence_score": 0.5,
            "date_score": 7.0,
            "last_updated": datetime.utcnow(),
            "reddit_data": source_data.get("reddit", {}).get("raw_data", []),
            "google_reviews_summary": review_insights,
            "tiktok_data": [],
        }

    @staticmethod
    def _format_json(data: Any) -> str:
        """Format data as pretty JSON string."""
        import json
        return json.dumps(data, indent=2) if data else "{}"

    async def close(self):
        """Close all agent connections."""
        if "reddit" in self.agents:
            await self.agents["reddit"].close()
