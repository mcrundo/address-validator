"""Tests for the Google Maps Address Validation API client."""

import httpx
import pytest
import respx

from address_validation.client import GOOGLE_API_URL, validate_address
from address_validation.exceptions import UpstreamError
from address_validation.models import AddressInput
from tests.fixtures.google_responses import (
    VALID_RESPONSE_SINGLE_LINE,
)

TEST_API_KEY = "test-api-key-123"
SAMPLE_ADDRESS = AddressInput(lines=["1600 Amphitheatre Parkway"], country="US")


class TestValidateAddress:
    @respx.mock
    def test_successful_request(self) -> None:
        route = respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        result = validate_address(SAMPLE_ADDRESS, api_key=TEST_API_KEY)

        assert result == VALID_RESPONSE_SINGLE_LINE
        assert route.called
        request = route.calls.last.request
        assert f"key={TEST_API_KEY}" in str(request.url)

    @respx.mock
    def test_sends_correct_request_body(self) -> None:
        import json

        route = respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(200, json=VALID_RESPONSE_SINGLE_LINE)
        )

        validate_address(SAMPLE_ADDRESS, api_key=TEST_API_KEY)

        body = json.loads(route.calls.last.request.content)
        assert body == {
            "address": {
                "addressLines": ["1600 Amphitheatre Parkway"],
                "regionCode": "US",
            },
        }

    @respx.mock
    def test_non_200_response(self) -> None:
        respx.post(GOOGLE_API_URL).mock(return_value=httpx.Response(403, text="Forbidden"))

        with pytest.raises(UpstreamError, match="returned 403"):
            validate_address(SAMPLE_ADDRESS, api_key=TEST_API_KEY)

    @respx.mock
    def test_500_response(self) -> None:
        respx.post(GOOGLE_API_URL).mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        with pytest.raises(UpstreamError, match="returned 500"):
            validate_address(SAMPLE_ADDRESS, api_key=TEST_API_KEY)

    @respx.mock
    def test_timeout(self) -> None:
        respx.post(GOOGLE_API_URL).mock(side_effect=httpx.ReadTimeout("timed out"))

        with pytest.raises(UpstreamError, match="timed out"):
            validate_address(SAMPLE_ADDRESS, api_key=TEST_API_KEY)

    @respx.mock
    def test_connection_error(self) -> None:
        respx.post(GOOGLE_API_URL).mock(side_effect=httpx.ConnectError("connection refused"))

        with pytest.raises(UpstreamError, match="request failed"):
            validate_address(SAMPLE_ADDRESS, api_key=TEST_API_KEY)
