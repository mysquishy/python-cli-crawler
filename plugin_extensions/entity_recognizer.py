#!/usr/bin/env python3
"""
EntityRecognizer plugin for the crawler.

Extracts named entities from the textual content of an HTML page using spaCy.
Returns a list of entities along with their labels.
Requires: spacy (and the "en_core_web_sm" model should be installed)
Usage:
  python -m spacy download en_core_web_sm
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
import spacy

class EntityRecognizer(PluginBase):
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            raise Exception("SpaCy model 'en_core_web_sm' not found. Please install it with 'python -m spacy download en_core_web_sm'") from e

    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        if not text:
            return "No text found to analyze."
        doc = self.nlp(text)
        # Extract entities with their labels.
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        return entities
