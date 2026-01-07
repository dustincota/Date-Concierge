"""
Location optimization service for multi-user planning.
Finds optimal meeting points and fair venues for all participants.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.session import SessionParticipant
from app.models.user import UserLocation
from app.models.venue import Venue
from app.services.travel import TravelService
from app.services.geocoding import GeocodingService


class LocationOptimizer:
    """Service for optimizing meeting locations for multiple people."""

    @classmethod
    def find_optimal_meeting_point(
        cls,
        locations: List[Tuple[float, float]],
        weights: Optional[List[float]] = None,
        mode: str = "centroid",
    ) -> Tuple[float, float]:
        """
        Find optimal meeting point for multiple people.

        Args:
            locations: List of (latitude, longitude) tuples
            weights: Optional flexibility weights (less flexible = higher weight)
            mode: Optimization mode
                - "centroid": Geographic center (equal travel for all)
                - "weighted": Weighted by flexibility
                - "minimize_max": Minimize the maximum travel time for anyone

        Returns:
            (latitude, longitude) of optimal meeting point
        """
        if not locations:
            raise ValueError("At least one location required")

        if len(locations) == 1:
            return locations[0]

        if mode == "centroid":
            return cls._find_centroid(locations)

        elif mode == "weighted":
            if weights is None:
                weights = [1.0] * len(locations)
            return cls._find_weighted_centroid(locations, weights)

        elif mode == "minimize_max":
            # For now, use centroid as approximation
            # TODO: Implement iterative optimization
            return cls._find_centroid(locations)

        else:
            raise ValueError(f"Unknown mode: {mode}")

    @staticmethod
    def _find_centroid(locations: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Find geographic centroid of locations."""
        lats = [loc[0] for loc in locations]
        lons = [loc[1] for loc in locations]

        return (
            np.mean(lats),
            np.mean(lons),
        )

    @staticmethod
    def _find_weighted_centroid(
        locations: List[Tuple[float, float]], weights: List[float]
    ) -> Tuple[float, float]:
        """Find weighted centroid based on flexibility."""
        total_weight = sum(weights)
        weighted_lat = sum(loc[0] * w for loc, w in zip(locations, weights))
        weighted_lon = sum(loc[1] * w for loc, w in zip(locations, weights))

        return (
            weighted_lat / total_weight,
            weighted_lon / total_weight,
        )

    @classmethod
    async def find_fair_venues(
        cls,
        participant_locations: List[Tuple[float, float]],
        candidate_venues: List[Venue],
        max_travel_difference_minutes: int = 15,
        mode: str = "transit",
    ) -> List[Dict[str, Any]]:
        """
        Filter venues where travel time difference between participants
        is within acceptable range.

        Args:
            participant_locations: List of participant (lat, lon) tuples
            candidate_venues: List of venue objects to evaluate
            max_travel_difference_minutes: Maximum acceptable travel time difference
            mode: Travel mode

        Returns:
            List of venues with fairness scores and travel times
        """
        fair_venues = []

        for venue in candidate_venues:
            venue_loc = (float(venue.latitude), float(venue.longitude))

            # Calculate travel time for each participant
            travel_times = []
            for participant_loc in participant_locations:
                travel_info = await TravelService.get_travel_time(
                    participant_loc, venue_loc, mode
                )
                travel_times.append(travel_info["duration_minutes"])

            # Check if venue is fair
            min_time = min(travel_times)
            max_time = max(travel_times)
            time_diff = max_time - min_time

            if time_diff <= max_travel_difference_minutes:
                # Calculate fairness score (0-1, higher is better)
                fairness_score = 1.0 - (time_diff / max_travel_difference_minutes)

                fair_venues.append(
                    {
                        "venue": venue,
                        "travel_times": travel_times,
                        "min_travel_time": min_time,
                        "max_travel_time": max_time,
                        "time_difference": time_diff,
                        "fairness_score": fairness_score,
                        "avg_travel_time": np.mean(travel_times),
                    }
                )

        # Sort by fairness score (descending) and average travel time (ascending)
        fair_venues.sort(key=lambda x: (-x["fairness_score"], x["avg_travel_time"]))

        return fair_venues

    @classmethod
    def merge_participant_preferences(
        cls, participants: List[SessionParticipant], db: Session
    ) -> Dict[str, Any]:
        """
        Find intersection of all participant preferences.
        Returns constraints that work for everyone.

        Args:
            participants: List of session participants
            db: Database session

        Returns:
            Merged constraints dictionary
        """
        if not participants:
            return {}

        # Collect all preferences
        all_prefs = []
        for participant in participants:
            # Check for session-specific override
            if participant.preferences_override:
                all_prefs.append(participant.preferences_override)
            # Otherwise use user's default preferences
            elif participant.user.preferences:
                prefs = participant.user.preferences
                all_prefs.append(
                    {
                        "budget_min": prefs.default_budget_min,
                        "budget_max": prefs.default_budget_max,
                        "cuisines_loved": prefs.cuisines_loved or [],
                        "cuisines_avoid": prefs.cuisines_avoid or [],
                        "dietary_restrictions": prefs.dietary_restrictions or [],
                        "vibes": prefs.vibes or [],
                    }
                )

        if not all_prefs:
            return {}

        # Budget: intersection of ranges
        budget_mins = [p.get("budget_min", 1) for p in all_prefs if p.get("budget_min")]
        budget_maxs = [p.get("budget_max", 4) for p in all_prefs if p.get("budget_max")]

        budget_min = max(budget_mins) if budget_mins else 1
        budget_max = min(budget_maxs) if budget_maxs else 4

        # Ensure valid range
        if budget_min > budget_max:
            budget_max = budget_min

        # Dietary restrictions: union (must accommodate all)
        all_dietary = set()
        for prefs in all_prefs:
            restrictions = prefs.get("dietary_restrictions", [])
            all_dietary.update(restrictions)

        # Cuisines to avoid: union (avoid if anyone dislikes)
        cuisines_avoid = set()
        for prefs in all_prefs:
            avoid = prefs.get("cuisines_avoid", [])
            cuisines_avoid.update(avoid)

        # Cuisines loved: keep only those liked by multiple people
        cuisine_counts = {}
        for prefs in all_prefs:
            loved = prefs.get("cuisines_loved", [])
            for cuisine in loved:
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1

        # Cuisines liked by at least 50% of participants
        threshold = len(all_prefs) / 2
        cuisines_preferred = [c for c, count in cuisine_counts.items() if count >= threshold]

        # Vibes: intersection (must appeal to all)
        vibe_sets = [set(p.get("vibes", [])) for p in all_prefs if p.get("vibes")]
        common_vibes = set.intersection(*vibe_sets) if vibe_sets else set()

        # If no common vibes, use most popular
        if not common_vibes:
            vibe_counts = {}
            for prefs in all_prefs:
                for vibe in prefs.get("vibes", []):
                    vibe_counts[vibe] = vibe_counts.get(vibe, 0) + 1
            # Take vibes mentioned by at least one person
            common_vibes = set(v for v, count in vibe_counts.items() if count >= 1)

        return {
            "budget_range": (budget_min, budget_max),
            "dietary_restrictions": list(all_dietary),
            "cuisines_avoid": list(cuisines_avoid),
            "cuisines_preferred": cuisines_preferred,
            "vibes": list(common_vibes) or ["casual"],
        }

    @classmethod
    def get_participant_locations(
        cls, participants: List[SessionParticipant], db: Session
    ) -> List[Tuple[float, float]]:
        """
        Extract participant locations as (lat, lon) tuples.

        Args:
            participants: List of session participants
            db: Database session

        Returns:
            List of (latitude, longitude) tuples
        """
        locations = []

        for participant in participants:
            if participant.location_id:
                # Use specified location
                location = (
                    db.query(UserLocation)
                    .filter(UserLocation.id == participant.location_id)
                    .first()
                )
                if location:
                    locations.append((float(location.latitude), float(location.longitude)))
            else:
                # Use default location
                default_loc = (
                    db.query(UserLocation)
                    .filter(
                        UserLocation.user_id == participant.user_id,
                        UserLocation.is_default == True,
                    )
                    .first()
                )
                if default_loc:
                    locations.append(
                        (float(default_loc.latitude), float(default_loc.longitude))
                    )

        return locations
