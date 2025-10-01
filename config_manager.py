# config_manager.py

import json

CONFIG_FILE = 'config.json'

def load_config():
    """Loads configuration from the JSON file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default settings if file doesn't exist
        return {
            'target_process_name': 'dota2.exe',
            'play_region_coords': [534, 243, 2028, 1251], # x, y, width, height
            'auto_solve_enabled': False
        }

def save_config(config_data):
    """Saves the current configuration to the JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)