"""
Roadmap API endpoints for the Weni Public Roadmap.

Provides public read-only access to roadmap items, modules, and statistics.
Also provides feature request submission endpoint for public users.
"""

# Standard library
import logging
import re
from datetime import datetime

# Third-party
from flask import Blueprint, jsonify, request

# Local
from .. import cache, limiter
from ..config import Config
from ..models.feature_request import (
    FeatureRequestPayload,
    FeatureRequestResponse,
    JiraIssueReference,
)
from ..services.cache_service import CacheService
from ..services.feature_request_routing_loader import FeatureRequestRoutingConfig
from ..services.jira_client import JiraClient
from ..services.slack_service import SlackService

logger = logging.getLogger(__name__)

roadmap_bp = Blueprint("roadmap", __name__)

# Initialize routing config
_routing_config = None


def get_routing_config() -> FeatureRequestRoutingConfig:
    """
    Get or rebuild dynamic routing configuration.

    Routing is rebuilt on each request to ensure it reflects current roadmap data.
    This is lightweight since it only analyzes cached data.
    """
    global _routing_config

    # Rebuild routing from current cache to keep it fresh
    cache_service = CacheService(cache)
    _routing_config = FeatureRequestRoutingConfig(cache_service)

    return _routing_config


@roadmap_bp.route("/items", methods=["GET"])
def get_items():
    """
    Get roadmap items with optional filtering.

    Query parameters:
        - status: Filter by delivery status (DELIVERED, NOW, NEXT, FUTURE)
        - year: Filter by release year (e.g., 2025)
        - quarter: Filter by quarter (Q1, Q2, Q3, Q4)
        - module: Filter by module ID (slug). Can be repeated for multi-module filtering.
                 Example: ?module=flows&module=integrations

    Returns:
        - items: List of roadmap items
        - total: Total count of items matching filters
        - lastSyncedAt: When data was last synced
        - isStale: True if data may be outdated
    """
    # Parse query parameters
    status = request.args.get("status")
    year = request.args.get("year", type=int)
    quarter = request.args.get("quarter")

    # Handle module parameter: can be single value or list
    # getlist() returns all values for a repeated parameter
    module_list = request.args.getlist("module")

    # Backward compatibility: support single module
    if len(module_list) == 1:
        module = module_list[0]
    elif len(module_list) > 1:
        # Validate: maximum 10 modules per request
        if len(module_list) > 10:
            return (
                jsonify(
                    {
                        "error": "INVALID_REQUEST",
                        "message": "Maximum 10 modules allowed per request",
                    }
                ),
                400,
            )
        module = module_list
    else:
        # No module filter
        module = None

    # Get filtered items
    cache_service = CacheService(cache)
    items = cache_service.get_filtered_items(
        status=status,
        year=year,
        quarter=quarter,
        module=module,
    )

    # Get metadata
    metadata = cache_service.get_metadata()

    return jsonify(
        {
            "items": [item.to_dict() for item in items],
            "total": len(items),
            "lastSyncedAt": (
                metadata.last_sync_at.isoformat() + "Z"
                if metadata.last_sync_at
                else None
            ),
            "isStale": metadata.is_stale(),
        }
    )


@roadmap_bp.route("/items/<item_id>", methods=["GET"])
def get_item(item_id: str):
    """
    Get a single roadmap item by ID.

    Path parameters:
        - item_id: JIRA issue key (e.g., "PROJ-123")

    Returns:
        - The roadmap item if found
        - 404 if not found
    """
    cache_service = CacheService(cache)
    item = cache_service.get_item_by_id(item_id)

    if item is None:
        return (
            jsonify(
                {
                    "error": "NOT_FOUND",
                    "message": f"Roadmap item '{item_id}' not found",
                }
            ),
            404,
        )

    return jsonify(item.to_dict())


@roadmap_bp.route("/items/<item_id>/like", methods=["POST"])
def like_item(item_id: str):
    """
    Like a roadmap item (epic) by incrementing its like count.

    This endpoint:
    1. Validates that the item exists in the cache
    2. Increments the like count by 1
    3. Updates the JIRA custom field
    4. Invalidates the cache to force a refresh

    Path parameters:
        - item_id: JIRA issue key (e.g., "PROJ-123")

    Returns:
        - id: The item ID
        - likes: The new like count
        - success: True if operation succeeded

    Error responses:
        - 404: Item not found
        - 500: JIRA API error
    """
    cache_service = CacheService(cache)

    # Get the current item from cache
    item = cache_service.get_item_by_id(item_id)
    if item is None:
        return (
            jsonify(
                {
                    "error": "NOT_FOUND",
                    "message": f"Roadmap item '{item_id}' not found",
                    "success": False,
                }
            ),
            404,
        )

    # Calculate new like count
    new_likes = item.likes + 1

    # Update JIRA
    try:
        from ..services.jira_client import JiraClient

        jira_client = JiraClient()
        updated_likes = jira_client.update_epic_likes(item_id, new_likes)

        # Update cache with new likes count (instead of invalidating)
        cache_service.update_item_likes(item_id, updated_likes)

        return jsonify(
            {
                "id": item_id,
                "likes": updated_likes,
                "success": True,
            }
        )
    except ValueError as e:
        # Configuration error (e.g., missing field mapping)
        return (
            jsonify(
                {
                    "error": "CONFIGURATION_ERROR",
                    "message": str(e),
                    "success": False,
                }
            ),
            500,
        )
    except Exception as e:
        # JIRA API error or network issue
        return (
            jsonify(
                {
                    "error": "JIRA_ERROR",
                    "message": f"Failed to update like count in JIRA: {str(e)}",
                    "success": False,
                }
            ),
            500,
        )


@roadmap_bp.route("/modules", methods=["GET"])
def get_modules():
    """
    Get all available modules for filtering.

    Returns list of modules that have at least one public roadmap item.
    Useful for populating filter dropdowns.

    Returns:
        - modules: List of modules with id, name, and itemCount
    """
    cache_service = CacheService(cache)
    modules = cache_service.get_modules()

    return jsonify(
        {
            "modules": [module.to_dict() for module in modules],
        }
    )


@roadmap_bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Get roadmap statistics (item counts by status).

    Query parameters:
        - year: Filter stats by year
        - quarter: Filter stats by quarter
        - module: Filter stats by module (can be repeated for multi-module filtering)

    Returns:
        - stats: Object with counts per status (DELIVERED, NOW, NEXT, FUTURE)
        - total: Total count across all statuses
        - lastSyncedAt: When data was last synced
    """
    # Parse query parameters
    year = request.args.get("year", type=int)
    quarter = request.args.get("quarter")

    # Handle module parameter: can be single value or list (same as /items)
    module_list = request.args.getlist("module")

    # Convert to appropriate format
    if len(module_list) == 1:
        module = module_list[0]
    elif len(module_list) > 1:
        module = module_list
    else:
        module = None

    # Get stats
    cache_service = CacheService(cache)
    stats = cache_service.get_stats(
        year=year,
        quarter=quarter,
        module=module,
    )

    # Add metadata
    metadata = cache_service.get_metadata()
    stats["lastSyncedAt"] = (
        metadata.last_sync_at.isoformat() + "Z" if metadata.last_sync_at else None
    )

    return jsonify(stats)


@roadmap_bp.route("/feature-request/modules", methods=["GET"])
@limiter.limit("30 per minute")
def get_feature_request_modules():
    """
    Get list of modules available for feature requests.

    Returns only routable modules - modules that have routing rules configured.
    Routing is dynamically determined by analyzing existing roadmap items.

    Returns:
        - modules: List of routable modules with id and name
    """
    try:
        cache_service = CacheService(cache)
        all_modules = cache_service.get_modules()

        # Get routing config to filter only routable modules
        routing_config = get_routing_config()
        routable_module_ids = set(routing_config.get_routable_module_ids())

        # Filter to only routable modules
        routable_modules = [
            module for module in all_modules if module.id in routable_module_ids
        ]

        logger.info(
            f"Returning {len(routable_modules)} routable modules "
            f"(filtered from {len(all_modules)} total)"
        )

        return jsonify({"modules": [module.to_dict() for module in routable_modules]})

    except Exception as e:
        logger.error(f"Failed to get feature request modules: {e}")
        return (
            jsonify(
                {
                    "error": "SERVER_ERROR",
                    "message": "Failed to load modules. Please try again later.",
                }
            ),
            500,
        )


@roadmap_bp.route("/feature-requests", methods=["POST"])
@limiter.limit("3 per minute")  # Stricter: 3 requests per minute per IP
@limiter.limit("10 per hour")  # Additional: max 10 per hour per IP
def create_feature_request():
    """
    Submit a feature request.

    Creates a Jira issue in the backlog for the selected module.

    Headers:
        - Idempotency-Key: Required for duplicate prevention

    Request body:
        - moduleId: Selected module (required)
        - title: Feature request title (required)
        - description: Detailed description (required)
        - contactEmail: Requester email (required)
        - website: Honeypot field (must be empty)

    Returns:
        - success: True if created
        - issueKey: Jira issue key
        - issueUrl: Browse URL
        - leaderNotificationStatus: Slack notification status
        - message: Human-readable message
    """
    # Check idempotency key
    idempotency_key = request.headers.get("Idempotency-Key", "").strip()
    if not idempotency_key:
        logger.warning("Feature request rejected: missing idempotency key")
        return (
            jsonify(
                {
                    "error": "MISSING_IDEMPOTENCY_KEY",
                    "message": "Idempotency-Key header is required",
                }
            ),
            400,
        )

    # Validate idempotency key length (prevent abuse with huge keys)
    if len(idempotency_key) < 8 or len(idempotency_key) > 128:
        logger.warning(
            f"Feature request rejected: invalid idempotency key length {len(idempotency_key)}"
        )
        return (
            jsonify(
                {
                    "error": "INVALID_IDEMPOTENCY_KEY",
                    "message": "Idempotency-Key must be between 8 and 128 characters",
                }
            ),
            400,
        )

    # Check request size (prevent huge payloads)
    if request.content_length and request.content_length > 50000:  # 50KB limit
        logger.warning(
            f"Feature request rejected: payload too large ({request.content_length} bytes)"
        )
        return (
            jsonify(
                {
                    "error": "PAYLOAD_TOO_LARGE",
                    "message": "Request payload is too large",
                }
            ),
            413,
        )

    # Check for cached response
    cache_service = CacheService(cache)
    cached_response = cache_service.get_idempotency_response(idempotency_key)
    if cached_response:
        logger.info("Feature request idempotency hit: returning cached response")
        return jsonify(cached_response), 200

    # Parse and validate payload
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {"error": "INVALID_REQUEST", "message": "Request body is required"}
                ),
                400,
            )

        payload = FeatureRequestPayload(
            module_id=data.get("moduleId", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            contact_email=data.get("contactEmail", ""),
            website=data.get("website", ""),
        )

        # Validation
        errors = _validate_feature_request_payload(payload)
        if errors:
            logger.info(
                f"Feature request validation failed: {errors[0]} (module: {payload.module_id})"
            )
            return jsonify({"error": "VALIDATION_ERROR", "message": errors[0]}), 400

    except Exception as e:
        logger.warning(f"Feature request payload parse error: {type(e).__name__}")
        return (
            jsonify({"error": "INVALID_REQUEST", "message": "Invalid request format"}),
            400,
        )

    # Module routing
    routing_config = get_routing_config()
    route = routing_config.get_route(payload.module_id)
    if not route:
        logger.warning(
            f"Feature request rejected: invalid module '{payload.module_id}'"
        )
        return (
            jsonify(
                {
                    "error": "INVALID_MODULE",
                    "message": f"Module '{payload.module_id}' is not available for feature requests",
                }
            ),
            400,
        )

    # Create Jira issue
    try:
        logger.info(
            f"Creating feature request: module={payload.module_id}, "
            f"title_length={len(payload.title)}, project={route.jira_project_key}"
        )

        jira_client = JiraClient()
        issue_type = (
            route.jira_issue_type_name or routing_config.default_issue_type_name
        )

        # Build Jira description with all details
        jira_description = _build_jira_description(payload)

        # Create issue with [FEATURE-REQUEST] prefix
        issue_summary = f"[FEATURE-REQUEST] {payload.title}"

        jira_response = jira_client.create_issue(
            project_key=route.jira_project_key,
            issue_type_name=issue_type,
            summary=issue_summary,
            description_text=jira_description,
            labels=route.labels or ["feature-request"],
        )

        logger.info(f"Feature request created: {jira_response['key']}")

        # Build response
        issue_reference = JiraIssueReference(
            key=jira_response["key"],
            url=f"{Config.JIRA_BASE_URL}/browse/{jira_response['key']}",
            created_at=datetime.utcnow(),
        )

        # Send Slack notification (non-blocking - don't fail the request if Slack fails)
        notification_status = "PENDING"
        if Config.is_slack_configured():
            try:
                # Get module display name
                cache_service_modules = CacheService(cache)
                all_modules = cache_service_modules.get_modules()
                module_name = payload.module_id
                for mod in all_modules:
                    if mod.id == payload.module_id:
                        module_name = mod.name
                        break

                # Send notification
                slack_service = SlackService()
                success, status = slack_service.send_feature_request_notification(
                    module_name=module_name,
                    title=payload.title,
                    description_excerpt=payload.description[:200],
                    contact_email=payload.contact_email,
                    jira_issue_key=issue_reference.key,
                    jira_issue_url=issue_reference.url,
                )
                notification_status = status
            except Exception as slack_error:
                logger.error(f"Failed to send Slack notification: {slack_error}")
                notification_status = "FAILED"
        else:
            logger.info("Slack not configured, skipping notification")

        response = FeatureRequestResponse(
            success=True,
            issue_key=issue_reference.key,
            issue_url=issue_reference.url,
            leader_notification_status=notification_status,
            message="Feature request submitted successfully",
        )

        # Cache the response
        response_dict = response.to_dict()
        cache_service.set_idempotency_response(idempotency_key, response_dict)

        return jsonify(response_dict), 201

    except Exception as e:
        logger.error(f"Failed to create feature request: {e}")
        return (
            jsonify(
                {
                    "error": "JIRA_ERROR",
                    "message": "Failed to create feature request. Please try again later.",
                }
            ),
            500,
        )


def _validate_feature_request_payload(payload: FeatureRequestPayload) -> list[str]:
    """
    Validate feature request payload.

    Args:
        payload: Feature request payload to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Honeypot check
    if payload.website:
        errors.append("Invalid submission")
        return errors

    # Required fields
    if not payload.module_id:
        errors.append("Module is required")
    if not payload.title:
        errors.append("Title is required")
    if not payload.description:
        errors.append("Description is required")
    if not payload.contact_email:
        errors.append("Contact email is required")

    # Length validation
    if payload.title and len(payload.title) < 3:
        errors.append("Title must be at least 3 characters")
    if payload.title and len(payload.title) > 200:
        errors.append("Title must be at most 200 characters")
    if payload.description and len(payload.description) < 10:
        errors.append("Description must be at least 10 characters")
    if payload.description and len(payload.description) > 5000:
        errors.append("Description must be at most 5000 characters")

    # Email format validation (basic)
    if payload.contact_email and not _is_valid_email(payload.contact_email):
        errors.append("Contact email must be a valid email address")

    return errors


def _is_valid_email(email: str) -> bool:
    """Validate basic email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def _sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent injection attacks.

    Args:
        text: Raw text input

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Limit consecutive newlines (prevent format abuse)
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    # Remove control characters except newlines and tabs
    text = "".join(char for char in text if char in "\n\t" or ord(char) >= 32)

    return text.strip()


def _build_jira_description(payload: FeatureRequestPayload) -> str:
    """
    Build Jira issue description from feature request payload.

    Args:
        payload: Feature request payload

    Returns:
        Formatted description text with sanitized inputs
    """
    # Sanitize all text inputs
    module_id = _sanitize_text(payload.module_id)
    description = _sanitize_text(payload.description)
    contact_email = _sanitize_text(payload.contact_email)

    return f"""Feature Request Details:

Module: {module_id}

Description:
{description}

Contact Email: {contact_email}

Submitted: {datetime.utcnow().isoformat()}Z"""
