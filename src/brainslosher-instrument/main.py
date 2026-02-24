import argparse
import subprocess
import sys
from pathlib import Path
import urllib.request
import zipfile
import json
import logging

UI_REPO = "AllenNeuralDynamics/brainslosher-web-ui"
FILE_NAME = "ui.zip"
UI_DIR = Path("ui")
VERSION_FILE = Path("ui/.version")

def get_latest_release_asset_url():
    url = f"https://api.github.com/repos/{UI_REPO}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as response:
        release = json.loads(response.read())
    
    for asset in release["assets"]:
        if asset["name"] == FILE_NAME:
            return asset["browser_download_url"], release["tag_name"]

def fetch_ui():
    latest_url, latest_tag = get_latest_release_asset_url()
    
    if VERSION_FILE.exists() and VERSION_FILE.read_text() == latest_tag:
        print(f"UI is up to date ({latest_tag})")
        return
    
    print(f"Downloading UI {latest_tag}...")
    urllib.request.urlretrieve(latest_url, FILE_NAME)
    
    with zipfile.ZipFile(FILE_NAME) as z:
        z.extractall(UI_DIR)
    
    VERSION_FILE.write_text(latest_tag)
    Path(FILE_NAME).unlink()
    print("UI ready")
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instrument-config", required=True)
    parser.add_argument("--ui-config", required=True)
    parser.add_argument("--log-level", default="INFO", choices=["INFO", "DEBUG"])
    
    args = parser.parse_args()
    logger = logging.getLogger()

    # Override console log level if specified.
    for handler in logger.handlers:
        if handler.get_name() == 'console':
            handler.setLevel(args.log_level)

    fetch_ui()

    instrument = subprocess.Popen([
        "uv", "run",
        "--group", "brainslosher_group",
        "brainslosher",
        "--config", args.instrument_config,
        "--log_level", args.log_level.lower()
    ], cwd="src/brainslosher-instrument")

    frontend = subprocess.Popen([
        "uv", "run", "src/main.py",
        "--config", args.ui_config,
        "--log_level", args.log_level,
        "--static_files", str(UI_DIR)
    ], cwd="src/brainslosher-web-ui")

    try:
        instrument.wait()
        frontend.wait()
    except KeyboardInterrupt:
        instrument.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()