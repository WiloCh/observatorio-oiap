import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_ENV_PATH = BASE_DIR / ".env"
ENV_DIR = BASE_DIR / "env"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(ROOT_ENV_PATH)
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
load_env_file(ENV_DIR / f"{APP_ENV}.env")

APP_NAME = os.getenv("APP_NAME", "Observatorio OIAP")
DATABASE_URL = os.getenv("OIAP_DATABASE_URL", "")

EVENT_TABLE = os.getenv("OIAP_EVENT_TABLE", "observatorio_eventos")
USER_TABLE = os.getenv("OIAP_USER_TABLE", "usuarios")
DECISION_TABLE = os.getenv("OIAP_DECISION_TABLE", "decisiones")
AUDIT_LOG_TABLE = os.getenv("OIAP_AUDIT_LOG_TABLE", "audit_log")
USER_SESSION_TABLE = os.getenv("OIAP_USER_SESSION_TABLE", "sesiones_usuario")
SCHEMA_MIGRATIONS_TABLE = os.getenv("OIAP_SCHEMA_MIGRATIONS_TABLE", "schema_migrations")
