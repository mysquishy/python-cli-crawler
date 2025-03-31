#!/usr/bin/env python3
"""
Unit test for the AdvancedContentSummarizer plugin.

This test verifies that the plugin generates a summary from the HTML content.
"""
import pytest
from plugin_extensions.advanced_content_summarizer import AdvancedContentSummarizer

def test_advanced_content_summarizer():
    html = """
    <html>
      <head><title>Advanced Summarization Test</title></head>
      <body>
        <p>
          The quick brown fox jumps over the lazy dog. 
          This sentence is added to provide enough text for summarization.
          Another sentence is here to ensure the content is long.
          Yet another sentence for good measure.
        </p>
      </body>
    </html>
    """
    plugin = AdvancedContentSummarizer()
    summary = plugin.process(html, "http://example.com")
    # Check that the summary is a non-empty string.
    assert isinstance(summary, str) and len(summary) > 0, "Summary should be a non-empty string."

if __name__ == "__main__":
    pytest.main([__file__])
