#!/usr/bin/env python3
"""
ImageExtractor plugin for the crawler.

Extracts all image sources and alt texts from HTML content.
"""
from plugins import PluginBase
from bs4 import BeautifulSoup

class ImageExtractor(PluginBase):
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "")
            if src:
                images.append({"src": src, "alt": alt})
        return images
