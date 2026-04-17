"""Lambda authorizer for API Gateway — validates x-api-key header."""

import logging
import os
from typing import Any

from address_validation.secrets import get_secret

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Validate the x-api-key header against the expected value.

    Returns an API Gateway authorizer response with isAuthorized: true/false.
    Uses the simple response format for HTTP API (v2) Lambda authorizers.
    """
    secret_name = os.environ.get("API_KEY_SECRET_NAME", "")
    if not secret_name:
        logger.error("API_KEY_SECRET_NAME environment variable is not configured")
        return {"isAuthorized": False}

    try:
        expected_key = get_secret(secret_name)
    except Exception:
        logger.exception("Failed to fetch API key from Secrets Manager")
        return {"isAuthorized": False}

    headers = event.get("headers", {})
    provided_key = headers.get("x-api-key", "")

    authorized = provided_key == expected_key
    if not authorized:
        logger.warning("Unauthorized request — invalid or missing x-api-key")

    return {"isAuthorized": authorized}
