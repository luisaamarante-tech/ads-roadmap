"""
Data models for roadmap items and related entities.

These are simple dataclasses representing the public roadmap data.
No database ORM - data is cached from JIRA.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DeliveryStatus(str, Enum):
    """Delivery status for roadmap items."""

    DELIVERED = "DELIVERED"
    NOW = "NOW"
    NEXT = "NEXT"
    FUTURE = "FUTURE"


class Quarter(str, Enum):
    """Calendar quarter."""

    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


@dataclass
class RoadmapItem:
    """
    Represents a single roadmap entry derived from a JIRA Epic.

    Only contains fields that are safe to expose publicly.
    """

    id: str  # JIRA issue key, e.g., "PROJ-123"
    title: str
    description: str
    status: DeliveryStatus
    module: str
    module_id: str  # URL-safe slug
    release_year: int
    release_quarter: Quarter
    release_month: Optional[int] = None
    images: list[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    likes: int = 0
    last_synced_at: datetime = field(default_factory=datetime.utcnow)
    semester_goals: List[str] = field(default_factory=list)
    semester_goal_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Ensure status is enum
        if isinstance(self.status, str):
            self.status = DeliveryStatus(self.status)

        # Ensure quarter is enum
        if isinstance(self.release_quarter, str):
            self.release_quarter = Quarter(self.release_quarter)

        # Limit images to 4
        self.images = self.images[:4] if self.images else []

        # Ensure module_id is a valid slug
        if not self.module_id:
            self.module_id = self._slugify(self.module)

        # Generate semester_goal_ids from semester_goals if not set
        if not self.semester_goal_ids and self.semester_goals:
            self.semester_goal_ids = [self._slugify(g) for g in self.semester_goals]

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-safe slug."""
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "module": self.module,
            "moduleId": self.module_id,
            "releaseYear": self.release_year,
            "releaseQuarter": self.release_quarter.value,
            "releaseMonth": self.release_month,
            "images": self.images,
            "documentationUrl": self.documentation_url,
            "likes": self.likes,
            "lastSyncedAt": self.last_synced_at.isoformat() + "Z",
            "semesterGoals": self.semester_goals,
            "semesterGoalIds": self.semester_goal_ids,
        }

    def matches_filters(
        self,
        status: Optional[str] = None,
        year: Optional[int] = None,
        quarter: Optional[str] = None,
        module: Optional[str | List[str]] = None,
        goal: Optional[str | List[str]] = None,
    ) -> bool:
        """
        Check if item matches the given filters.

        Args:
            status: Filter by delivery status
            year: Filter by release year
            quarter: Filter by release quarter
            module: Filter by module (can be a single string or list of module IDs)
        """
        if status and self.status.value != status:
            return False
        if year and self.release_year != year:
            return False
        if quarter and self.release_quarter.value != quarter:
            return False
        if module:
            if isinstance(module, list):
                if self.module_id not in module:
                    return False
            else:
                if self.module_id != module:
                    return False
        if goal:
            if isinstance(goal, list):
                if not any(gid in self.semester_goal_ids for gid in goal):
                    return False
            else:
                if goal not in self.semester_goal_ids:
                    return False
        return True


@dataclass
class Module:
    """
    Represents a product module/area for filtering.
    """

    id: str  # URL-safe slug
    name: str  # Display name
    item_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "itemCount": self.item_count,
        }


@dataclass
class Goal:
    """Represents a semester goal for filtering."""

    id: str  # URL-safe slug
    name: str  # Display name
    item_count: int = 0

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "itemCount": self.item_count}


@dataclass
class SyncMetadata:
    """
    Tracks the synchronization status with JIRA.
    """

    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None  # SUCCESS, PARTIAL, FAILED
    item_count: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "lastSyncAt": (
                self.last_sync_at.isoformat() + "Z" if self.last_sync_at else None
            ),
            "lastSyncStatus": self.last_sync_status,
            "itemCount": self.item_count,
            "errorMessage": self.error_message,
        }

    def is_stale(self, threshold_minutes: int = 10) -> bool:
        """Check if data is stale (last sync more than threshold_minutes ago)."""
        if not self.last_sync_at:
            return True
        delta = datetime.utcnow() - self.last_sync_at
        return delta.total_seconds() > threshold_minutes * 60
