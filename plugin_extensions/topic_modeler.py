#!/usr/bin/env python3
"""
TopicModeler plugin for the crawler.

Uses gensim's LDA model to extract topics from the text content of a webpage.
Configuration parameters (nested):
  - topic_modeling:
      num_topics: integer (default: 3)
      passes: integer (default: 10)
Requires: gensim, beautifulsoup4, nltk

Note: Ensure you have downloaded the necessary NLTK data:
    python -m nltk.downloader punkt
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
from gensim import corpora, models
from gensim.utils import simple_preprocess
import nltk

class TopicModeler(PluginBase):
    def __init__(self):
        self.num_topics = 3
        self.passes = 10

    def configure(self, settings):
        topic_config = settings.get("topic_modeling", {})
        self.num_topics = topic_config.get("num_topics", self.num_topics)
        self.passes = topic_config.get("passes", self.passes)

    def process(self, html, url):
        nltk.download("punkt", quiet=True)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return "No text found for topic modeling."
        # Tokenize text into a list of words (tokens)
        tokens = simple_preprocess(text)
        if not tokens:
            return "No valid tokens extracted from text."
        # Create a dictionary and corpus for LDA
        dictionary = corpora.Dictionary([tokens])
        corpus = [dictionary.doc2bow(tokens)]
        # Build the LDA model using gensim
        lda_model = models.LdaModel(
            corpus,
            num_topics=self.num_topics,
            id2word=dictionary,
            passes=self.passes,
            random_state=42
        )
        topics = lda_model.print_topics(num_words=5)
        return topics
