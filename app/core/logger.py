import logging
import sys
import structlog
from app.core.event_bus import event_bus
from app.core.events import create_event, SystemEvent


class AppLogger:
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)

    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
        self._emit_event(message, "INFO")

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
        self._emit_event(message, "WARNING")

    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
        self._emit_event(message, "ERROR")

    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)
        self._emit_event(message, "CRITICAL")

    def _emit_event(self, message: str, severity: str, **kwargs):
        formatted = f"{message} | {kwargs}" if kwargs else message
        event_bus.emit(create_event(SystemEvent, message=formatted, severity=severity))


def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )


def get_logger(name: str) -> AppLogger:
    return AppLogger(name)
