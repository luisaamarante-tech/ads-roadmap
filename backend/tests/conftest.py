"""Pytest configuration and shared fixtures."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from app.models import DeliveryStatus, Module, Quarter, RoadmapItem, SyncMetadata


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield


@pytest.fixture
def mock_cache():
    """Mock Flask-Caching instance."""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = True
    return cache


@pytest.fixture
def sample_roadmap_item():
    """Sample RoadmapItem for testing."""
    return RoadmapItem(
        id="TEST-123",
        title="Test Feature",
        description="A test feature description",
        status=DeliveryStatus.NOW,
        module="Test Module",
        module_id="test-module",
        release_year=2025,
        release_quarter=Quarter.Q1,
    )


@pytest.fixture
def sample_roadmap_items():
    """List of sample RoadmapItems for testing."""
    return [
        RoadmapItem(
            id="TEST-001",
            title="Feature One",
            description="Description one",
            status=DeliveryStatus.DELIVERED,
            module="Module A",
            module_id="module-a",
            release_year=2025,
            release_quarter=Quarter.Q1,
        ),
        RoadmapItem(
            id="TEST-002",
            title="Feature Two",
            description="Description two",
            status=DeliveryStatus.NOW,
            module="Module A",
            module_id="module-a",
            release_year=2025,
            release_quarter=Quarter.Q2,
        ),
        RoadmapItem(
            id="TEST-003",
            title="Feature Three",
            description="Description three",
            status=DeliveryStatus.NEXT,
            module="Module B",
            module_id="module-b",
            release_year=2025,
            release_quarter=Quarter.Q3,
        ),
    ]


@pytest.fixture
def sample_modules():
    """List of sample Modules for testing."""
    return [
        Module(id="module-a", name="Module A", item_count=2),
        Module(id="module-b", name="Module B", item_count=1),
    ]


@pytest.fixture
def sample_metadata():
    """Sample SyncMetadata for testing."""
    return SyncMetadata(
        last_sync_at=datetime(2025, 1, 1, 12, 0, 0),
        last_sync_status="SUCCESS",
        item_count=3,
        error_message=None,
    )


@pytest.fixture
def mock_jira_response():
    """Mock JIRA API response."""
    return {
        "issues": [
            {
                "key": "TEST-123",
                "fields": {
                    "project": {"key": "PROJ"},
                    "summary": "Test Feature",
                    "description": {
                        "type": "doc",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"type": "text", "text": "Description text"}
                                ],
                            }
                        ],
                    },
                    "customfield_10001": {"value": "Yes"},
                    "customfield_10002": {"value": "NOW"},
                    "customfield_10003": {"value": "Test Module"},
                    "customfield_10004": 2025,
                    "customfield_10005": {"value": "Q1"},
                    "customfield_10006": None,
                    "customfield_10007": "https://docs.example.com",
                    "attachment": [],
                },
            }
        ]
    }


@pytest.fixture
def mock_jira_client():
    """Mock JiraClient for testing."""
    with patch("app.services.jira_client.JiraClient") as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_requests():
    """Mock requests library for JIRA API calls."""
    with patch("app.services.jira_client.requests") as mock:
        yield mock
