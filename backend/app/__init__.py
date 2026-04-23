"""
Flask application factory for the VTEX Ads Public Roadmap API.
"""

import logging

from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config

# Configure logging to show INFO level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize extensions
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No default limits; apply per-route
    storage_uri="memory://",  # Use in-memory storage for rate limit tracking
    strategy="fixed-window",  # Fixed window strategy
)


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Load project-specific custom field configuration
    config_class.load_project_config()

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register CLI commands
    _register_cli_commands(app)

    # Start background sync scheduler (avoid in Flask reloader subprocess)
    _init_scheduler(app)

    return app


def _init_extensions(app: Flask):
    """Initialize Flask extensions."""
    # CORS - allow all origins
    CORS(app)

    # Cache
    cache_config = {
        "CACHE_TYPE": app.config.get("CACHE_TYPE", "simple"),
    }
    if app.config.get("REDIS_URL"):
        cache_config["CACHE_REDIS_URL"] = app.config["REDIS_URL"]
    cache.init_app(app, config=cache_config)

    # Rate limiter with custom error handler
    limiter.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit errors and return custom error response."""
        from flask import jsonify

        return (
            jsonify(
                {
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please wait and try again. Limits: 3 per minute, 10 per hour.",
                }
            ),
            429,
        )


def _register_blueprints(app: Flask):
    """Register API blueprints."""
    from .routes import health_bp, roadmap_bp

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(roadmap_bp, url_prefix="/api/v1/roadmap")


def _register_cli_commands(app: Flask):
    """Register Flask CLI commands."""
    # Import and register CLI command groups
    try:
        from .cli import jira_cli

        app.cli.add_command(jira_cli)
        logger.info("Registered JIRA CLI commands")
    except ImportError as e:
        logger.warning(f"Failed to register CLI commands: {e}")


def _init_scheduler(app: Flask):
    """Initialize the background sync scheduler.

    Disabled when ENABLE_SCHEDULER=false (e.g. Vercel serverless).
    In that case, use the POST /api/v1/sync endpoint triggered by Vercel Cron.
    """
    if not app.config.get("ENABLE_SYNC", True):
        logger.info("JIRA sync is disabled (ENABLE_SYNC=false)")
        return

    if not app.config.get("ENABLE_SCHEDULER", True):
        logger.info(
            "Scheduler disabled (ENABLE_SCHEDULER=false) - "
            "use POST /api/v1/sync with Vercel Cron Jobs"
        )
        return

    logger.info("Initializing JIRA sync scheduler...")
    from .services.sync_service import start_scheduler

    with app.app_context():
        start_scheduler(app)
