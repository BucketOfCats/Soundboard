from soundboard import Soundboard
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "assets")
sounds_path = os.path.join(assets_path, "sounds")
config_path = os.path.join(assets_path, "config.json")

# Load config
with open(config_path, "r") as f:
    config = json.load(f)

# Access config fields
combo_keys = config.get("combo_keys", [])
echo_keys = config.get("echo_keys", [])
sounds = config.get("sounds", [])

# Create soundboard
soundboard = Soundboard(combo_keys, echo_keys)

# Register every sound from config
for sound_data in sounds:
    key_combo = sound_data.get("key_combo", [])
    volume = sound_data.get("volume", 1)
    path = sound_data.get("path", "")

    if os.path.isabs(path):
        file_path = path
    else:
        file_path = os.path.join(sounds_path, path)

    soundboard.register_sound(key_combo, file_path, volume)

soundboard.start()
