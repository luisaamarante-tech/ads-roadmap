"""
Data models for feature request submissions.

These are DTOs (Data Transfer Objects) for validating and processing
feature requests from the roadmap page.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeatureRequestPayload:
    """
    User-submitted feature request payload.

    Attributes:
        module_id: Selected module slug (must match routing config)
        title: Short summary of the feature request
        description: Detailed explanation of the need and context
        contact_email: Email for follow-up
        website: Honeypot field for bot mitigation (must be empty)
    """

    module_id: str
    title: str
    description: str
    contact_email: str
    pillar: str = ""
    website: str = ""  # Honeypot field

    def __post_init__(self):
        """Trim whitespace from text fields."""
        self.module_id = self.module_id.strip() if self.module_id else ""
        self.title = self.title.strip() if self.title else ""
        self.description = self.description.strip() if self.description else ""
        self.contact_email = self.contact_email.strip() if self.contact_email else ""
        self.pillar = self.pillar.strip() if self.pillar else ""


@dataclass
class FeatureRequestRoutingRule:
    """
    Routing rule for mapping module to Jira destination.

    Attributes:
        module_id: Module identifier (slug)
        jira_project_key: Target Jira project key
        jira_issue_type_name: Optional issue type override
        labels: Optional labels to apply
    """

    module_id: str
    jira_project_key: str
    jira_issue_type_name: Optional[str] = None
    labels: Optional[list[str]] = None


@dataclass
class JiraIssueReference:
    """
    Reference to a created Jira issue.

    Attributes:
        key: Jira issue key (e.g., "NEXUS-123")
        url: Browse URL for the issue
        created_at: When Jira confirmed creation
    """

    key: str
    url: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class FeatureRequestResponse:
    """
    Response returned to the requester after submission.

    Attributes:
        success: True if Jira issue was created
        issue_key: Jira issue key
        issue_url: Browse URL for the issue
        leader_notification_status: Status of Slack notification (SENT/PENDING/FAILED)
        message: Human-readable message
    """

    success: bool
    issue_key: str
    issue_url: Optional[str] = None
    leader_notification_status: str = "PENDING"
    message: str = "Feature request submitted successfully"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "issueKey": self.issue_key,
            "issueUrl": self.issue_url,
            "leaderNotificationStatus": self.leader_notification_status,
            "message": self.message,
        }
