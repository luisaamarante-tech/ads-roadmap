"""
Configuration management for the VTEX Ads Public Roadmap API.

Loads settings from environment variables with sensible defaults.
Supports JSON-based project-specific custom field configuration.
"""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from dotenv import load_dotenv

if TYPE_CHECKING:
    from app.services.config_loader import ProjectConfig

# Load .env file if present
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration loaded from environment variables."""

    # Project-specific custom field configuration (loaded from JSON)
    # Type hint using string to avoid circular import
    _project_config: Optional["ProjectConfig"] = None

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"

    # JIRA Configuration
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

    @classmethod
    def get_project_keys(cls) -> list[str]:
        """
        Return list of JIRA project keys to sync.

        Projects are defined in config/jira_projects.json.
        Only projects with configured custom field mappings will be synced.
        """
        if cls._project_config is None:
            # Try to load config if not already loaded
            cls.load_project_config()

        if cls._project_config is None:
            logger.warning("No project configuration loaded from jira_projects.json")
            return []

        return list(cls._project_config.projects.keys())

    # JIRA Custom Field IDs
    JIRA_FIELD_PUBLIC_ROADMAP = os.getenv(
        "JIRA_FIELD_PUBLIC_ROADMAP", "customfield_10001"
    )
    JIRA_FIELD_ROADMAP_STATUS = os.getenv(
        "JIRA_FIELD_ROADMAP_STATUS", "customfield_10002"
    )
    JIRA_FIELD_MODULE = os.getenv("JIRA_FIELD_MODULE", "customfield_10003")
    JIRA_FIELD_RELEASE_YEAR = os.getenv("JIRA_FIELD_RELEASE_YEAR", "customfield_10004")
    JIRA_FIELD_RELEASE_QUARTER = os.getenv(
        "JIRA_FIELD_RELEASE_QUARTER", "customfield_10005"
    )
    JIRA_FIELD_RELEASE_MONTH = os.getenv(
        "JIRA_FIELD_RELEASE_MONTH", "customfield_10006"
    )
    JIRA_FIELD_DOCUMENTATION_URL = os.getenv(
        "JIRA_FIELD_DOCUMENTATION_URL", "customfield_10007"
    )

    # Sync Configuration
    SYNC_INTERVAL_MINUTES = int(os.getenv("SYNC_INTERVAL_MINUTES", "5"))
    ENABLE_SYNC = os.getenv("ENABLE_SYNC", "true").lower() == "true"
    # Set ENABLE_SCHEDULER=false on Vercel (use Cron Jobs + POST /api/v1/sync instead)
    ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    # Secret for authenticating Vercel Cron Job requests to POST /api/v1/sync
    CRON_SECRET = os.getenv("CRON_SECRET", "")

    # Cache Configuration
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    REDIS_URL = os.getenv("REDIS_URL", "")

    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
    )

    # Rate Limiting
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100 per minute")

    # Feature Requests - Slack Notification
    SLACK_FEATURE_REQUEST_WEBHOOK_URL = os.getenv(
        "SLACK_FEATURE_REQUEST_WEBHOOK_URL", ""
    )

    @classmethod
    def get_jira_field_mapping(cls) -> dict:
        """Return mapping of RoadmapItem fields to JIRA custom field IDs."""
        return {
            "public_roadmap": cls.JIRA_FIELD_PUBLIC_ROADMAP,
            "roadmap_status": cls.JIRA_FIELD_ROADMAP_STATUS,
            "module": cls.JIRA_FIELD_MODULE,
            "release_year": cls.JIRA_FIELD_RELEASE_YEAR,
            "release_quarter": cls.JIRA_FIELD_RELEASE_QUARTER,
            "release_month": cls.JIRA_FIELD_RELEASE_MONTH,
            "documentation_url": cls.JIRA_FIELD_DOCUMENTATION_URL,
        }

    @classmethod
    def is_jira_configured(cls) -> bool:
        """Check if JIRA credentials are configured."""
        return bool(cls.JIRA_BASE_URL and cls.JIRA_EMAIL and cls.JIRA_API_TOKEN)

    @classmethod
    def is_slack_configured(cls) -> bool:
        """Check if Slack webhook is configured for feature requests."""
        return bool(cls.SLACK_FEATURE_REQUEST_WEBHOOK_URL)

    @classmethod
    def load_project_config(cls):
        """
        Load project-specific custom field configuration from JSON file.

        This should be called once at application startup.
        If the config file doesn't exist or is invalid, logs a warning
        and falls back to environment variable configuration.
        """
        # Lazy import to avoid circular dependency
        from .services.config_loader import load_config

        config_path = Path(__file__).parent.parent / "config" / "jira_projects.json"

        if not config_path.exists():
            logger.info(
                "Project configuration file not found, using environment variables"
            )
            return

        cls._project_config = load_config(str(config_path))

        if cls._project_config:
            logger.info(
                f"Loaded custom field configuration for "
                f"{len(cls._project_config.projects)} projects"
            )
        else:
            logger.warning(
                "Failed to load project configuration, falling back to environment variables"
            )

    @classmethod
    def get_project_custom_fields(cls, project_key: str) -> Optional[dict[str, str]]:
        """
        Get ALL custom field IDs for a specific project.

        Args:
            project_key: JIRA project key (e.g., "PROJ1")

        Returns:
            Dictionary mapping field names to custom field IDs, or None if
            project not configured in JSON file (caller should use env var defaults)

        Example return:
            {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                "module": "customfield_10003",
                ...
                "roadmap_title": "customfield_10101",
                "roadmap_description": "customfield_10102",
                "roadmap_image_url_1": "customfield_10103",
                ...
            }
        """
        if cls._project_config is None:
            return None

        project_mapping = cls._project_config.projects.get(project_key)
        if project_mapping is None:
            return None

        # Convert ProjectFieldMapping dataclass to dictionary with ALL fields
        return {
            "public_roadmap": project_mapping.public_roadmap,
            "roadmap_status": project_mapping.roadmap_status,
            "media_type": project_mapping.media_type,
            "release_year": project_mapping.release_year,
            "release_quarter": project_mapping.release_quarter,
            "release_month": project_mapping.release_month,
            "documentation_url": project_mapping.documentation_url,
            "roadmap_title": project_mapping.roadmap_title,
            "roadmap_description": project_mapping.roadmap_description,
            "roadmap_image_url_1": project_mapping.roadmap_image_url_1,
            "roadmap_image_url_2": project_mapping.roadmap_image_url_2,
            "roadmap_image_url_3": project_mapping.roadmap_image_url_3,
            "roadmap_image_url_4": project_mapping.roadmap_image_url_4,
            "roadmap_likes": project_mapping.roadmap_likes,
        }
