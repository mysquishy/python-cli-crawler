#!/usr/bin/env python3
"""
Plugin Reloader

Watches the plugin_config.json file for changes and dynamically reloads plugin configurations.
Requires: watchdog

Usage:
  Run this script alongside your crawler to enable runtime configuration updates.
"""
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Assuming plugin_manager.py defines a reload_config() function
from plugin_manager import reload_config

class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Check if the modified file is plugin_config.json
        if os.path.basename(event.src_path) == "plugin_config.json":
            print("Plugin configuration changed, reloading configuration...")
            reload_config()  # This function should reload configuration for all plugins

def main():
    config_path = os.path.abspath("plugin_config.json")
    watch_dir = os.path.dirname(config_path)
    
    event_handler = ConfigChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.start()
    
    print(f"Watching {config_path} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
