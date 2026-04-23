"""
Sync service for synchronizing roadmap data from JIRA.

Runs on a schedule using APScheduler to periodically fetch
and cache public roadmap items.
"""

# Standard library
import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

# Third-party
from apscheduler.schedulers.background import BackgroundScheduler

# Local
from ..config import Config
from ..models import Module, RoadmapItem, SyncMetadata
from .cache_service import CacheService
from .jira_client import JiraClient

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[BackgroundScheduler] = None


class SyncService:
    """
    Service for synchronizing roadmap data from JIRA.
    """

    def __init__(
        self, cache_service: CacheService, jira_client: Optional[JiraClient] = None
    ):
        """Initialize with cache and JIRA client."""
        self.cache = cache_service
        self.jira = jira_client or JiraClient()

    def sync(self) -> SyncMetadata:
        """
        Perform a full sync from JIRA.

        Fetches all public epics, transforms them to RoadmapItems,
        and updates the cache.
        """
        logger.info("Starting JIRA sync...")
        start_time = datetime.utcnow()

        try:
            # Fetch epics from JIRA
            issues = self.jira.fetch_public_epics()
            logger.info(f"Fetched {len(issues)} issues from JIRA")

            # Transform to RoadmapItems
            items = []
            for issue in issues:
                item = self.jira.extract_roadmap_item(issue)
                if item:
                    items.append(item)

            logger.info(f"Transformed {len(items)} valid roadmap items")

            # Extract modules from items
            modules = self._extract_modules(items)

            # Update cache
            self.cache.set_items(items)
            self.cache.set_modules(modules)

            # Create success metadata
            metadata = SyncMetadata(
                last_sync_at=datetime.utcnow(),
                last_sync_status="SUCCESS",
                item_count=len(items),
                error_message=None,
            )
            self.cache.set_metadata(metadata)

            # Save to fallback file
            self.cache.save_to_fallback()

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Sync completed successfully in {duration:.2f}s: {len(items)} items, {len(modules)} modules"
            )

            return metadata

        except Exception as e:
            logger.error(f"Sync failed: {e}")

            # Create failure metadata
            metadata = SyncMetadata(
                last_sync_at=datetime.utcnow(),
                last_sync_status="FAILED",
                item_count=self.cache.get_metadata().item_count,  # Keep previous count
                error_message=str(e),
            )
            self.cache.set_metadata(metadata)

            return metadata

    def _extract_modules(self, items: list[RoadmapItem]) -> list[Module]:
        """
        Extract unique modules from items with counts.
        """
        module_counts: dict[str, dict] = defaultdict(lambda: {"name": "", "count": 0})

        for item in items:
            module_id = item.module_id
            module_counts[module_id]["name"] = item.module
            module_counts[module_id]["count"] += 1

        modules = [
            Module(id=module_id, name=data["name"], item_count=data["count"])
            for module_id, data in sorted(module_counts.items())
        ]

        return modules


def start_scheduler(app):
    """
    Start the background scheduler for periodic sync.

    Called from app factory during initialization.
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return

    interval_minutes = Config.SYNC_INTERVAL_MINUTES

    _scheduler = BackgroundScheduler()

    # Import here to avoid circular imports
    from .. import cache

    def run_sync():
        """Run sync within app context."""
        with app.app_context():
            cache_service = CacheService(cache)
            sync_service = SyncService(cache_service)
            sync_service.sync()

    # Add sync job
    _scheduler.add_job(
        run_sync,
        "interval",
        minutes=interval_minutes,
        id="jira_sync",
        name="JIRA Sync",
        replace_existing=True,
    )

    # Run initial sync immediately
    logger.info("Scheduling initial sync...")
    _scheduler.add_job(
        run_sync,
        "date",
        run_date=datetime.utcnow(),
        id="jira_sync_initial",
        name="JIRA Sync (Initial)",
    )

    _scheduler.start()
    logger.info(f"Scheduler started: syncing every {interval_minutes} minutes")

    # Run sync directly on startup to ensure data is available immediately
    try:
        logger.info("Running immediate sync on startup...")
        run_sync()
    except Exception as e:
        logger.error(f"Immediate sync failed: {e}", exc_info=True)


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler

    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Scheduler stopped")


def trigger_sync(app) -> SyncMetadata:
    """
    Manually trigger a sync (for admin/testing).
    """
    from .. import cache

    with app.app_context():
        cache_service = CacheService(cache)
        sync_service = SyncService(cache_service)
        return sync_service.sync()
