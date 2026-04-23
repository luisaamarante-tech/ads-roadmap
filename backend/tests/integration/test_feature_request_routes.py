"""
Integration tests for feature request routes.

Mocks external services (Jira API) to test the full request flow.
"""

from unittest.mock import MagicMock, patch

import pytest

from app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_routing_config():
    """Mock routing configuration."""
    mock_config = MagicMock()
    mock_config.get_routable_module_ids.return_value = ["nexus", "engage"]

    mock_route = MagicMock()
    mock_route.jira_project_key = "NEXUS"
    mock_route.jira_issue_type_name = None
    mock_route.labels = None

    mock_config.get_route.return_value = mock_route
    mock_config.default_issue_type_name = "Task"
    return mock_config


@pytest.fixture
def mock_jira_client():
    """Mock Jira client."""
    mock_client = MagicMock()
    mock_client.create_issue.return_value = {
        "key": "NEXUS-123",
        "id": "10001",
        "self": "https://test.atlassian.net/rest/api/3/issue/10001",
    }
    return mock_client


class TestFeatureRequestModulesEndpoint:
    """Tests for GET /feature-request/modules."""

    def test_get_requestable_modules(self, client, mock_routing_config):
        """Test getting requestable modules."""
        with patch(
            "app.routes.roadmap.get_routing_config", return_value=mock_routing_config
        ):
            with patch("app.routes.roadmap.CacheService") as mock_cache_service:
                mock_module_1 = MagicMock()
                mock_module_1.id = "nexus"
                mock_module_1.to_dict.return_value = {"id": "nexus", "name": "Nexus"}

                mock_module_2 = MagicMock()
                mock_module_2.id = "engage"
                mock_module_2.to_dict.return_value = {
                    "id": "engage",
                    "name": "Engage",
                }

                mock_module_3 = MagicMock()
                mock_module_3.id = "other"
                mock_module_3.to_dict.return_value = {"id": "other", "name": "Other"}

                mock_cache = MagicMock()
                mock_cache.get_modules.return_value = [
                    mock_module_1,
                    mock_module_2,
                    mock_module_3,
                ]
                mock_cache_service.return_value = mock_cache

                response = client.get("/api/v1/roadmap/feature-request/modules")

                assert response.status_code == 200
                data = response.get_json()
                assert "modules" in data
                assert len(data["modules"]) == 2  # Only routable modules
                module_ids = [m["id"] for m in data["modules"]]
                assert "nexus" in module_ids
                assert "engage" in module_ids
                assert "other" not in module_ids


class TestCreateFeatureRequestEndpoint:
    """Tests for POST /feature-requests."""

    def test_create_feature_request_success(
        self, client, mock_routing_config, mock_jira_client
    ):
        """Test successful feature request creation."""
        with patch(
            "app.routes.roadmap.get_routing_config", return_value=mock_routing_config
        ):
            with patch("app.routes.roadmap.JiraClient", return_value=mock_jira_client):
                with patch("app.routes.roadmap.CacheService") as mock_cache_service:
                    mock_cache = MagicMock()
                    mock_cache.get_idempotency_response.return_value = None
                    mock_cache_service.return_value = mock_cache

                    payload = {
                        "moduleId": "nexus",
                        "title": "Add bulk export feature",
                        "description": "We need to export reports as CSV files for our team.",
                        "contactEmail": "user@example.com",
                    }

                    response = client.post(
                        "/api/v1/roadmap/feature-requests",
                        json=payload,
                        headers={"Idempotency-Key": "test-key-123"},
                    )

                    assert response.status_code == 201
                    data = response.get_json()
                    assert data["success"] is True
                    assert data["issueKey"] == "NEXUS-123"
                    assert "issueUrl" in data

                    # Verify Jira client was called with correct params
                    mock_jira_client.create_issue.assert_called_once()
                    call_args = mock_jira_client.create_issue.call_args[1]
                    assert call_args["project_key"] == "NEXUS"
                    assert call_args["summary"].startswith("[FEATURE-REQUEST]")

    def test_create_feature_request_missing_idempotency_key(self, client):
        """Test request without idempotency key."""
        payload = {
            "moduleId": "nexus",
            "title": "Test",
            "description": "Test description",
            "contactEmail": "user@example.com",
        }

        response = client.post("/api/v1/roadmap/feature-requests", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "MISSING_IDEMPOTENCY_KEY"

    def test_create_feature_request_missing_fields(self, client):
        """Test request with missing required fields."""
        payload = {"moduleId": "nexus"}

        response = client.post(
            "/api/v1/roadmap/feature-requests",
            json=payload,
            headers={"Idempotency-Key": "test-key"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "VALIDATION_ERROR"

    def test_create_feature_request_honeypot_triggered(self, client):
        """Test request with honeypot field filled (bot detection)."""
        payload = {
            "moduleId": "nexus",
            "title": "Test",
            "description": "Test description",
            "contactEmail": "user@example.com",
            "website": "http://spam.com",
        }

        response = client.post(
            "/api/v1/roadmap/feature-requests",
            json=payload,
            headers={"Idempotency-Key": "test-key"},
        )

        assert response.status_code == 400

    def test_create_feature_request_invalid_module(self, client, mock_routing_config):
        """Test request with non-routable module."""
        mock_routing_config.get_route.return_value = None

        with patch(
            "app.routes.roadmap.get_routing_config", return_value=mock_routing_config
        ):
            payload = {
                "moduleId": "unknown",
                "title": "Test",
                "description": "Test description",
                "contactEmail": "user@example.com",
            }

            response = client.post(
                "/api/v1/roadmap/feature-requests",
                json=payload,
                headers={"Idempotency-Key": "test-key"},
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["error"] == "INVALID_MODULE"

    def test_create_feature_request_idempotency(
        self, client, mock_routing_config, mock_jira_client
    ):
        """Test idempotency - same key returns cached response."""
        cached_response = {
            "success": True,
            "issueKey": "NEXUS-456",
            "issueUrl": "https://test.atlassian.net/browse/NEXUS-456",
            "leaderNotificationStatus": "SENT",
            "message": "Feature request submitted successfully",
        }

        with patch(
            "app.routes.roadmap.get_routing_config", return_value=mock_routing_config
        ):
            with patch("app.routes.roadmap.CacheService") as mock_cache_service:
                mock_cache = MagicMock()
                mock_cache.get_idempotency_response.return_value = cached_response
                mock_cache_service.return_value = mock_cache

                payload = {
                    "moduleId": "nexus",
                    "title": "Test",
                    "description": "Test description",
                    "contactEmail": "user@example.com",
                }

                response = client.post(
                    "/api/v1/roadmap/feature-requests",
                    json=payload,
                    headers={"Idempotency-Key": "test-key"},
                )

                assert response.status_code == 200  # 200, not 201 for cached
                data = response.get_json()
                assert data["issueKey"] == "NEXUS-456"

                # Verify Jira was NOT called (used cache)
                mock_jira_client.create_issue.assert_not_called()
