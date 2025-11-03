from __future__ import annotations

import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from core.config import settings


class KeyValueFormatter(logging.Formatter):
    """Formatter that outputs logs as single-line JSON for easier parsing."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - inherited docstring
        base = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                continue
            base[key] = value

        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)

        return json.dumps(base, ensure_ascii=False)


def _configure_logging() -> logging.Logger:
    if logging.getLogger("chatbot_ai").handlers:
        return logging.getLogger("chatbot_ai")

    os.makedirs("logs", exist_ok=True)
    log_path = Path("logs") / "chatbot-ai.log"

    file_handler = TimedRotatingFileHandler(
        filename=str(log_path),
        when="midnight",
        encoding="utf-8",
        backupCount=7,
    )
    stream_handler = logging.StreamHandler()

    formatter = KeyValueFormatter()
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger_instance = logging.getLogger("chatbot_ai")
    logger_instance.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logger_instance.addHandler(file_handler)
    logger_instance.addHandler(stream_handler)
    logger_instance.propagate = False

    return logger_instance


logger = _configure_logging()
