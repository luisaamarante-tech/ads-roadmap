"""
Unit tests for feature request routing configuration loader.
"""

from unittest.mock import MagicMock

import pytest

from app.services.feature_request_routing_loader import FeatureRequestRoutingConfig


@pytest.fixture
def mock_cache_service():
    """Return mock cache service with roadmap items."""
    mock_cache = MagicMock()

    # Create mock roadmap items
    mock_item_1 = MagicMock()
    mock_item_1.id = "NEXUS-123"
    mock_item_1.module_id = "nexus"

    mock_item_2 = MagicMock()
    mock_item_2.id = "ENGAGE-456"
    mock_item_2.module_id = "engage"

    mock_cache.get_items.return_value = [mock_item_1, mock_item_2]

    return mock_cache


class TestFeatureRequestRoutingConfig:
    """Tests for FeatureRequestRoutingConfig."""

    def test_load_valid_config(self, mock_cache_service):
        """Test loading a valid routing configuration from cache."""
        config = FeatureRequestRoutingConfig(cache_service=mock_cache_service)

        assert config.default_issue_type_name == "Task"
        assert len(config.routes) == 2
        assert "nexus" in config.routes
        assert "engage" in config.routes

    def test_get_route_returns_rule(self, mock_cache_service):
        """Test getting a routing rule by module ID."""
        config = FeatureRequestRoutingConfig(cache_service=mock_cache_service)
        rule = config.get_route("nexus")

        assert rule is not None
        assert rule.module_id == "nexus"
        assert rule.jira_project_key == "NEXUS"

    def test_get_route_with_overrides(self, mock_cache_service):
        """Test getting a routing rule with default labels."""
        config = FeatureRequestRoutingConfig(cache_service=mock_cache_service)
        rule = config.get_route("engage")

        assert rule is not None
        assert rule.labels == ["feature-request"]

    def test_get_route_not_found(self, mock_cache_service):
        """Test getting a routing rule for non-existent module."""
        config = FeatureRequestRoutingConfig(cache_service=mock_cache_service)
        rule = config.get_route("unknown")

        assert rule is None

    def test_get_routable_module_ids(self, mock_cache_service):
        """Test getting list of all routable module IDs."""
        config = FeatureRequestRoutingConfig(cache_service=mock_cache_service)
        module_ids = config.get_routable_module_ids()

        assert len(module_ids) == 2
        assert "nexus" in module_ids
        assert "engage" in module_ids

    def test_is_routable(self, mock_cache_service):
        """Test checking if a module is routable."""
        config = FeatureRequestRoutingConfig(cache_service=mock_cache_service)

        assert config.is_routable("nexus") is True
        assert config.is_routable("unknown") is False

    def test_no_cache_service(self):
        """Test initialization without cache service."""
        config = FeatureRequestRoutingConfig()

        assert len(config.routes) == 0
        assert config.default_issue_type_name == "Task"
