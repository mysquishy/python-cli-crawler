#!/usr/bin/env python3
"""
AdvancedContentSummarizer plugin for the crawler.

Uses the Hugging Face transformers pipeline to produce a summary from the text content.
Configuration parameters:
  - model_name: Hugging Face model identifier (default: "sshleifer/distilbart-cnn-12-6")
  - max_length: Maximum length of the summary (default: 130)
  - min_length: Minimum length of the summary (default: 30)
  - do_sample: Boolean flag to enable sampling (default: False)

If the text is large, it may be truncated automatically by the summarization pipeline.
"""
from plugins import PluginBase
from transformers import pipeline
from bs4 import BeautifulSoup

class AdvancedContentSummarizer(PluginBase):
    def __init__(self):
        # Default configuration parameters
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        self.max_length = 130
        self.min_length = 30
        self.do_sample = False
        self.summarizer = pipeline("summarization", model=self.model_name)

    def configure(self, settings):
        """Configure plugin settings via the plugin configuration file."""
        self.model_name = settings.get("model_name", self.model_name)
        self.max_length = settings.get("max_length", self.max_length)
        self.min_length = settings.get("min_length", self.min_length)
        self.do_sample = settings.get("do_sample", self.do_sample)
        # Reinitialize the summarization pipeline with the updated model.
        self.summarizer = pipeline("summarization", model=self.model_name)

    def process(self, html, url):
        """
        Process the HTML content to extract text and generate a summary using the transformers pipeline.
        """
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return "No text found to summarize."
        # Run the summarizer on the text.
        summary = self.summarizer(text, max_length=self.max_length, min_length=self.min_length, do_sample=self.do_sample)
        if summary and isinstance(summary, list) and "summary_text" in summary[0]:
            return summary[0]["summary_text"]
        else:
            return "Summary could not be generated."
