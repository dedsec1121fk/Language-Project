from pathlib import Path
import os

# Installed source code lives under $HOME/Language Project/app by default.
APP_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get('LANGUAGE_PROJECT_HOME', str(Path.home() / 'Language Project'))).expanduser().resolve()

BUILD_DIR = DATA_ROOT / 'build'
STATE_DIR = DATA_ROOT / 'state'
RESULTS_DIR = DATA_ROOT / 'results'
BUNDLES_DIR = DATA_ROOT / 'bundles'
BACKUPS_DIR = DATA_ROOT / 'backups'
REPORTS_DIR = DATA_ROOT / 'reports'
LOGS_DIR = DATA_ROOT / 'logs'
CACHE_DIR = DATA_ROOT / 'cache'
TEMP_DIR = DATA_ROOT / 'tmp'
DOWNLOADS_DIR = DATA_ROOT / 'downloads'
WORKSPACE_DIR = DATA_ROOT / 'workspace'
CHECKPOINTS_DIR = STATE_DIR / 'checkpoints'
DATABASE_FILE = STATE_DIR / 'history.sqlite3'
ACTIVE_STATE_FILE = STATE_DIR / 'active.json'
CALIBRATION_FILE = STATE_DIR / 'calibration.json'
POLYTOOLS_STATE_FILE = STATE_DIR / 'polytools.json'

RUNTIME_DIRS = (
    BUILD_DIR, STATE_DIR, RESULTS_DIR, BUNDLES_DIR, BACKUPS_DIR, REPORTS_DIR,
    LOGS_DIR, CACHE_DIR, TEMP_DIR, DOWNLOADS_DIR, WORKSPACE_DIR, CHECKPOINTS_DIR,
)

def ensure_data_tree():
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME_DIRS:
        path.mkdir(parents=True, exist_ok=True)
    return DATA_ROOT


def runtime_path(*parts):
    ensure_data_tree()
    return DATA_ROOT.joinpath(*parts)


def app_path(*parts):
    return APP_ROOT.joinpath(*parts)
