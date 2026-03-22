"""Lambda authorizer for API Gateway — validates x-api-key header."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Validate the x-api-key header against the expected value.

    Returns an API Gateway authorizer response with isAuthorized: true/false.
    Uses the simple response format for HTTP API (v2) Lambda authorizers.
    """
    expected_key = os.environ.get("API_KEY", "")
    if not expected_key:
        logger.error("API_KEY environment variable is not configured")
        return {"isAuthorized": False}

    headers = event.get("headers", {})
    provided_key = headers.get("x-api-key", "")

    authorized = provided_key == expected_key
    if not authorized:
        logger.warning("Unauthorized request — invalid or missing x-api-key")

    return {"isAuthorized": authorized}
