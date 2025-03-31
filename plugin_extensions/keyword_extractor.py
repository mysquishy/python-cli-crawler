#!/usr/bin/env python3
"""
KeywordExtractor plugin for the crawler.

Extracts keywords from HTML text using basic frequency analysis.
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
import re
from collections import Counter

class KeywordExtractor(PluginBase):
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").lower()
        # Extract words with at least 3 letters.
        words = re.findall(r'\b[a-z]{3,}\b', text)
        # Define a simple set of stopwords.
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 
            'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'this', 'that', 'with'
        }
        filtered_words = [word for word in words if word not in stopwords]
        counts = Counter(filtered_words)
        # Return top 5 keywords based on frequency.
        keywords = [word for word, count in counts.most_common(5)]
        return keywords
