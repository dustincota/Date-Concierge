"""
Review scraping agent for Google Reviews, Yelp, etc.
"""

from typing import List, Dict, Any
from app.agents.base import IntelligenceAgent
from app.config import settings
import httpx


class ReviewAgent(IntelligenceAgent):
    """
    Scrapes and analyzes reviews from multiple platforms.

    Note: For production, use proper APIs or scraping services.
    This is a simplified version using Google Places API.
    """

    source_name = "reviews"

    async def search(self, venue_name: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch reviews for a venue.

        For now, this is a placeholder that would integrate with:
        - Google Places API (reviews)
        - Yelp API
        - Resy/OpenTable scraping
        """
        reviews = []

        # If Google Places API key is available, fetch reviews
        if settings.GOOGLE_PLACES_API_KEY:
            try:
                reviews = await self._fetch_google_reviews(venue_name, location)
            except Exception as e:
                print(f"Error fetching Google reviews: {e}")

        return reviews

    async def _fetch_google_reviews(
        self, venue_name: str, location: str
    ) -> List[Dict[str, Any]]:
        """Fetch reviews from Google Places API."""
        # First, find the place ID
        async with httpx.AsyncClient() as client:
            # Find place
            find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            find_params = {
                "input": f"{venue_name} {location}",
                "inputtype": "textquery",
                "fields": "place_id,name",
                "key": settings.GOOGLE_PLACES_API_KEY,
            }

            find_response = await client.get(find_url, params=find_params)
            find_data = find_response.json()

            if not find_data.get("candidates"):
                return []

            place_id = find_data["candidates"][0]["place_id"]

            # Get place details with reviews
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "name,rating,reviews,user_ratings_total",
                "key": settings.GOOGLE_PLACES_API_KEY,
            }

            details_response = await client.get(details_url, params=details_params)
            details_data = details_response.json()

            if "result" not in details_data:
                return []

            result = details_data["result"]
            reviews = result.get("reviews", [])

            # Format reviews
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append(
                    {
                        "author": review.get("author_name"),
                        "rating": review.get("rating"),
                        "text": review.get("text"),
                        "time": review.get("time"),
                        "source": "Google",
                    }
                )

            return formatted_reviews

    async def extract_insights(
        self, venue_name: str, raw_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze reviews to extract insights."""
        if not self.llm_client or not raw_data:
            return {}

        # Combine review texts
        combined_reviews = "\n\n".join(
            [
                f"★{r.get('rating', 0)}/5 - {r.get('text', '')[:500]}"
                for r in raw_data[:20]
            ]
        )

        prompt = f"""Analyze these reviews for "{venue_name}" and extract insights.

Reviews:
{combined_reviews}

Extract and return as JSON:

{{
  "overall_sentiment": 0.85,
  "praised_aspects": [
    {{"aspect": "food quality", "mentions": 15}},
    {{"aspect": "service", "mentions": 12}}
  ],
  "complaints": [
    {{"issue": "slow service", "mentions": 3}},
    {{"issue": "noisy", "mentions": 5}}
  ],
  "dish_mentions": [
    {{
      "dish": "specific dish name",
      "positive": 10,
      "negative": 1,
      "sentiment": 0.9
    }}
  ],
  "date_mentions": {{
    "romantic_mentions": 5,
    "anniversary_suitable": true,
    "first_date_feedback": "positive/mixed/negative"
  }},
  "service_notes": ["quick seating", "attentive staff"],
  "value_assessment": "expensive but worth it/overpriced/good value"
}}

Be specific and data-driven."""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            return self._parse_llm_response(response_text)

        except Exception as e:
            print(f"Error extracting review insights: {e}")
            return {}
