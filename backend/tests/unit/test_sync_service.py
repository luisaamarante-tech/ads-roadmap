"""Unit tests for SyncService."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models import DeliveryStatus, Quarter, RoadmapItem, SyncMetadata
from app.services.sync_service import SyncService


class TestSyncService:
    """Tests for SyncService class."""

    @pytest.fixture
    def mock_cache_service(self):
        """Create mock CacheService."""
        cache = MagicMock()
        cache.get_metadata.return_value = SyncMetadata(
            last_sync_at=datetime.utcnow(),
            last_sync_status="SUCCESS",
            item_count=0,
        )
        return cache

    @pytest.fixture
    def mock_jira_client(self):
        """Create mock JiraClient."""
        jira = MagicMock()
        return jira

    @pytest.fixture
    def sync_service(self, mock_cache_service, mock_jira_client):
        """Create SyncService with mocks."""
        return SyncService(mock_cache_service, mock_jira_client)

    def test_sync_success(self, sync_service, mock_jira_client, mock_cache_service):
        """Test successful sync."""
        # Setup mock JIRA client
        mock_jira_client.fetch_public_epics.return_value = [
            {"key": "TEST-001", "fields": {}},
            {"key": "TEST-002", "fields": {}},
        ]
        mock_jira_client.extract_roadmap_item.side_effect = [
            RoadmapItem(
                id="TEST-001",
                title="Feature 1",
                description="Desc 1",
                status=DeliveryStatus.NOW,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
            ),
            RoadmapItem(
                id="TEST-002",
                title="Feature 2",
                description="Desc 2",
                status=DeliveryStatus.DELIVERED,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
            ),
        ]

        result = sync_service.sync()

        assert result.last_sync_status == "SUCCESS"
        assert result.item_count == 2
        mock_cache_service.set_items.assert_called_once()
        mock_cache_service.set_modules.assert_called_once()
        mock_cache_service.set_metadata.assert_called()
        mock_cache_service.save_to_fallback.assert_called_once()

    def test_sync_with_invalid_items(
        self, sync_service, mock_jira_client, mock_cache_service
    ):
        """Test sync skips invalid items."""
        mock_jira_client.fetch_public_epics.return_value = [
            {"key": "TEST-001", "fields": {}},
            {"key": "TEST-002", "fields": {}},
        ]
        # First item is valid, second returns None (invalid)
        mock_jira_client.extract_roadmap_item.side_effect = [
            RoadmapItem(
                id="TEST-001",
                title="Feature 1",
                description="Desc 1",
                status=DeliveryStatus.NOW,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
            ),
            None,
        ]

        result = sync_service.sync()

        assert result.item_count == 1

    def test_sync_failure(self, sync_service, mock_jira_client, mock_cache_service):
        """Test sync handles failure gracefully."""
        mock_jira_client.fetch_public_epics.side_effect = Exception("API Error")

        result = sync_service.sync()

        assert result.last_sync_status == "FAILED"
        assert "API Error" in result.error_message

    def test_extract_modules(self, sync_service):
        """Test extracting modules from items."""
        items = [
            RoadmapItem(
                id="TEST-001",
                title="Feature 1",
                description="Desc",
                status=DeliveryStatus.NOW,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
            ),
            RoadmapItem(
                id="TEST-002",
                title="Feature 2",
                description="Desc",
                status=DeliveryStatus.NOW,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
            ),
            RoadmapItem(
                id="TEST-003",
                title="Feature 3",
                description="Desc",
                status=DeliveryStatus.NOW,
                module="Module B",
                module_id="module-b",
                release_year=2025,
                release_quarter=Quarter.Q1,
            ),
        ]

        modules = sync_service._extract_modules(items)

        assert len(modules) == 2
        module_a = next(m for m in modules if m.id == "module-a")
        assert module_a.item_count == 2
        module_b = next(m for m in modules if m.id == "module-b")
        assert module_b.item_count == 1

    def test_extract_modules_empty(self, sync_service):
        """Test extracting modules from empty list."""
        modules = sync_service._extract_modules([])
        assert modules == []

    def test_sync_includes_likes_in_cached_data(
        self, sync_service, mock_jira_client, mock_cache_service
    ):
        """Test that sync includes likes field in cached data."""
        # Setup mock JIRA client to return items with likes
        mock_jira_client.fetch_public_epics.return_value = [
            {"key": "TEST-001", "fields": {}},
            {"key": "TEST-002", "fields": {}},
        ]
        mock_jira_client.extract_roadmap_item.side_effect = [
            RoadmapItem(
                id="TEST-001",
                title="Feature 1",
                description="Desc 1",
                status=DeliveryStatus.NOW,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
                likes=15,
            ),
            RoadmapItem(
                id="TEST-002",
                title="Feature 2",
                description="Desc 2",
                status=DeliveryStatus.DELIVERED,
                module="Module A",
                module_id="module-a",
                release_year=2025,
                release_quarter=Quarter.Q1,
                likes=42,
            ),
        ]

        result = sync_service.sync()

        # Verify sync succeeded
        assert result.last_sync_status == "SUCCESS"
        assert result.item_count == 2

        # Verify cached items include likes
        cached_items_call = mock_cache_service.set_items.call_args
        cached_items = cached_items_call[0][0]
        assert len(cached_items) == 2
        assert all(hasattr(item, "likes") for item in cached_items)
        assert cached_items[0].likes == 15
        assert cached_items[1].likes == 42


class TestSchedulerFunctions:
    """Tests for scheduler-related functions."""

    def test_start_scheduler(self):
        """Test starting the scheduler."""
        with patch("app.services.sync_service._scheduler", None):
            with patch(
                "app.services.sync_service.BackgroundScheduler"
            ) as mock_scheduler:
                with patch("app.services.sync_service.Config") as mock_config:
                    mock_config.SYNC_INTERVAL_MINUTES = 5

                    from app.services.sync_service import start_scheduler

                    mock_app = MagicMock()
                    mock_app.app_context.return_value.__enter__ = MagicMock()
                    mock_app.app_context.return_value.__exit__ = MagicMock()

                    start_scheduler(mock_app)

                    mock_scheduler.assert_called_once()

    def test_stop_scheduler(self):
        """Test stopping the scheduler."""
        with patch("app.services.sync_service._scheduler") as mock_scheduler:
            mock_scheduler.shutdown = MagicMock()

            from app.services.sync_service import stop_scheduler

            stop_scheduler()

    def test_trigger_sync(self):
        """Test manually triggering sync."""
        from app.services.sync_service import trigger_sync

        mock_app = MagicMock()
        mock_app.app_context.return_value.__enter__ = MagicMock()
        mock_app.app_context.return_value.__exit__ = MagicMock()

        with patch("app.services.sync_service.CacheService"):
            with patch("app.services.sync_service.SyncService") as mock_sync:
                mock_sync_instance = MagicMock()
                mock_sync.return_value = mock_sync_instance
                mock_sync_instance.sync.return_value = SyncMetadata(
                    last_sync_at=datetime.utcnow(),
                    last_sync_status="SUCCESS",
                    item_count=5,
                )

                result = trigger_sync(mock_app)

                assert result.last_sync_status == "SUCCESS"
