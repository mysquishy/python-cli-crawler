#!/usr/bin/env python3
"""
AdvancedContentSummarizer plugin for the crawler.

Uses HuggingFace transformers pipeline for summarization.
Configuration parameters (nested):
  - summarization:
      model_name: string (default: "sshleifer/distilbart-cnn-12-6")
      max_length: integer (default: 150)
      min_length: integer (default: 40)
      do_sample: boolean (default: false)
Requires: transformers, beautifulsoup4, nltk

Note: You may need to download the NLTK data for sentence tokenization:
    python -m nltk.downloader punkt
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
from transformers import pipeline
import nltk

class AdvancedContentSummarizer(PluginBase):
    def __init__(self):
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        self.max_length = 150
        self.min_length = 40
        self.do_sample = False
        self.summarizer = pipeline("summarization", model=self.model_name)

    def configure(self, settings):
        summarization_config = settings.get("summarization", {})
        self.model_name = summarization_config.get("model_name", self.model_name)
        self.max_length = summarization_config.get("max_length", self.max_length)
        self.min_length = summarization_config.get("min_length", self.min_length)
        self.do_sample = summarization_config.get("do_sample", self.do_sample)
        # Reload the summarization pipeline with updated configuration
        self.summarizer = pipeline("summarization", model=self.model_name)

    def process(self, html, url):
        nltk.download("punkt", quiet=True)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return "No text found for summarization."
        summary = self.summarizer(
            text,
            max_length=self.max_length,
            min_length=self.min_length,
            do_sample=self.do_sample
        )
        if summary and isinstance(summary, list) and "summary_text" in summary[0]:
            return summary[0]["summary_text"]
        return "Failed to generate summary."
