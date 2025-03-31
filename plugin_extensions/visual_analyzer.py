#!/usr/bin/env python3
"""
VisualAnalyzer plugin for the crawler.

Analyzes the dominant color of the first image found in the HTML content.
It downloads the image and calculates the average color as a proxy for the dominant color.

Requires: opencv-python, numpy
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
import requests
import cv2
import numpy as np
import urllib.parse

class VisualAnalyzer(PluginBase):
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        # Find the first image tag
        img_tag = soup.find("img")
        if not img_tag or not img_tag.get("src"):
            return "No image found."
        img_url = urllib.parse.urljoin(url, img_tag["src"])
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            data = np.asarray(bytearray(response.content), dtype="uint8")
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if image is None:
                return "Failed to decode image."
            # Calculate the mean color of the image (in BGR)
            mean_color = cv2.mean(image)[:3]
            # Convert BGR to RGB
            mean_color = tuple(int(c) for c in mean_color[::-1])
            return {"dominant_color": mean_color}
        except Exception as e:
            return f"Error processing image: {e}"
