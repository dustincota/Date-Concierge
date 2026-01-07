"""
Reddit intelligence agent for gathering venue insights from Reddit discussions.
"""

import asyncpraw
from typing import List, Dict, Any
import asyncio
from app.agents.base import IntelligenceAgent
from app.config import settings


class RedditAgent(IntelligenceAgent):
    """
    Scrapes Reddit for venue recommendations and discussions.

    Key subreddits:
    - r/AskNYC - general recommendations
    - r/FoodNYC - restaurant specific
    - r/Brooklyn - neighborhood specific
    - r/nyc - broader discussions
    """

    source_name = "reddit"

    SUBREDDITS = [
        "AskNYC",
        "FoodNYC",
        "Brooklyn",
        "nyc",
        "restaurants",
    ]

    SEARCH_TEMPLATES = [
        "{venue_name}",
        "{venue_name} {neighborhood}",
        "{venue_name} review",
        "{venue_name} date",
        "best seat {venue_name}",
        "what to order {venue_name}",
    ]

    def __init__(self):
        """Initialize Reddit agent."""
        super().__init__()
        self.reddit = None

        # Initialize Reddit client if credentials available
        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            self.reddit = asyncpraw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT,
            )

    async def search(self, venue_name: str, location: str) -> List[Dict[str, Any]]:
        """Search Reddit for mentions of venue."""
        if not self.reddit:
            return []

        results = []
        neighborhood = location.split(",")[0].strip() if location else ""

        try:
            for subreddit_name in self.SUBREDDITS:
                subreddit = await self.reddit.subreddit(subreddit_name)

                # Try different search queries
                for template in self.SEARCH_TEMPLATES[:3]:  # Limit to avoid rate limits
                    query = template.format(
                        venue_name=venue_name, neighborhood=neighborhood
                    )

                    try:
                        async for submission in subreddit.search(query, limit=5):
                            # Load submission comments
                            await submission.load()
                            await submission.comments.replace_more(limit=0)

                            comments = []
                            for comment in submission.comments[:10]:
                                comments.append(
                                    {
                                        "body": comment.body,
                                        "score": comment.score,
                                        "author": str(comment.author),
                                    }
                                )

                            results.append(
                                {
                                    "subreddit": subreddit_name,
                                    "title": submission.title,
                                    "selftext": submission.selftext,
                                    "url": f"https://reddit.com{submission.permalink}",
                                    "score": submission.score,
                                    "num_comments": submission.num_comments,
                                    "created_utc": submission.created_utc,
                                    "comments": comments,
                                }
                            )

                        # Rate limiting
                        await asyncio.sleep(self.rate_limit_delay)

                    except Exception as e:
                        print(f"Error searching {subreddit_name}: {e}")
                        continue

        except Exception as e:
            print(f"Reddit search error: {e}")

        return results

    async def extract_insights(
        self, venue_name: str, raw_data: List[Dict]
    ) -> Dict[str, Any]:
        """Use Claude to extract structured insights from Reddit discussions."""
        if not self.llm_client or not raw_data:
            return {}

        # Prepare text for LLM (limit to avoid token limits)
        combined_text = ""
        for post in raw_data[:15]:
            combined_text += f"\n\n--- Post: {post['title']} (👍 {post['score']}) ---\n"
            combined_text += post["selftext"][:800]
            for comment in post["comments"][:5]:
                combined_text += f"\n> Comment (👍 {comment['score']}): {comment['body'][:400]}"

        prompt = f"""Analyze these Reddit discussions about "{venue_name}" and extract actionable insights.

Reddit discussions:
{combined_text}

Extract and return as JSON:

{{
  "seating": [
    {{
      "spot": "specific location like 'back corner booth' or 'bar seats'",
      "why": "reason this spot is recommended",
      "how_to_request": "how to ask for this spot",
      "mentions": 2,
      "confidence": 0.8
    }}
  ],
  "dishes": [
    {{
      "item": "dish name",
      "category": "appetizer/entree/dessert/drink",
      "must_try": true,
      "pro_tips": ["tip 1", "tip 2"],
      "mentions": 5,
      "sentiment": 0.9
    }}
  ],
  "timing": {{
    "best_times": ["Tuesday 7pm", "Wednesday evening"],
    "avoid_times": ["Friday 8pm - 2 hour wait"],
    "reservation_difficulty": "hard/moderate/easy",
    "walk_in_friendly": false
  }},
  "vibe": {{
    "noise_level": "quiet/conversational/loud",
    "crowd_type": ["young professionals", "foodies"],
    "date_suitable": true,
    "romantic": true
  }},
  "tips": [
    {{
      "tip": "specific actionable tip",
      "category": "ordering/timing/seating/service",
      "upvotes": 15
    }}
  ],
  "warnings": ["cash only", "no reservations", "loud music"]
}}

Only include items that are explicitly mentioned in the discussions. Be specific and quote-worthy."""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON from response
            response_text = response.content[0].text
            return self._parse_llm_response(response_text)

        except Exception as e:
            print(f"Error extracting insights: {e}")
            return {}

    async def close(self):
        """Close the Reddit client."""
        if self.reddit:
            await self.reddit.close()
