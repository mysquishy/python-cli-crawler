import os
import importlib.util
import json
from plugins import PluginBase

def load_config(config_path="plugin_config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config.get("plugins", {})

def load_plugins(plugin_dir, config_path="plugin_config.json"):
    plugins = []
    config = load_config(config_path)
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(plugin_dir, filename)
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, PluginBase) and attribute != PluginBase:
                    instance = attribute()
                    plugin_name = attribute.__name__
                    if plugin_name in config:
                        settings = config[plugin_name].get("settings", {})
                        instance.configure(settings)
                    plugins.append(instance)
    return plugins

# Global variable to hold the currently loaded plugins
_loaded_plugins = []

def load_all_plugins(plugin_dir, config_path="plugin_config.json"):
    global _loaded_plugins
    _loaded_plugins = load_plugins(plugin_dir, config_path)
    return _loaded_plugins

def reload_config(config_path="plugin_config.json"):
    """
    Reloads plugin configuration from the config file and reconfigures all loaded plugins.
    """
    config = load_config(config_path)
    global _loaded_plugins
    for plugin in _loaded_plugins:
        plugin_name = plugin.__class__.__name__
        if plugin_name in config:
            new_settings = config[plugin_name].get("settings", {})
            if hasattr(plugin, "configure"):
                plugin.configure(new_settings)
                print(f"Reloaded configuration for {plugin_name}")
    print("All plugin configurations reloaded.")
