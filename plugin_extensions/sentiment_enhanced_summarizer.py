#!/usr/bin/env python3
"""
SentimentEnhancedSummarizer plugin for the crawler.

This plugin enhances summarization by incorporating sentiment analysis.
It extracts text from HTML content, creates a simple summary by selecting the first N sentences,
and computes sentiment polarity and subjectivity using TextBlob.
Configuration parameters (nested):
  - summarization:
      num_sentences: integer (default: 3)
  - sentiment:
      method: string (default: "textblob")
Requires: textblob, beautifulsoup4, nltk

Note: Ensure you have downloaded the necessary NLTK data:
    python -m nltk.downloader punkt
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk

class SentimentEnhancedSummarizer(PluginBase):
    def __init__(self):
        # Default configuration settings
        self.num_sentences = 3
        self.sentiment_method = "textblob"  # can extend to other methods

    def configure(self, settings):
        summarization_config = settings.get("summarization", {})
        self.num_sentences = summarization_config.get("num_sentences", 3)
        sentiment_config = settings.get("sentiment", {})
        self.sentiment_method = sentiment_config.get("method", "textblob")

    def process(self, html, url):
        # Ensure necessary NLTK data is available
        nltk.download("punkt", quiet=True)

        # Extract text from HTML content
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return "No text content found."

        # Use TextBlob to split text into sentences
        blob = TextBlob(text)
        sentences = blob.sentences
        if not sentences:
            return "No sentences could be extracted from text."

        # Create a simple summary by selecting the first N sentences
        summary_sentences = sentences[:self.num_sentences]
        summary = " ".join(str(sentence) for sentence in summary_sentences)

        # Analyze sentiment using TextBlob
        summary_blob = TextBlob(summary)
        sentiment = summary_blob.sentiment  # returns (polarity, subjectivity)

        result = {
            "summary": summary,
            "sentiment": {
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity
            }
        }
        return result
