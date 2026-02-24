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
DIST_PATH = Path(__file__).resolve().parents[2] / "ui" / "dist"
VERSION_FILE = Path("ui/.version")

def get_ui_submodule_tag() -> str:
    result = subprocess.run(
        ["git", "describe", "--tags"],
        cwd="src/brainslosher-web-ui",
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def get_release_asset_url(tag: str):
    url = f"https://api.github.com/repos/{UI_REPO}/releases/tags/{tag}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as response:
        release = json.loads(response.read())
    
    for asset in release["assets"]:
        if asset["name"] == FILE_NAME:
            return asset["browser_download_url"]

def fetch_ui():
    tag = get_ui_submodule_tag()
    
    if VERSION_FILE.exists() and VERSION_FILE.read_text() == tag:
        logging.debug(f"UI is up to date ({tag})")
        return
    
    logging.debug(f"Downloading UI {tag}...")
    url = get_release_asset_url(tag)
    urllib.request.urlretrieve(url, FILE_NAME)
    
    with zipfile.ZipFile(FILE_NAME) as z:
        z.extractall(UI_DIR)
    
    VERSION_FILE.write_text(tag)
    Path(FILE_NAME).unlink()
    logging.debug("UI ready")
    

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
        "--log-level", args.log_level
    ], cwd="src/brainwasher")

    frontend = subprocess.Popen([
        "uv", "run", "src/main.py",
        "--config", args.ui_config,
        "--log-level", args.log_level,
        "--static-files", str(DIST_PATH)
    ], cwd="src/brainslosher-web-ui/backend")



    try:
        instrument.wait()
        frontend.wait()
    except KeyboardInterrupt:
        instrument.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()