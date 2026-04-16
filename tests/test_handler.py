"""Integration tests for the address validation Lambda handler."""

import json

import httpx
import pytest
import respx

from address_validation.client import GOOGLE_API_URL
from address_validation.handler import handler
from tests.fixtures.google_responses import (
    VALID_RESPONSE_SINGLE_LINE,
    VALID_RESPONSE_TWO_LINES,
    VALID_RESPONSE_UNCONFIRMED_COMPONENT,
)


def _make_event(body: dict | str | None = None) -> dict:
    """Build a minimal API Gateway v2 proxy event."""
    raw_body = json.dumps(body) if isinstance(body, dict) else body
    return {
        "body": raw_body or "",
        "isBase64Encoded": False,
    }


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")


class TestHandlerSuccess:
    @respx.mock
    def test_valid_address_single_line(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["1600 Amphitheatre Parkway"]}}), None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["address"]["line1"] == "1600 Amphitheatre Pkwy"
        assert body["address"]["line2"] is None
        assert body["address"]["city"] == "Mountain View"
        assert body["address"]["state"] == "CA"
        assert body["address"]["postal_code"] == "94043-1351"
        assert body["address"]["country"] == "US"

    @respx.mock
    def test_valid_address_two_lines(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_TWO_LINES)
        )

        result = handler(
            _make_event(
                {
                    "address": {
                        "lines": ["350 5th Ave", "Ste 3301"],
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10118",
                        "country": "US",
                    }
                }
            ),
            None,
        )

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["address"]["line1"] == "350 5th Ave"
        assert body["address"]["line2"] == "Ste 3301"

    @respx.mock
    def test_response_has_json_content_type(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        assert result["headers"]["Content-Type"] == "application/json"


class TestHandlerResponseEnvelope:
    @respx.mock
    def test_is_valid_true(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["1600 Amphitheatre Parkway"]}}), None)

        body = json.loads(result["body"])
        assert body["is_valid"] is True

    @respx.mock
    def test_is_valid_false(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_UNCONFIRMED_COMPONENT)
        )

        result = handler(_make_event({"address": {"lines": ["9999 Amphitheatre Parkway"]}}), None)

        body = json.loads(result["body"])
        assert body["is_valid"] is False

    @respx.mock
    def test_formatted_address(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["1600 Amphitheatre Parkway"]}}), None)

        body = json.loads(result["body"])
        assert (
            body["formatted_address"]
            == "1600 Amphitheatre Pkwy, Mountain View, CA 94043-1351, USA"
        )

    @respx.mock
    def test_validation_results_present(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["1600 Amphitheatre Parkway"]}}), None)

        body = json.loads(result["body"])
        assert "validation_results" in body
        assert body["validation_results"]["granularity"] == "premise"
        assert isinstance(body["validation_results"]["messages"], list)
        assert len(body["validation_results"]["messages"]) > 0

    @respx.mock
    def test_original_address_echoed(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        input_address = {
            "lines": ["1600 Amphitheatre Parkway"],
            "city": "Mountain View",
            "state": "CA",
            "postal_code": "94043",
            "country": "US",
        }
        result = handler(_make_event({"address": input_address}), None)

        body = json.loads(result["body"])
        assert body["original_address"] == input_address

    @respx.mock
    def test_original_response_included(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["1600 Amphitheatre Parkway"]}}), None)

        body = json.loads(result["body"])
        assert body["original_response"] == VALID_RESPONSE_SINGLE_LINE

    @respx.mock
    def test_all_top_level_keys_present(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        body = json.loads(result["body"])
        assert set(body.keys()) == {
            "is_valid",
            "address",
            "validation_results",
            "formatted_address",
            "original_address",
            "original_response",
        }


class TestHandlerOptions:
    @respx.mock
    def test_options_passed_to_google(self) -> None:
        route = respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(
            _make_event(
                {
                    "address": {"lines": ["123 Main St"]},
                    "options": {"enable_usps_cass": True},
                }
            ),
            None,
        )

        assert result["statusCode"] == 200
        body = json.loads(route.calls.last.request.content)
        assert body["enableUspsCass"] is True

    @respx.mock
    def test_no_options_still_works(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = handler(
            _make_event({"address": {"lines": ["123 Main St"]}}),
            None,
        )

        assert result["statusCode"] == 200

    def test_invalid_options_type(self) -> None:
        result = handler(
            _make_event(
                {
                    "address": {"lines": ["123 Main St"]},
                    "options": "bad",
                }
            ),
            None,
        )

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "options must be an object" in body["error"]

    def test_invalid_option_value_type(self) -> None:
        result = handler(
            _make_event(
                {
                    "address": {"lines": ["123 Main St"]},
                    "options": {"enable_usps_cass": "yes"},
                }
            ),
            None,
        )

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "enable_usps_cass" in body["error"]


class TestHandlerInputValidation:
    def test_empty_body(self) -> None:
        result = handler({"body": "", "isBase64Encoded": False}, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "empty" in body["error"].lower()

    def test_invalid_json(self) -> None:
        result = handler({"body": "not json", "isBase64Encoded": False}, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "not valid JSON" in body["error"]

    def test_missing_address_field(self) -> None:
        result = handler(_make_event({"not_address": {}}), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "address" in body["error"].lower()

    def test_missing_lines(self) -> None:
        result = handler(_make_event({"address": {"city": "Test"}}), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "lines" in body["error"].lower()

    def test_empty_lines_array(self) -> None:
        result = handler(_make_event({"address": {"lines": []}}), None)

        assert result["statusCode"] == 400

    def test_all_blank_lines(self) -> None:
        result = handler(_make_event({"address": {"lines": ["", "  "]}}), None)

        assert result["statusCode"] == 400

    def test_body_is_json_array(self) -> None:
        result = handler({"body": "[1,2,3]", "isBase64Encoded": False}, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "JSON object" in body["error"]

    def test_base64_encoded_body(self) -> None:
        import base64

        raw = json.dumps({"address": {"lines": ["123 Main St"]}})
        encoded = base64.b64encode(raw.encode()).decode()

        with respx.mock:
            respx.post(GOOGLE_API_URL).mock(
                return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
            )
            result = handler({"body": encoded, "isBase64Encoded": True}, None)

        assert result["statusCode"] == 200


class TestHandlerErrorHandling:
    def test_missing_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GOOGLE_MAPS_API_KEY")

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "GOOGLE_MAPS_API_KEY" in body["error"]

    @respx.mock
    def test_upstream_timeout(self) -> None:
        respx.post(GOOGLE_API_URL).mock(side_effect=httpx.ReadTimeout("timed out"))

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        assert result["statusCode"] == 502
        body = json.loads(result["body"])
        assert "timed out" in body["error"].lower()

    @respx.mock
    def test_upstream_403(self) -> None:
        respx.post(GOOGLE_API_URL).mock(return_value=httpx.Response(403, text="Forbidden"))

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        assert result["statusCode"] == 502
        body = json.loads(result["body"])
        assert "403" in body["error"]

    @respx.mock
    def test_upstream_connection_error(self) -> None:
        respx.post(GOOGLE_API_URL).mock(side_effect=httpx.ConnectError("connection refused"))

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        assert result["statusCode"] == 502

    @respx.mock
    def test_upstream_malformed_response(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json={"responseId": "bad"})
        )

        result = handler(_make_event({"address": {"lines": ["123 Main St"]}}), None)

        assert result["statusCode"] == 502
        body = json.loads(result["body"])
        assert "Unexpected response" in body["error"]
