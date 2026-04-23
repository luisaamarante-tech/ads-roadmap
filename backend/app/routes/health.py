"""
Health check endpoint for the VTEX Ads Public Roadmap API.

Provides status information about the service and sync status.
"""

from flask import Blueprint, jsonify, request

from .. import cache
from ..services.cache_service import CacheService

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns:
        - status: healthy, degraded, or unhealthy
        - lastSyncAt: When data was last synced from JIRA
        - lastSyncStatus: SUCCESS, PARTIAL, or FAILED
        - itemCount: Number of items in cache
        - isStale: True if last sync was more than 10 minutes ago

    Status codes:
        - 200: Service is healthy or degraded
        - 503: Service is unhealthy
    """
    cache_service = CacheService(cache)
    metadata = cache_service.get_metadata()

    # Determine health status
    is_stale = metadata.is_stale(threshold_minutes=10)

    if metadata.last_sync_status == "SUCCESS" and not is_stale:
        status = "healthy"
    elif metadata.last_sync_status == "FAILED" and metadata.item_count == 0:
        status = "unhealthy"
    else:
        status = "degraded"

    from ..config import Config
    from ..services.sync_service import SyncService

    project_keys = Config.get_project_keys()

    # Auto-sync if cache is empty OR data is older than 30 minutes
    from datetime import datetime, timedelta
    is_due_for_sync = (
        metadata.item_count == 0
        or metadata.last_sync_at is None
        or (datetime.utcnow() - metadata.last_sync_at).total_seconds() > 300
    )
    if is_due_for_sync and Config.is_jira_configured() and project_keys:
        try:
            sync_service = SyncService(cache_service)
            metadata = sync_service.sync()
        except Exception:
            pass

    response = {
        "status": status,
        "lastSyncAt": (
            metadata.last_sync_at.isoformat() + "Z" if metadata.last_sync_at else None
        ),
        "lastSyncStatus": metadata.last_sync_status,
        "itemCount": metadata.item_count,
        "isStale": is_stale,
        "configuredProjects": project_keys,
    }

    if metadata.error_message:
        response["errorMessage"] = metadata.error_message

    status_code = 503 if status == "unhealthy" else 200
    return jsonify(response), status_code


@health_bp.route("/sync", methods=["POST"])
def trigger_sync():
    """
    Trigger JIRA sync on demand.

    Intended for Vercel Cron Jobs (set schedule in vercel.json).
    Requires Authorization: Bearer <CRON_SECRET> when CRON_SECRET is set.
    """
    from flask import current_app

    from ..config import Config

    cron_secret = Config.CRON_SECRET
    if cron_secret:
        auth_header = request.headers.get("Authorization", "")
        if auth_header != f"Bearer {cron_secret}":
            return jsonify({"error": "Unauthorized"}), 401

    try:
        from ..services.cache_service import CacheService
        from ..services.sync_service import SyncService

        sync_service = SyncService(CacheService(cache))
        sync_service.sync()
        return jsonify({"status": "ok", "message": "Sync completed successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Sync failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
