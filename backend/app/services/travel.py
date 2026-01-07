"""
Travel time and routing service.
"""

import httpx
from typing import Dict, Any, Optional, Tuple
from app.config import settings
from app.services.geocoding import GeocodingService


class TravelService:
    """Service for calculating travel times and routes."""

    GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
    GOOGLE_DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

    @classmethod
    async def get_travel_time(
        cls,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "transit",
        departure_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get travel time between two locations.

        Args:
            origin: (latitude, longitude) tuple for origin
            destination: (latitude, longitude) tuple for destination
            mode: Travel mode (driving, walking, transit, bicycling)
            departure_time: Optional departure time for transit

        Returns:
            Dictionary with travel information
        """
        if settings.GOOGLE_MAPS_API_KEY:
            return await cls._get_travel_time_google(
                origin, destination, mode, departure_time
            )

        # Fallback to simple distance-based estimate
        return cls._estimate_travel_time(origin, destination, mode)

    @classmethod
    async def _get_travel_time_google(
        cls,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str,
        departure_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get travel time using Google Maps API."""
        params = {
            "origins": f"{origin[0]},{origin[1]}",
            "destinations": f"{destination[0]},{destination[1]}",
            "mode": mode,
            "key": settings.GOOGLE_MAPS_API_KEY,
        }

        if departure_time:
            params["departure_time"] = departure_time

        async with httpx.AsyncClient() as client:
            response = await client.get(cls.GOOGLE_DISTANCE_MATRIX_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data["status"] != "OK":
            return cls._estimate_travel_time(origin, destination, mode)

        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return cls._estimate_travel_time(origin, destination, mode)

        return {
            "duration_minutes": element["duration"]["value"] // 60,
            "duration_text": element["duration"]["text"],
            "distance_miles": element["distance"]["value"] / 1609.34,
            "distance_text": element["distance"]["text"],
            "mode": mode,
        }

    @classmethod
    def _estimate_travel_time(
        cls,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str,
    ) -> Dict[str, Any]:
        """
        Estimate travel time based on distance and mode.

        Simple fallback when Google Maps API is not available.
        """
        distance = GeocodingService.calculate_distance(
            origin[0], origin[1], destination[0], destination[1]
        )

        # Estimate speeds (mph)
        speeds = {
            "walking": 3.0,
            "bicycling": 12.0,
            "transit": 20.0,
            "driving": 25.0,  # City driving
        }

        speed = speeds.get(mode, 20.0)
        duration_hours = distance / speed
        duration_minutes = int(duration_hours * 60)

        return {
            "duration_minutes": duration_minutes,
            "duration_text": f"{duration_minutes} mins",
            "distance_miles": round(distance, 1),
            "distance_text": f"{round(distance, 1)} mi",
            "mode": mode,
            "estimated": True,
        }

    @classmethod
    async def get_directions(
        cls,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "transit",
    ) -> Dict[str, Any]:
        """
        Get detailed directions between two locations.

        Args:
            origin: (latitude, longitude) tuple for origin
            destination: (latitude, longitude) tuple for destination
            mode: Travel mode

        Returns:
            Dictionary with route and step-by-step directions
        """
        if not settings.GOOGLE_MAPS_API_KEY:
            return {
                "error": "Directions API not available",
                "travel_time": await cls.get_travel_time(origin, destination, mode),
            }

        params = {
            "origin": f"{origin[0]},{origin[1]}",
            "destination": f"{destination[0]},{destination[1]}",
            "mode": mode,
            "key": settings.GOOGLE_MAPS_API_KEY,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(cls.GOOGLE_DIRECTIONS_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data["status"] != "OK" or not data["routes"]:
            return {
                "error": "No route found",
                "travel_time": await cls.get_travel_time(origin, destination, mode),
            }

        route = data["routes"][0]
        leg = route["legs"][0]

        steps = []
        for step in leg["steps"]:
            steps.append(
                {
                    "instruction": step["html_instructions"],
                    "distance": step["distance"]["text"],
                    "duration": step["duration"]["text"],
                    "travel_mode": step["travel_mode"],
                }
            )

        return {
            "duration_minutes": leg["duration"]["value"] // 60,
            "duration_text": leg["duration"]["text"],
            "distance_miles": leg["distance"]["value"] / 1609.34,
            "distance_text": leg["distance"]["text"],
            "steps": steps,
            "mode": mode,
        }

    @classmethod
    async def get_multi_destination_times(
        cls,
        origin: Tuple[float, float],
        destinations: list[Tuple[float, float]],
        mode: str = "transit",
    ) -> list[Dict[str, Any]]:
        """
        Get travel times from one origin to multiple destinations.

        Args:
            origin: (latitude, longitude) tuple for origin
            destinations: List of (latitude, longitude) tuples
            mode: Travel mode

        Returns:
            List of travel time dictionaries
        """
        results = []
        for dest in destinations:
            travel_time = await cls.get_travel_time(origin, dest, mode)
            results.append(travel_time)

        return results
