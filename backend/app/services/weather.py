"""
Weather service using Open-Meteo API.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import date, datetime


class WeatherService:
    """Service for fetching weather data."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    async def get_forecast(
        cls,
        latitude: float,
        longitude: float,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            target_date: Optional target date for forecast

        Returns:
            Weather forecast data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "hourly": "temperature_2m,precipitation_probability,weathercode",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
            "forecast_days": 7,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(cls.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        # Process and format the data
        formatted_data = {
            "current": {
                "temperature": data["current_weather"]["temperature"],
                "weathercode": data["current_weather"]["weathercode"],
                "description": cls._get_weather_description(
                    data["current_weather"]["weathercode"]
                ),
                "is_day": data["current_weather"]["is_day"] == 1,
            },
            "daily": [],
        }

        # Add daily forecasts
        for i in range(len(data["daily"]["time"])):
            daily_forecast = {
                "date": data["daily"]["time"][i],
                "temp_max": data["daily"]["temperature_2m_max"][i],
                "temp_min": data["daily"]["temperature_2m_min"][i],
                "precipitation": data["daily"]["precipitation_sum"][i],
                "weathercode": data["daily"]["weathercode"][i],
                "description": cls._get_weather_description(data["daily"]["weathercode"][i]),
            }
            formatted_data["daily"].append(daily_forecast)

        # If target date specified, extract that day's forecast
        if target_date:
            target_str = target_date.isoformat()
            for day in formatted_data["daily"]:
                if day["date"] == target_str:
                    formatted_data["target_day"] = day
                    break

        return formatted_data

    @staticmethod
    def _get_weather_description(weathercode: int) -> str:
        """
        Convert weather code to human-readable description.

        Weather codes from Open-Meteo:
        0 = Clear sky
        1, 2, 3 = Mainly clear, partly cloudy, overcast
        45, 48 = Fog
        51, 53, 55 = Drizzle
        61, 63, 65 = Rain
        71, 73, 75 = Snow
        95 = Thunderstorm
        """
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return weather_codes.get(weathercode, "Unknown")

    @classmethod
    def get_date_suitability(cls, forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze weather forecast for date suitability.

        Args:
            forecast: Weather forecast data

        Returns:
            Suitability analysis
        """
        if "target_day" not in forecast:
            return {"suitable": True, "warnings": [], "recommendations": []}

        day = forecast["target_day"]
        warnings = []
        recommendations = []
        suitable = True

        # Check temperature
        if day["temp_max"] < 32:
            warnings.append("Very cold - dress warmly!")
            recommendations.append("Consider indoor venues")
        elif day["temp_max"] > 90:
            warnings.append("Very hot - stay hydrated!")
            recommendations.append("Look for air-conditioned venues")

        # Check precipitation
        if day["precipitation"] > 0.5:
            warnings.append(f"Rain expected ({day['precipitation']} inches)")
            recommendations.append("Bring an umbrella")
            recommendations.append("Consider venues with covered/indoor options")

        # Check weather code
        if day["weathercode"] >= 95:
            warnings.append("Severe weather possible - thunderstorms")
            suitable = False
            recommendations.append("Consider rescheduling or choosing indoor venues")
        elif day["weathercode"] >= 71:
            warnings.append("Snow expected")
            recommendations.append("Allow extra travel time")

        return {
            "suitable": suitable,
            "warnings": warnings,
            "recommendations": recommendations,
            "summary": cls._get_summary(day),
        }

    @staticmethod
    def _get_summary(day: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the day's weather."""
        temp_range = f"{int(day['temp_min'])}°-{int(day['temp_max'])}°F"
        return f"{day['description']}, {temp_range}"
