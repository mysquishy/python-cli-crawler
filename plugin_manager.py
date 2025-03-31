#!/usr/bin/env python3
"""
Plugin Manager for dynamic discovery of crawler plugins.

Plugins should be placed in the "plugin_extensions" directory under this project.
Each plugin must implement a subclass of PluginBase (defined in plugins.py).
This manager also reads "plugin_config.json" to determine which plugins are enabled
and to pass per-plugin configuration to plugins that implement a "configure" method.
"""

import importlib.util
import os
import sys
import json
from plugins import PluginBase

def load_config(config_path):
    """
    Load the plugin configuration from a JSON file and return a dict mapping plugin names
    to their settings. Only plugins with "enabled": true are returned.
    """
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                plugin_configs = {}
                for plugin_cfg in config.get("plugins", []):
                    if plugin_cfg.get("enabled", False):
                        # Store configuration settings for the plugin, default to empty dict if missing.
                        plugin_configs[plugin_cfg["name"]] = plugin_cfg.get("settings", {})
                return plugin_configs
        except Exception as e:
            print(f"Error loading config file: {e}")
    return {}

def load_plugins(plugin_dir):
    plugins = []
    # Determine the path to the configuration file (assumed to be in the project root)
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugin_config.json")
    plugin_configs = load_config(config_path)
    if not os.path.isdir(plugin_dir):
        print(f"Plugin directory {plugin_dir} does not exist.")
        return plugins
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            filepath = os.path.join(plugin_dir, filename)
            module_name = os.path.splitext(filename)[0]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    print(f"Error loading module {module_name}: {e}")
                    continue
                # Iterate through module attributes to find plugin classes.
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                        # Check if the plugin is enabled via configuration.
                        if not plugin_configs or obj.__name__ in plugin_configs:
                            try:
                                plugin_instance = obj()
                                # If the plugin has a "configure" method, pass its settings.
                                if hasattr(plugin_instance, "configure"):
                                    settings = plugin_configs.get(obj.__name__, {})
                                    plugin_instance.configure(settings)
                                plugins.append(plugin_instance)
                            except Exception as e:
                                print(f"Error instantiating plugin {obj.__name__}: {e}")
            else:
                print(f"Could not load module from {filepath}")
    return plugins

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(base_dir, "plugin_extensions")
    loaded_plugins = load_plugins(plugin_dir)
    print("Loaded plugins:")
    for plugin in loaded_plugins:
        print(f"- {plugin.__class__.__name__}")
