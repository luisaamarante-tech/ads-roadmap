"""Unit tests for JiraClient."""

import base64
from unittest.mock import MagicMock, patch

import pytest

from app.models import DeliveryStatus, Quarter
from app.services.jira_client import JiraClient


class TestJiraClient:
    """Tests for JiraClient class."""

    @pytest.fixture
    def jira_client(self):
        """Create JiraClient with mocked config."""
        with patch("app.services.jira_client.Config") as mock_config:
            mock_config.JIRA_BASE_URL = "https://test.atlassian.net"
            mock_config.JIRA_EMAIL = "test@example.com"
            mock_config.JIRA_API_TOKEN = "test-token"
            mock_config.get_jira_field_mapping.return_value = {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                "module": "customfield_10003",
                "release_year": "customfield_10004",
                "release_quarter": "customfield_10005",
                "release_month": "customfield_10006",
                "documentation_url": "customfield_10007",
            }
            mock_config.is_jira_configured.return_value = True
            mock_config.get_project_keys.return_value = ["PROJ"]
            mock_config.get_project_custom_fields.return_value = {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                "module": "customfield_10003",
                "release_year": "customfield_10004",
                "release_quarter": "customfield_10005",
                "release_month": "customfield_10006",
                "documentation_url": "customfield_10007",
            }

            client = JiraClient(mock_config)
            yield client

    def test_create_auth_header(self, jira_client):
        """Test auth header is correctly created."""
        expected_creds = "test@example.com:test-token"
        expected_encoded = base64.b64encode(expected_creds.encode()).decode()

        assert jira_client.auth_header == f"Basic {expected_encoded}"

    def test_build_jql_query_single_project(self, jira_client):
        """Test JQL query for single project."""
        jql = jira_client.build_jql_query()

        assert 'project = "PROJ"' in jql
        assert "issuetype = Epic" in jql
        assert 'cf[10001] = "Yes"' in jql

    def test_build_jql_query_multiple_projects(self, jira_client):
        """Test JQL query for multiple projects."""
        jira_client.config.get_project_keys.return_value = ["PROJ1", "PROJ2"]

        # Mock get_project_custom_fields for both projects
        def mock_get_project_custom_fields(project_key):
            return {
                "public_roadmap": "customfield_10001",
                "roadmap_status": "customfield_10002",
                "module": "customfield_10003",
            }

        jira_client.config.get_project_custom_fields.side_effect = (
            mock_get_project_custom_fields
        )

        jql = jira_client.build_jql_query()

        assert 'project = "PROJ1"' in jql
        assert 'project = "PROJ2"' in jql
        assert " OR " in jql

    def test_build_jql_query_no_projects(self, jira_client):
        """Test JQL query with no projects configured."""
        jira_client.config.get_project_keys.return_value = []

        jql = jira_client.build_jql_query()

        assert 'project = "NONE"' in jql

    def test_fetch_public_epics_not_configured(self, jira_client):
        """Test fetch returns empty when JIRA not configured."""
        jira_client.config.is_jira_configured.return_value = False

        result = jira_client.fetch_public_epics()

        assert result == []

    def test_fetch_public_epics_success(self, jira_client, mock_jira_response):
        """Test successful fetch of epics."""
        with patch.object(jira_client, "_make_request") as mock_request:
            mock_request.return_value = mock_jira_response

            result = jira_client.fetch_public_epics()

            assert len(result) == 1
            assert result[0]["key"] == "TEST-123"

    def test_fetch_public_epics_error(self, jira_client):
        """Test fetch handles errors gracefully."""
        with patch.object(jira_client, "_make_request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                jira_client.fetch_public_epics()

    def test_extract_roadmap_item(self, jira_client, mock_jira_response):
        """Test extracting RoadmapItem from JIRA issue."""
        issue = mock_jira_response["issues"][0]

        item = jira_client.extract_roadmap_item(issue)

        assert item is not None
        assert item.id == "TEST-123"
        assert item.title == "Test Feature"
        assert item.status == DeliveryStatus.NOW
        assert item.release_year == 2025
        assert item.release_quarter == Quarter.Q1

    def test_extract_roadmap_item_missing_fields(self, jira_client):
        """Test extraction returns None for missing required fields."""
        issue = {
            "key": "TEST-001",
            "fields": {
                "summary": "",  # Empty title
            },
        }

        item = jira_client.extract_roadmap_item(issue)

        assert item is None

    def test_extract_roadmap_item_includes_likes(self, jira_client):
        """Test that JiraClient extracts likes field from JIRA response."""
        # Mock the project custom fields to include roadmap_likes
        jira_client.config.get_project_custom_fields.return_value = {
            "public_roadmap": "customfield_10001",
            "roadmap_status": "customfield_10002",
            "module": "customfield_10003",
            "release_year": "customfield_10004",
            "release_quarter": "customfield_10005",
            "release_month": "customfield_10006",
            "documentation_url": "customfield_10007",
            "roadmap_likes": "customfield_10008",
        }

        issue = {
            "key": "TEST-123",
            "fields": {
                "project": {"key": "PROJ"},
                "summary": "Test Feature",
                "description": "Test description",
                "customfield_10001": {"value": "Yes"},
                "customfield_10002": {"value": "NOW"},
                "customfield_10003": {"value": "Test Module"},
                "customfield_10004": 2025,
                "customfield_10005": {"value": "Q1"},
                "customfield_10006": None,
                "customfield_10007": "https://docs.example.com",
                "customfield_10008": 42,  # Likes field
            },
        }

        item = jira_client.extract_roadmap_item(issue)

        assert item is not None
        assert hasattr(item, "likes")
        assert item.likes == 42

    def test_extract_roadmap_item_defaults_likes_when_missing(self, jira_client):
        """Test that JiraClient defaults to 0 when likes field is missing."""
        # Mock the project custom fields to include roadmap_likes
        jira_client.config.get_project_custom_fields.return_value = {
            "public_roadmap": "customfield_10001",
            "roadmap_status": "customfield_10002",
            "module": "customfield_10003",
            "release_year": "customfield_10004",
            "release_quarter": "customfield_10005",
            "release_month": "customfield_10006",
            "documentation_url": "customfield_10007",
            "roadmap_likes": "customfield_10008",
        }

        issue = {
            "key": "TEST-123",
            "fields": {
                "project": {"key": "PROJ"},
                "summary": "Test Feature",
                "description": "Test description",
                "customfield_10001": {"value": "Yes"},
                "customfield_10002": {"value": "NOW"},
                "customfield_10003": {"value": "Test Module"},
                "customfield_10004": 2025,
                "customfield_10005": {"value": "Q1"},
                "customfield_10006": None,
                "customfield_10007": "https://docs.example.com",
                # customfield_10008 (likes) is missing
            },
        }

        item = jira_client.extract_roadmap_item(issue)

        assert item is not None
        assert hasattr(item, "likes")
        assert item.likes == 0

    def test_update_epic_likes(self, jira_client):
        """Test updating epic likes in JIRA."""
        # Mock the project custom fields
        jira_client.config.get_project_custom_fields.return_value = {
            "roadmap_likes": "customfield_10008",
        }

        # Mock the _make_request method to return None (PUT returns no content)
        jira_client._make_request = MagicMock(return_value=None)

        result = jira_client.update_epic_likes("PROJ-123", 43)

        assert result == 43
        jira_client._make_request.assert_called_once_with(
            "/rest/api/3/issue/PROJ-123",
            method="PUT",
            json_data={"fields": {"customfield_10008": 43}},
        )

    def test_update_epic_likes_missing_field_config(self, jira_client):
        """Test update_epic_likes raises error when field not configured."""
        # Mock missing field configuration
        jira_client.config.get_project_custom_fields.return_value = {}

        with pytest.raises(ValueError, match="roadmap_likes field not configured"):
            jira_client.update_epic_likes("PROJ-123", 43)

    def test_extract_description_string(self, jira_client):
        """Test extracting string description."""
        result = jira_client._extract_description("Simple text")
        assert result == "Simple text"

    def test_extract_description_adf(self, jira_client):
        """Test extracting ADF description."""
        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Hello "},
                        {"type": "text", "text": "World"},
                    ],
                }
            ],
        }

        result = jira_client._extract_description(adf)

        assert "Hello World" in result

    def test_extract_description_empty(self, jira_client):
        """Test extracting empty description."""
        assert jira_client._extract_description(None) == ""
        assert jira_client._extract_description("") == ""

    def test_extract_status(self, jira_client):
        """Test extracting delivery status."""
        assert jira_client._extract_status({"value": "NOW"}) == DeliveryStatus.NOW
        assert (
            jira_client._extract_status({"value": "DELIVERED"})
            == DeliveryStatus.DELIVERED
        )
        assert jira_client._extract_status(None) is None

    def test_extract_status_invalid(self, jira_client):
        """Test extracting invalid status returns None."""
        result = jira_client._extract_status({"value": "INVALID"})
        assert result is None

    def test_extract_quarter(self, jira_client):
        """Test extracting quarter."""
        assert jira_client._extract_quarter({"value": "Q1"}) == Quarter.Q1
        assert jira_client._extract_quarter({"value": "Q4"}) == Quarter.Q4
        assert jira_client._extract_quarter(None) is None

    def test_extract_text_field(self, jira_client):
        """Test extracting text field."""
        assert jira_client._extract_text_field({"value": "Test"}) == "Test"
        assert jira_client._extract_text_field("Direct") == "Direct"
        assert jira_client._extract_text_field(None) == ""

    def test_extract_number_field(self, jira_client):
        """Test extracting number field."""
        assert jira_client._extract_number_field(2025) == 2025
        assert jira_client._extract_number_field("2025") == 2025
        assert jira_client._extract_number_field(None) is None
        assert jira_client._extract_number_field("invalid") is None

    def test_extract_url_field(self, jira_client):
        """Test extracting URL field."""
        assert (
            jira_client._extract_url_field("https://example.com")
            == "https://example.com"
        )
        assert (
            jira_client._extract_url_field({"url": "https://example.com"})
            == "https://example.com"
        )
        assert jira_client._extract_url_field(None) is None

    def test_extract_images(self, jira_client):
        """Test extracting images from attachments."""
        attachments = [
            {"mimeType": "image/png", "content": "https://url1.png"},
            {"mimeType": "image/jpeg", "content": "https://url2.jpg"},
            {"mimeType": "application/pdf", "content": "https://doc.pdf"},
            {"mimeType": "image/gif", "content": "https://url3.gif"},
            {"mimeType": "image/webp", "content": "https://url4.webp"},
            {"mimeType": "image/png", "content": "https://url5.png"},
        ]

        images = jira_client._extract_images(attachments)

        # Should be limited to 4 images
        assert len(images) == 4
        assert "https://doc.pdf" not in images

    def test_extract_images_empty(self, jira_client):
        """Test extracting images from empty attachments."""
        assert jira_client._extract_images([]) == []
        assert jira_client._extract_images(None) == []

    def test_get_custom_fields_success(self, jira_client):
        """Test successful retrieval of custom fields using two-step approach."""
        # Mock the search response (Step 1: find an issue)
        mock_search_response = {"issues": [{"key": "NEXUS-1"}]}

        # Mock the issue response (Step 2: get all fields)
        mock_issue_response = {
            "names": {
                "summary": "Summary",
                "description": "Description",
                "customfield_10101": "Roadmap Title",
                "customfield_10102": "Roadmap Description",
            },
            "fields": {
                "summary": "Test",
                "description": "Test description",
                "customfield_10101": "My Title",
                "customfield_10102": {"type": "doc", "content": []},
            },
        }

        with patch.object(jira_client, "_make_request") as mock_request:
            mock_request.side_effect = [mock_search_response, mock_issue_response]

            fields = jira_client.get_custom_fields("NEXUS")

            # Should filter to custom fields only
            assert len(fields) > 0
            assert all(field.is_custom for field in fields)

            # Check that we got expected fields
            field_ids = [field.id for field in fields]
            assert "customfield_10101" in field_ids
            assert "customfield_10102" in field_ids

            # System fields should be filtered out
            assert "summary" not in field_ids

            # Verify two requests were made
            assert mock_request.call_count == 2

    def test_get_custom_fields_no_project_key(self, jira_client):
        """Test get_custom_fields raises ValueError when no project key provided."""
        with pytest.raises(ValueError) as exc_info:
            jira_client.get_custom_fields(None)
        assert "project_key is required" in str(exc_info.value)

    def test_get_custom_fields_no_issues_found(self, jira_client):
        """Test get_custom_fields raises ValueError when no issues found."""
        mock_response = {"issues": []}

        with patch.object(jira_client, "_make_request") as mock_request:
            # Both Epic and any-issue queries return empty
            mock_request.return_value = mock_response

            with pytest.raises(ValueError) as exc_info:
                jira_client.get_custom_fields("NEXUS")
            assert "No issues found in project NEXUS" in str(exc_info.value)

    def test_get_custom_fields_api_error(self, jira_client):
        """Test get_custom_fields handles API errors with clear error message."""
        import requests

        with patch.object(jira_client, "_make_request") as mock_request:
            # Both JQL queries fail with API errors
            mock_request.side_effect = requests.RequestException("API Error")

            with pytest.raises(ValueError) as exc_info:
                jira_client.get_custom_fields("NEXUS")
            # When both queries fail, we get the "No issues found" error
            assert "No issues found in project NEXUS" in str(exc_info.value)

    def test_is_text_field_type_textfield(self, jira_client):
        """Test is_text_field_type returns True for textfield."""
        field_type = "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
        assert jira_client.is_text_field_type(field_type) is True

    def test_is_text_field_type_textarea(self, jira_client):
        """Test is_text_field_type returns True for textarea."""
        field_type = "com.atlassian.jira.plugin.system.customfieldtypes:textarea"
        assert jira_client.is_text_field_type(field_type) is True

    def test_is_text_field_type_url(self, jira_client):
        """Test is_text_field_type returns True for URL."""
        field_type = "com.atlassian.jira.plugin.system.customfieldtypes:url"
        assert jira_client.is_text_field_type(field_type) is True

    def test_is_text_field_type_non_text(self, jira_client):
        """Test is_text_field_type returns False for non-text types."""
        field_type = "com.atlassian.jira.plugin.system.customfieldtypes:datepicker"
        assert jira_client.is_text_field_type(field_type) is False

    def test_filter_text_fields(self, jira_client):
        """Test filtering fields to text types only."""
        from app.models.custom_field import CustomFieldMetadata

        fields = [
            CustomFieldMetadata(
                id="customfield_10101",
                name="Text Field",
                field_type="com.atlassian.jira.plugin.system.customfieldtypes:textfield",
                is_custom=True,
                project_key="NEXUS",
            ),
            CustomFieldMetadata(
                id="customfield_10102",
                name="Date Field",
                field_type="com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
                is_custom=True,
                project_key="NEXUS",
            ),
            CustomFieldMetadata(
                id="customfield_10103",
                name="URL Field",
                field_type="com.atlassian.jira.plugin.system.customfieldtypes:url",
                is_custom=True,
                project_key="NEXUS",
            ),
        ]

        text_fields = jira_client.filter_text_fields(fields)

        assert len(text_fields) == 2
        assert text_fields[0].id == "customfield_10101"
        assert text_fields[1].id == "customfield_10103"


class TestADFConversion:
    """Test ADF to HTML conversion."""

    @pytest.fixture
    def jira_client(self):
        """Create JiraClient for testing."""
        with patch("app.services.jira_client.Config") as mock_config:
            mock_config.JIRA_BASE_URL = "https://test.atlassian.net"
            mock_config.JIRA_EMAIL = "test@example.com"
            mock_config.JIRA_API_TOKEN = "test-token"
            mock_config.get_jira_field_mapping.return_value = {}
            mock_config.get_project_keys.return_value = []
            client = JiraClient(mock_config)
            return client

    def test_empty_adf_document(self, jira_client):
        """Test that empty ADF document returns empty string."""
        adf = {"type": "doc", "version": 1, "content": []}
        result = jira_client._adf_to_html(adf)
        assert result == ""

    def test_simple_paragraph(self, jira_client):
        """Test simple paragraph conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello, world!"}],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert result == "<p>Hello, world!</p>"

    def test_bold_text(self, jira_client):
        """Test bold text (strong mark) conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "This is "},
                        {
                            "type": "text",
                            "text": "bold",
                            "marks": [{"type": "strong"}],
                        },
                        {"type": "text", "text": " text."},
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<strong>bold</strong>" in result

    def test_italic_text(self, jira_client):
        """Test italic text (em mark) conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "italic",
                            "marks": [{"type": "em"}],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<em>italic</em>" in result

    def test_underline_text(self, jira_client):
        """Test underline text conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "underlined",
                            "marks": [{"type": "underline"}],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<u>underlined</u>" in result

    def test_bullet_list(self, jira_client):
        """Test bullet list conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Item 1"}],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Item 2"}],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "</ul>" in result

    def test_ordered_list(self, jira_client):
        """Test ordered list conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "First"}],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<ol>" in result
        assert "<li>First</li>" in result

    def test_link(self, jira_client):
        """Test link with href conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "link",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {"href": "https://example.com"},
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert 'href="https://example.com"' in result
        assert "<a" in result

    def test_heading(self, jira_client):
        """Test heading (h1-h6) conversion."""
        for level in range(1, 7):
            adf = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": level},
                        "content": [{"type": "text", "text": "Heading"}],
                    }
                ],
            }
            result = jira_client._adf_to_html(adf)
            assert f"<h{level}>Heading</h{level}>" in result

    def test_hard_break(self, jira_client):
        """Test hard break (<br>) conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Line 1"},
                        {"type": "hardBreak"},
                        {"type": "text", "text": "Line 2"},
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<br>" in result

    def test_unknown_node_type(self, jira_client):
        """Test unknown node type graceful handling."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "unknownType",
                    "content": [{"type": "text", "text": "fallback"}],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        # Should extract text from children
        assert "fallback" in result

    def test_malformed_adf(self, jira_client):
        """Test malformed ADF graceful fallback."""
        adf = None
        result = jira_client._adf_to_html(adf)
        assert result == ""

        adf = {"type": "paragraph"}  # Missing content
        result = jira_client._adf_to_html(adf)
        # Should not crash
        assert isinstance(result, str)

    def test_sanitization_integration(self, jira_client):
        """Test that HTML output is sanitized."""
        # Create ADF that would produce unsafe HTML
        description_field = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Safe text"}],
                }
            ],
        }
        result = jira_client._extract_description(description_field)
        assert "<p>Safe text</p>" in result
        # Sanitizer is integrated in _extract_description


class TestMixedFormatting:
    """Test mixed formatting (User Story 3)."""

    @pytest.fixture
    def jira_client(self):
        """Create JiraClient for testing."""
        with patch("app.services.jira_client.Config") as mock_config:
            mock_config.JIRA_BASE_URL = "https://test.atlassian.net"
            mock_config.JIRA_EMAIL = "test@example.com"
            mock_config.JIRA_API_TOKEN = "test-token"
            mock_config.get_jira_field_mapping.return_value = {}
            mock_config.get_project_keys.return_value = []
            client = JiraClient(mock_config)
            return client

    def test_combined_marks_bold_italic(self, jira_client):
        """Test combined marks (bold + italic) conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "important",
                            "marks": [{"type": "strong"}, {"type": "em"}],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<strong>" in result
        assert "<em>" in result
        assert "important" in result

    def test_list_with_formatted_items(self, jira_client):
        """Test list with formatted items (bold, italic, links)."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "bold item",
                                            "marks": [{"type": "strong"}],
                                        }
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "link item",
                                            "marks": [
                                                {
                                                    "type": "link",
                                                    "attrs": {
                                                        "href": "https://example.com"
                                                    },
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<ul>" in result
        assert "<strong>bold item</strong>" in result
        assert 'href="https://example.com"' in result

    def test_nested_lists(self, jira_client):
        """Test nested lists (3+ levels) conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Level 1"}],
                                },
                                {
                                    "type": "bulletList",
                                    "content": [
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "type": "text",
                                                            "text": "Level 2",
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<ul>" in result
        assert "Level 1" in result
        assert "Level 2" in result

    def test_strikethrough_text(self, jira_client):
        """Test strikethrough text conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "deleted",
                            "marks": [{"type": "strike"}],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<s>deleted</s>" in result


class TestCodeBlocksAndPreformatted:
    """Test code blocks and preformatted text (User Story 2)."""

    @pytest.fixture
    def jira_client(self):
        """Create JiraClient for testing."""
        with patch("app.services.jira_client.Config") as mock_config:
            mock_config.JIRA_BASE_URL = "https://test.atlassian.net"
            mock_config.JIRA_EMAIL = "test@example.com"
            mock_config.JIRA_API_TOKEN = "test-token"
            mock_config.get_jira_field_mapping.return_value = {}
            mock_config.get_project_keys.return_value = []
            client = JiraClient(mock_config)
            return client

    def test_code_block_with_language(self, jira_client):
        """Test code block conversion with language class."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "def hello():\n    print('Hello')",
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<pre>" in result
        assert "<code" in result
        assert 'class="language-python"' in result
        assert "def hello()" in result

    def test_inline_code(self, jira_client):
        """Test inline code conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Use "},
                        {
                            "type": "text",
                            "text": "print()",
                            "marks": [{"type": "code"}],
                        },
                        {"type": "text", "text": " function."},
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<code>print()</code>" in result

    def test_blockquote(self, jira_client):
        """Test blockquote conversion."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "This is a quote."}],
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        assert "<blockquote>" in result
        assert "<p>This is a quote.</p>" in result

    def test_code_block_whitespace_preservation(self, jira_client):
        """Test whitespace preservation in code blocks."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "def hello():\n    print('Hi')\n    return True",
                        }
                    ],
                }
            ],
        }
        result = jira_client._adf_to_html(adf)
        # Whitespace should be preserved
        assert "\n    print" in result
        assert "\n    return" in result
