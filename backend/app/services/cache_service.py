"""
Cache service for storing and retrieving roadmap data.

Provides both in-memory caching and file-based fallback for
persistence across restarts and JIRA outages.
"""

# Standard library
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Local
from ..models import DeliveryStatus, Goal, Module, Quarter, RoadmapItem, SyncMetadata

logger = logging.getLogger(__name__)

# Cache keys
CACHE_KEY_ITEMS = "roadmap:items"
CACHE_KEY_MODULES = "roadmap:modules"
CACHE_KEY_GOALS = "roadmap:goals"
CACHE_KEY_METADATA = "roadmap:metadata"

# Fallback file path
FALLBACK_FILE = Path(
    os.getenv(
        "ROADMAP_CACHE_FILE",
        "/tmp/roadmap_cache.json",
    )
)


class CacheService:
    """
    Service for caching roadmap data.

    Uses Flask-Caching for primary storage with file-based fallback.
    """

    def __init__(self, cache):
        """Initialize with Flask-Caching instance."""
        self.cache = cache
        self._ensure_fallback_dir()

    def _ensure_fallback_dir(self):
        """Ensure the fallback cache directory exists."""
        FALLBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    # ==================== Item Operations ====================

    def get_items(self) -> list[RoadmapItem]:
        """Get all cached roadmap items."""
        items_data = self.cache.get(CACHE_KEY_ITEMS)

        if items_data is None:
            # Try fallback
            items_data = self._load_from_fallback().get("items", [])

        return [self._dict_to_item(item) for item in items_data]

    def set_items(self, items: list[RoadmapItem]):
        """Cache all roadmap items."""
        items_data = [item.to_dict() for item in items]
        self.cache.set(CACHE_KEY_ITEMS, items_data, timeout=0)

    def get_filtered_items(
        self,
        status: Optional[str] = None,
        year: Optional[int] = None,
        quarter: Optional[str] = None,
        module: Optional[str | list[str]] = None,
        goal: Optional[str | list[str]] = None,
    ) -> list[RoadmapItem]:
        """Get items matching the given filters."""
        items = self.get_items()
        return [
            item
            for item in items
            if item.matches_filters(status, year, quarter, module, goal)
        ]

    def get_item_by_id(self, item_id: str) -> Optional[RoadmapItem]:
        """Get a single item by ID."""
        items = self.get_items()
        for item in items:
            if item.id == item_id:
                return item
        return None

    # ==================== Goal Operations ====================

    def get_goals(self) -> list[Goal]:
        """Get all cached semester goals."""
        goals_data = self.cache.get(CACHE_KEY_GOALS)
        if goals_data is None:
            goals_data = self._load_from_fallback().get("goals", [])
        return [self._dict_to_goal(g) for g in goals_data]

    def set_goals(self, goals: list[Goal]):
        """Cache all semester goals."""
        goals_data = [g.to_dict() for g in goals]
        self.cache.set(CACHE_KEY_GOALS, goals_data, timeout=0)

    # ==================== Module Operations ====================

    def get_modules(self) -> list[Module]:
        """Get all cached modules."""
        modules_data = self.cache.get(CACHE_KEY_MODULES)

        if modules_data is None:
            # Try fallback
            modules_data = self._load_from_fallback().get("modules", [])

        return [self._dict_to_module(m) for m in modules_data]

    def set_modules(self, modules: list[Module]):
        """Cache all modules."""
        modules_data = [m.to_dict() for m in modules]
        self.cache.set(CACHE_KEY_MODULES, modules_data, timeout=0)

    # ==================== Metadata Operations ====================

    def get_metadata(self) -> SyncMetadata:
        """Get sync metadata."""
        metadata_data = self.cache.get(CACHE_KEY_METADATA)

        if metadata_data is None:
            # Try fallback
            metadata_data = self._load_from_fallback().get("metadata", {})

        return self._dict_to_metadata(metadata_data)

    def set_metadata(self, metadata: SyncMetadata):
        """Cache sync metadata."""
        self.cache.set(CACHE_KEY_METADATA, metadata.to_dict(), timeout=0)

    def invalidate(self):
        """Clear all cached data to force a refresh on next request."""
        self.cache.delete(CACHE_KEY_ITEMS)
        self.cache.delete(CACHE_KEY_MODULES)
        self.cache.delete(CACHE_KEY_GOALS)
        self.cache.delete(CACHE_KEY_METADATA)
        logger.info("Cache invalidated")

    def update_item_likes(self, item_id: str, new_likes: int) -> bool:
        """
        Update the likes count for a specific item in both in-memory cache and fallback file.

        Args:
            item_id: The item ID (JIRA key) to update
            new_likes: The new likes count

        Returns:
            True if item was found and updated, False otherwise
        """
        item_found = False

        # First, update the fallback file (source of truth)
        fallback_data = self._load_from_fallback()
        for item in fallback_data.get("items", []):
            if item.get("id") == item_id:
                item["likes"] = new_likes
                item_found = True
                break

        if item_found:
            # Save updated data to fallback file
            try:
                with open(FALLBACK_FILE, "w") as f:
                    json.dump(fallback_data, f, indent=2)
                logger.info(
                    f"Updated likes for {item_id} to {new_likes} in fallback file"
                )
            except IOError as e:
                logger.error(f"Failed to update fallback file: {e}")
                return False

            # Clear the in-memory cache so next request reads from updated fallback file
            self.cache.delete(CACHE_KEY_ITEMS)
            logger.info("Cleared in-memory cache to force reload from fallback")

        return item_found

    # ==================== Statistics ====================

    def get_stats(
        self,
        year: Optional[int] = None,
        quarter: Optional[str] = None,
        module: Optional[str | list[str]] = None,
        goal: Optional[str | list[str]] = None,
    ) -> dict:
        """Get item counts by status, optionally filtered."""
        items = self.get_filtered_items(
            status=None,
            year=year,
            quarter=quarter,
            module=module,
            goal=goal,
        )

        stats = {
            "DELIVERED": 0,
            "NOW": 0,
            "NEXT": 0,
            "FUTURE": 0,
        }

        for item in items:
            stats[item.status.value] += 1

        return {
            "stats": stats,
            "total": sum(stats.values()),
        }

    # ==================== Fallback Operations ====================

    def save_to_fallback(self):
        """Save current cache to fallback file."""
        try:
            data = {
                "items": self.cache.get(CACHE_KEY_ITEMS) or [],
                "modules": self.cache.get(CACHE_KEY_MODULES) or [],
                "goals": self.cache.get(CACHE_KEY_GOALS) or [],
                "metadata": self.cache.get(CACHE_KEY_METADATA) or {},
                "saved_at": datetime.utcnow().isoformat() + "Z",
            }

            with open(FALLBACK_FILE, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved cache to fallback file: {FALLBACK_FILE}")
        except Exception as e:
            logger.error(f"Failed to save fallback cache: {e}")

    def _load_from_fallback(self) -> dict:
        """Load cache from fallback file."""
        try:
            if FALLBACK_FILE.exists():
                with open(FALLBACK_FILE) as f:
                    data = json.load(f)
                logger.info(f"Loaded cache from fallback file: {FALLBACK_FILE}")
                return data
        except Exception as e:
            logger.error(f"Failed to load fallback cache: {e}")

        return {}

    # ==================== Helpers ====================

    def _dict_to_item(self, data: dict) -> RoadmapItem:
        """Convert dictionary to RoadmapItem."""
        return RoadmapItem(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=DeliveryStatus(data.get("status", "FUTURE")),
            module=data.get("module", ""),
            module_id=data.get("moduleId", ""),
            release_year=data.get("releaseYear", 2025),
            release_quarter=Quarter(data.get("releaseQuarter", "Q1")),
            release_month=data.get("releaseMonth"),
            images=data.get("images", []),
            documentation_url=data.get("documentationUrl"),
            likes=data.get("likes", 0),
            last_synced_at=datetime.fromisoformat(
                data.get("lastSyncedAt", datetime.utcnow().isoformat()).replace("Z", "")
            ),
            semester_goals=data.get("semesterGoals", []),
            semester_goal_ids=data.get("semesterGoalIds", []),
        )

    def _dict_to_goal(self, data: dict) -> Goal:
        """Convert dictionary to Goal."""
        return Goal(
            id=data.get("id", ""),
            name=data.get("name", ""),
            item_count=data.get("itemCount", 0),
        )

    def _dict_to_module(self, data: dict) -> Module:
        """Convert dictionary to Module."""
        return Module(
            id=data.get("id", ""),
            name=data.get("name", ""),
            item_count=data.get("itemCount", 0),
        )

    def _dict_to_metadata(self, data: dict) -> SyncMetadata:
        """Convert dictionary to SyncMetadata."""
        last_sync_at = None
        if data.get("lastSyncAt"):
            last_sync_at = datetime.fromisoformat(data["lastSyncAt"].replace("Z", ""))

        return SyncMetadata(
            last_sync_at=last_sync_at,
            last_sync_status=data.get("lastSyncStatus"),
            item_count=data.get("itemCount", 0),
            error_message=data.get("errorMessage"),
        )

    # ==================== Idempotency Operations ====================

    def get_idempotency_response(self, idempotency_key: str) -> Optional[dict]:
        """
        Get cached response for an idempotency key.

        Args:
            idempotency_key: Client-provided idempotency key

        Returns:
            Cached response dict if found, None otherwise
        """
        if not idempotency_key or len(idempotency_key) > 128:
            logger.warning(f"Invalid idempotency key length: {len(idempotency_key)}")
            return None

        cache_key = f"idempotency:{idempotency_key}"
        try:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Idempotency cache hit for key: {idempotency_key}")
            return cached
        except Exception as e:
            logger.error(f"Failed to get idempotency response: {e}")
            return None

    def set_idempotency_response(
        self, idempotency_key: str, response: dict, ttl_seconds: int = 3600
    ):
        """
        Cache a response for an idempotency key.

        Provides safe fallback if cache write fails to avoid blocking the request.

        Args:
            idempotency_key: Client-provided idempotency key
            response: Response dict to cache
            ttl_seconds: Time-to-live in seconds (default 1 hour)
        """
        if not idempotency_key or len(idempotency_key) > 128:
            logger.warning(
                f"Invalid idempotency key, skipping cache: {idempotency_key}"
            )
            return

        cache_key = f"idempotency:{idempotency_key}"
        try:
            self.cache.set(cache_key, response, timeout=ttl_seconds)
            logger.info(
                f"Cached idempotency response for key: {idempotency_key} (TTL: {ttl_seconds}s)"
            )
        except Exception as e:
            logger.error(f"Failed to cache idempotency response: {e}")
