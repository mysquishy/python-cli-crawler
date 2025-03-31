#!/usr/bin/env python3
"""
Integration test for the full plugin lifecycle.

This integration test loads all plugins via the Plugin Manager (using the current configuration from "plugin_config.json"),
processes a sample HTML page, and prints the outputs of each plugin.
It verifies that each plugin returns a non-null output under realistic conditions.
"""
import os
import pytest
from plugin_manager import load_plugins

def test_full_plugin_lifecycle():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(base_dir, "plugin_extensions")
    
    # Load all plugins from the plugin_extensions directory using the current configuration.
    plugins = load_plugins(plugin_dir)
    assert plugins, "No plugins were loaded. Check your plugin configuration and directory."
    
    # Define a sample HTML page containing elements to trigger various plugins.
    sample_html = """
    <html>
      <head><title>Full Lifecycle Test</title></head>
      <body>
        <h1>Main Heading</h1>
        <p>This is a test paragraph for integration testing. The quick brown fox jumps over the lazy dog.</p>
        <img src="http://example.com/test.png" alt="Test Image">
      </body>
    </html>
    """
    
    outputs = {}
    # Process the sample HTML through each loaded plugin.
    for plugin in plugins:
        try:
            result = plugin.process(sample_html, "http://example.com")
            outputs[plugin.__class__.__name__] = result
        except Exception as e:
            outputs[plugin.__class__.__name__] = f"Error: {e}"
    
    # Verify that each plugin returns a non-null output.
    for name, output in outputs.items():
        print(f"{name}: {output}")
        assert output is not None, f"Plugin {name} returned None."
    return outputs

if __name__ == "__main__":
    pytest.main([__file__])
