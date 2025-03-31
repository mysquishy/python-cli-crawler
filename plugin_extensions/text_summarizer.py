#!/usr/bin/env python3
"""
TextSummarizer plugin for the crawler.

Extracts a summary of text content by returning the first N sentences of the page.
Configuration:
  - sentence_count: The number of sentences to include in the summary (default is 2).
"""
from plugins import PluginBase
import re
from bs4 import BeautifulSoup

class TextSummarizer(PluginBase):
    def __init__(self):
        self.sentence_count = 2

    def configure(self, settings):
        """Configure the plugin with provided settings."""
        self.sentence_count = settings.get("sentence_count", 2)

    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        # Simplistic sentence splitting based on punctuation.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = " ".join(sentences[:self.sentence_count]) if len(sentences) >= self.sentence_count else text
        return summary
