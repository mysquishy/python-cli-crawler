#!/usr/bin/env python3
"""
SentimentEnhancedSummarizer plugin for the crawler.

This plugin first generates a summary of the textual content of an HTML page using a Hugging Face transformers pipeline and then analyzes the sentiment of the summary using TextBlob.
It returns both the summary and sentiment scores.

Configuration parameters:
  - model_name: Hugging Face model identifier for summarization (default: "sshleifer/distilbart-cnn-12-6")
  - max_length: Maximum length of the summary (default: 130)
  - min_length: Minimum length of the summary (default: 30)
  - do_sample: Boolean flag to enable sampling (default: False)

Requires: transformers, textblob
"""
from plugins import PluginBase
from transformers import pipeline
from textblob import TextBlob
from bs4 import BeautifulSoup

class SentimentEnhancedSummarizer(PluginBase):
    def __init__(self):
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        self.max_length = 130
        self.min_length = 30
        self.do_sample = False
        self.summarizer = pipeline("summarization", model=self.model_name)

    def configure(self, settings):
        self.model_name = settings.get("model_name", self.model_name)
        self.max_length = settings.get("max_length", self.max_length)
        self.min_length = settings.get("min_length", self.min_length)
        self.do_sample = settings.get("do_sample", self.do_sample)
        self.summarizer = pipeline("summarization", model=self.model_name)

    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return "No text found to summarize."
        summary = self.summarizer(text, max_length=self.max_length, min_length=self.min_length, do_sample=self.do_sample)
        if summary and isinstance(summary, list) and "summary_text" in summary[0]:
            summary_text = summary[0]["summary_text"]
            blob = TextBlob(summary_text)
            sentiment = blob.sentiment  # contains polarity and subjectivity
            return {
                "summary": summary_text,
                "sentiment": {
                    "polarity": sentiment.polarity,
                    "subjectivity": sentiment.subjectivity
                }
            }
        else:
            return "Summary could not be generated."
