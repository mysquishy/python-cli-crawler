#!/usr/bin/env python3
"""
Plugin Reloader monitors plugin_config.json for changes and reloads plugins dynamically.

This script uses the watchdog library to observe changes in the plugin_config.json file.
When a change is detected, it reloads all plugins from the "plugin_extensions" directory and prints out the loaded plugin names.

Requirements:
  pip install watchdog

Usage:
  python plugin_reloader.py
"""
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plugin_manager import load_plugins

class PluginConfigEventHandler(FileSystemEventHandler):
    def __init__(self, plugin_dir):
        super().__init__()
        self.plugin_dir = plugin_dir

    def on_modified(self, event):
        if event.src_path.endswith("plugin_config.json"):
            print("Plugin configuration changed. Reloading plugins...")
            plugins = load_plugins(self.plugin_dir)
            print("Reloaded plugins:")
            for plugin in plugins:
                print(f" - {plugin.__class__.__name__}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(base_dir, "plugin_extensions")
    config_file = os.path.join(base_dir, "plugin_config.json")
    
    event_handler = PluginConfigEventHandler(plugin_dir)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(config_file), recursive=False)
    observer.start()
    print("Monitoring plugin_config.json for changes. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
