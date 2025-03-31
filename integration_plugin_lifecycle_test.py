#!/usr/bin/env python3
"""
Integration test for the complete plugin lifecycle.

This test simulates:
 - Creating a temporary plugin directory with dummy plugins.
 - Setting up a temporary plugin configuration (plugin_config.json) that enables these plugins with specific settings.
 - Loading the plugins using the Plugin Manager.
 - Processing a sample HTML page through each loaded plugin.
 - Verifying that each plugin returns the expected output and that per‐plugin configuration is applied.

Run this test using pytest.
"""
import os
import tempfile
import json
import pytest
from plugin_manager import load_plugins

def test_plugin_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a temporary plugin directory
        plugin_dir = os.path.join(tmpdir, "plugin_extensions")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create two dummy plugin files
        dummy_plugin_1 = """
from plugins import PluginBase
class DummyPluginOne(PluginBase):
    def __init__(self):
        self.setting = "default"
    def configure(self, settings):
        self.setting = settings.get("setting", "default")
    def process(self, html, url):
        return f"OutputOne with setting {self.setting}"
"""
        dummy_plugin_2 = """
from plugins import PluginBase
class DummyPluginTwo(PluginBase):
    def process(self, html, url):
        return "OutputTwo"
"""
        with open(os.path.join(plugin_dir, "dummy_one.py"), "w") as f:
            f.write(dummy_plugin_1)
        with open(os.path.join(plugin_dir, "dummy_two.py"), "w") as f:
            f.write(dummy_plugin_2)
        
        # Create a temporary plugin configuration file
        config = {
            "plugins": [
                {"name": "DummyPluginOne", "enabled": True, "settings": {"setting": "custom_value"}},
                {"name": "DummyPluginTwo", "enabled": True}
            ]
        }
        config_path = os.path.join(tmpdir, "plugin_config.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        # Override the load_config function in the plugin_manager to use our temporary config
        import plugin_manager
        def temp_load_config(x):
            # Return a dict mapping plugin name to settings
            return {p["name"]: p.get("settings", {}) for p in config["plugins"] if p.get("enabled", False)}
        plugin_manager.load_config = temp_load_config
        
        # Load plugins from the temporary plugin directory
        plugins = load_plugins(plugin_dir)
        outputs = []
        for plugin in plugins:
            output = plugin.process("<html><body>Test content</body></html>", "http://example.com")
            outputs.append(output)
        
        # Assert that DummyPluginOne was configured with "custom_value"
        assert any("custom_value" in str(o) for o in outputs), "DummyPluginOne did not use custom configuration."
        # Assert that DummyPluginTwo processed correctly
        assert any(o == "OutputTwo" for o in outputs), "DummyPluginTwo did not process correctly."

if __name__ == "__main__":
    pytest.main([__file__])
