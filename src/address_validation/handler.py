"""AWS Lambda handler for address validation."""

import json
import logging
import os
from typing import Any

from address_validation.client import validate_address
from address_validation.exceptions import AddressValidationError, InvalidInputError
from address_validation.models import AddressInput
from address_validation.parser import parse_response

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda entry point.

    Expects an API Gateway v2 (HTTP API) proxy event with a JSON body.
    """
    try:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            raise AddressValidationError("GOOGLE_MAPS_API_KEY is not configured", status_code=500)

        body = _parse_body(event)
        address_data = body.get("address")
        if address_data is None:
            raise InvalidInputError("Missing required field: address")

        address_input = AddressInput.from_dict(address_data)
        google_response = validate_address(address_input, api_key=api_key)
        normalized = parse_response(google_response)

        return _response(200, normalized.to_dict())

    except AddressValidationError as exc:
        logger.warning("Validation error: %s", exc)
        return _response(exc.status_code, {"error": str(exc)})
    except Exception:
        logger.exception("Unhandled exception")
        return _response(500, {"error": "Internal server error"})


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    """Extract and parse the JSON body from an API Gateway v2 event."""
    raw_body = event.get("body", "")
    if not raw_body:
        raise InvalidInputError("Request body is empty")

    if event.get("isBase64Encoded"):
        import base64

        raw_body = base64.b64decode(raw_body).decode("utf-8")

    try:
        parsed: dict[str, Any] = json.loads(raw_body)
    except (json.JSONDecodeError, TypeError) as exc:
        raise InvalidInputError("Request body is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise InvalidInputError("Request body must be a JSON object")

    return parsed


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    """Build an API Gateway v2 proxy response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
