"""
Celery tasks for intelligence gathering.
"""

import asyncio
from datetime import datetime, timedelta
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.venue import Venue, VenueIntelligence, IntelligenceJob
from app.agents.orchestrator import IntelligenceOrchestrator


@celery_app.task(bind=True)
def gather_venue_intelligence(self, venue_id: str):
    """
    Gather intelligence for a venue using all agents.

    Args:
        venue_id: Venue ID (UUID as string)

    Returns:
        Dictionary with success status and intelligence data
    """
    db = SessionLocal()

    try:
        # Get venue
        venue = db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            return {"success": False, "error": "Venue not found"}

        # Create or update intelligence job
        job = db.query(IntelligenceJob).filter(
            IntelligenceJob.id == self.request.id
        ).first()

        if not job:
            job = IntelligenceJob(
                id=self.request.id,
                venue_id=venue_id,
                status="running",
                started_at=datetime.utcnow(),
            )
            db.add(job)
        else:
            job.status = "running"
            job.started_at = datetime.utcnow()

        db.commit()

        # Run orchestrator
        orchestrator = IntelligenceOrchestrator()

        # Run async gathering in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        intelligence_data = loop.run_until_complete(
            orchestrator.gather_intelligence(venue)
        )
        loop.run_until_complete(orchestrator.close())
        loop.close()

        # Save or update intelligence
        existing_intel = db.query(VenueIntelligence).filter(
            VenueIntelligence.venue_id == venue_id
        ).first()

        if existing_intel:
            # Update existing
            existing_intel.seating_recommendations = intelligence_data.get(
                "seating_recommendations", []
            )
            existing_intel.dish_recommendations = intelligence_data.get(
                "dish_recommendations", []
            )
            existing_intel.timing_insights = intelligence_data.get("timing_insights", {})
            existing_intel.commute_insights = intelligence_data.get("commute_insights", {})
            existing_intel.vibe_check = intelligence_data.get("vibe_check", {})
            existing_intel.insider_tips = intelligence_data.get("insider_tips", [])
            existing_intel.warnings = intelligence_data.get("warnings", [])
            existing_intel.date_score = intelligence_data.get("date_score", 7.0)
            existing_intel.trending_score = intelligence_data.get("trending_score", 5.0)
            existing_intel.intelligence_score = intelligence_data.get(
                "intelligence_score", 0.5
            )
            existing_intel.reddit_data = intelligence_data.get("reddit_data", [])
            existing_intel.google_reviews_summary = intelligence_data.get(
                "google_reviews_summary", {}
            )
            existing_intel.tiktok_data = intelligence_data.get("tiktok_data", [])
            existing_intel.last_updated = datetime.utcnow()
        else:
            # Create new
            new_intel = VenueIntelligence(
                venue_id=venue_id,
                seating_recommendations=intelligence_data.get("seating_recommendations", []),
                dish_recommendations=intelligence_data.get("dish_recommendations", []),
                timing_insights=intelligence_data.get("timing_insights", {}),
                commute_insights=intelligence_data.get("commute_insights", {}),
                vibe_check=intelligence_data.get("vibe_check", {}),
                insider_tips=intelligence_data.get("insider_tips", []),
                warnings=intelligence_data.get("warnings", []),
                date_score=intelligence_data.get("date_score", 7.0),
                trending_score=intelligence_data.get("trending_score", 5.0),
                intelligence_score=intelligence_data.get("intelligence_score", 0.5),
                reddit_data=intelligence_data.get("reddit_data", []),
                google_reviews_summary=intelligence_data.get("google_reviews_summary", {}),
                tiktok_data=intelligence_data.get("tiktok_data", []),
                last_updated=datetime.utcnow(),
            )
            db.add(new_intel)

        # Update job status
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.agents_completed = ["reddit", "reviews", "tiktok"]

        db.commit()

        return {
            "success": True,
            "venue_id": venue_id,
            "intelligence_score": intelligence_data.get("intelligence_score", 0.5),
        }

    except Exception as e:
        # Update job with error
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

        return {"success": False, "error": str(e)}

    finally:
        db.close()


@celery_app.task
def refresh_stale_intelligence():
    """
    Periodic task to refresh intelligence for venues with stale data.

    Runs hourly, refreshes venues that haven't been updated in the
    configured update frequency period.
    """
    db = SessionLocal()

    try:
        # Find venues with stale intelligence
        cutoff_time = datetime.utcnow() - timedelta(
            hours=settings.INTELLIGENCE_UPDATE_FREQUENCY_HOURS
        )

        stale_venues = (
            db.query(Venue)
            .join(VenueIntelligence)
            .filter(VenueIntelligence.last_updated < cutoff_time)
            .limit(10)  # Process max 10 per run to avoid overload
            .all()
        )

        refreshed_count = 0
        for venue in stale_venues:
            # Trigger refresh task
            gather_venue_intelligence.delay(str(venue.id))
            refreshed_count += 1

        return {
            "success": True,
            "refreshed_count": refreshed_count,
            "message": f"Triggered refresh for {refreshed_count} venues",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        db.close()
