"""Tests for the health check handler."""

import json

from address_validation.health import handler


class TestHealth:
    def test_returns_200(self) -> None:
        result = handler({}, None)
        assert result["statusCode"] == 200

    def test_returns_ok_status(self) -> None:
        result = handler({}, None)
        body = json.loads(result["body"])
        assert body["status"] == "ok"

    def test_content_type_json(self) -> None:
        result = handler({}, None)
        assert result["headers"]["Content-Type"] == "application/json"
