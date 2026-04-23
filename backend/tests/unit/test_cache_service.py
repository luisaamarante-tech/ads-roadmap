"""Unit tests for CacheService."""

from unittest.mock import MagicMock, patch

import pytest

from app.models import DeliveryStatus, Quarter
from app.services.cache_service import CACHE_KEY_ITEMS, CACHE_KEY_MODULES, CacheService


class TestCacheService:
    """Tests for CacheService class."""

    @pytest.fixture
    def cache_service(self, mock_cache):
        """Create CacheService with mock cache."""
        return CacheService(mock_cache)

    def test_get_items_from_cache(
        self, cache_service, mock_cache, sample_roadmap_items
    ):
        """Test getting items from cache."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        items = cache_service.get_items()

        assert len(items) == 3
        assert items[0].id == "TEST-001"
        mock_cache.get.assert_called_with(CACHE_KEY_ITEMS)

    def test_get_items_from_fallback(self, cache_service, mock_cache):
        """Test getting items from fallback when cache is empty."""
        mock_cache.get.return_value = None

        with patch.object(cache_service, "_load_from_fallback") as mock_fallback:
            mock_fallback.return_value = {"items": []}
            items = cache_service.get_items()

            assert items == []
            mock_fallback.assert_called_once()

    def test_set_items(self, cache_service, mock_cache, sample_roadmap_items):
        """Test setting items in cache."""
        cache_service.set_items(sample_roadmap_items)

        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args[0]
        assert call_args[0] == CACHE_KEY_ITEMS
        assert len(call_args[1]) == 3

    def test_get_filtered_items_by_status(
        self, cache_service, mock_cache, sample_roadmap_items
    ):
        """Test filtering items by status."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        items = cache_service.get_filtered_items(status="DELIVERED")

        assert len(items) == 1
        assert items[0].status == DeliveryStatus.DELIVERED

    def test_get_filtered_items_by_year(
        self, cache_service, mock_cache, sample_roadmap_items
    ):
        """Test filtering items by year."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        items = cache_service.get_filtered_items(year=2025)

        assert len(items) == 3

    def test_get_filtered_items_by_quarter(
        self, cache_service, mock_cache, sample_roadmap_items
    ):
        """Test filtering items by quarter."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        items = cache_service.get_filtered_items(quarter="Q1")

        assert len(items) == 1
        assert items[0].release_quarter == Quarter.Q1

    def test_get_filtered_items_by_module(
        self, cache_service, mock_cache, sample_roadmap_items
    ):
        """Test filtering items by module."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        items = cache_service.get_filtered_items(module="module-a")

        assert len(items) == 2

    def test_get_item_by_id(self, cache_service, mock_cache, sample_roadmap_items):
        """Test getting item by ID."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        item = cache_service.get_item_by_id("TEST-002")

        assert item is not None
        assert item.id == "TEST-002"

    def test_get_item_by_id_not_found(self, cache_service, mock_cache):
        """Test getting non-existent item returns None."""
        mock_cache.get.return_value = []

        item = cache_service.get_item_by_id("NONEXISTENT")

        assert item is None

    def test_get_modules(self, cache_service, mock_cache, sample_modules):
        """Test getting modules from cache."""
        mock_cache.get.return_value = [m.to_dict() for m in sample_modules]

        modules = cache_service.get_modules()

        assert len(modules) == 2
        assert modules[0].name == "Module A"
        mock_cache.get.assert_called_with(CACHE_KEY_MODULES)

    def test_set_modules(self, cache_service, mock_cache, sample_modules):
        """Test setting modules in cache."""
        cache_service.set_modules(sample_modules)

        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args[0]
        assert call_args[0] == CACHE_KEY_MODULES

    def test_get_metadata(self, cache_service, mock_cache, sample_metadata):
        """Test getting metadata from cache."""
        mock_cache.get.return_value = sample_metadata.to_dict()

        metadata = cache_service.get_metadata()

        assert metadata.last_sync_status == "SUCCESS"
        assert metadata.item_count == 3

    def test_set_metadata(self, cache_service, mock_cache, sample_metadata):
        """Test setting metadata in cache."""
        cache_service.set_metadata(sample_metadata)

        mock_cache.set.assert_called_once()

    def test_get_stats(self, cache_service, mock_cache, sample_roadmap_items):
        """Test getting stats."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        stats = cache_service.get_stats()

        assert stats["stats"]["DELIVERED"] == 1
        assert stats["stats"]["NOW"] == 1
        assert stats["stats"]["NEXT"] == 1
        assert stats["stats"]["FUTURE"] == 0
        assert stats["total"] == 3

    def test_get_stats_with_filters(
        self, cache_service, mock_cache, sample_roadmap_items
    ):
        """Test getting stats with filters."""
        mock_cache.get.return_value = [item.to_dict() for item in sample_roadmap_items]

        stats = cache_service.get_stats(module="module-a")

        assert stats["total"] == 2

    def test_save_to_fallback(self, cache_service, mock_cache):
        """Test saving to fallback file."""
        mock_cache.get.return_value = []

        with patch("builtins.open", MagicMock()):
            with patch("json.dump") as mock_dump:
                cache_service.save_to_fallback()
                mock_dump.assert_called_once()

    def test_load_from_fallback_file_exists(self, cache_service):
        """Test loading from fallback when file exists."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", MagicMock()):
                with patch("json.load", return_value={"items": []}):
                    result = cache_service._load_from_fallback()
                    assert result == {"items": []}

    def test_load_from_fallback_file_not_exists(self, cache_service):
        """Test loading from fallback when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = cache_service._load_from_fallback()
            assert result == {}

    def test_dict_to_item(self, cache_service):
        """Test converting dict to RoadmapItem."""
        data = {
            "id": "TEST-001",
            "title": "Test",
            "description": "Desc",
            "status": "NOW",
            "module": "Test Module",
            "moduleId": "test-module",
            "releaseYear": 2025,
            "releaseQuarter": "Q1",
            "releaseMonth": None,
            "images": [],
            "documentationUrl": None,
            "lastSyncedAt": "2025-01-01T00:00:00Z",
        }

        item = cache_service._dict_to_item(data)

        assert item.id == "TEST-001"
        assert item.status == DeliveryStatus.NOW
        assert item.release_quarter == Quarter.Q1

    def test_dict_to_module(self, cache_service):
        """Test converting dict to Module."""
        data = {"id": "test", "name": "Test", "itemCount": 5}

        module = cache_service._dict_to_module(data)

        assert module.id == "test"
        assert module.item_count == 5

    def test_dict_to_metadata(self, cache_service):
        """Test converting dict to SyncMetadata."""
        data = {
            "lastSyncAt": "2025-01-01T00:00:00Z",
            "lastSyncStatus": "SUCCESS",
            "itemCount": 10,
            "errorMessage": None,
        }

        metadata = cache_service._dict_to_metadata(data)

        assert metadata.last_sync_status == "SUCCESS"
        assert metadata.item_count == 10
