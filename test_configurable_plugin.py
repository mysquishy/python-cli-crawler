#!/usr/bin/env python3
"""
Unit test for the ConfigurablePlugin.

This test verifies that the plugin's configuration is correctly applied through its configure method,
and that the process method returns the expected output reflecting the configuration.
"""
import pytest
from plugin_extensions.configurable_plugin import ConfigurablePlugin

def test_configurable_plugin_configuration():
    plugin = ConfigurablePlugin()
    config_settings = {"option": "value", "threshold": 10}
    plugin.configure(config_settings)
    output = plugin.process("<html></html>", "http://example.com")
    expected_output = f"Configured with: {config_settings}"
    assert output == expected_output, f"Expected '{expected_output}' but got '{output}'"

if __name__ == "__main__":
    pytest.main([__file__])
