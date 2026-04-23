"""
Dynamic feature request routing based on existing roadmap data.

Automatically maps modules to Jira projects by analyzing existing roadmap items.
This ensures new modules appear automatically without manual configuration.
"""

import logging
from collections import defaultdict
from typing import Optional

from ..models.feature_request import FeatureRequestRoutingRule

logger = logging.getLogger(__name__)


class FeatureRequestRoutingConfig:
    """
    Manages dynamic feature request routing.

    Builds module-to-project mapping by analyzing existing roadmap items
    in the cache. This ensures:
    - New modules appear automatically when added to Jira
    - No manual configuration needed
    - Routing always reflects current roadmap structure
    """

    def __init__(self, cache_service=None):
        """
        Initialize routing configuration.

        Args:
            cache_service: CacheService instance to access roadmap data.
                          If None, routing will be empty until build_from_cache is called.
        """
        self.default_issue_type_name: str = "Task"
        self.routes: dict[str, FeatureRequestRoutingRule] = {}

        if cache_service:
            self.build_from_cache(cache_service)

    def build_from_cache(self, cache_service):
        """
        Build dynamic routing by analyzing existing roadmap items.

        For each module, determines the Jira project by examining issue key prefixes
        from existing roadmap items.

        Args:
            cache_service: CacheService instance to access roadmap items
        """
        try:
            # Get all roadmap items
            items = cache_service.get_items()

            # Build mapping: moduleId → set of project keys
            module_projects: dict[str, set[str]] = defaultdict(set)

            for item in items:
                # Extract project key from issue ID (e.g., "NEXUS-123" → "NEXUS")
                if "-" in item.id:
                    project_key = item.id.split("-")[0]
                    module_projects[item.module_id].add(project_key)

            # Create routing rules for each module
            self.routes = {}
            for module_id, project_keys in module_projects.items():
                if not project_keys:
                    continue

                # If module appears in multiple projects, use the most common one
                # For simplicity, just use the first one alphabetically
                primary_project = sorted(project_keys)[0]

                rule = FeatureRequestRoutingRule(
                    module_id=module_id,
                    jira_project_key=primary_project,
                    jira_issue_type_name=None,
                    labels=["feature-request"],
                )
                self.routes[module_id] = rule

            logger.info(
                f"Built dynamic routing for {len(self.routes)} modules from roadmap cache"
            )

            # Log the mappings for visibility
            for module_id, rule in sorted(self.routes.items()):
                logger.info(f"  {module_id} → {rule.jira_project_key}")

        except Exception as e:
            logger.error(f"Failed to build dynamic routing from cache: {e}")
            self.routes = {}

    def get_route(self, module_id: str) -> Optional[FeatureRequestRoutingRule]:
        """
        Get routing rule for a module.

        Args:
            module_id: Module identifier (slug)

        Returns:
            Routing rule if found, None otherwise
        """
        return self.routes.get(module_id)

    def get_routable_module_ids(self) -> list[str]:
        """
        Get list of all routable module IDs.

        Returns:
            List of module IDs that have routing rules (all modules with roadmap items)
        """
        return sorted(self.routes.keys())

    def is_routable(self, module_id: str) -> bool:
        """
        Check if a module is routable.

        Args:
            module_id: Module identifier to check

        Returns:
            True if module has a routing rule (has existing roadmap items)
        """
        return module_id in self.routes

    def get_module_project_key(self, module_id: str) -> Optional[str]:
        """
        Get the Jira project key for a module.

        Args:
            module_id: Module identifier

        Returns:
            Jira project key if found, None otherwise
        """
        route = self.get_route(module_id)
        return route.jira_project_key if route else None
