"""
Grafana Loki logging handler for centralized log aggregation.
"""
import json
import logging
import time
import traceback
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings


class LokiHandlerWrapper(logging.Handler):
    """
    A logging handler that sends logs directly to Grafana Loki using HTTP requests.

    This handler sends logs to Grafana Loki only if LOKI_ENABLED is True
    in settings. It includes metadata like environment and application name
    as stream labels.

    Uses stdlib urllib instead of requests library to avoid extra dependencies.
    """

    def __init__(self, level: int = logging.INFO) -> None:
        super().__init__(level)
        self._enabled: bool = settings.LOKI_ENABLED
        self._headers: Optional[dict[str, str]] = None

        if self._enabled:
            self._setup_headers()

    def _setup_headers(self) -> None:
        """Set up HTTP headers for Loki requests."""
        try:
            self._headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.LOKI_BEARER_TOKEN}",
            }
        except Exception as e:
            # Setup failure must not crash the app — disable Loki gracefully
            print(f"Warning: Failed to setup Loki headers: {e}", flush=True)
            self._enabled = False

    def _get_stream_labels(self, record: logging.LogRecord) -> dict[str, str]:
        """Get stream labels for the log record."""
        environment = 'production' if not settings.DEBUG else 'development'

        labels: dict[str, str] = {
            'application': settings.LOKI_APPLICATION_NAME,
            'environment': environment,
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'has_exception': 'false',
        }

        if record.exc_info:
            labels['has_exception'] = 'true'
            exc_type = record.exc_info[0]
            if exc_type:
                labels['exception_type'] = exc_type.__name__

        return labels

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Loki."""
        if not self._enabled or self._headers is None:
            return

        try:
            log_message = record.message if record.message else self.format(record)

            if record.exc_info:
                if not record.exc_text:
                    record.exc_text = ''.join(traceback.format_exception(*record.exc_info))
                log_message = f"{log_message}\n\n{record.exc_text}"

            stream_labels = self._get_stream_labels(record)
            timestamp_ns = str(int(time.time() * 1000000000))

            payload = {
                "streams": [
                    {
                        "stream": stream_labels,
                        "values": [[timestamp_ns, log_message]],
                    }
                ]
            }

            data = json.dumps(payload).encode('utf-8')
            req = Request(
                url=settings.LOKI_URL,
                data=data,
                headers=self._headers,
                method='POST',
            )

            with urlopen(req, timeout=5) as response:
                if response.status >= 400:
                    print(f"Loki returned error {response.status}", flush=True)

        except URLError as e:
            # Network errors — don't crash the app
            print(f"Failed to send log to Loki (network error): {e}", flush=True)
        except Exception as e:
            # Other errors — don't crash the app
            print(f"Failed to send log to Loki: {e}", flush=True)
            self.handleError(record)


def is_loki_enabled() -> bool:
    """Check if Loki logging is enabled."""
    return settings.LOKI_ENABLED
