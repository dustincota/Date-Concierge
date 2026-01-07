"""
Base intelligence agent for venue data gathering.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import anthropic
from app.config import settings


class IntelligenceAgent(ABC):
    """Base class for all intelligence gathering agents."""

    def __init__(self):
        """Initialize the agent."""
        self.llm_client = None
        if settings.ANTHROPIC_API_KEY:
            self.llm_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    @abstractmethod
    async def search(self, venue_name: str, location: str) -> List[Dict[str, Any]]:
        """
        Search for content about a venue.

        Args:
            venue_name: Name of the venue
            location: Location/neighborhood

        Returns:
            List of raw data dictionaries
        """
        pass

    @abstractmethod
    async def extract_insights(
        self, venue_name: str, raw_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Use LLM to extract structured insights from raw data.

        Args:
            venue_name: Name of the venue
            raw_data: Raw data collected from search

        Returns:
            Dictionary of structured insights
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of this data source."""
        pass

    @property
    def rate_limit_delay(self) -> float:
        """Seconds to wait between requests."""
        return 1.0

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response text as JSON.

        Args:
            response_text: Response text from LLM

        Returns:
            Parsed dictionary
        """
        import json
        import re

        # Try to extract JSON from response
        # Sometimes Claude wraps JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If parsing fails, return empty structure
            return {}

    async def run(
        self, venue_name: str, location: str
    ) -> Dict[str, Any]:
        """
        Run the complete intelligence gathering pipeline.

        Args:
            venue_name: Name of the venue
            location: Location/neighborhood

        Returns:
            Dictionary with raw data and insights
        """
        try:
            # Search for raw data
            raw_data = await self.search(venue_name, location)

            # Extract insights using LLM
            if raw_data and self.llm_client:
                insights = await self.extract_insights(venue_name, raw_data)
            else:
                insights = {}

            return {
                "source": self.source_name,
                "raw_data": raw_data,
                "insights": insights,
                "success": True,
                "error": None,
            }

        except Exception as e:
            return {
                "source": self.source_name,
                "raw_data": [],
                "insights": {},
                "success": False,
                "error": str(e),
            }
