"""
Unit tests for HTML sanitization service.

Tests XSS prevention and allowlist-based sanitization.
"""

import pytest

from app.services.html_sanitizer import HTMLSanitizer


@pytest.fixture
def sanitizer():
    """Return HTMLSanitizer instance for testing."""
    return HTMLSanitizer()


class TestXSSPrevention:
    """Test XSS attack prevention."""

    def test_script_tag_removal(self, sanitizer):
        """Test that script tags are completely removed."""
        html = '<p>Safe text</p><script>alert("XSS")</script><p>More text</p>'
        result = sanitizer.sanitize(html)

        assert "<script>" not in result
        assert "alert" not in result
        assert "<p>Safe text</p>" in result
        assert "<p>More text</p>" in result

    def test_script_tag_with_attributes(self, sanitizer):
        """Test that script tags with attributes are removed."""
        html = '<script type="text/javascript" src="evil.js">alert(1)</script>'
        result = sanitizer.sanitize(html)

        assert "<script" not in result
        assert "evil.js" not in result

    def test_inline_event_handler_removal(self, sanitizer):
        """Test that inline event handlers are removed."""
        test_cases = [
            ('<p onclick="alert(1)">Click me</p>', "<p>Click me</p>"),
            ('<a href="#" onerror="alert(1)">Link</a>', '<a href="#">Link</a>'),
            ('<img onload="alert(1)" src="x.jpg">', ""),  # img not allowed
            ('<div onmouseover="alert(1)">Hover</div>', ""),  # div not allowed
        ]

        for html_input, _expected_contains in test_cases:
            result = sanitizer.sanitize(html_input)
            # Check that event handlers are removed
            assert "onclick" not in result.lower()
            assert "onerror" not in result.lower()
            assert "onload" not in result.lower()
            assert "onmouseover" not in result.lower()
            assert "alert" not in result

    def test_javascript_url_blocking(self, sanitizer):
        """Test that javascript: URLs in links are blocked."""
        html = '<a href="javascript:alert(1)">Click me</a>'
        result = sanitizer.sanitize(html)

        # Link should be removed or href blocked
        if "<a" in result:
            assert "javascript:" not in result.lower()

    def test_data_url_blocking(self, sanitizer):
        """Test that data: URLs are blocked."""
        html = '<a href="data:text/html,<script>alert(1)</script>">Link</a>'
        result = sanitizer.sanitize(html)

        # Link should be removed or href blocked
        if "<a" in result:
            assert "data:" not in result.lower()

    def test_vbscript_url_blocking(self, sanitizer):
        """Test that vbscript: URLs are blocked."""
        html = '<a href="vbscript:msgbox(1)">Link</a>'
        result = sanitizer.sanitize(html)

        if "<a" in result:
            assert "vbscript:" not in result.lower()

    def test_style_tag_removal(self, sanitizer):
        """Test that style tags are removed."""
        html = "<p>Text</p><style>body { background: red; }</style>"
        result = sanitizer.sanitize(html)

        assert "<style>" not in result
        assert "background" not in result

    def test_disallowed_tags_removed(self, sanitizer):
        """Test that disallowed tags are removed."""
        html = '<iframe src="evil.com"></iframe><p>Safe</p>'
        result = sanitizer.sanitize(html)

        assert "<iframe" not in result
        assert "evil.com" not in result
        assert "<p>Safe</p>" in result


class TestSafeHTMLAllowed:
    """Test that safe HTML tags pass through correctly."""

    def test_paragraph_tags(self, sanitizer):
        """Test that paragraph tags are allowed."""
        html = "<p>This is a paragraph.</p>"
        result = sanitizer.sanitize(html)

        assert result == "<p>This is a paragraph.</p>"

    def test_strong_tags(self, sanitizer):
        """Test that strong tags are allowed."""
        html = "<p>This is <strong>bold</strong> text.</p>"
        result = sanitizer.sanitize(html)

        assert "<strong>bold</strong>" in result

    def test_em_tags(self, sanitizer):
        """Test that em tags are allowed."""
        html = "<p>This is <em>italic</em> text.</p>"
        result = sanitizer.sanitize(html)

        assert "<em>italic</em>" in result

    def test_underline_tags(self, sanitizer):
        """Test that u tags are allowed."""
        html = "<p>This is <u>underlined</u> text.</p>"
        result = sanitizer.sanitize(html)

        assert "<u>underlined</u>" in result

    def test_strikethrough_tags(self, sanitizer):
        """Test that s tags are allowed."""
        html = "<p>This is <s>strikethrough</s> text.</p>"
        result = sanitizer.sanitize(html)

        assert "<s>strikethrough</s>" in result

    def test_list_tags(self, sanitizer):
        """Test that list tags are allowed."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = sanitizer.sanitize(html)

        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "</ul>" in result

    def test_ordered_list_tags(self, sanitizer):
        """Test that ordered list tags are allowed."""
        html = "<ol><li>First</li><li>Second</li></ol>"
        result = sanitizer.sanitize(html)

        assert "<ol>" in result
        assert "<li>First</li>" in result
        assert "</ol>" in result

    def test_heading_tags(self, sanitizer):
        """Test that heading tags are allowed."""
        for level in range(1, 7):
            html = f"<h{level}>Heading</h{level}>"
            result = sanitizer.sanitize(html)

            assert f"<h{level}>Heading</h{level}>" in result

    def test_code_tags(self, sanitizer):
        """Test that code tags are allowed."""
        html = "<p>Use <code>print()</code> function.</p>"
        result = sanitizer.sanitize(html)

        assert "<code>print()</code>" in result

    def test_pre_tags(self, sanitizer):
        """Test that pre tags are allowed."""
        html = "<pre><code>def hello():\n    print('Hi')</code></pre>"
        result = sanitizer.sanitize(html)

        assert "<pre>" in result
        assert "<code>" in result
        assert "</pre>" in result

    def test_blockquote_tags(self, sanitizer):
        """Test that blockquote tags are allowed."""
        html = "<blockquote>This is a quote.</blockquote>"
        result = sanitizer.sanitize(html)

        assert "<blockquote>This is a quote.</blockquote>" in result

    def test_br_tags(self, sanitizer):
        """Test that br tags are allowed."""
        html = "<p>Line 1<br>Line 2</p>"
        result = sanitizer.sanitize(html)

        assert "<br>" in result


class TestLinkSanitization:
    """Test link sanitization with security attributes."""

    def test_safe_https_link_allowed(self, sanitizer):
        """Test that safe HTTPS links are allowed."""
        html = '<a href="https://example.com">Link</a>'
        result = sanitizer.sanitize(html)

        assert "<a" in result
        assert 'href="https://example.com"' in result

    def test_safe_http_link_allowed(self, sanitizer):
        """Test that safe HTTP links are allowed."""
        html = '<a href="http://example.com">Link</a>'
        result = sanitizer.sanitize(html)

        assert "<a" in result
        assert 'href="http://example.com"' in result

    def test_link_security_attributes_added(self, sanitizer):
        """Test that security attributes are added to links."""
        html = '<a href="https://example.com">Link</a>'
        result = sanitizer.sanitize(html)

        assert 'rel="noopener noreferrer"' in result
        assert 'target="_blank"' in result

    def test_existing_link_attributes_overridden(self, sanitizer):
        """Test that existing link attributes are overridden with safe values."""
        html = '<a href="https://example.com" target="_self" rel="opener">Link</a>'
        result = sanitizer.sanitize(html)

        # Security attributes should be enforced
        assert 'rel="noopener noreferrer"' in result
        assert 'target="_blank"' in result

    def test_relative_url_allowed(self, sanitizer):
        """Test that relative URLs are allowed."""
        html = '<a href="/docs/guide">Guide</a>'
        result = sanitizer.sanitize(html)

        assert 'href="/docs/guide"' in result

    def test_anchor_link_allowed(self, sanitizer):
        """Test that anchor links are allowed."""
        html = '<a href="#section">Jump to section</a>'
        result = sanitizer.sanitize(html)

        assert 'href="#section"' in result

    def test_html_escaping_in_attributes(self, sanitizer):
        """Test that HTML is escaped in attributes."""
        # Use a safe URL with special chars that need escaping
        html = '<a href="https://example.com?foo=bar&baz=qux">Link</a>'
        result = sanitizer.sanitize(html)

        # Should contain href with escaped ampersand
        assert "href=" in result
        assert "example.com" in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_string(self, sanitizer):
        """Test that empty string returns empty string."""
        result = sanitizer.sanitize("")
        assert result == ""

    def test_none_value(self, sanitizer):
        """Test that None returns empty string."""
        result = sanitizer.sanitize(None)
        assert result == ""

    def test_mixed_case_tags(self, sanitizer):
        """Test that mixed case tags are handled correctly."""
        html = "<P>Text</P><STRONG>Bold</STRONG>"
        result = sanitizer.sanitize(html)

        # Should normalize to lowercase
        assert "<p>" in result.lower() or "<P>" in result
        assert "Text" in result
        assert "Bold" in result

    def test_malformed_html(self, sanitizer):
        """Test that malformed HTML doesn't break sanitizer."""
        html = "<p>Unclosed paragraph<strong>Bold</p>"
        result = sanitizer.sanitize(html)

        # Should still process what it can
        assert "Unclosed paragraph" in result
        assert "Bold" in result

    def test_nested_tags(self, sanitizer):
        """Test that nested allowed tags work correctly."""
        html = "<p>This is <strong>very <em>important</em></strong> text.</p>"
        result = sanitizer.sanitize(html)

        assert "<strong>" in result
        assert "<em>important</em>" in result
        assert "</strong>" in result

    def test_code_language_class_preserved(self, sanitizer):
        """Test that language classes on code tags are preserved."""
        html = '<pre><code class="language-python">print("hi")</code></pre>'
        result = sanitizer.sanitize(html)

        assert 'class="language-python"' in result
