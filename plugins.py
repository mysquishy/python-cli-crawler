#!/usr/bin/env python3
"""
Plugin architecture for the crawler.

Plugins can process the raw HTML and extract additional metadata.
Each plugin should inherit from PluginBase and implement the process(html, url) method.
"""

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class PluginBase(ABC):
    @abstractmethod
    def process(self, html, url):
        """
        Process raw HTML content for the given URL.
        Should return a dictionary of extracted data.
        """
        pass

class MetaTagExtractor(PluginBase):
    def process(self, html, url):
        """
        Extracts meta tag information from the HTML content.
        Returns a dictionary with meta tag names (or properties) as keys and their content as values.
        """
        soup = BeautifulSoup(html, "html.parser")
        meta_data = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                meta_data[name] = content
        return meta_data

# Additional plugins can be added here.

if __name__ == "__main__":
    # Example usage of the MetaTagExtractor plugin.
    sample_html = """
    <html>
      <head>
        <meta name="description" content="This is a test description">
        <meta property="og:title" content="Test OG Title">
      </head>
      <body>
        <h1>Sample Page</h1>
      </body>
    </html>
    """
    extractor = MetaTagExtractor()
    data = extractor.process(sample_html, "http://example.com")
    print("Extracted Meta Tags:", data)
