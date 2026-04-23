"""
Data models for CLI JIRA custom field mapping.

These models represent custom field metadata retrieved from JIRA
and the mapping structures used during interactive CLI sessions.
"""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class CustomFieldMetadata:
    """Metadata for a JIRA custom field retrieved via API."""

    id: str
    name: str
    field_type: str
    is_custom: bool
    project_key: str
    description: Optional[str] = None
    projects: List[str] = field(
        default_factory=list
    )  # List of project keys this field is scoped to

    @property
    def display_name(self) -> str:
        """Formatted name for CLI display."""
        return f"{self.name} ({self.id})"

    @property
    def field_type_display(self) -> str:
        """Human-readable field type."""
        type_map = {
            "textfield": "Text Field",
            "textarea": "Text Area",
            "url": "URL",
            "select": "Select/Dropdown",
            "radiobuttons": "Radio Buttons",
            "multicheckboxes": "Checkboxes",
            "checkbox": "Checkbox",
            "labels": "Labels",
            "userpicker": "User Picker",
            "multiselect": "Multi-Select",
            "cascadingselect": "Cascading Select",
            "multiuserpicker": "Multi-User Picker",
            "readonlyfield": "Read-Only",
            "number": "Number",
            "unknown": "Field",
        }
        # Check field_type (lowercase) against our map
        field_type_lower = self.field_type.lower()
        for key, display in type_map.items():
            if key in field_type_lower:
                return display
        return "Custom Field"

    def is_text_field(self) -> bool:
        """
        Check if field is suitable for roadmap data.

        Includes most field types that can store text, options, or simple values.
        Excludes only complex types like attachments, dates, and users.
        """
        # Exclude these complex types
        excluded_types = [
            "date",  # Date picker
            "datetime",  # DateTime picker
            "attachment",  # File attachments
            "user",  # User object
            "version",  # Version picker
            "component",  # Component picker
            "issuetype",  # Issue type
            "priority",  # Priority
            "resolution",  # Resolution
            "status",  # Status
            "project",  # Project
        ]

        field_type_lower = self.field_type.lower()

        # If it's unknown, include it (better to show than hide)
        if field_type_lower == "unknown":
            return True

        # Exclude complex types
        return not any(excluded in field_type_lower for excluded in excluded_types)

    @classmethod
    def from_jira_response(cls, data: dict, project_key: str) -> "CustomFieldMetadata":
        """
        Create instance from JIRA /field API response (fallback method).

        Args:
            data: Field data from /rest/api/3/field endpoint
            project_key: Project key to associate with the field

        Returns:
            CustomFieldMetadata instance
        """
        # Get field type from schema
        field_type = "unknown"
        if "schema" in data:
            schema = data["schema"]
            if "custom" in schema:
                field_type = schema["custom"]
            elif "type" in schema:
                field_type = schema["type"]

        return cls(
            id=data.get("id", ""),
            name=data.get("name", "Unknown Field"),
            field_type=field_type,
            is_custom=data.get("custom", False),
            project_key=project_key,
            description=data.get("description"),
            projects=[],  # Fallback method doesn't have project info
        )


@dataclass
class FieldMapping:
    """User's selection for a specific config field."""

    config_key: str
    field_id: str
    field_name: Optional[str] = None
    is_selected: bool = True

    @property
    def is_optional(self) -> bool:
        """Check if this mapping is optional (can be skipped)."""
        optional_fields = [
            "roadmap_image_url_1",
            "roadmap_image_url_2",
            "roadmap_image_url_3",
            "roadmap_image_url_4",
        ]
        return self.config_key in optional_fields

    @property
    def display_label(self) -> str:
        """Human-readable label for CLI prompts."""
        labels = {
            "public_roadmap": "Public Roadmap (checkbox)",
            "roadmap_status": "Roadmap Status (DELIVERED/NOW/NEXT/FUTURE)",
            "media_type": "Media Type",
            "release_year": "Release Year",
            "release_quarter": "Release Quarter (Q1-Q4)",
            "release_month": "Release Month (1-12)",
            "documentation_url": "Documentation URL",
            "roadmap_title": "Roadmap Title (public display)",
            "roadmap_description": "Roadmap Description (public display)",
            "roadmap_image_url_1": "Roadmap Image URL 1 (optional)",
            "roadmap_image_url_2": "Roadmap Image URL 2 (optional)",
            "roadmap_image_url_3": "Roadmap Image URL 3 (optional)",
            "roadmap_image_url_4": "Roadmap Image URL 4 (optional)",
        }
        return labels.get(self.config_key, self.config_key)


@dataclass
class ProjectFieldConfiguration:
    """Custom field mapping for a JIRA project."""

    public_roadmap: str
    roadmap_status: str
    module: str
    release_year: str
    release_quarter: str
    release_month: str
    documentation_url: str
    roadmap_title: str
    roadmap_description: str
    roadmap_image_url_1: str
    roadmap_image_url_2: str
    roadmap_image_url_3: str
    roadmap_image_url_4: str
    roadmap_likes: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_mappings(cls, mappings: list) -> "ProjectFieldConfiguration":
        """Create from list of FieldMapping instances."""
        mapping_dict = {m.config_key: m.field_id for m in mappings}
        return cls(**mapping_dict)

    def validate_all_fields_set(self) -> bool:
        """Check that all fields have valid custom field IDs."""
        import re

        pattern = re.compile(r"^customfield_\d{5,}$")
        for field_id in asdict(self).values():
            if not pattern.match(field_id):
                return False
        return True


@dataclass
class JiraProjectsConfig:
    """Root configuration for all JIRA projects."""

    version: str
    projects: Dict[str, ProjectFieldConfiguration]

    def add_or_update_project(
        self, project_key: str, config: ProjectFieldConfiguration
    ) -> None:
        """Add or update a project configuration."""
        self.projects[project_key] = config

    def get_project(self, project_key: str) -> Optional[ProjectFieldConfiguration]:
        """Get configuration for a specific project."""
        return self.projects.get(project_key)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "projects": {
                key: config.to_dict() for key, config in self.projects.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JiraProjectsConfig":
        """Create from dictionary (loaded from JSON)."""
        projects = {
            key: ProjectFieldConfiguration(**value)
            for key, value in data["projects"].items()
        }
        return cls(version=data["version"], projects=projects)
