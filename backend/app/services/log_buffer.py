from collections import deque
from logging import Handler, LogRecord


_RECENT_LOGS: deque[str] = deque(maxlen=200)


class InMemoryLogHandler(Handler):
    def emit(self, record: LogRecord) -> None:
        message = self.format(record)
        _RECENT_LOGS.append(message)


def get_recent_logs(limit: int = 50) -> list[str]:
    if limit <= 0:
        return []
    return list(_RECENT_LOGS)[-limit:]
