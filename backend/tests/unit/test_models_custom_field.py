"""
Unit tests for custom field data models.

Tests the CustomFieldMetadata, FieldMapping, and ProjectFieldConfiguration
dataclasses used in CLI field mapping.
"""

from app.models.custom_field import (
    CustomFieldMetadata,
    FieldMapping,
    JiraProjectsConfig,
    ProjectFieldConfiguration,
)


class TestCustomFieldMetadata:
    """Tests for CustomFieldMetadata dataclass."""

    def test_from_jira_response_textfield(self):
        """Test creating CustomFieldMetadata from JIRA API response for textfield."""
        jira_response = {
            "id": "customfield_10101",
            "name": "Roadmap Title",
            "description": "Public-facing title",
            "custom": True,
            "schema": {
                "type": "string",
                "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
                "customId": 10101,
            },
        }

        field = CustomFieldMetadata.from_jira_response(jira_response, "NEXUS")

        assert field.id == "customfield_10101"
        assert field.name == "Roadmap Title"
        assert field.description == "Public-facing title"
        assert field.is_custom is True
        assert field.project_key == "NEXUS"
        assert "textfield" in field.field_type

    def test_from_jira_response_textarea(self):
        """Test creating CustomFieldMetadata from JIRA API response for textarea."""
        jira_response = {
            "id": "customfield_10102",
            "name": "Roadmap Description",
            "custom": True,
            "schema": {
                "type": "string",
                "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
            },
        }

        field = CustomFieldMetadata.from_jira_response(jira_response, "NEXUS")

        assert field.id == "customfield_10102"
        assert field.name == "Roadmap Description"
        assert "textarea" in field.field_type

    def test_display_name(self):
        """Test display_name property formatting."""
        field = CustomFieldMetadata(
            id="customfield_10101",
            name="Test Field",
            field_type="textfield",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.display_name == "Test Field (customfield_10101)"

    def test_field_type_display_textfield(self):
        """Test field_type_display for single-line text."""
        field = CustomFieldMetadata(
            id="customfield_10101",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.field_type_display == "Text Field"

    def test_field_type_display_textarea(self):
        """Test field_type_display for multi-line text."""
        field = CustomFieldMetadata(
            id="customfield_10102",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:textarea",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.field_type_display == "Text Area"

    def test_field_type_display_url(self):
        """Test field_type_display for URL field."""
        field = CustomFieldMetadata(
            id="customfield_10103",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:url",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.field_type_display == "URL"

    def test_field_type_display_other(self):
        """Test field_type_display for unknown field type."""
        field = CustomFieldMetadata(
            id="customfield_10104",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.field_type_display == "Custom Field"

    def test_is_text_field_textfield(self):
        """Test is_text_field returns True for textfield."""
        field = CustomFieldMetadata(
            id="customfield_10101",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.is_text_field() is True

    def test_is_text_field_textarea(self):
        """Test is_text_field returns True for textarea."""
        field = CustomFieldMetadata(
            id="customfield_10102",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:textarea",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.is_text_field() is True

    def test_is_text_field_url(self):
        """Test is_text_field returns True for URL."""
        field = CustomFieldMetadata(
            id="customfield_10103",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:url",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.is_text_field() is True

    def test_is_text_field_non_text(self):
        """Test is_text_field returns False for non-text field types."""
        field = CustomFieldMetadata(
            id="customfield_10104",
            name="Test",
            field_type="com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
            is_custom=True,
            project_key="NEXUS",
        )

        assert field.is_text_field() is False


class TestFieldMapping:
    """Tests for FieldMapping dataclass."""

    def test_is_optional_image_fields(self):
        """Test that image URL fields are optional."""
        for i in range(1, 5):
            mapping = FieldMapping(
                config_key=f"roadmap_image_url_{i}", field_id=f"customfield_1010{i}"
            )
            assert mapping.is_optional is True

    def test_is_optional_required_fields(self):
        """Test that required fields are not optional."""
        required_fields = [
            "public_roadmap",
            "roadmap_status",
            "module",
            "release_year",
            "roadmap_title",
            "roadmap_description",
        ]

        for config_key in required_fields:
            mapping = FieldMapping(config_key=config_key, field_id="customfield_10001")
            assert mapping.is_optional is False

    def test_display_label(self):
        """Test display_label returns human-readable labels."""
        mapping = FieldMapping(config_key="roadmap_title", field_id="customfield_10101")

        assert "Roadmap Title" in mapping.display_label
        assert "public display" in mapping.display_label


class TestProjectFieldConfiguration:
    """Tests for ProjectFieldConfiguration dataclass."""

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = ProjectFieldConfiguration(
            public_roadmap="customfield_14619",
            roadmap_status="customfield_14621",
            module="customfield_14622",
            release_year="customfield_14623",
            release_quarter="customfield_14624",
            release_month="customfield_14625",
            documentation_url="customfield_14626",
            roadmap_title="customfield_10101",
            roadmap_description="customfield_10102",
            roadmap_image_url_1="customfield_10103",
            roadmap_image_url_2="customfield_10104",
            roadmap_image_url_3="customfield_10105",
            roadmap_image_url_4="customfield_10106",
            roadmap_likes="customfield_10107",
        )

        result = config.to_dict()

        assert result["public_roadmap"] == "customfield_14619"
        assert result["roadmap_title"] == "customfield_10101"
        assert len(result) == 14

    def test_from_mappings(self):
        """Test creating configuration from FieldMapping list."""
        mappings = [
            FieldMapping(config_key="public_roadmap", field_id="customfield_14619"),
            FieldMapping(config_key="roadmap_status", field_id="customfield_14621"),
            FieldMapping(config_key="module", field_id="customfield_14622"),
            FieldMapping(config_key="release_year", field_id="customfield_14623"),
            FieldMapping(config_key="release_quarter", field_id="customfield_14624"),
            FieldMapping(config_key="release_month", field_id="customfield_14625"),
            FieldMapping(config_key="documentation_url", field_id="customfield_14626"),
            FieldMapping(config_key="roadmap_title", field_id="customfield_10101"),
            FieldMapping(
                config_key="roadmap_description", field_id="customfield_10102"
            ),
            FieldMapping(
                config_key="roadmap_image_url_1", field_id="customfield_10103"
            ),
            FieldMapping(
                config_key="roadmap_image_url_2", field_id="customfield_10104"
            ),
            FieldMapping(
                config_key="roadmap_image_url_3", field_id="customfield_10105"
            ),
            FieldMapping(
                config_key="roadmap_image_url_4", field_id="customfield_10106"
            ),
            FieldMapping(config_key="roadmap_likes", field_id="customfield_10107"),
        ]

        config = ProjectFieldConfiguration.from_mappings(mappings)

        assert config.public_roadmap == "customfield_14619"
        assert config.roadmap_title == "customfield_10101"

    def test_validate_all_fields_set_valid(self):
        """Test validation passes for valid field IDs."""
        config = ProjectFieldConfiguration(
            public_roadmap="customfield_14619",
            roadmap_status="customfield_14621",
            module="customfield_14622",
            release_year="customfield_14623",
            release_quarter="customfield_14624",
            release_month="customfield_14625",
            documentation_url="customfield_14626",
            roadmap_title="customfield_10101",
            roadmap_description="customfield_10102",
            roadmap_image_url_1="customfield_10103",
            roadmap_image_url_2="customfield_10104",
            roadmap_image_url_3="customfield_10105",
            roadmap_image_url_4="customfield_10106",
            roadmap_likes="customfield_10107",
        )

        assert config.validate_all_fields_set() is True

    def test_validate_all_fields_set_invalid(self):
        """Test validation fails for invalid field IDs."""
        config = ProjectFieldConfiguration(
            public_roadmap="invalid_id",  # Invalid format
            roadmap_status="customfield_14621",
            module="customfield_14622",
            release_year="customfield_14623",
            release_quarter="customfield_14624",
            release_month="customfield_14625",
            documentation_url="customfield_14626",
            roadmap_title="customfield_10101",
            roadmap_description="customfield_10102",
            roadmap_image_url_1="customfield_10103",
            roadmap_image_url_2="customfield_10104",
            roadmap_image_url_3="customfield_10105",
            roadmap_image_url_4="customfield_10106",
            roadmap_likes="customfield_10107",
        )

        assert config.validate_all_fields_set() is False


class TestJiraProjectsConfig:
    """Tests for JiraProjectsConfig dataclass."""

    def test_add_or_update_project(self):
        """Test adding/updating project configuration."""
        config = JiraProjectsConfig(version="1.0", projects={})

        project_config = ProjectFieldConfiguration(
            public_roadmap="customfield_14619",
            roadmap_status="customfield_14621",
            module="customfield_14622",
            release_year="customfield_14623",
            release_quarter="customfield_14624",
            release_month="customfield_14625",
            documentation_url="customfield_14626",
            roadmap_title="customfield_10101",
            roadmap_description="customfield_10102",
            roadmap_image_url_1="customfield_10103",
            roadmap_image_url_2="customfield_10104",
            roadmap_image_url_3="customfield_10105",
            roadmap_image_url_4="customfield_10106",
            roadmap_likes="customfield_10107",
        )

        config.add_or_update_project("NEXUS", project_config)

        assert "NEXUS" in config.projects
        assert config.projects["NEXUS"].roadmap_title == "customfield_10101"

    def test_get_project(self):
        """Test retrieving project configuration."""
        project_config = ProjectFieldConfiguration(
            public_roadmap="customfield_14619",
            roadmap_status="customfield_14621",
            module="customfield_14622",
            release_year="customfield_14623",
            release_quarter="customfield_14624",
            release_month="customfield_14625",
            documentation_url="customfield_14626",
            roadmap_title="customfield_10101",
            roadmap_description="customfield_10102",
            roadmap_image_url_1="customfield_10103",
            roadmap_image_url_2="customfield_10104",
            roadmap_image_url_3="customfield_10105",
            roadmap_image_url_4="customfield_10106",
            roadmap_likes="customfield_10107",
        )

        config = JiraProjectsConfig(version="1.0", projects={"NEXUS": project_config})

        retrieved = config.get_project("NEXUS")
        assert retrieved is not None
        assert retrieved.roadmap_title == "customfield_10101"

        not_found = config.get_project("NOTEXIST")
        assert not_found is None

    def test_to_dict(self):
        """Test converting root config to dictionary."""
        project_config = ProjectFieldConfiguration(
            public_roadmap="customfield_14619",
            roadmap_status="customfield_14621",
            module="customfield_14622",
            release_year="customfield_14623",
            release_quarter="customfield_14624",
            release_month="customfield_14625",
            documentation_url="customfield_14626",
            roadmap_title="customfield_10101",
            roadmap_description="customfield_10102",
            roadmap_image_url_1="customfield_10103",
            roadmap_image_url_2="customfield_10104",
            roadmap_image_url_3="customfield_10105",
            roadmap_image_url_4="customfield_10106",
            roadmap_likes="customfield_10107",
        )

        config = JiraProjectsConfig(version="1.0", projects={"NEXUS": project_config})
        result = config.to_dict()

        assert result["version"] == "1.0"
        assert "NEXUS" in result["projects"]
        assert result["projects"]["NEXUS"]["roadmap_title"] == "customfield_10101"

    def test_from_dict(self):
        """Test creating root config from dictionary."""
        data = {
            "version": "1.0",
            "projects": {
                "NEXUS": {
                    "public_roadmap": "customfield_14619",
                    "roadmap_status": "customfield_14621",
                    "module": "customfield_14622",
                    "release_year": "customfield_14623",
                    "release_quarter": "customfield_14624",
                    "release_month": "customfield_14625",
                    "documentation_url": "customfield_14626",
                    "roadmap_title": "customfield_10101",
                    "roadmap_description": "customfield_10102",
                    "roadmap_image_url_1": "customfield_10103",
                    "roadmap_image_url_2": "customfield_10104",
                    "roadmap_image_url_3": "customfield_10105",
                    "roadmap_image_url_4": "customfield_10106",
                    "roadmap_likes": "customfield_10107",
                }
            },
        }

        config = JiraProjectsConfig.from_dict(data)

        assert config.version == "1.0"
        assert "NEXUS" in config.projects
        assert config.projects["NEXUS"].roadmap_title == "customfield_10101"
