"""
Unit tests for feature request idempotency handling.
"""

from unittest.mock import MagicMock

import pytest

from app.services.cache_service import CacheService


class TestIdempotencyOperations:
    """Tests for idempotency cache operations."""

    @pytest.fixture
    def mock_cache(self):
        """Mock cache backend."""
        return MagicMock()

    @pytest.fixture
    def cache_service(self, mock_cache):
        """Create CacheService with mock cache."""
        return CacheService(mock_cache)

    def test_set_and_get_idempotency_response(self, cache_service, mock_cache):
        """Test setting and retrieving idempotency response."""
        test_key = "test-key-123"
        test_response = {
            "success": True,
            "issueKey": "NEXUS-123",
            "message": "Test",
        }

        # Set response
        cache_service.set_idempotency_response(test_key, test_response)

        # Verify cache.set was called
        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        assert call_args[0][0] == f"idempotency:{test_key}"
        assert call_args[0][1] == test_response
        assert call_args[1]["timeout"] == 3600  # Default TTL

    def test_get_idempotency_response_hit(self, cache_service, mock_cache):
        """Test retrieving cached idempotency response (cache hit)."""
        test_key = "test-key-123"
        test_response = {"success": True, "issueKey": "NEXUS-123"}

        mock_cache.get.return_value = test_response

        result = cache_service.get_idempotency_response(test_key)

        assert result == test_response
        mock_cache.get.assert_called_once_with(f"idempotency:{test_key}")

    def test_get_idempotency_response_miss(self, cache_service, mock_cache):
        """Test retrieving idempotency response when not cached (cache miss)."""
        test_key = "test-key-456"

        mock_cache.get.return_value = None

        result = cache_service.get_idempotency_response(test_key)

        assert result is None
        mock_cache.get.assert_called_once_with(f"idempotency:{test_key}")

    def test_set_idempotency_custom_ttl(self, cache_service, mock_cache):
        """Test setting idempotency response with custom TTL."""
        test_key = "test-key-789"
        test_response = {"success": True}
        custom_ttl = 1800  # 30 minutes

        cache_service.set_idempotency_response(test_key, test_response, custom_ttl)

        call_args = mock_cache.set.call_args
        assert call_args[1]["timeout"] == custom_ttl

    def test_get_idempotency_invalid_key_length(self, cache_service, mock_cache):
        """Test handling of invalid idempotency key (too long)."""
        invalid_key = "x" * 200  # Exceeds max length

        result = cache_service.get_idempotency_response(invalid_key)

        assert result is None
        mock_cache.get.assert_not_called()

    def test_get_idempotency_empty_key(self, cache_service, mock_cache):
        """Test handling of empty idempotency key."""
        result = cache_service.get_idempotency_response("")

        assert result is None
        mock_cache.get.assert_not_called()

    def test_set_idempotency_invalid_key(self, cache_service, mock_cache):
        """Test setting response with invalid key skips cache."""
        invalid_key = "x" * 200
        test_response = {"success": True}

        cache_service.set_idempotency_response(invalid_key, test_response)

        mock_cache.set.assert_not_called()

    def test_get_idempotency_cache_failure(self, cache_service, mock_cache):
        """Test graceful handling of cache backend failure on get."""
        test_key = "test-key-fail"
        mock_cache.get.side_effect = Exception("Cache unavailable")

        result = cache_service.get_idempotency_response(test_key)

        assert result is None  # Graceful fallback

    def test_set_idempotency_cache_failure(self, cache_service, mock_cache):
        """Test graceful handling of cache backend failure on set."""
        test_key = "test-key-fail"
        test_response = {"success": True}
        mock_cache.set.side_effect = Exception("Cache unavailable")

        # Should not raise exception
        cache_service.set_idempotency_response(test_key, test_response)

        # Verify it attempted to set
        mock_cache.set.assert_called_once()
