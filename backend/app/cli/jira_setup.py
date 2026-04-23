"""
Flask CLI commands for setting up JIRA custom fields.

Provides automation for creating custom fields in JIRA projects
and updating the configuration file.
"""

import json
import logging
import os
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Optional

import click
import requests
from flask.cli import with_appcontext

from ..config import Config

logger = logging.getLogger(__name__)

# Validation patterns
PROJECT_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
CUSTOM_FIELD_ID_PATTERN = re.compile(r"^customfield_\d{5,}$")


def validate_project_key(key: str) -> bool:
    """
    Validate JIRA project key format.

    Args:
        key: Project key to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(PROJECT_KEY_PATTERN.match(key))


def validate_custom_field_id(field_id: str) -> bool:
    """
    Validate JIRA custom field ID format.

    Args:
        field_id: Custom field ID to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(CUSTOM_FIELD_ID_PATTERN.match(field_id))


# Helper functions for automatic field matching


def normalize_string(s: str) -> str:
    """
    Normalize string for comparison.

    Converts to lowercase, replaces underscores and hyphens with spaces,
    and strips whitespace for consistent fuzzy matching.

    Args:
        s: String to normalize

    Returns:
        Normalized string suitable for comparison

    Example:
        >>> normalize_string("Roadmap_Title")
        'roadmap title'
        >>> normalize_string("Release-Year")
        'release year'
    """
    return s.lower().replace("_", " ").replace("-", " ").strip()


def fuzzy_match_score(str1: str, str2: str) -> float:
    """
    Calculate similarity score between two strings using fuzzy matching.

    Uses Python's difflib.SequenceMatcher (Ratcliff/Obershelp algorithm)
    to compute similarity ratio between 0.0 (no match) and 1.0 (exact match).

    Args:
        str1: First string to compare
        str2: Second string to compare

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (identical)

    Example:
        >>> fuzzy_match_score("Roadmap Title", "roadmap_title")
        0.96
        >>> fuzzy_match_score("Status", "Delivery Status")
        0.72
    """
    s1 = normalize_string(str1)
    s2 = normalize_string(str2)
    return SequenceMatcher(None, s1, s2).ratio()


def generate_expected_names(config_key: str) -> List[str]:
    """
    Generate list of expected field names for a configuration key.

    Maps internal config keys (e.g., 'roadmap_title') to EXACT JIRA
    field names. The first name in each list is the exact field name
    from JIRA, followed by alternative variations.

    Args:
        config_key: Configuration key to generate names for

    Returns:
        List of expected field name variations (exact match first)

    Example:
        >>> generate_expected_names("roadmap_title")
        ['Roadmap Title', 'Public Title', 'Title']
    """
    mappings = {
        # EXACT JIRA field names are FIRST in each list (from JIRA API)
        "public_roadmap": [
            "Public Roadmap",
            "Roadmap Public",
            "Show in Roadmap",
            "Public",
            "Is Public",
        ],
        "roadmap_status": [
            "Roadmap Status",
            "Delivery Status",
            "Status",
            "Release Status",
        ],
        "module": ["Roadmap Module", "Module", "Product Module", "Area", "Component"],
        "release_year": ["Roadmap Release Year", "Release Year", "Year"],
        "release_quarter": ["Roadmap Release Quarter", "Release Quarter", "Quarter"],
        "release_month": ["Roadmap Release Month", "Release Month", "Month"],
        "documentation_url": [
            "Release Documentation URL",
            "Documentation URL",
            "Docs URL",
            "Documentation",
            "Docs",
            "Doc Link",
        ],
        "roadmap_title": ["Roadmap Title", "Public Title", "Title"],
        "roadmap_description": [
            "Roadmap Description",
            "Public Description",
            "Description",
        ],
        "roadmap_image_url_1": [
            "Roadmap Image URL 1",
            "Image URL 1",
            "Roadmap Image 1",
            "Image 1",
            "Screenshot 1",
        ],
        "roadmap_image_url_2": [
            "Roadmap Image URL 2",
            "Image URL 2",
            "Roadmap Image 2",
            "Image 2",
            "Screenshot 2",
        ],
        "roadmap_image_url_3": [
            "Roadmap Image URL 3",
            "Image URL 3",
            "Roadmap Image 3",
            "Image 3",
            "Screenshot 3",
        ],
        "roadmap_image_url_4": [
            "Roadmap Image URL 4",
            "Image URL 4",
            "Roadmap Image 4",
            "Image 4",
            "Screenshot 4",
        ],
        "roadmap_likes": [
            "Roadmap Likes",
            "Likes",
            "Like Count",
            "Likes Count",
            "User Likes",
        ],
    }

    # Return mapped names or generate from config_key
    if config_key in mappings:
        return mappings[config_key]
    else:
        # Fallback: convert config_key to title case
        return [config_key.replace("_", " ").title()]


def auto_match_field(config_key: str, available_fields: List) -> tuple[Optional, float]:
    """
    Automatically match a config key to a custom field by name similarity.

    Uses a two-pass approach:
    1. Try exact string matches first (case-insensitive, normalized)
    2. Fall back to fuzzy string matching (>= 85% similarity)

    This ensures we prioritize exact matches when multiple similar field names exist
    (e.g., "Public Roadmap" vs "Roadmap Public", "Title" vs "Roadmap Title").

    Args:
        config_key: Configuration key to match (e.g., 'roadmap_title')
        available_fields: List of CustomFieldMetadata objects to match against

    Returns:
        Tuple of (matched field, confidence score) or (None, 0.0) if no match

    Example:
        >>> field, score = auto_match_field("roadmap_title", fields)
        >>> if field:
        ...     print(f"Matched: {field.name} ({score:.0%})")
    """
    expected_names = generate_expected_names(config_key)

    # Pass 1: Try exact matches (normalized strings)
    for expected in expected_names:
        normalized_expected = normalize_string(expected)
        for field in available_fields:
            normalized_field = normalize_string(field.name)
            if normalized_expected == normalized_field:
                logger.debug(
                    f"Exact match for {config_key}: '{expected}' == '{field.name}'"
                )
                return (field, 1.0)  # 100% confidence for exact matches

    # Pass 2: Try fuzzy matching
    best_match = None
    best_score = 0.0

    for field in available_fields:
        for expected in expected_names:
            score = fuzzy_match_score(field.name, expected)
            if score > best_score:
                best_score = score
                best_match = field

    # Return match only if confidence is very high (>= 85%)
    if best_score >= 0.85:
        return (best_match, best_score)
    else:
        return (None, 0.0)


# Helper functions for project-scope field filtering


def get_field_context(base_url: str, auth_header: str, field_id: str) -> dict:
    """
    Get field context information from JIRA to determine scope.

    Queries the JIRA API to retrieve context information for a custom field,
    which indicates whether the field is global or project-specific.

    Args:
        base_url: JIRA base URL
        auth_header: Authorization header value
        field_id: Custom field ID to query

    Returns:
        Dictionary with 'values' key containing context information,
        or empty dict with empty 'values' list on error

    Example:
        >>> context = get_field_context(base_url, auth, "customfield_10101")
        >>> if context['values']:
        ...     is_global = context['values'][0].get('isGlobalContext', True)
    """
    try:
        url = f"{base_url}/rest/api/3/field/{field_id}/context"
        headers = {
            "Authorization": auth_header,
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        logger.debug(f"Failed to retrieve context for field {field_id}: {e}")
        return {"values": []}


def is_project_scoped_field(
    field, project_key: str, base_url: str, auth_header: str
) -> bool:
    """
    Check if a custom field is scoped to a specific project.

    Determines if a field is project-specific (not global) by examining
    its projects attribute. This avoids slow API calls to the context endpoint.

    Args:
        field: CustomFieldMetadata object to check
        project_key: JIRA project key to check scope against
        base_url: JIRA base URL (not used in optimized version)
        auth_header: Authorization header value (not used in optimized version)

    Returns:
        True if field is project-scoped (matches project or unclear),
        False if definitively global (empty projects list)

    Note:
        Optimized approach: Uses only the field's projects attribute to avoid
        slow API calls. If projects list exists and is empty, assumes global.
        If projects list has items, checks if project_key matches.
        If no projects attribute, conservatively assumes project-scoped.
    """
    # Check if field has projects attribute
    if hasattr(field, "projects"):
        projects_list = field.projects
        logger.debug(f"Field {field.id} has projects attribute: {projects_list}")

        # Empty list means global field (available to all projects)
        if not projects_list:
            logger.debug(
                f"Field {field.id} ({field.name}) is GLOBAL (empty projects list)"
            )
            return False

        # Non-empty list means project-scoped, check if our project is included
        is_scoped = project_key in projects_list
        logger.debug(
            f"Field {field.id} ({field.name}) project-scoped check: {project_key} in {projects_list} = {is_scoped}"
        )
        return is_scoped

    # No projects attribute - conservatively assume project-scoped
    # This avoids filtering out potentially relevant fields
    # (Better to show extra fields than hide relevant ones)
    logger.debug(
        f"Field {field.id} ({field.name}) has NO projects attribute, assuming project-scoped"
    )
    return True


def filter_project_scoped_fields(
    fields: List, project_key: str, base_url: str = "", auth_header: str = ""
) -> List:
    """
    Filter a list of custom fields to include only project-scoped fields.

    Removes global custom fields that appear across all projects, keeping
    only fields that are specifically configured for the target project.

    Args:
        fields: List of CustomFieldMetadata objects to filter
        project_key: JIRA project key to filter by
        base_url: JIRA base URL (optional, not used in optimized version)
        auth_header: Authorization header value (optional, not used in optimized version)

    Returns:
        Filtered list containing only project-scoped fields

    Note:
        Optimized version that uses only field metadata, no API calls.
        Very fast even with hundreds of fields.
    """
    filtered = []

    for field in fields:
        # Pass empty strings for base_url and auth_header since we don't use them
        if is_project_scoped_field(field, project_key, base_url, auth_header):
            filtered.append(field)

    return filtered


@click.group("jira")
def jira_cli():
    """JIRA management commands."""
    pass


@jira_cli.command("list-fields")
@click.argument("project_key")
@click.option(
    "--type",
    "-t",
    "field_type",
    type=click.Choice(["text", "all"]),
    default="text",
    help="Filter by field type",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
@with_appcontext
def list_fields(
    project_key: str, field_type: str, output_format: str
):  # pragma: no cover
    """
    List all custom fields available in a JIRA project.

    PROJECT_KEY: The JIRA project key (e.g., NEXUS, FLOW)

    This command retrieves all custom fields from the specified project
    and displays them for exploration and field mapping purposes.

    Example:
        flask jira list-fields NEXUS
        flask jira list-fields NEXUS --type all
        flask jira list-fields NEXUS --format json
    """
    click.echo(f"Listing custom fields for project: {project_key}")
    click.echo()

    # Validate project key format
    if not validate_project_key(project_key):
        click.secho("✗ Invalid project key format", fg="red")
        click.echo(
            "Project keys must be 2-10 uppercase alphanumeric characters starting with a letter"
        )
        return

    # Validate configuration
    if not Config.is_jira_configured():
        click.secho("✗ JIRA is not configured", fg="red")
        click.echo("Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN")
        return

    # Get JIRA credentials
    base_url = Config.JIRA_BASE_URL.rstrip("/")
    import base64

    credentials = f"{Config.JIRA_EMAIL}:{Config.JIRA_API_TOKEN}"
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"

    # Validate authentication
    click.echo("Validating JIRA authentication...")
    try:
        response = requests.get(
            f"{base_url}/rest/api/3/myself",
            headers={"Authorization": auth_header},
            timeout=30,
        )
        response.raise_for_status()
        click.secho("✓ Authentication successful", fg="green")
        click.echo()
    except requests.RequestException as e:
        click.secho(f"✗ Authentication failed: {e}", fg="red")
        return

    # Retrieve custom fields
    click.echo(f"Retrieving custom fields for {project_key}...")
    try:
        from ..services.jira_client import JiraClient

        client = JiraClient()
        fields = client.get_custom_fields(project_key)

        # Filter by type if requested
        if field_type == "text":
            fields = client.filter_text_fields(fields)
            click.secho(f"✓ Found {len(fields)} custom text fields", fg="green")
        else:
            click.secho(f"✓ Found {len(fields)} custom fields", fg="green")

        if not fields:
            click.echo("No custom fields found for this project")
            return

        click.echo()

        # Output in requested format
        if output_format == "table":
            _output_table(fields)
        elif output_format == "json":
            _output_json(fields)
        elif output_format == "csv":
            _output_csv(fields)

    except requests.RequestException as e:
        click.secho(f"✗ Failed to retrieve fields: {e}", fg="red")
        if "404" in str(e):
            click.echo(f"Project '{project_key}' not found or not accessible")
        return
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        return


def _output_table(fields):  # pragma: no cover
    """Output custom fields in table format."""
    import click

    # Header
    click.secho("Custom Fields:", bold=True)
    click.echo()
    click.echo(f"{'ID':<25} {'Name':<40} {'Type':<30}")
    click.echo("-" * 95)

    # Rows
    for field in fields:
        click.echo(
            f"{field.id:<25} {field.name[:38]:<40} {field.field_type_display:<30}"
        )


def _output_json(fields):  # pragma: no cover
    """Output custom fields in JSON format."""
    import json

    import click

    output = [
        {
            "id": field.id,
            "name": field.name,
            "type": field.field_type,
            "description": field.description or "",
        }
        for field in fields
    ]

    click.echo(json.dumps(output, indent=2))


def _output_csv(fields):  # pragma: no cover
    """Output custom fields in CSV format."""
    import csv
    import sys

    writer = csv.writer(sys.stdout)
    writer.writerow(["ID", "Name", "Type", "Description"])

    for field in fields:
        writer.writerow(
            [field.id, field.name, field.field_type, field.description or ""]
        )


@jira_cli.command("map-fields")
@click.argument("project_key", required=False)
@click.option(
    "--all",
    "-a",
    "map_all",
    is_flag=True,
    help="Map fields for all projects in config/jira_projects.json",
)
@click.option(
    "--show-all-types", is_flag=True, help="Show all custom field types (not just text)"
)
@click.option(
    "--no-auto-match", is_flag=True, help="Disable automatic field name matching"
)
@click.option(
    "--include-global",
    is_flag=True,
    help="Include global custom fields (default: project-scoped only)",
)
@click.option("--dry-run", is_flag=True, help="Preview changes without writing")
@with_appcontext
def map_fields(  # pragma: no cover
    project_key: Optional[str],
    map_all: bool,
    show_all_types: bool,
    no_auto_match: bool,
    include_global: bool,
    dry_run: bool,
):
    """
    Map custom fields to roadmap configuration interactively.

    PROJECT_KEY: The JIRA project key (e.g., NEXUS) - required unless --all is used

    This command retrieves custom fields from JIRA and automatically matches
    them to roadmap attributes based on name similarity. Fields with >80%
    similarity are auto-matched, reducing manual selection. By default, only
    project-scoped fields are shown to reduce noise.

    Examples:
        flask jira map-fields NEXUS
        flask jira map-fields --all
        flask jira map-fields NEXUS --no-auto-match  # Disable auto-matching
        flask jira map-fields NEXUS --include-global # Show all fields including global
        flask jira map-fields NEXUS --dry-run
    """
    from ..models.custom_field import FieldMapping, ProjectFieldConfiguration
    from ..services.jira_client import JiraClient

    # Determine which projects to process
    if map_all:
        project_keys = Config.get_project_keys()
        if not project_keys:
            click.secho(
                "✗ No projects configured in config/jira_projects.json", fg="red"
            )
            click.echo("Add projects to the JSON configuration file first")
            return
    elif project_key:
        if not validate_project_key(project_key):
            click.secho("✗ Invalid project key format", fg="red")
            click.echo("Project keys must be 2-10 uppercase alphanumeric characters")
            return
        project_keys = [project_key]
    else:
        click.secho("✗ Either PROJECT_KEY or --all flag is required", fg="red")
        return

    # Validate configuration
    if not Config.is_jira_configured():
        click.secho("✗ JIRA is not configured", fg="red")
        click.echo("Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN")
        return

    # Create JIRA client
    client = JiraClient()

    # Configuration keys in order
    config_keys = [
        "public_roadmap",
        "roadmap_status",
        "module",
        "release_year",
        "release_quarter",
        "release_month",
        "documentation_url",
        "roadmap_title",
        "roadmap_description",
        "roadmap_image_url_1",
        "roadmap_image_url_2",
        "roadmap_image_url_3",
        "roadmap_image_url_4",
        "roadmap_likes",
    ]

    # Process each project
    for proj_key in project_keys:
        click.echo()
        click.secho(
            f"=== Mapping fields for project: {proj_key} ===", fg="cyan", bold=True
        )
        click.echo()

        # Retrieve custom fields
        click.echo("Retrieving custom fields...")
        try:
            fields = client.get_custom_fields(proj_key)
            total_fields = len(fields)
            logger.info(
                f"Retrieved {total_fields} fields from JIRA for project {proj_key}"
            )

            if total_fields > 0:
                logger.debug(
                    f"Sample fields: {[(f.id, f.name, f.field_type) for f in fields[:3]]}"
                )

            # Filter to project-scoped fields unless --include-global is set
            if not include_global:
                click.echo("Filtering to project-scoped fields...", nl=False)
                logger.info(f"Filtering {total_fields} fields to project-scoped only")

                # Fast filtering using field metadata only (no API calls)
                fields = filter_project_scoped_fields(fields, proj_key)
                logger.info(f"After project-scope filter: {len(fields)} fields remain")

                if len(fields) > 0:
                    logger.debug(
                        f"Project-scoped sample: {[(f.id, f.name, hasattr(f, 'projects'), getattr(f, 'projects', None)) for f in fields[:3]]}"
                    )

                click.secho(f" ✓ ({len(fields)} of {total_fields} fields)", fg="green")

            # Filter by type if requested
            if not show_all_types:
                pre_type_filter = len(fields)
                fields = client.filter_text_fields(fields)
                logger.info(
                    f"After text-field filter: {len(fields)} fields remain (was {pre_type_filter})"
                )

                if len(fields) > 0:
                    logger.debug(
                        f"Text fields sample: {[(f.id, f.name, f.field_type) for f in fields[:3]]}"
                    )

                if include_global:
                    click.secho(f"✓ Found {len(fields)} custom text fields", fg="green")
                else:
                    click.secho(
                        f"✓ {len(fields)} text fields after filtering", fg="green"
                    )
            else:
                if include_global:
                    click.secho(f"✓ Found {len(fields)} custom fields", fg="green")

            if not fields:
                click.echo("No custom fields found. Skipping this project.")
                logger.warning(
                    f"No fields remaining after filtering for project {proj_key}"
                )
                continue

        except Exception as e:
            click.secho(f"✗ Failed to retrieve fields: {e}", fg="red")
            logger.error(f"Field retrieval failed: {e}", exc_info=True)
            continue

        click.echo()

        # Attempt automatic field matching if enabled
        auto_matched = {}
        unmatched_keys = []

        if not no_auto_match:
            click.echo("Attempting automatic field matching...")
            click.echo()

            for config_key in config_keys:
                match, score = auto_match_field(config_key, fields)
                if match:
                    auto_matched[config_key] = (match, score)
                    click.echo(
                        f"  ✓ {config_key:25} → {match.name} ({match.id}) [{score:.0%} confidence]"
                    )
                else:
                    unmatched_keys.append(config_key)

            click.echo()
            click.echo(f"Auto-matched: {len(auto_matched)} fields")
            click.echo(f"Need input:   {len(unmatched_keys)} fields")
            click.echo()

            # Offer review of auto-matched fields
            if auto_matched and click.confirm(
                "Review auto-matched fields?", default=False
            ):
                click.echo()
                click.echo(
                    "Review auto-matched fields (press Enter to keep, or enter a different number):"
                )
                click.echo()

                revised_matches = {}
                for config_key, (field, score) in auto_matched.items():
                    mapping = FieldMapping(
                        config_key=config_key, field_id="", is_selected=False
                    )
                    click.secho(f"\n{mapping.display_label}", fg="yellow", bold=True)
                    click.echo(
                        f"  Auto-matched to: {field.name} ({field.id}) [{score:.0%}]"
                    )
                    click.echo()

                    if click.confirm("  Keep this match?", default=True):
                        revised_matches[config_key] = (field, score)
                    else:
                        unmatched_keys.append(config_key)

                auto_matched = revised_matches
                click.echo()
                click.echo(f"Confirmed: {len(auto_matched)} fields")
                click.echo(f"Need input: {len(unmatched_keys)} fields")
        else:
            unmatched_keys = config_keys.copy()

        click.echo()
        click.echo(
            "Select custom fields for remaining attributes:"
            if auto_matched
            else "Select custom fields for each roadmap attribute:"
        )
        click.echo()

        # Create mappings list with auto-matched fields
        mappings = []

        # Add auto-matched fields first
        for config_key, (field, _score) in auto_matched.items():
            mapping = FieldMapping(
                config_key=config_key,
                field_id=field.id,
                field_name=field.name,
                is_selected=True,
            )
            mappings.append(mapping)

        # Interactive selection for unmatched fields
        for config_key in unmatched_keys:
            mapping = FieldMapping(
                config_key=config_key, field_id="", is_selected=False
            )

            click.secho(f"\n{mapping.display_label}", fg="yellow", bold=True)
            click.echo()

            # Display available fields with numbers
            for idx, field in enumerate(fields, start=1):
                click.echo(
                    f"  {idx}. {field.display_name} - {field.field_type_display}"
                )

            skip_idx = len(fields) + 1
            click.echo(
                f"  {skip_idx}. Skip this field {'(optional)' if mapping.is_optional else '(required)'}"
            )
            click.echo()

            # Prompt for selection
            while True:
                try:
                    selection = click.prompt(
                        "Enter selection",
                        type=int,
                        default=skip_idx if mapping.is_optional else None,
                    )

                    if selection == skip_idx:
                        if not mapping.is_optional:
                            click.secho(
                                "This field is required. Please select a field.",
                                fg="red",
                            )
                            continue
                        # Skip optional field
                        mapping.field_id = "customfield_00000"  # Placeholder
                        mapping.is_selected = False
                        break
                    elif 1 <= selection <= len(fields):
                        selected_field = fields[selection - 1]
                        mapping.field_id = selected_field.id
                        mapping.field_name = selected_field.name
                        mapping.is_selected = True
                        break
                    else:
                        click.secho("Invalid selection. Please try again.", fg="red")
                except (ValueError, click.Abort):
                    click.secho("\nMapping cancelled.", fg="yellow")
                    return

            mappings.append(mapping)

        # Display confirmation summary
        click.echo()
        click.secho("=" * 70, fg="cyan")
        click.secho(
            f"Confirm field mappings for project {proj_key}:", fg="cyan", bold=True
        )
        click.secho("=" * 70, fg="cyan")
        click.echo()

        for mapping in mappings:
            if mapping.is_selected:
                click.echo(
                    f"  {mapping.display_label:45} → {mapping.field_name} ({mapping.field_id})"
                )
            else:
                click.echo(f"  {mapping.display_label:45} → (skipped)")

        click.echo()

        if dry_run:
            click.secho("Dry run mode - no changes will be saved", fg="yellow")
            continue

        # Confirm before saving
        if not click.confirm("Save configuration?", default=True):
            click.echo("Cancelled. No changes made.")
            continue

        # Create configuration and update file
        try:
            config = ProjectFieldConfiguration.from_mappings(mappings)

            # Update configuration file
            config_path = (
                Path(__file__).parent.parent.parent / "config" / "jira_projects.json"
            )

            # Atomic update
            import shutil
            import tempfile

            # Load existing or create new
            if config_path.exists():
                with open(config_path, "r") as f:
                    config_data = json.load(f)
            else:
                config_data = {"version": "1.0", "projects": {}}

            # Update project
            config_data["projects"][proj_key] = config.to_dict()

            # Write to temp file then rename (atomic)
            temp_fd, temp_path = tempfile.mkstemp(
                dir=config_path.parent, suffix=".json", text=True
            )
            try:
                with os.fdopen(temp_fd, "w") as temp_file:
                    json.dump(config_data, temp_file, indent=2)
                    temp_file.write("\n")

                shutil.move(temp_path, str(config_path))
                click.secho(f"✓ Configuration updated for {proj_key}", fg="green")

            except Exception:
                Path(temp_path).unlink(missing_ok=True)
                raise

        except Exception as e:
            click.secho(f"✗ Failed to update configuration: {e}", fg="red")
            continue

    click.echo()
    click.secho("Field mapping complete!", fg="green", bold=True)
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Validate configuration: flask jira validate-config")
    click.echo("  2. Test sync: flask sync run --once")
    click.echo("  3. Check roadmap display")


@jira_cli.command("validate-config")
@click.argument("project_key", required=False)
@click.option("--fix", is_flag=True, help="Attempt to auto-fix issues by re-prompting")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed validation checks")
@with_appcontext
def validate_config(
    project_key: Optional[str], fix: bool, verbose: bool
):  # pragma: no cover
    """
    Validate that custom field IDs in configuration exist and are accessible in JIRA.

    PROJECT_KEY: Optional project key to validate (validates all projects if omitted)

    This command checks each configured custom field ID against JIRA to ensure
    they exist and are accessible with current credentials.

    Examples:
        flask jira validate-config
        flask jira validate-config NEXUS
        flask jira validate-config --verbose
    """
    from ..services.jira_client import JiraClient

    click.echo("Validating JIRA custom field configuration...")
    click.echo()

    # Validate JIRA configuration
    if not Config.is_jira_configured():
        click.secho("✗ JIRA is not configured", fg="red")
        click.echo("Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN")
        return 1

    # Load configuration file
    config_path = Path(__file__).parent.parent.parent / "config" / "jira_projects.json"

    if not config_path.exists():
        click.secho("✗ Configuration file not found", fg="red")
        click.echo(f"Expected location: {config_path}")
        click.echo("Run 'flask jira map-fields' to create configuration")
        return 1

    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
    except Exception as e:
        click.secho(f"✗ Failed to load configuration: {e}", fg="red")
        return 1

    # Determine which projects to validate
    if project_key:
        if project_key not in config_data.get("projects", {}):
            click.secho(
                f"✗ Project '{project_key}' not found in configuration", fg="red"
            )
            return 1
        projects_to_validate = {project_key: config_data["projects"][project_key]}
    else:
        projects_to_validate = config_data.get("projects", {})

    if not projects_to_validate:
        click.secho("✗ No projects configured", fg="red")
        return 1

    # Create JIRA client
    try:
        client = JiraClient()
    except Exception as e:
        click.secho(f"✗ Failed to create JIRA client: {e}", fg="red")
        return 1

    # Validate each project
    validation_results = {}
    total_fields = 0
    valid_fields = 0
    invalid_fields = 0
    inaccessible_fields = 0

    for proj_key, proj_config in projects_to_validate.items():
        click.secho(f"\nValidating project: {proj_key}", fg="cyan", bold=True)

        if verbose:
            click.echo("Retrieving custom fields from JIRA...")

        try:
            # Get all custom fields from JIRA
            jira_fields = client.get_custom_fields(proj_key)
            jira_field_ids = {field.id for field in jira_fields}

            if verbose:
                click.echo(f"Found {len(jira_field_ids)} custom fields in JIRA")

            # Validate each configured field
            project_results = {}

            for field_name, field_id in proj_config.items():
                total_fields += 1

                # Check if field exists
                if field_id in jira_field_ids:
                    if verbose:
                        click.echo(f"  ✓ {field_name} ({field_id})")
                    project_results[field_name] = "valid"
                    valid_fields += 1
                elif (
                    field_id == "customfield_00000"
                ):  # Placeholder for skipped optional fields
                    if verbose:
                        click.echo(f"  ⊘ {field_name} (skipped/optional)")
                    project_results[field_name] = "skipped"
                else:
                    click.secho(
                        f"  ✗ {field_name} ({field_id}) - Field not found", fg="red"
                    )
                    project_results[field_name] = "invalid"
                    invalid_fields += 1

            validation_results[proj_key] = project_results

        except Exception as e:
            click.secho(f"✗ Failed to validate {proj_key}: {e}", fg="red")
            validation_results[proj_key] = {"error": str(e)}
            inaccessible_fields += len(proj_config)

    # Display summary
    click.echo()
    click.secho("=" * 70, fg="cyan")
    click.secho("Validation Summary", fg="cyan", bold=True)
    click.secho("=" * 70, fg="cyan")
    click.echo(f"Projects Validated: {len(projects_to_validate)}")
    click.echo(f"Fields Validated: {total_fields}")
    click.echo(f"Valid: {valid_fields} ✓")
    click.echo(f"Invalid: {invalid_fields} ✗")
    click.echo(f"Inaccessible: {inaccessible_fields} ⚠")
    click.echo()

    # Determine exit code
    if invalid_fields > 0 or inaccessible_fields > 0:
        click.secho("Configuration has issues.", fg="yellow")
        if fix:
            click.echo("Use 'flask jira map-fields PROJECT_KEY' to fix configuration")
        return 1
    else:
        click.secho("Configuration is valid and ready to use.", fg="green")
        return 0


@jira_cli.command("test-create-issue")
@click.argument("project_key")
@click.option("--summary", default="[TEST] Feature Request", help="Issue summary")
@click.option("--type", "issue_type", default="Task", help="Issue type name")
@with_appcontext
def test_create_issue(project_key, summary, issue_type):
    """
    Test creating a Jira issue in a project.

    This helps diagnose issue creation failures by showing detailed error messages.

    Examples:
        flask jira test-create-issue NEXUS
        flask jira test-create-issue NEXUS --type Story
        flask jira test-create-issue ENGAGE --summary "Test Feature"
    """
    from app.services.jira_client import JiraClient

    click.echo(f"Testing issue creation in project: {project_key}")
    click.echo(f"Issue type: {issue_type}")
    click.echo(f"Summary: {summary}")
    click.echo()

    try:
        client = JiraClient()

        # Test description
        description = """Test feature request submitted via CLI.

This is a test to verify issue creation works correctly.

Contact: test@example.com
Submitted: 2026-01-21"""

        click.echo("Creating issue...")
        response = client.create_issue(
            project_key=project_key,
            issue_type_name=issue_type,
            summary=summary,
            description_text=description,
            labels=["test", "feature-request"],
        )

        click.secho(f"✓ Success! Created issue: {response['key']}", fg="green")
        click.echo(f"Issue URL: {client.base_url}/browse/{response['key']}")

    except Exception as e:
        click.secho("✗ Failed to create issue", fg="red")
        click.echo(f"Error: {e}")
        click.echo()
        click.echo("Common solutions:")
        click.echo(
            "  1. Check that issue type exists: flask jira list-fields PROJECT_KEY"
        )
        click.echo("  2. Verify you have create permission in the project")
        click.echo("  3. Check if project has required custom fields")
        return 1


# Register the CLI group with Flask
def init_app(app):
    """Register CLI commands with Flask app."""
    app.cli.add_command(jira_cli)
