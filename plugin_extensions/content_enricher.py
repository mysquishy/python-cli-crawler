#!/usr/bin/env python3
"""
ContentEnricher plugin for the crawler.

Simulates content enrichment by extracting text from HTML and appending an enrichment string.
Configuration parameters (nested):
  - enrichment:
      level: integer (default: 1)
      append_text: string (default: " [enriched]")
  - api: 
      endpoint: string (default: "http://dummyapi")
      key: string (default: "dummy_key")
"""
from plugins import PluginBase
from bs4 import BeautifulSoup

class ContentEnricher(PluginBase):
    def __init__(self):
        # Default nested configuration options
        self.enrichment_level = 1
        self.append_text = " [enriched]"
        self.api_endpoint = "http://dummyapi"
        self.api_key = "dummy_key"
    
    def configure(self, settings):
        enrichment_config = settings.get("enrichment", {})
        self.enrichment_level = enrichment_config.get("level", 1)
        self.append_text = enrichment_config.get("append_text", " [enriched]")
        api_config = settings.get("api", {})
        self.api_endpoint = api_config.get("endpoint", "http://dummyapi")
        self.api_key = api_config.get("key", "dummy_key")
    
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        # Simulate enrichment by appending text repeatedly based on the enrichment level.
        enriched_text = text + self.append_text * self.enrichment_level
        return enriched_text
