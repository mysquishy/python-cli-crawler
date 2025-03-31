#!/usr/bin/env python3
"""
SentimentAnalyzer plugin for the crawler.

Analyzes the sentiment of the text content extracted from HTML using TextBlob.
Outputs the polarity and subjectivity scores.
Requires: pip install textblob
"""
from plugins import PluginBase
from textblob import TextBlob
from bs4 import BeautifulSoup

class SentimentAnalyzer(PluginBase):
    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return {"polarity": 0.0, "subjectivity": 0.0}
        blob = TextBlob(text)
        sentiment = blob.sentiment
        return {"polarity": sentiment.polarity, "subjectivity": sentiment.subjectivity}
