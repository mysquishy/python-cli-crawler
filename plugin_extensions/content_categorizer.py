#!/usr/bin/env python3
"""
ContentCategorizer plugin for the crawler.

Categorizes the content of an HTML page into topics based on the presence of keywords.
This simplistic, rule-based plugin checks for keywords associated with topics like:
- Sports
- Politics
- Technology
- Entertainment

If no keywords are found, it returns "Uncategorized".
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
import re

class ContentCategorizer(PluginBase):
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").lower()
        topics = {
            "Sports": ["sport", "game", "team", "player", "match"],
            "Politics": ["election", "government", "policy", "vote", "senate"],
            "Technology": ["tech", "software", "hardware", "computer", "internet"],
            "Entertainment": ["movie", "music", "concert", "television", "festival"]
        }
        category_scores = {}
        for topic, keywords in topics.items():
            score = sum(len(re.findall(r'\b' + kw + r'\b', text)) for kw in keywords)
            category_scores[topic] = score
        best_topic = max(category_scores, key=category_scores.get)
        if category_scores[best_topic] == 0:
            best_topic = "Uncategorized"
        return best_topic
