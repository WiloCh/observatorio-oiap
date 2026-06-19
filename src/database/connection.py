from contextlib import contextmanager
from typing import Iterator

from src.config import DATABASE_URL


def get_placeholder() -> str:
    return "%s"


def placeholders(count: int) -> str:
    return ", ".join([get_placeholder()] * count)


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("OIAP_DATABASE_URL es obligatorio para conectar con PostgreSQL.")
    try:
        import psycopg
    except ImportError as error:
        raise RuntimeError(
            "Falta instalar psycopg. Ejecuta: pip install 'psycopg[binary]'"
        ) from error
    return psycopg.connect(DATABASE_URL)


@contextmanager
def transaction() -> Iterator:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
