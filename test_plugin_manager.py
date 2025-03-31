#!/usr/bin/env python3
"""
Unit tests for the Plugin Manager.

This test creates a temporary plugin directory with a dummy plugin and a temporary
plugin configuration that enables the DummyPlugin. It then verifies that the Plugin
Manager successfully loads the DummyPlugin.
"""

import os
import tempfile
import json
import pytest
from plugin_manager import load_plugins

def test_load_plugins_with_dummy_plugin():
    # Create a temporary directory to serve as the plugin directory.
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = os.path.join(tmpdir, "plugin_extensions")
        os.makedirs(plugin_dir, exist_ok=True)

        # Create a dummy plugin file.
        dummy_plugin_code = '''
from plugins import PluginBase
class DummyPlugin(PluginBase):
    def process(self, html, url):
        return "dummy_output"
'''
        dummy_plugin_path = os.path.join(plugin_dir, "dummy_plugin.py")
        with open(dummy_plugin_path, "w") as f:
            f.write(dummy_plugin_code)

        # Override the configuration loader to simulate a config that enables DummyPlugin.
        import plugin_manager
        plugin_manager.load_config = lambda config_path: {"DummyPlugin"}

        # Load plugins from the temporary plugin directory.
        plugins = load_plugins(plugin_dir)
        plugin_names = [plugin.__class__.__name__ for plugin in plugins]
        # Verify that DummyPlugin has been loaded.
        assert "DummyPlugin" in plugin_names

if __name__ == "__main__":
    pytest.main([__file__])
