"""
HTML sanitization service for XSS prevention.

Provides allowlist-based HTML sanitization to ensure safe rendering
of JIRA descriptions with formatting.
"""

import re
from html import escape
from urllib.parse import urlparse


class HTMLSanitizer:
    """
    Sanitize HTML content using allowlist-based approach.

    Only allows safe HTML tags and attributes required for text formatting.
    Blocks all potentially dangerous content (scripts, event handlers, etc.).
    """

    # Allowed HTML tags (security allowlist)
    ALLOWED_TAGS = {
        "p",
        "br",
        "strong",
        "em",
        "u",
        "s",
        "ul",
        "ol",
        "li",
        "code",
        "pre",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "a",
    }

    # Allowed attributes per tag
    ALLOWED_ATTRS = {
        "a": ["href", "rel", "target"],
        "code": ["class"],  # For language-* classes
    }

    # Allowed URL protocols
    ALLOWED_PROTOCOLS = {"http", "https"}

    def sanitize(self, html: str) -> str:
        """
        Sanitize HTML content by removing dangerous elements.

        Args:
            html: Raw HTML string

        Returns:
            Sanitized HTML safe for rendering
        """
        if not html:
            return ""

        # Remove script tags and their content
        html = re.sub(
            r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove style tags and their content
        html = re.sub(
            r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove event handler attributes
        html = re.sub(
            r'\s+on\w+\s*=\s*["\'][^"\']*["\']',
            "",
            html,
            flags=re.IGNORECASE,
        )

        # Process tags - keep only allowed ones
        html = self._process_tags(html)

        # Validate and sanitize links
        html = self._sanitize_links(html)

        return html

    def _process_tags(self, html: str) -> str:
        """
        Process HTML tags, keeping only allowed ones.

        Args:
            html: HTML string

        Returns:
            HTML with only allowed tags
        """
        # Pattern to match opening and closing tags
        tag_pattern = re.compile(r"<(/?)(\w+)([^>]*)>")

        def replace_tag(match):
            is_closing = match.group(1)
            tag_name = match.group(2).lower()
            attributes = match.group(3)

            # If tag not allowed, remove it
            if tag_name not in self.ALLOWED_TAGS:
                return ""

            # For closing tags, just return if allowed
            if is_closing:
                return f"</{tag_name}>"

            # For opening tags, filter attributes
            filtered_attrs = self._filter_attributes(tag_name, attributes)

            if filtered_attrs:
                return f"<{tag_name} {filtered_attrs}>"
            return f"<{tag_name}>"

        return tag_pattern.sub(replace_tag, html)

    def _filter_attributes(self, tag_name: str, attributes: str) -> str:
        """
        Filter attributes for a tag, keeping only allowed ones.

        Args:
            tag_name: HTML tag name
            attributes: Raw attribute string

        Returns:
            Filtered attribute string
        """
        if tag_name not in self.ALLOWED_ATTRS:
            return ""

        allowed = self.ALLOWED_ATTRS[tag_name]

        # Parse attributes
        attr_pattern = re.compile(r'(\w+)\s*=\s*["\']([^"\']*)["\']')
        matches = attr_pattern.findall(attributes)

        filtered = []
        for attr_name, attr_value in matches:
            if attr_name.lower() in allowed:
                # Escape attribute value
                safe_value = escape(attr_value, quote=True)
                filtered.append(f'{attr_name}="{safe_value}"')

        return " ".join(filtered)

    def _sanitize_links(self, html: str) -> str:
        """
        Sanitize link tags with security headers and URL validation.

        Args:
            html: HTML string

        Returns:
            HTML with sanitized links
        """
        # Pattern to match <a> tags
        link_pattern = re.compile(
            r'<a\s+([^>]*href\s*=\s*["\']([^"\']*)["\'][^>]*)>',
            re.IGNORECASE,
        )

        def sanitize_link(match):
            attributes = match.group(1)
            href = match.group(2)

            # Validate URL
            if not self._is_safe_url(href):
                # Remove unsafe link, keep text only
                return ""

            # Build safe link with security headers
            safe_attrs = [f'href="{escape(href, quote=True)}"']
            safe_attrs.append('rel="noopener noreferrer"')
            safe_attrs.append('target="_blank"')

            # Check for class attribute (might be present)
            class_match = re.search(
                r'class\s*=\s*["\']([^"\']*)["\']', attributes, re.IGNORECASE
            )
            if class_match:
                class_value = class_match.group(1)
                safe_attrs.append(f'class="{escape(class_value, quote=True)}"')

            return f'<a {" ".join(safe_attrs)}>'

        return link_pattern.sub(sanitize_link, html)

    def _is_safe_url(self, url: str) -> bool:
        """
        Check if URL is safe (http/https only, no javascript:, data:, etc.).

        Args:
            url: URL string

        Returns:
            True if URL is safe, False otherwise
        """
        if not url:
            return False

        # Check for dangerous protocols
        url_lower = url.lower().strip()

        if url_lower.startswith("javascript:"):
            return False
        if url_lower.startswith("data:"):
            return False
        if url_lower.startswith("vbscript:"):
            return False
        if url_lower.startswith("file:"):
            return False

        # Parse URL
        try:
            parsed = urlparse(url)
            # If no scheme, assume relative URL (safe)
            if not parsed.scheme:
                return True
            # Only allow http/https
            return parsed.scheme.lower() in self.ALLOWED_PROTOCOLS
        except Exception:
            return False
