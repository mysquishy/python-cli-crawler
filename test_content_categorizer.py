#!/usr/bin/env python3
"""
Unit test for the ContentCategorizer plugin.

This test verifies that the ContentCategorizer plugin categorizes HTML content correctly based on keyword matching.
"""
import pytest
from plugin_extensions.content_categorizer import ContentCategorizer

def test_content_categorizer_sports():
    html = """
    <html>
      <head><title>Sports Test</title></head>
      <body>
        <p>The team played a great match. The sport event was exciting and full of energy.</p>
      </body>
    </html>
    """
    plugin = ContentCategorizer()
    category = plugin.process(html, "http://example.com")
    assert category == "Sports", f"Expected 'Sports', but got '{category}'"

def test_content_categorizer_politics():
    html = """
    <html>
      <head><title>Political News</title></head>
      <body>
        <p>The government announced a new policy. The election campaign is heating up.</p>
      </body>
    </html>
    """
    plugin = ContentCategorizer()
    category = plugin.process(html, "http://example.com")
    assert category == "Politics", f"Expected 'Politics', but got '{category}'"

def test_content_categorizer_technology():
    html = """
    <html>
      <head><title>Tech Update</title></head>
      <body>
        <p>The latest software release has many improvements. Computer and internet trends are evolving.</p>
      </body>
    </html>
    """
    plugin = ContentCategorizer()
    category = plugin.process(html, "http://example.com")
    assert category == "Technology", f"Expected 'Technology', but got '{category}'"

def test_content_categorizer_entertainment():
    html = """
    <html>
      <head><title>Entertainment Buzz</title></head>
      <body>
        <p>The concert was fantastic with great music and an amazing festival atmosphere.</p>
      </body>
    </html>
    """
    plugin = ContentCategorizer()
    category = plugin.process(html, "http://example.com")
    assert category == "Entertainment", f"Expected 'Entertainment', but got '{category}'"

def test_content_categorizer_uncategorized():
    html = """
    <html>
      <head><title>General Article</title></head>
      <body>
        <p>This article does not contain specific keywords to match any category.</p>
      </body>
    </html>
    """
    plugin = ContentCategorizer()
    category = plugin.process(html, "http://example.com")
    assert category == "Uncategorized", f"Expected 'Uncategorized', but got '{category}'"

if __name__ == "__main__":
    pytest.main([__file__])
