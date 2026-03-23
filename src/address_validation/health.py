"""Health check handler — returns 200 OK without external calls."""

import json
from typing import Any


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Health check endpoint for uptime monitoring."""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok"}),
    }
