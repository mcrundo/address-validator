"""Tests for Google Maps API response parser."""

import pytest

from address_validation.exceptions import UpstreamError
from address_validation.parser import parse_response
from tests.fixtures.google_responses import (
    RESPONSE_EMPTY_ADDRESS_LINES,
    RESPONSE_MISSING_POSTAL_ADDRESS,
    RESPONSE_MISSING_RESULT,
    VALID_RESPONSE_SINGLE_LINE,
    VALID_RESPONSE_TWO_LINES,
)


class TestParseResponse:
    def test_single_address_line(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert result.line1 == "1600 Amphitheatre Pkwy"
        assert result.line2 is None
        assert result.city == "Mountain View"
        assert result.state == "CA"
        assert result.postal_code == "94043-1351"
        assert result.country == "US"

    def test_two_address_lines(self) -> None:
        result = parse_response(VALID_RESPONSE_TWO_LINES)
        assert result.line1 == "350 5th Ave"
        assert result.line2 == "Ste 3301"
        assert result.city == "New York"
        assert result.state == "NY"
        assert result.postal_code == "10118"
        assert result.country == "US"

    def test_missing_result_key(self) -> None:
        with pytest.raises(UpstreamError, match="Unexpected response structure"):
            parse_response(RESPONSE_MISSING_RESULT)

    def test_missing_postal_address(self) -> None:
        with pytest.raises(UpstreamError, match="Unexpected response structure"):
            parse_response(RESPONSE_MISSING_POSTAL_ADDRESS)

    def test_empty_address_lines(self) -> None:
        with pytest.raises(UpstreamError, match="no address lines"):
            parse_response(RESPONSE_EMPTY_ADDRESS_LINES)

    def test_completely_empty_response(self) -> None:
        with pytest.raises(UpstreamError):
            parse_response({})

    def test_none_result(self) -> None:
        with pytest.raises(UpstreamError):
            parse_response({"result": None})
