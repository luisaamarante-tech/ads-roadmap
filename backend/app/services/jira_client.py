"""
JIRA API client for fetching public roadmap epics.

Security: Only extracts allowlisted fields to prevent data leakage.
"""

# Standard library
import base64
import logging
from datetime import datetime
from typing import Optional

# Third-party
import requests

# Local
from ..config import Config
from ..models import DeliveryStatus, Quarter, RoadmapItem

logger = logging.getLogger(__name__)


class JiraClient:
    """
    Client for interacting with JIRA Cloud REST API v3.

    Fetches epics marked as public for the roadmap and extracts
    only the allowed fields for public display.
    """

    # Fields allowed to be extracted from JIRA (security allowlist)
    ALLOWED_FIELDS = [
        "key",
        "summary",
        "description",
        "attachment",
    ]

    def __init__(self, config: Optional[Config] = None):
        """Initialize the JIRA client with configuration."""
        self.config = config or Config
        self.base_url = self.config.JIRA_BASE_URL.rstrip("/")
        self.auth_header = self._create_auth_header()
        self.field_mapping = self.config.get_jira_field_mapping()
        self._current_user_account_id = None  # Lazy loaded

        # Add custom fields to allowlist from both env vars and project config
        # 1. Add environment variable custom fields
        self.ALLOWED_FIELDS.extend(self.field_mapping.values())

        # 2. Add project-specific custom fields from jira_projects.json
        project_keys = self.config.get_project_keys()
        for project_key in project_keys:
            project_fields = self.config.get_project_custom_fields(project_key)
            if project_fields:
                # Add all custom field IDs from this project
                for field_id in project_fields.values():
                    if field_id and field_id not in self.ALLOWED_FIELDS:
                        self.ALLOWED_FIELDS.append(field_id)

        # Add project field for extraction
        if "project" not in self.ALLOWED_FIELDS:
            self.ALLOWED_FIELDS.append("project")

    def _create_auth_header(self) -> str:
        """Create Basic auth header for JIRA API."""
        credentials = f"{self.config.JIRA_EMAIL}:{self.config.JIRA_API_TOKEN}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> Optional[dict]:
        """Make authenticated request to JIRA API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if method == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data, timeout=30)
        else:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        # PUT requests to update issues return 204 No Content
        if response.status_code == 204:
            return None

        return response.json()

    def build_jql_query(self) -> str:
        """
        Build JQL query to fetch public roadmap epics.

        Only fetches epics that:
        - Are in one of the configured projects
        - Are of type Epic
        - Have the public roadmap flag set to true (using project-specific field IDs)
        """
        project_keys = self.config.get_project_keys()

        # Build project filter for multiple projects
        if not project_keys:
            logger.warning("No JIRA projects configured")
            return 'project = "NONE"'  # Will return no results

        # Get project-specific field mappings
        project_conditions = []
        for project_key in project_keys:
            # Get project-specific custom fields
            project_fields = self.config.get_project_custom_fields(project_key)

            # Only include projects that have custom fields configured in jira_projects.json
            if project_fields:
                # Use project-specific public_roadmap field
                public_field = project_fields.get("public_roadmap")

                if public_field:
                    # The new POST /rest/api/3/search/jql endpoint requires cf[ID]
                    # syntax instead of customfield_ID for option/select fields.
                    cf_id = public_field.replace("customfield_", "")
                    jql_field = f"cf[{cf_id}]" if cf_id.isdigit() else public_field
                    condition = f'(project = "{project_key}" AND {jql_field} = "Yes")'
                    project_conditions.append(condition)
                    logger.debug(f"JQL for {project_key}: using field {public_field}")
                else:
                    logger.warning(
                        f"Project {project_key} has no public_roadmap field configured, skipping"
                    )
            else:
                logger.warning(
                    f"Project {project_key} has no custom fields configured in jira_projects.json, skipping"
                )

        if not project_conditions:
            logger.warning("No public roadmap fields configured for any project")
            return 'project = "NONE"'

        # Combine all project conditions with OR
        if len(project_conditions) == 1:
            combined_filter = project_conditions[0]
        else:
            combined_filter = " OR ".join(project_conditions)

        return f"({combined_filter}) " f"AND issuetype = Epic " f"ORDER BY updated DESC"

    def fetch_public_epics(self) -> list[dict]:
        """
        Fetch all public epics from JIRA using the new /search/jql endpoint.

        Returns raw JIRA issue data for processing.
        """
        if not self.config.is_jira_configured():
            logger.warning("JIRA is not configured, returning empty list")
            return []

        jql = self.build_jql_query()

        try:
            response = self._make_request(
                "/rest/api/3/search/jql",
                method="POST",
                json_data={
                    "jql": jql,
                    "fields": self.ALLOWED_FIELDS,
                    "maxResults": 100,
                },
            )
            return response.get("issues", [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch epics from JIRA: {e}")
            raise

    def extract_roadmap_item(self, issue: dict) -> Optional[RoadmapItem]:
        """
        Extract a RoadmapItem from a JIRA issue.

        Applies validation and only extracts allowed fields.
        Returns None if required fields are missing.
        """
        try:
            fields = issue.get("fields", {})
            issue_key = issue.get("key", "")

            # Get project key from issue for project-specific field mapping
            project_key = fields.get("project", {}).get("key", "")

            # Try to get project-specific custom fields, otherwise use defaults
            project_fields = self.config.get_project_custom_fields(project_key)
            if project_fields:
                field_mapping = project_fields
                logger.debug(f"Using project-specific field mapping for {project_key}")
            else:
                field_mapping = self.field_mapping
                logger.debug(f"Using default field mapping for {project_key}")

            # Extract basic fields - try custom fields first, fall back to defaults
            custom_title = self._extract_text_field(
                fields.get(field_mapping.get("roadmap_title", ""))
            )
            custom_description = self._extract_description(
                fields.get(field_mapping.get("roadmap_description"))
            )

            # Use custom fields if available, otherwise use default epic fields
            title = custom_title if custom_title else fields.get("summary", "")
            description = (
                custom_description
                if custom_description
                else self._extract_description(fields.get("description"))
            )

            # Extract custom fields for roadmap data
            status = self._extract_status(fields.get(field_mapping["roadmap_status"]))
            module = self._extract_text_field(fields.get(field_mapping["module"]))
            release_year = self._extract_number_field(
                fields.get(field_mapping["release_year"])
            )
            release_quarter = self._extract_quarter(
                fields.get(field_mapping["release_quarter"])
            )
            release_month = self._extract_number_field(
                fields.get(field_mapping["release_month"])
            )
            documentation_url = self._extract_url_field(
                fields.get(field_mapping["documentation_url"])
            )

            # Extract likes field (default to 0 if missing or not configured)
            likes = 0
            if "roadmap_likes" in field_mapping:
                likes_field = field_mapping.get("roadmap_likes")
                likes_value = fields.get(likes_field)
                if likes_value is not None:
                    try:
                        likes = int(likes_value)
                        if likes < 0:
                            likes = 0
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Invalid likes value for {issue_key}: {likes_value}, defaulting to 0"
                        )
                        likes = 0

            # Extract images from custom field URLs (new approach)
            # Try custom image URL fields first, fall back to attachments
            images = []
            for i in range(1, 5):
                url_field = field_mapping.get(f"roadmap_image_url_{i}")
                if url_field:
                    url = self._extract_url_field(fields.get(url_field))
                    if url and self._validate_url(url):
                        images.append(url)

            # If no custom image URLs, fall back to attachments (legacy)
            if not images:
                images = self._extract_images(fields.get("attachment", []))

            # Validate required fields
            if not all(
                [
                    issue_key,
                    title,
                    description,
                    status,
                    module,
                    release_year,
                    release_quarter,
                ]
            ):
                logger.warning(f"Issue {issue_key} missing required fields, skipping")
                return None

            return RoadmapItem(
                id=issue_key,
                title=title[:200],  # Limit title length
                description=description[:5000],  # Limit description length
                status=status,
                module=module,
                module_id="",  # Will be generated in __post_init__
                release_year=release_year,
                release_quarter=release_quarter,
                release_month=release_month,
                images=images,
                documentation_url=documentation_url,
                likes=likes,
                last_synced_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Failed to extract roadmap item from issue: {e}")
            return None

    def _extract_description(self, description_field) -> str:
        """
        Extract description from JIRA Atlassian Document Format (ADF).

        Converts ADF to plain text/HTML for display.
        """
        if not description_field:
            return ""

        # If it's already a string, return it
        if isinstance(description_field, str):
            return description_field

        # ADF is a complex JSON structure, convert to HTML
        if isinstance(description_field, dict):
            html = self._adf_to_html(description_field)
            # Sanitize HTML for security
            from .html_sanitizer import HTMLSanitizer

            sanitizer = HTMLSanitizer()
            return sanitizer.sanitize(html)

        return ""

    def _adf_to_html(self, adf: dict) -> str:
        """
        Convert Atlassian Document Format to HTML.

        Handles common ADF node types and converts them to semantic HTML.
        """
        if not adf or not isinstance(adf, dict):
            return ""

        def convert_node(node):
            """Recursively convert ADF node to HTML."""
            if isinstance(node, str):
                return node
            if not isinstance(node, dict):
                return ""

            node_type = node.get("type", "")
            content = node.get("content", [])
            attrs = node.get("attrs", {})
            marks = node.get("marks", [])

            # Text node - apply marks (formatting)
            if node_type == "text":
                text = node.get("text", "")
                return self._apply_marks(text, marks)

            # Paragraph
            if node_type == "paragraph":
                inner_html = "".join(convert_node(child) for child in content)
                return f"<p>{inner_html}</p>"

            # Heading (h1-h6)
            if node_type == "heading":
                level = attrs.get("level", 1)
                level = max(1, min(6, level))  # Ensure 1-6
                inner_html = "".join(convert_node(child) for child in content)
                return f"<h{level}>{inner_html}</h{level}>"

            # Bullet list
            if node_type == "bulletList":
                items_html = "".join(convert_node(child) for child in content)
                return f"<ul>{items_html}</ul>"

            # Ordered list
            if node_type == "orderedList":
                items_html = "".join(convert_node(child) for child in content)
                return f"<ol>{items_html}</ol>"

            # List item
            if node_type == "listItem":
                # List items contain paragraphs, extract content
                inner_html = ""
                for child in content:
                    if isinstance(child, dict) and child.get("type") == "paragraph":
                        # Unwrap paragraph for list items
                        para_content = child.get("content", [])
                        inner_html += "".join(convert_node(c) for c in para_content)
                    else:
                        inner_html += convert_node(child)
                return f"<li>{inner_html}</li>"

            # Hard break
            if node_type == "hardBreak":
                return "<br>"

            # Code block
            if node_type == "codeBlock":
                language = attrs.get("language", "")
                code_text = "".join(convert_node(child) for child in content)
                if language:
                    return f'<pre><code class="language-{language}">{code_text}</code></pre>'
                return f"<pre><code>{code_text}</code></pre>"

            # Blockquote
            if node_type == "blockquote":
                inner_html = "".join(convert_node(child) for child in content)
                return f"<blockquote>{inner_html}</blockquote>"

            # Document root - just process children
            if node_type == "doc":
                return "".join(convert_node(child) for child in content)

            # Unknown node type - try to extract children
            if content:
                return "".join(convert_node(child) for child in content)

            return ""

        try:
            return convert_node(adf)
        except Exception as e:
            logger.warning(f"Error converting ADF to HTML: {e}")
            return ""

    def _apply_marks(self, text: str, marks: list) -> str:
        """
        Apply text formatting marks (bold, italic, underline, links, etc.).

        Args:
            text: Plain text content
            marks: List of mark objects from ADF

        Returns:
            HTML with marks applied
        """
        if not marks:
            return text

        # Apply marks in order (they stack)
        html = text
        for mark in marks:
            mark_type = mark.get("type", "")
            attrs = mark.get("attrs", {})

            if mark_type == "strong":
                html = f"<strong>{html}</strong>"
            elif mark_type == "em":
                html = f"<em>{html}</em>"
            elif mark_type == "underline":
                html = f"<u>{html}</u>"
            elif mark_type == "strike":
                html = f"<s>{html}</s>"
            elif mark_type == "code":
                html = f"<code>{html}</code>"
            elif mark_type == "link":
                href = attrs.get("href", "")
                if href:
                    html = f'<a href="{href}">{html}</a>'

        return html

    def _extract_status(self, field_value) -> Optional[DeliveryStatus]:
        """Extract delivery status from custom field."""
        if not field_value:
            return None

        # Handle select field (object with value property)
        if isinstance(field_value, dict):
            value = field_value.get("value", "")
        else:
            value = str(field_value)

        # Map to DeliveryStatus enum
        value_upper = value.upper().strip()
        try:
            return DeliveryStatus(value_upper)
        except ValueError:
            logger.warning(f"Unknown delivery status: {value}")
            return None

    def _extract_quarter(self, field_value) -> Optional[Quarter]:
        """Extract quarter from custom field."""
        if not field_value:
            return None

        # Handle select field (object with value property)
        if isinstance(field_value, dict):
            value = field_value.get("value", "")
        else:
            value = str(field_value)

        # Map to Quarter enum
        value_upper = value.upper().strip()
        try:
            return Quarter(value_upper)
        except ValueError:
            logger.warning(f"Unknown quarter: {value}")
            return None

    def _extract_text_field(self, field_value) -> str:
        """Extract text from a custom field."""
        if not field_value:
            return ""

        # Handle select field (object with value property)
        if isinstance(field_value, dict):
            return field_value.get("value", "")

        return str(field_value)

    def _extract_number_field(self, field_value) -> Optional[int]:
        """Extract number from a custom field."""
        if field_value is None:
            return None

        try:
            return int(field_value)
        except (ValueError, TypeError):
            return None

    def _extract_url_field(self, field_value) -> Optional[str]:
        """Extract URL from a custom field."""
        if not field_value:
            return None

        # Could be a string or an object with URL property
        if isinstance(field_value, dict):
            return field_value.get("url") or field_value.get("value")

        return str(field_value) if field_value else None

    def _validate_url(self, url: str) -> bool:
        """
        Validate if a string is a valid HTTP(S) URL.

        Args:
            url: URL string to validate

        Returns:
            True if valid URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        # Basic URL validation - must start with http:// or https://
        return url.startswith("http://") or url.startswith("https://")

    def _extract_images(self, attachments: list) -> list[str]:
        """
        Extract image URLs from attachments.

        Filters for image types and limits to 4 images.
        """
        if not attachments:
            return []

        image_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        images = []

        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue

            mime_type = attachment.get("mimeType", "")
            if mime_type in image_types:
                content_url = attachment.get("content")
                if content_url:
                    images.append(content_url)
                    if len(images) >= 4:
                        break

        return images

    def update_epic_likes(self, issue_key: str, new_count: int) -> int:
        """
        Update the roadmap_likes custom field in JIRA for a given epic.

        Args:
            issue_key: JIRA issue key (e.g., "PROJ-123")
            new_count: New like count to set

        Returns:
            The new like count that was set

        Raises:
            ValueError: If roadmap_likes field is not configured for this project
            requests.RequestException: If JIRA API call fails
        """
        # Extract project key from issue key (e.g., "PROJ-123" -> "PROJ")
        project_key = issue_key.split("-")[0] if "-" in issue_key else None
        if not project_key:
            raise ValueError(f"Invalid issue key format: {issue_key}")

        # Get field mapping for the project
        field_mapping = self.config.get_project_custom_fields(project_key)
        if not field_mapping or "roadmap_likes" not in field_mapping:
            raise ValueError(
                f"roadmap_likes field not configured for project {project_key}"
            )

        likes_field_id = field_mapping["roadmap_likes"]

        # Validate new_count
        if new_count < 0:
            logger.warning(f"Negative like count ({new_count}), setting to 0")
            new_count = 0

        logger.info(f"Updating {issue_key} field {likes_field_id} to {new_count} likes")

        # Update JIRA field via PUT /rest/api/3/issue/{issueIdOrKey}
        try:
            self._make_request(
                f"/rest/api/3/issue/{issue_key}",
                method="PUT",
                json_data={"fields": {likes_field_id: new_count}},
            )
            logger.info(f"Successfully updated {issue_key} likes to {new_count}")
            return new_count
        except requests.RequestException as e:
            logger.error(f"Failed to update likes for {issue_key}: {e}")
            raise

    def get_custom_fields(self, project_key: Optional[str] = None):
        """
        Retrieve custom fields available in a specific JIRA project.

        This method queries an actual issue from the project with all fields
        to determine which custom fields are available. This is the ONLY
        reliable way to get project-specific fields.

        Strategy:
        1. Search for any issue in the project using /search/jql
        2. Query that specific issue with fields=*all&expand=names
        3. Extract field metadata from the response

        Args:
            project_key: JIRA project key (required for accurate results)

        Returns:
            List of CustomFieldMetadata instances for custom fields
            available in the specified project

        Raises:
            ValueError: If project_key is not provided or no issues found
            requests.RequestException: If API call fails
        """
        from ..models.custom_field import CustomFieldMetadata

        if not project_key:
            raise ValueError(
                "project_key is required to get project-specific custom fields"
            )

        logger.info(f"Retrieving custom fields for project {project_key}")

        # Step 1: Find an Epic in the project (Epics have roadmap-related custom fields)
        # Try Epic first, fall back to any issue if no Epics found
        jql_epic = f"project = {project_key} AND issuetype = Epic ORDER BY updated DESC"
        jql_any = f"project = {project_key} ORDER BY updated DESC"

        issues = []
        for jql in [jql_epic, jql_any]:
            try:
                search_response = self._make_request(
                    "/rest/api/3/search/jql",
                    method="POST",
                    json_data={
                        "jql": jql,
                        "fields": ["key"],  # Only need the key
                        "maxResults": 1,
                    },
                )
                issues = search_response.get("issues", [])
                if issues:
                    logger.info(f"Found issue using JQL: {jql}")
                    break
            except requests.RequestException as e:
                logger.warning(f"JQL search failed: {jql}, error: {e}")
                continue

        if not issues:
            raise ValueError(
                f"No issues found in project {project_key}. "
                f"Please create at least one Epic in the project before mapping fields."
            )

        issue_key = issues[0].get("key")
        logger.info(f"Found issue {issue_key}, querying for all fields...")

        # Step 2: Query the specific issue with all fields and names expanded
        try:
            issue_response = self._make_request(
                f"/rest/api/3/issue/{issue_key}?fields=*all&expand=names"
            )
        except requests.RequestException as e:
            logger.error(f"Failed to get issue details for {issue_key}: {e}")
            raise ValueError(
                f"Could not retrieve field information from issue {issue_key}. "
                f"Error: {e}"
            )

        # Extract field names and data from the issue response
        names = issue_response.get("names", {})
        fields_data = issue_response.get("fields", {})

        logger.info(f"Retrieved {len(names)} total fields from issue {issue_key}")

        # Build CustomFieldMetadata for each custom field present in this project
        custom_fields = []
        for field_id, field_name in names.items():
            # Only include custom fields (starting with customfield_)
            if not field_id.startswith("customfield_"):
                continue

            # Get the field value to determine type
            field_value = fields_data.get(field_id)
            field_type = self._infer_field_type(field_value)

            logger.debug(f"  {field_id}: {field_name} (type={field_type})")

            cf = CustomFieldMetadata(
                id=field_id,
                name=field_name,
                field_type=field_type,
                is_custom=True,
                project_key=project_key,
                description=None,
                projects=[project_key],
            )
            custom_fields.append(cf)

        logger.info(
            f"Found {len(custom_fields)} custom fields in project {project_key}"
        )

        if custom_fields:
            # Log sample of field names for debugging
            sample = [f.name for f in custom_fields[:5]]
            logger.info(f"Sample fields: {sample}")

        return custom_fields

    def _infer_field_type(self, field_value) -> str:
        """
        Infer field type from the field value structure.

        Args:
            field_value: The value from the JIRA API

        Returns:
            String describing the field type
        """
        if field_value is None:
            return "unknown"

        # Check value structure to infer type
        if isinstance(field_value, str):
            return "textfield"
        elif isinstance(field_value, (int, float)):
            return "number"
        elif isinstance(field_value, dict):
            if "value" in field_value:
                # Select field
                return "select"
            elif "type" in field_value and field_value.get("type") == "doc":
                # Rich text field (Atlassian Document Format)
                return "textarea"
            elif "self" in field_value and "value" in field_value:
                # Option field (select, checkbox, radio)
                return "select"
        elif isinstance(field_value, list):
            return "multiselect"

        return "unknown"

    def is_text_field_type(self, field_type: str) -> bool:
        """
        Check if a field type is text-based (suitable for roadmap data).

        Args:
            field_type: JIRA field type identifier

        Returns:
            True if field is text-based, False otherwise
        """
        text_field_types = [
            "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
            "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield",
        ]
        return field_type in text_field_types

    def filter_text_fields(self, fields: list) -> list:
        """
        Filter a list of CustomFieldMetadata to only text-type fields.

        Args:
            fields: List of CustomFieldMetadata instances

        Returns:
            Filtered list of text fields only
        """
        return [field for field in fields if field.is_text_field()]

    def get_current_user_account_id(self) -> str:
        """
        Get the account ID of the authenticated user.

        Returns:
            Account ID string

        Raises:
            requests.RequestException: If API call fails
        """
        if self._current_user_account_id:
            return self._current_user_account_id

        try:
            response = self._make_request("/rest/api/3/myself")
            self._current_user_account_id = response["accountId"]
            logger.info(f"Current user account ID: {self._current_user_account_id}")
            return self._current_user_account_id
        except requests.RequestException as e:
            logger.error(f"Failed to get current user: {e}")
            raise

    def create_issue(
        self,
        project_key: str,
        issue_type_name: str,
        summary: str,
        description_text: str,
        labels: Optional[list[str]] = None,
    ) -> dict:
        """
        Create a new Jira issue.

        Args:
            project_key: Jira project key (e.g., "NEXUS")
            issue_type_name: Issue type (e.g., "Task", "Story")
            summary: Issue summary/title
            description_text: Plain text description (will be converted to ADF)
            labels: Optional list of labels to apply

        Returns:
            Created issue response with key, id, and self URL

        Raises:
            requests.RequestException: If API call fails
        """
        # Build ADF description
        description_adf = self._text_to_adf(description_text)

        # Get current user account ID for assignee
        try:
            current_user_account_id = self.get_current_user_account_id()
        except Exception as e:
            logger.warning(
                f"Could not get current user, will try without assignee: {e}"
            )
            current_user_account_id = None

        # Build issue payload with minimal required fields
        # Note: Some projects may have additional required fields
        payload = {
            "fields": {
                "project": {"key": project_key},
                "issuetype": {"name": issue_type_name},
                "summary": summary[:255],  # Jira has a 255 char limit on summary
                "description": description_adf,
            }
        }

        # Assign to current user if we have the account ID
        if current_user_account_id:
            payload["fields"]["assignee"] = {"accountId": current_user_account_id}

        # Add labels if provided
        if labels:
            payload["fields"]["labels"] = labels

        logger.info(
            f"Creating Jira issue in {project_key} (type: {issue_type_name}): {summary[:50]}..."
        )

        try:
            response = self._make_request(
                "/rest/api/3/issue",
                method="POST",
                json_data=payload,
            )
            logger.info(f"Created Jira issue: {response.get('key')}")
            return response
        except requests.RequestException as e:
            # Log the full error details from Jira
            error_detail = "Unknown error"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Jira API error details: {error_detail}")
                except Exception:
                    error_detail = e.response.text
                    logger.error(f"Jira API error response: {error_detail}")

            logger.error(f"Failed to create Jira issue in {project_key}: {e}")
            logger.error(f"Issue payload was: {payload}")
            raise

    def _text_to_adf(self, text: str) -> dict:
        """
        Convert plain text to Atlassian Document Format (ADF).

        Args:
            text: Plain text content

        Returns:
            ADF document structure
        """
        if not text or not text.strip():
            # Return minimal valid ADF for empty content
            return {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": " "}],
                    }
                ],
            }

        # Split text into paragraphs (separated by blank lines)
        paragraphs = []
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                paragraphs.append(
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": para}],
                    }
                )

        # Ensure at least one paragraph
        if not paragraphs:
            paragraphs.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text.strip() or " "}],
                }
            )

        return {"version": 1, "type": "doc", "content": paragraphs}
