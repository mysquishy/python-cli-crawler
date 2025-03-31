#!/usr/bin/env python3
"""
TopicModeler plugin for the crawler.

Uses gensim's LDA for topic modeling from the text content of an HTML page.
Configuration parameters:
  - num_topics: number of topics to extract (default: 3)

Requires: gensim, nltk
Make sure to download NLTK stopwords (e.g., via: python -m nltk.downloader stopwords)
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
import re
from gensim import corpora, models
import nltk

class TopicModeler(PluginBase):
    def __init__(self):
        self.num_topics = 3

    def configure(self, settings):
        self.num_topics = settings.get("num_topics", 3)

    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").lower()
        # Basic tokenization: extract alphabetic words.
        tokens = re.findall(r'\b[a-z]+\b', text)
        # Download and use nltk stopwords.
        nltk.download("stopwords", quiet=True)
        stopwords = set(nltk.corpus.stopwords.words("english"))
        tokens = [token for token in tokens if token not in stopwords]
        if not tokens:
            return "No text found for topic modeling."
        # Create a dictionary and corpus for LDA.
        dictionary = corpora.Dictionary([tokens])
        corpus = [dictionary.doc2bow(tokens)]
        lda_model = models.LdaModel(corpus, num_topics=self.num_topics, id2word=dictionary, passes=5)
        topics = lda_model.print_topics(num_words=5)
        return topics
