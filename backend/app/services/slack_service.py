"""
Slack notification service for feature requests.

Sends webhook notifications to the leaders' channel when feature
requests are submitted.
"""

import logging
import time
from typing import Optional

import requests

from ..config import Config

logger = logging.getLogger(__name__)


class SlackService:
    """
    Service for sending Slack notifications via incoming webhooks.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack service.

        Args:
            webhook_url: Slack incoming webhook URL.
                        If None, uses Config.SLACK_FEATURE_REQUEST_WEBHOOK_URL
        """
        self.webhook_url = webhook_url or Config.SLACK_FEATURE_REQUEST_WEBHOOK_URL
        self.max_retries = 3
        self.retry_delay_seconds = 1
        self.timeout_seconds = 10

    def send_feature_request_notification(
        self,
        module_name: str,
        title: str,
        description_excerpt: str,
        contact_email: str,
        jira_issue_key: str,
        jira_issue_url: str,
    ) -> tuple[bool, str]:
        """
        Send a feature request notification to the leaders' channel.

        Args:
            module_name: Module display name
            title: Feature request title
            description_excerpt: Short excerpt from description (max 200 chars)
            contact_email: Requester email
            jira_issue_key: Created Jira issue key
            jira_issue_url: Browse URL for the issue

        Returns:
            Tuple of (success: bool, status: str)
            Status can be: "SENT", "FAILED"
        """
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured, skipping notification")
            return False, "FAILED"

        # Build message payload
        message = self._build_message(
            module_name=module_name,
            title=title,
            description_excerpt=description_excerpt,
            contact_email=contact_email,
            jira_issue_key=jira_issue_key,
            jira_issue_url=jira_issue_url,
        )

        # Send with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=message,
                    timeout=self.timeout_seconds,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    logger.info(
                        f"Slack notification sent successfully for {jira_issue_key}"
                    )
                    return True, "SENT"
                else:
                    logger.warning(
                        f"Slack notification failed (attempt {attempt}/{self.max_retries}): "
                        f"status {response.status_code}, response: {response.text}"
                    )

            except requests.RequestException as e:
                logger.warning(
                    f"Slack notification error (attempt {attempt}/{self.max_retries}): {e}"
                )

            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                # Exponential backoff
                delay = self.retry_delay_seconds * (2 ** (attempt - 1))
                time.sleep(delay)

        # All retries exhausted
        logger.error(
            f"Slack notification failed after {self.max_retries} attempts for {jira_issue_key}"
        )
        return False, "FAILED"

    def _build_message(
        self,
        module_name: str,
        title: str,
        description_excerpt: str,
        contact_email: str,
        jira_issue_key: str,
        jira_issue_url: str,
    ) -> dict:
        """
        Build Slack message payload with sanitized inputs.

        Args:
            module_name: Module display name
            title: Feature request title
            description_excerpt: Short description excerpt
            contact_email: Requester email
            jira_issue_key: Jira issue key
            jira_issue_url: Jira issue URL

        Returns:
            Slack webhook message payload
        """
        # Sanitize inputs (remove special Slack formatting chars)
        module_name = self._sanitize_slack_text(module_name)
        title = self._sanitize_slack_text(title)
        description_excerpt = self._sanitize_slack_text(description_excerpt)
        contact_email = self._sanitize_slack_text(contact_email)

        # Truncate description to 200 chars
        if len(description_excerpt) > 200:
            description_excerpt = description_excerpt[:197] + "..."

        text = (
            f":bulb: *New Feature Request*\n\n"
            f"*Module:* {module_name}\n"
            f"*Title:* {title}\n"
            f"*Description:* {description_excerpt}\n"
            f"*Contact:* {contact_email}\n"
            f"*Jira Issue:* <{jira_issue_url}|{jira_issue_key}>"
        )

        return {"text": text}

    def _sanitize_slack_text(self, text: str) -> str:
        """
        Sanitize text for Slack to prevent formatting injection.

        Args:
            text: Raw text

        Returns:
            Sanitized text safe for Slack
        """
        if not text:
            return ""

        # Escape special Slack markdown characters
        # Don't escape * and _ in user content to prevent display issues
        text = text.replace("<", "&lt;").replace(">", "&gt;")

        # Remove control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

        return text.strip()
