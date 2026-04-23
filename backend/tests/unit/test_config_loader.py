"""
Unit tests for the JSON configuration loader module.

Tests cover configuration loading, validation, project lookup, and error handling.
"""

import json
import os
import tempfile

import pytest

from app.services.config_loader import (
    ProjectConfig,
    ProjectFieldMapping,
    get_project_config,
    load_config,
    validate_config,
)

# Test fixtures


@pytest.fixture
def valid_config_data():
    """Return valid configuration data for testing."""
    return {
        "version": "1.0",
        "projects": {
            "TEST1": {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                "module": "customfield_10003",
                "release_year": "customfield_10004",
                "release_quarter": "customfield_10005",
                "release_month": "customfield_10006",
                "documentation_url": "customfield_10007",
                "roadmap_title": "customfield_10101",
                "roadmap_description": "customfield_10102",
                "roadmap_image_url_1": "customfield_10103",
                "roadmap_image_url_2": "customfield_10104",
                "roadmap_image_url_3": "customfield_10105",
                "roadmap_image_url_4": "customfield_10106",
                "roadmap_likes": "customfield_10107",
            },
            "TEST2": {
                "public_roadmap": "customfield_10201",
                "roadmap_status": "customfield_10202",
                "module": "customfield_10203",
                "release_year": "customfield_10204",
                "release_quarter": "customfield_10205",
                "release_month": "customfield_10206",
                "documentation_url": "customfield_10207",
                "roadmap_title": "customfield_10208",
                "roadmap_description": "customfield_10209",
                "roadmap_image_url_1": "customfield_10210",
                "roadmap_image_url_2": "customfield_10211",
                "roadmap_image_url_3": "customfield_10212",
                "roadmap_image_url_4": "customfield_10213",
                "roadmap_likes": "customfield_10214",
            },
        },
    }


@pytest.fixture
def valid_config_file(valid_config_data):
    """Create a temporary valid configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid_config_data, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def invalid_json_file():
    """Create a temporary file with invalid JSON syntax."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"version": "1.0", "projects": {')  # Missing closing braces
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def invalid_schema_file():
    """Create a temporary file with invalid schema (missing required fields)."""
    invalid_data = {
        "version": "1.0",
        "projects": {
            "TEST1": {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                # Missing other required fields
            }
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


# Tests for load_config()


def test_load_valid_config(valid_config_file):
    """Test loading a valid configuration file."""
    config = load_config(valid_config_file)

    assert config is not None
    assert isinstance(config, ProjectConfig)
    assert config.version == "1.0"
    assert "TEST1" in config.projects
    assert "TEST2" in config.projects
    assert isinstance(config.projects["TEST1"], ProjectFieldMapping)
    assert config.projects["TEST1"].roadmap_title == "customfield_10101"


def test_load_invalid_json_syntax(invalid_json_file):
    """Test handling of malformed JSON returns None."""
    config = load_config(invalid_json_file)

    assert config is None


def test_missing_config_file():
    """Test fallback behavior when config file doesn't exist."""
    config = load_config("/nonexistent/path/to/config.json")

    assert config is None


# Tests for validate_config()


def test_schema_validation(valid_config_data):
    """Test schema validation with valid data."""
    is_valid, errors = validate_config(valid_config_data)

    assert is_valid is True
    assert errors is None


def test_schema_validation_missing_version():
    """Test schema validation catches missing version."""
    invalid_data = {
        "projects": {
            "TEST1": {
                "roadmap_title": "customfield_10101",
                "roadmap_description": "customfield_10102",
                "roadmap_image_url_1": "customfield_10103",
                "roadmap_image_url_2": "customfield_10104",
                "roadmap_image_url_3": "customfield_10105",
                "roadmap_image_url_4": "customfield_10106",
            }
        }
    }

    is_valid, errors = validate_config(invalid_data)

    assert is_valid is False
    assert errors is not None
    assert "version" in str(errors).lower()


def test_schema_validation_missing_required_field():
    """Test schema validation catches missing required fields."""
    invalid_data = {
        "version": "1.0",
        "projects": {
            "TEST1": {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                # Missing other required fields
            }
        },
    }

    is_valid, errors = validate_config(invalid_data)

    assert is_valid is False
    assert errors is not None


# Tests for get_project_config()


def test_get_project_config(valid_config_data):
    """Test project-specific configuration lookup."""
    config = ProjectConfig(
        version=valid_config_data["version"],
        projects={
            k: ProjectFieldMapping(**v)
            for k, v in valid_config_data["projects"].items()
        },
    )

    project_config = get_project_config(config, "TEST1")

    assert project_config is not None
    assert isinstance(project_config, ProjectFieldMapping)
    assert project_config.roadmap_title == "customfield_10101"
    assert project_config.roadmap_image_url_4 == "customfield_10106"


def test_get_project_config_not_found(valid_config_data):
    """Test project lookup when project doesn't exist."""
    config = ProjectConfig(
        version=valid_config_data["version"],
        projects={
            k: ProjectFieldMapping(**v)
            for k, v in valid_config_data["projects"].items()
        },
    )

    project_config = get_project_config(config, "NONEXISTENT")

    assert project_config is None


# Tests for invalid field ID format


def test_invalid_field_id_format():
    """Test validation of invalid custom field ID format."""
    invalid_data = {
        "version": "1.0",
        "projects": {
            "TEST1": {
                "roadmap_title": "invalid_field_id",  # Wrong format
                "roadmap_description": "customfield_10102",
                "roadmap_image_url_1": "customfield_10103",
                "roadmap_image_url_2": "customfield_10104",
                "roadmap_image_url_3": "customfield_10105",
                "roadmap_image_url_4": "customfield_10106",
            }
        },
    }

    is_valid, errors = validate_config(invalid_data)

    assert is_valid is False
    assert errors is not None


# Tests for multiple projects


def test_multiple_projects(valid_config_data):
    """Test configuration with multiple projects."""
    config = ProjectConfig(
        version=valid_config_data["version"],
        projects={
            k: ProjectFieldMapping(**v)
            for k, v in valid_config_data["projects"].items()
        },
    )

    assert len(config.projects) == 2
    assert "TEST1" in config.projects
    assert "TEST2" in config.projects

    # Verify each project has independent configuration
    test1_config = get_project_config(config, "TEST1")
    test2_config = get_project_config(config, "TEST2")

    assert test1_config.roadmap_title != test2_config.roadmap_title
    assert test1_config.roadmap_description != test2_config.roadmap_description
    assert test1_config.public_roadmap != test2_config.public_roadmap
    assert test1_config.module != test2_config.module
