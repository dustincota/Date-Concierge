"""
Geocoding service using Nominatim/OpenStreetMap and Google Maps.
"""

import httpx
from typing import Dict, Any, Optional, Tuple
from app.config import settings


class GeocodingService:
    """Service for geocoding addresses and calculating distances."""

    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    @classmethod
    async def geocode_address(cls, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to latitude/longitude.

        Args:
            address: Address string to geocode

        Returns:
            Dictionary with latitude, longitude, and formatted address
        """
        # Try Google Maps API if available
        if settings.GOOGLE_MAPS_API_KEY:
            return await cls._geocode_google(address)

        # Fallback to Nominatim
        return await cls._geocode_nominatim(address)

    @classmethod
    async def _geocode_nominatim(cls, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using Nominatim (OpenStreetMap)."""
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }

        headers = {
            "User-Agent": "DateConcierge/1.0",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{cls.NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        if not data:
            return None

        result = data[0]
        return {
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "formatted_address": result.get("display_name"),
            "neighborhood": result.get("address", {}).get("neighbourhood")
            or result.get("address", {}).get("suburb"),
            "city": result.get("address", {}).get("city")
            or result.get("address", {}).get("town"),
        }

    @classmethod
    async def _geocode_google(cls, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using Google Maps API."""
        params = {
            "address": address,
            "key": settings.GOOGLE_MAPS_API_KEY,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(cls.GOOGLE_GEOCODE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data["status"] != "OK" or not data["results"]:
            return None

        result = data["results"][0]
        location = result["geometry"]["location"]

        # Extract neighborhood and city from address components
        neighborhood = None
        city = None
        for component in result["address_components"]:
            if "neighborhood" in component["types"]:
                neighborhood = component["long_name"]
            if "locality" in component["types"]:
                city = component["long_name"]

        return {
            "latitude": location["lat"],
            "longitude": location["lng"],
            "formatted_address": result["formatted_address"],
            "neighborhood": neighborhood,
            "city": city,
        }

    @classmethod
    async def reverse_geocode(
        cls, latitude: float, longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to address.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Dictionary with address information
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
        }

        headers = {
            "User-Agent": "DateConcierge/1.0",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{cls.NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            return None

        return {
            "formatted_address": data.get("display_name"),
            "neighborhood": data.get("address", {}).get("neighbourhood")
            or data.get("address", {}).get("suburb"),
            "city": data.get("address", {}).get("city")
            or data.get("address", {}).get("town"),
        }

    @staticmethod
    def calculate_distance(
        lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1: First latitude
            lon1: First longitude
            lat2: Second latitude
            lon2: Second longitude

        Returns:
            Distance in miles
        """
        from math import radians, sin, cos, sqrt, atan2

        # Earth radius in miles
        R = 3959.0

        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance
