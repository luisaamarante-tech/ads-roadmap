"""
Configuration loader for JIRA custom field mappings.

Provides JSON-based configuration management for mapping JIRA project keys
to their custom field IDs. Supports validation and project-specific lookup.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import jsonschema

logger = logging.getLogger(__name__)


@dataclass
class ProjectFieldMapping:
    """
    Custom field ID mapping for a single JIRA project.

    Contains ALL custom field IDs used by the roadmap system:
    - Existing fields: public_roadmap, roadmap_status, module, release fields, documentation_url
    - New fields: roadmap_title, roadmap_description, roadmap_image_url_1-4, roadmap_likes
    """

    # Existing custom fields (previously in .env)
    public_roadmap: str
    roadmap_status: str
    media_type: str
    release_year: str
    release_quarter: str
    release_month: str
    documentation_url: str

    # New custom fields for public display
    roadmap_title: str
    roadmap_description: str
    roadmap_image_url_1: str
    roadmap_image_url_2: str
    roadmap_image_url_3: str
    roadmap_image_url_4: str
    roadmap_likes: str


@dataclass
class ProjectConfig:
    """
    Root configuration object containing all project mappings.

    Attributes:
        version: Configuration format version (semantic versioning)
        projects: Dictionary mapping project keys to field mappings
    """

    version: str
    projects: dict[str, ProjectFieldMapping]


def load_config(config_path: str) -> Optional[ProjectConfig]:
    """
    Load and parse JIRA projects configuration from JSON file.

    Args:
        config_path: Path to the JSON configuration file

    Returns:
        ProjectConfig object if successful, None if file missing or invalid

    Logs warnings for errors but does not raise exceptions to enable
    fallback behavior in the application.
    """
    try:
        # Check if file exists
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file not found: {config_path}")
            return None

        # Read and parse JSON
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Validate against schema
        is_valid, errors = validate_config(config_data)
        if not is_valid:
            logger.warning(f"Configuration validation failed: {errors}")
            return None

        # Convert to dataclasses
        projects = {}
        for project_key, field_mapping in config_data.get("projects", {}).items():
            try:
                projects[project_key] = ProjectFieldMapping(**field_mapping)
            except TypeError as e:
                logger.warning(f"Invalid field mapping for project {project_key}: {e}")
                continue

        config = ProjectConfig(version=config_data["version"], projects=projects)

        logger.info(
            f"Loaded configuration for {len(projects)} projects from {config_path}"
        )
        return config

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON configuration: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        return None


def validate_config(config_data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate configuration data against JSON schema.

    Args:
        config_data: Parsed configuration dictionary

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if validation passed, False otherwise
        - error_message: Error description if validation failed, None if passed
    """
    try:
        # Load schema file
        schema_path = (
            Path(__file__).parent.parent.parent / "config" / "jira_projects.schema.json"
        )

        if not schema_path.exists():
            logger.warning(f"Schema file not found: {schema_path}")
            # If schema doesn't exist, do basic validation
            if "version" not in config_data or "projects" not in config_data:
                return False, "Missing required fields: version or projects"
            return True, None

        with open(schema_path, "r") as f:
            schema = json.load(f)

        # Validate against schema
        jsonschema.validate(instance=config_data, schema=schema)
        return True, None

    except jsonschema.ValidationError as e:
        return False, str(e.message)
    except Exception as e:
        logger.error(f"Error during schema validation: {e}")
        return False, str(e)


def get_project_config(
    config: ProjectConfig, project_key: str
) -> Optional[ProjectFieldMapping]:
    """
    Get custom field mapping for a specific project.

    Args:
        config: Loaded ProjectConfig object
        project_key: JIRA project key (e.g., "PROJ1")

    Returns:
        ProjectFieldMapping if project exists in config, None otherwise
    """
    return config.projects.get(project_key)
