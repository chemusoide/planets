from pathlib import Path

from app.database import get_connection


class SQLiteSyncRepository:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def get_status(self) -> dict[str, str | int | bool | None]:
        with get_connection(self._database_path) as connection:
            row = connection.execute(
                """
                SELECT source_name, source_url, last_attempted_at, last_success_at,
                       last_status, last_message, records_processed, using_cached_data
                FROM sync_status
                WHERE id = 1
                """
            ).fetchone()

        if row is None:
            return {
                "source_name": "Fuente externa no configurada",
                "source_url": "",
                "last_attempted_at": None,
                "last_success_at": None,
                "last_status": "never",
                "last_message": "Sin estado de sincronización.",
                "records_processed": 0,
                "using_cached_data": True,
            }

        return {
            "source_name": row["source_name"],
            "source_url": row["source_url"],
            "last_attempted_at": row["last_attempted_at"],
            "last_success_at": row["last_success_at"],
            "last_status": row["last_status"],
            "last_message": row["last_message"],
            "records_processed": row["records_processed"],
            "using_cached_data": bool(row["using_cached_data"]),
        }

    def update_status(
        self,
        *,
        source_name: str,
        source_url: str,
        last_attempted_at: str,
        last_success_at: str | None,
        last_status: str,
        last_message: str,
        records_processed: int,
        using_cached_data: bool,
    ) -> None:
        with get_connection(self._database_path) as connection:
            connection.execute(
                """
                INSERT INTO sync_status (
                    id, source_name, source_url, last_attempted_at, last_success_at,
                    last_status, last_message, records_processed, using_cached_data
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_name = excluded.source_name,
                    source_url = excluded.source_url,
                    last_attempted_at = excluded.last_attempted_at,
                    last_success_at = excluded.last_success_at,
                    last_status = excluded.last_status,
                    last_message = excluded.last_message,
                    records_processed = excluded.records_processed,
                    using_cached_data = excluded.using_cached_data
                """,
                (
                    source_name,
                    source_url,
                    last_attempted_at,
                    last_success_at,
                    last_status,
                    last_message,
                    records_processed,
                    1 if using_cached_data else 0,
                ),
            )