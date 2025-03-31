#!/usr/bin/env python3
"""
ConfigurablePlugin plugin for the crawler.

This plugin demonstrates per‐plugin configuration.
It implements a configuration method and returns its configuration settings as output.
"""
from plugins import PluginBase

class ConfigurablePlugin(PluginBase):
    def __init__(self):
        self.config = {}

    def configure(self, settings):
        """Configure the plugin with provided settings."""
        self.config = settings

    def process(self, html, url):
        """Return the plugin's configuration as its output for demonstration."""
        return f"Configured with: {self.config}"
