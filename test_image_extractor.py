#!/usr/bin/env python3
"""
Unit test for the ImageExtractor plugin.

This test verifies that the ImageExtractor plugin correctly extracts 
image sources and alt texts from HTML content.
"""
import pytest
from plugin_extensions.image_extractor import ImageExtractor

def test_image_extractor():
    html = """
    <html>
      <head><title>Image Test</title></head>
      <body>
        <img src="http://example.com/image1.png" alt="Image1">
        <img src="http://example.com/image2.jpg" alt="Image2">
      </body>
    </html>
    """
    plugin = ImageExtractor()
    result = plugin.process(html, "http://example.com")
    expected = [
        {"src": "http://example.com/image1.png", "alt": "Image1"},
        {"src": "http://example.com/image2.jpg", "alt": "Image2"}
    ]
    assert result == expected, f"Expected {expected}, got {result}"

if __name__ == "__main__":
    pytest.main([__file__])
