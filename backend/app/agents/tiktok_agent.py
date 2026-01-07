"""
TikTok intelligence agent for discovering trending venues.

Note: TikTok scraping is complex and may require:
- Playwright for JS rendering
- Unofficial APIs or RapidAPI
- Proxy rotation to avoid blocks

This is a simplified placeholder implementation.
"""

from typing import List, Dict, Any
from app.agents.base import IntelligenceAgent


class TikTokAgent(IntelligenceAgent):
    """
    Discovers TikTok content about venues.

    Looks for:
    - Restaurant reviews/tours
    - "What I ordered" videos
    - Date spot recommendations
    - Viral moments
    """

    source_name = "tiktok"

    async def search(self, venue_name: str, location: str) -> List[Dict[str, Any]]:
        """
        Search TikTok for venue content.

        Note: This is a placeholder. In production, you would:
        1. Use Playwright to scrape TikTok search results
        2. Use unofficial TikTok API via RapidAPI
        3. Use a scraping service like Apify or ScrapingBee

        For now, returns empty list to avoid blocking.
        """
        # Placeholder implementation
        # In production, use Playwright or TikTok API
        return []

    async def extract_insights(
        self, venue_name: str, raw_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze TikTok content for trends."""
        if not self.llm_client or not raw_data:
            return {}

        # Format TikTok data
        videos_text = "\n\n".join(
            [
                f"Video: {v.get('caption', '')} (👁️ {v.get('views', 0)} views)"
                for v in raw_data[:15]
            ]
        )

        prompt = f"""Analyze these TikTok videos about "{venue_name}":

{videos_text}

Extract and return as JSON:

{{
  "trending_score": 8.5,
  "viral_dishes": [
    {{"dish": "specific dish", "video_count": 5, "views": 100000}}
  ],
  "visual_highlights": [
    "beautiful plating",
    "waterfront views",
    "aesthetic interior"
  ],
  "creator_tips": [
    "ask for window seat at sunset",
    "go on weekdays to avoid crowds"
  ],
  "date_vibes": {{
    "romantic": true,
    "instagrammable": true,
    "trending_for_dates": true
  }},
  "recent_buzz": [
    "Featured in viral date night series",
    "Celebrity spotted here"
  ]
}}"""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            return self._parse_llm_response(response_text)

        except Exception as e:
            print(f"Error extracting TikTok insights: {e}")
            return {}
