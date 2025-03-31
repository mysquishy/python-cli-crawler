#!/usr/bin/env python3
"""
HeadingExtractor plugin for the crawler.

Extracts all h1, h2, and h3 headings from HTML content.
"""
from plugins import PluginBase
from bs4 import BeautifulSoup

class HeadingExtractor(PluginBase):
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        headings = {}
        for level in ['h1', 'h2', 'h3']:
            tags = soup.find_all(level)
            headings[level] = [tag.get_text(strip=True) for tag in tags if tag.get_text(strip=True)]
        return headings
