#!/usr/bin/env python3
"""
Unit tests for the TextSummarizer plugin.

This test verifies that the TextSummarizer plugin extracts a summary consisting of the first two sentences.
"""
import pytest
from plugin_extensions.text_summarizer import TextSummarizer

def test_text_summarizer():
    html = """
    <html>
      <head><title>Test Page</title></head>
      <body>
        <p>This is the first sentence. This is the second sentence. This is the third sentence.</p>
      </body>
    </html>
    """
    plugin = TextSummarizer()
    summary = plugin.process(html, "http://example.com")
    expected = "This is the first sentence. This is the second sentence."
    assert expected in summary, f"Expected summary to contain:\n{expected}\nbut got:\n{summary}"

if __name__ == "__main__":
    pytest.main([__file__])
