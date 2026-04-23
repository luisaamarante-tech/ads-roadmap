"""
Unit tests for Slack notification service.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.services.slack_service import SlackService


class TestSlackService:
    """Tests for SlackService."""

    @pytest.fixture
    def slack_service(self):
        """Create SlackService with test webhook URL."""
        return SlackService(webhook_url="https://hooks.slack.com/services/TEST/WEBHOOK")

    def test_send_notification_success(self, slack_service):
        """Test successful Slack notification."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            success, status = slack_service.send_feature_request_notification(
                module_name="Nexus",
                title="Test Feature",
                description_excerpt="This is a test",
                contact_email="user@example.com",
                jira_issue_key="NEXUS-123",
                jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
            )

            assert success is True
            assert status == "SENT"
            mock_post.assert_called_once()

    def test_send_notification_with_retry(self, slack_service):
        """Test Slack notification with retry on failure."""
        with patch("requests.post") as mock_post:
            # Fail first, succeed second
            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 500
            mock_response_fail.text = "Internal Server Error"

            mock_response_success = MagicMock()
            mock_response_success.status_code = 200

            mock_post.side_effect = [mock_response_fail, mock_response_success]

            with patch("time.sleep"):  # Mock sleep to speed up test
                success, status = slack_service.send_feature_request_notification(
                    module_name="Nexus",
                    title="Test Feature",
                    description_excerpt="Test description",
                    contact_email="user@example.com",
                    jira_issue_key="NEXUS-123",
                    jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
                )

            assert success is True
            assert status == "SENT"
            assert mock_post.call_count == 2

    def test_send_notification_all_retries_fail(self, slack_service):
        """Test Slack notification when all retries fail."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response

            with patch("time.sleep"):  # Mock sleep to speed up test
                success, status = slack_service.send_feature_request_notification(
                    module_name="Nexus",
                    title="Test Feature",
                    description_excerpt="Test",
                    contact_email="user@example.com",
                    jira_issue_key="NEXUS-123",
                    jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
                )

            assert success is False
            assert status == "FAILED"
            assert mock_post.call_count == 3  # max_retries

    def test_send_notification_network_error(self, slack_service):
        """Test Slack notification with network error."""
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Network error")

            with patch("time.sleep"):
                success, status = slack_service.send_feature_request_notification(
                    module_name="Nexus",
                    title="Test",
                    description_excerpt="Test",
                    contact_email="user@example.com",
                    jira_issue_key="NEXUS-123",
                    jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
                )

            assert success is False
            assert status == "FAILED"

    def test_send_notification_no_webhook_configured(self):
        """Test notification when webhook URL not configured."""
        slack_service = SlackService(webhook_url="")

        success, status = slack_service.send_feature_request_notification(
            module_name="Nexus",
            title="Test",
            description_excerpt="Test",
            contact_email="user@example.com",
            jira_issue_key="NEXUS-123",
            jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
        )

        assert success is False
        assert status == "FAILED"

    def test_build_message_truncates_description(self, slack_service):
        """Test that long descriptions are truncated."""
        long_description = "A" * 250

        message = slack_service._build_message(
            module_name="Nexus",
            title="Test",
            description_excerpt=long_description,
            contact_email="user@example.com",
            jira_issue_key="NEXUS-123",
            jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
        )

        # Check that description was truncated to 200 chars (197 + "...")
        assert "..." in message["text"]
        # Description should be truncated to exactly 200 chars
        text = message["text"]
        # Extract the description part between "*Description:* " and "\n*Contact:*"
        desc_start = text.find("*Description:* ") + len("*Description:* ")
        desc_end = text.find("\n*Contact:*")
        description_in_message = text[desc_start:desc_end]
        assert len(description_in_message) == 200
        assert description_in_message.endswith("...")

    def test_build_message_format(self, slack_service):
        """Test message format includes all required fields."""
        message = slack_service._build_message(
            module_name="Nexus",
            title="Test Feature",
            description_excerpt="Test description",
            contact_email="user@example.com",
            jira_issue_key="NEXUS-123",
            jira_issue_url="https://test.atlassian.net/browse/NEXUS-123",
        )

        text = message["text"]
        assert "Nexus" in text
        assert "Test Feature" in text
        assert "Test description" in text
        assert "user@example.com" in text
        assert "NEXUS-123" in text
        assert "https://test.atlassian.net/browse/NEXUS-123" in text
