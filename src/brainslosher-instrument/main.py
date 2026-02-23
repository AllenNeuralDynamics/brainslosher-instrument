import argparse
import subprocess
import sys
from pathlib import Path
import urllib.request
import zipfile
import json

UI_REPO = "AllenNeuralDynamics/brainslosher-web-ui"
FILE_NAME = "ui.zip"
UI_DIR = Path("ui")

def get_latest_release_asset_url():
    url = f"https://api.github.com/repos/{UI_REPO}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as response:
        release = json.loads(response.read())
    
    for asset in release["assets"]:
        if asset["name"] == FILE_NAME:
            return asset["browser_download_url"]

def fetch_ui():
    if UI_DIR.exists():
        print("UI already present, skipping download")
        return
    
    print("Downloading latest UI release...")
    url = get_latest_release_asset_url()
    urllib.request.urlretrieve(url, FILE_NAME)
    
    with zipfile.ZipFile(FILE_NAME) as z:
        z.extractall(UI_DIR)
    
    Path(FILE_NAME).unlink()
    print("UI ready")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instrument-config", required=True)
    parser.add_argument("--ui-config", required=True)
    parser.add_argument("--log-level", default="INFO", choices=["INFO", "DEBUG"])
    args = parser.parse_args()

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