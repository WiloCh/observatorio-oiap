import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("OIAP_DATA_DIR", BASE_DIR / "data"))
DB_PATH = Path(os.getenv("OIAP_DB_PATH", DATA_DIR / "observatorio_oiap.db"))

