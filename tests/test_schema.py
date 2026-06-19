from src.config import AUDIT_LOG_TABLE, DECISION_TABLE, EVENT_TABLE, USER_TABLE
from src.database.connection import get_connection
from src.database.schema import create_table


def test_create_table_creates_institutional_tables():
    create_table()

    with get_connection() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            ).fetchall()
        }
        user_columns = {
            row[0]
            for row in conn.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                """,
                (USER_TABLE,),
            ).fetchall()
        }

    assert EVENT_TABLE in tables
    assert USER_TABLE in tables
    assert DECISION_TABLE in tables
    assert AUDIT_LOG_TABLE in tables
    assert "password_hash" in user_columns
