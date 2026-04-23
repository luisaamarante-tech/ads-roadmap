"""Unit tests for roadmap models."""

from datetime import datetime

from app.models import DeliveryStatus, Module, Quarter, RoadmapItem, SyncMetadata


class TestDeliveryStatus:
    """Tests for DeliveryStatus enum."""

    def test_delivery_status_values(self):
        """Test that all delivery status values exist."""
        assert DeliveryStatus.DELIVERED.value == "DELIVERED"
        assert DeliveryStatus.NOW.value == "NOW"
        assert DeliveryStatus.NEXT.value == "NEXT"
        assert DeliveryStatus.FUTURE.value == "FUTURE"

    def test_delivery_status_from_string(self):
        """Test creating DeliveryStatus from string."""
        assert DeliveryStatus("DELIVERED") == DeliveryStatus.DELIVERED
        assert DeliveryStatus("NOW") == DeliveryStatus.NOW


class TestQuarter:
    """Tests for Quarter enum."""

    def test_quarter_values(self):
        """Test that all quarter values exist."""
        assert Quarter.Q1.value == "Q1"
        assert Quarter.Q2.value == "Q2"
        assert Quarter.Q3.value == "Q3"
        assert Quarter.Q4.value == "Q4"


class TestRoadmapItem:
    """Tests for RoadmapItem dataclass."""

    def test_create_roadmap_item(self, sample_roadmap_item):
        """Test creating a RoadmapItem."""
        assert sample_roadmap_item.id == "TEST-123"
        assert sample_roadmap_item.title == "Test Feature"
        assert sample_roadmap_item.status == DeliveryStatus.NOW

    def test_roadmap_item_auto_module_id(self):
        """Test that module_id is auto-generated from module name."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="My Test Module",
            module_id="",
            release_year=2025,
            release_quarter=Quarter.Q1,
        )
        assert item.module_id == "my-test-module"

    def test_roadmap_item_limits_images(self):
        """Test that images are limited to 4."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="Test",
            module_id="test",
            release_year=2025,
            release_quarter=Quarter.Q1,
            images=["a", "b", "c", "d", "e", "f"],
        )
        assert len(item.images) == 4

    def test_roadmap_item_to_dict(self, sample_roadmap_item):
        """Test converting RoadmapItem to dictionary."""
        data = sample_roadmap_item.to_dict()
        assert data["id"] == "TEST-123"
        assert data["title"] == "Test Feature"
        assert data["status"] == "NOW"
        assert data["moduleId"] == "test-module"
        assert data["releaseYear"] == 2025
        assert data["releaseQuarter"] == "Q1"

    def test_roadmap_item_matches_filters_all(self, sample_roadmap_item):
        """Test filter matching with all filters."""
        assert sample_roadmap_item.matches_filters(
            status="NOW",
            year=2025,
            quarter="Q1",
            module="test-module",
        )

    def test_roadmap_item_matches_filters_partial(self, sample_roadmap_item):
        """Test filter matching with partial filters."""
        assert sample_roadmap_item.matches_filters(status="NOW")
        assert sample_roadmap_item.matches_filters(year=2025)
        assert sample_roadmap_item.matches_filters()

    def test_roadmap_item_no_match(self, sample_roadmap_item):
        """Test filter not matching."""
        assert not sample_roadmap_item.matches_filters(status="DELIVERED")
        assert not sample_roadmap_item.matches_filters(year=2024)
        assert not sample_roadmap_item.matches_filters(quarter="Q4")

    def test_roadmap_item_slugify(self):
        """Test slugify static method."""
        assert RoadmapItem._slugify("Hello World") == "hello-world"
        assert RoadmapItem._slugify("Test@Module!") == "testmodule"
        assert RoadmapItem._slugify("  spaces  ") == "spaces"

    def test_roadmap_item_status_string_conversion(self):
        """Test that string status is converted to enum."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status="NOW",  # type: ignore
            module="Test",
            module_id="test",
            release_year=2025,
            release_quarter="Q1",  # type: ignore
        )
        assert item.status == DeliveryStatus.NOW
        assert item.release_quarter == Quarter.Q1

    def test_roadmap_item_includes_likes_field(self):
        """Test that RoadmapItem includes likes field with default value 0."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="Test",
            module_id="test",
            release_year=2025,
            release_quarter=Quarter.Q1,
        )
        assert hasattr(item, "likes")
        assert item.likes == 0

    def test_roadmap_item_likes_field_custom_value(self):
        """Test that RoadmapItem accepts custom likes value."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="Test",
            module_id="test",
            release_year=2025,
            release_quarter=Quarter.Q1,
            likes=42,
        )
        assert item.likes == 42

    def test_roadmap_item_to_dict_includes_likes(self):
        """Test that to_dict() serializes likes field."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="Test",
            module_id="test",
            release_year=2025,
            release_quarter=Quarter.Q1,
            likes=15,
        )
        data = item.to_dict()
        assert "likes" in data
        assert data["likes"] == 15

    def test_roadmap_item_matches_filters_module_list(self):
        """Test filter matching with module as a list."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="Test Module",
            module_id="test-module",
            release_year=2025,
            release_quarter=Quarter.Q1,
        )
        # Should match when module_id is in the list
        assert item.matches_filters(module=["test-module", "other-module"])
        # Should not match when module_id is not in the list
        assert not item.matches_filters(module=["other-module", "another-module"])

    def test_roadmap_item_matches_filters_empty_module_list(self):
        """Test filter matching with empty module list (should match all)."""
        item = RoadmapItem(
            id="TEST-001",
            title="Test",
            description="Desc",
            status=DeliveryStatus.NOW,
            module="Test Module",
            module_id="test-module",
            release_year=2025,
            release_quarter=Quarter.Q1,
        )
        # Empty list should match all items (no filtering)
        assert item.matches_filters(module=[])


class TestModule:
    """Tests for Module dataclass."""

    def test_create_module(self):
        """Test creating a Module."""
        module = Module(id="test-module", name="Test Module", item_count=5)
        assert module.id == "test-module"
        assert module.name == "Test Module"
        assert module.item_count == 5

    def test_module_to_dict(self):
        """Test converting Module to dictionary."""
        module = Module(id="test-module", name="Test Module", item_count=5)
        data = module.to_dict()
        assert data["id"] == "test-module"
        assert data["name"] == "Test Module"
        assert data["itemCount"] == 5


class TestSyncMetadata:
    """Tests for SyncMetadata dataclass."""

    def test_create_sync_metadata(self, sample_metadata):
        """Test creating SyncMetadata."""
        assert sample_metadata.last_sync_status == "SUCCESS"
        assert sample_metadata.item_count == 3
        assert sample_metadata.error_message is None

    def test_sync_metadata_to_dict(self, sample_metadata):
        """Test converting SyncMetadata to dictionary."""
        data = sample_metadata.to_dict()
        assert data["lastSyncStatus"] == "SUCCESS"
        assert data["itemCount"] == 3
        assert "lastSyncAt" in data

    def test_sync_metadata_is_stale_true(self):
        """Test is_stale returns True for old data."""
        old_metadata = SyncMetadata(
            last_sync_at=datetime(2020, 1, 1),
            last_sync_status="SUCCESS",
            item_count=0,
        )
        assert old_metadata.is_stale(threshold_minutes=1)

    def test_sync_metadata_is_stale_no_sync(self):
        """Test is_stale returns True when never synced."""
        metadata = SyncMetadata()
        assert metadata.is_stale()

    def test_sync_metadata_is_stale_fresh(self):
        """Test is_stale returns False for fresh data."""
        fresh_metadata = SyncMetadata(
            last_sync_at=datetime.utcnow(),
            last_sync_status="SUCCESS",
            item_count=5,
        )
        assert not fresh_metadata.is_stale(threshold_minutes=10)
