#!/usr/bin/env python3
"""
Unit test for the AdvancedContentSummarizer plugin.
This test verifies that the plugin correctly processes sample HTML content
and returns a non-empty summary string.
"""
import pytest
from plugin_extensions.advanced_content_summarizer import AdvancedContentSummarizer

def test_advanced_content_summarizer():
    # Sample HTML content with multiple sentences.
    html = (
        "<html><head><title>Test Page</title></head>"
        "<body><p>"
        "This is the first sentence. "
        "Here is the second sentence. "
        "Now comes the third sentence. "
        "Finally, this is the fourth sentence."
        "</p></body></html>"
    )
    summarizer = AdvancedContentSummarizer()
    output = summarizer.process(html, "http://example.com")
    # Verify that the output is a non-empty string.
    assert isinstance(output, str)
    assert len(output) > 0
    print("AdvancedContentSummarizer output:", output)

if __name__ == "__main__":
    pytest.main([__file__])
