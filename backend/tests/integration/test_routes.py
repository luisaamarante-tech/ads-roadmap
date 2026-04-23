"""Integration tests for roadmap routes."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models import SyncMetadata


class TestRoadmapRoutes:
    """Integration tests for /api/v1/roadmap/* endpoints."""

    @pytest.fixture
    def mock_cache_service(self, sample_roadmap_items, sample_modules, sample_metadata):
        """Mock CacheService for route testing."""
        with patch("app.routes.roadmap.CacheService") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            # Setup default returns
            mock_instance.get_filtered_items.return_value = sample_roadmap_items
            mock_instance.get_items.return_value = sample_roadmap_items
            mock_instance.get_item_by_id.return_value = sample_roadmap_items[0]
            mock_instance.get_modules.return_value = sample_modules
            mock_instance.get_metadata.return_value = sample_metadata
            mock_instance.get_stats.return_value = {
                "stats": {"DELIVERED": 1, "NOW": 1, "NEXT": 1, "FUTURE": 0},
                "total": 3,
            }

            yield mock_instance

    def test_get_items(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items returns items."""
        response = client.get("/api/v1/roadmap/items")

        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert "total" in data
        assert "lastSyncedAt" in data
        assert "isStale" in data

    def test_get_items_with_status_filter(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items?status=DELIVERED."""
        response = client.get("/api/v1/roadmap/items?status=DELIVERED")

        assert response.status_code == 200
        mock_cache_service.get_filtered_items.assert_called_once()
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        assert call_kwargs["status"] == "DELIVERED"

    def test_get_items_with_year_filter(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items?year=2025."""
        response = client.get("/api/v1/roadmap/items?year=2025")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        assert call_kwargs["year"] == 2025

    def test_get_items_with_quarter_filter(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items?quarter=Q1."""
        response = client.get("/api/v1/roadmap/items?quarter=Q1")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        assert call_kwargs["quarter"] == "Q1"

    def test_get_items_with_module_filter(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items?module=module-a."""
        response = client.get("/api/v1/roadmap/items?module=module-a")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        assert call_kwargs["module"] == "module-a"

    def test_get_items_with_multiple_filters(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items with multiple filters."""
        response = client.get("/api/v1/roadmap/items?status=NOW&year=2025&quarter=Q2")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        assert call_kwargs["status"] == "NOW"
        assert call_kwargs["year"] == 2025
        assert call_kwargs["quarter"] == "Q2"

    def test_get_items_with_multiple_modules(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items?module=X&module=Y for multi-module filtering."""
        response = client.get("/api/v1/roadmap/items?module=flows&module=integrations")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        # Should pass module as a list
        assert call_kwargs["module"] == ["flows", "integrations"]

    def test_get_items_with_no_module(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items with no module parameter (show all)."""
        response = client.get("/api/v1/roadmap/items")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_filtered_items.call_args[1]
        # Should be None when no module param provided
        assert call_kwargs.get("module") is None

    def test_get_item_by_id(self, client, mock_cache_service, sample_roadmap_items):
        """Test GET /api/v1/roadmap/items/<id> returns single item."""
        response = client.get("/api/v1/roadmap/items/TEST-001")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == "TEST-001"

    def test_get_item_by_id_not_found(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/items/<id> returns 404 for missing item."""
        mock_cache_service.get_item_by_id.return_value = None

        response = client.get("/api/v1/roadmap/items/NONEXISTENT")

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "NOT_FOUND"

    def test_get_modules(self, client, mock_cache_service, sample_modules):
        """Test GET /api/v1/roadmap/modules returns modules."""
        response = client.get("/api/v1/roadmap/modules")

        assert response.status_code == 200
        data = response.get_json()
        assert "modules" in data
        assert len(data["modules"]) == 2

    def test_get_stats(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/stats returns statistics."""
        response = client.get("/api/v1/roadmap/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert "stats" in data
        assert "total" in data
        assert data["stats"]["DELIVERED"] == 1
        assert data["stats"]["NOW"] == 1

    def test_get_stats_with_filters(self, client, mock_cache_service):
        """Test GET /api/v1/roadmap/stats with filters."""
        response = client.get("/api/v1/roadmap/stats?year=2025&module=module-a")

        assert response.status_code == 200
        call_kwargs = mock_cache_service.get_stats.call_args[1]
        assert call_kwargs["year"] == 2025
        assert call_kwargs["module"] == "module-a"

    def test_like_item_success(self, client, mock_cache_service, sample_roadmap_items):
        """Test POST /api/v1/roadmap/items/{id}/like success case."""
        mock_cache_service.get_item_by_id.return_value = sample_roadmap_items[0]
        mock_cache_service.update_item_likes.return_value = True

        with patch("app.services.jira_client.JiraClient") as mock_jira_class:
            mock_jira = MagicMock()
            mock_jira_class.return_value = mock_jira
            mock_jira.update_epic_likes.return_value = 16

            response = client.post("/api/v1/roadmap/items/TEST-001/like")

            assert response.status_code == 200
            data = response.get_json()
            assert data["id"] == "TEST-001"
            assert data["likes"] == 16
            assert data["success"] is True
            mock_jira.update_epic_likes.assert_called_once()
            mock_cache_service.update_item_likes.assert_called_once_with("TEST-001", 16)

    def test_like_item_not_found(self, client, mock_cache_service):
        """Test POST /api/v1/roadmap/items/{id}/like with invalid item ID."""
        mock_cache_service.get_item_by_id.return_value = None

        response = client.post("/api/v1/roadmap/items/INVALID-999/like")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_like_item_jira_error(
        self, client, mock_cache_service, sample_roadmap_items
    ):
        """Test POST /api/v1/roadmap/items/{id}/like with JIRA API error."""
        mock_cache_service.get_item_by_id.return_value = sample_roadmap_items[0]

        with patch("app.services.jira_client.JiraClient") as mock_jira_class:
            mock_jira = MagicMock()
            mock_jira_class.return_value = mock_jira
            mock_jira.update_epic_likes.side_effect = Exception("JIRA API unavailable")

            response = client.post("/api/v1/roadmap/items/TEST-001/like")

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data


class TestHealthRoutes:
    """Integration tests for /api/v1/health endpoint."""

    def test_health_endpoint(self, client):
        """Test GET /api/v1/health returns health status."""
        with patch("app.routes.health.CacheService") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance
            mock_instance.get_metadata.return_value = SyncMetadata(
                last_sync_at=datetime.utcnow(),
                last_sync_status="SUCCESS",
                item_count=10,
            )

            response = client.get("/api/v1/health")

            assert response.status_code == 200
            data = response.get_json()
            assert "status" in data
