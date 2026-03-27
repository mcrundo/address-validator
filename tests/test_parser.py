"""Tests for Google Maps API response parser."""

import pytest

from address_validation.exceptions import UpstreamError
from address_validation.parser import parse_response
from tests.fixtures.google_responses import (
    RESPONSE_EMPTY_ADDRESS_LINES,
    RESPONSE_MISSING_POSTAL_ADDRESS,
    RESPONSE_MISSING_RESULT,
    VALID_RESPONSE_SINGLE_LINE,
    VALID_RESPONSE_SUSPICIOUS_COMPONENT,
    VALID_RESPONSE_TWO_LINES,
    VALID_RESPONSE_UNCONFIRMED_COMPONENT,
)


class TestParseResponseAddress:
    """Tests for address extraction (existing behavior)."""

    def test_single_address_line(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert result.address.line1 == "1600 Amphitheatre Pkwy"
        assert result.address.line2 is None
        assert result.address.city == "Mountain View"
        assert result.address.state == "CA"
        assert result.address.postal_code == "94043-1351"
        assert result.address.country == "US"

    def test_two_address_lines(self) -> None:
        result = parse_response(VALID_RESPONSE_TWO_LINES)
        assert result.address.line1 == "350 5th Ave"
        assert result.address.line2 == "Ste 3301"
        assert result.address.city == "New York"
        assert result.address.state == "NY"
        assert result.address.postal_code == "10118"
        assert result.address.country == "US"

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


class TestParseResponseVerdict:
    """Tests for is_valid and granularity extraction."""

    def test_is_valid_true_when_address_complete(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert result.is_valid is True

    def test_is_valid_false_when_address_incomplete(self) -> None:
        result = parse_response(VALID_RESPONSE_UNCONFIRMED_COMPONENT)
        assert result.is_valid is False

    def test_granularity_extracted_and_lowercased(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert result.granularity == "premise"

    def test_granularity_route_level(self) -> None:
        result = parse_response(VALID_RESPONSE_UNCONFIRMED_COMPONENT)
        assert result.granularity == "route"

    def test_two_lines_is_valid_true(self) -> None:
        result = parse_response(VALID_RESPONSE_TWO_LINES)
        assert result.is_valid is True

    def test_two_lines_granularity_sub_premise(self) -> None:
        result = parse_response(VALID_RESPONSE_TWO_LINES)
        assert result.granularity == "sub_premise"

    def test_missing_verdict_defaults(self) -> None:
        """When verdict is absent, is_valid defaults to False and granularity to 'unknown'."""
        data = {
            "result": {
                "address": {
                    "postalAddress": {
                        "regionCode": "US",
                        "addressLines": ["123 Main St"],
                    },
                },
            },
        }
        result = parse_response(data)
        assert result.is_valid is False
        assert result.granularity == "unknown"


class TestParseResponseFormattedAddress:
    def test_formatted_address_extracted(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert (
            result.formatted_address == "1600 Amphitheatre Pkwy, Mountain View, CA 94043-1351, USA"
        )

    def test_two_lines_formatted_address(self) -> None:
        result = parse_response(VALID_RESPONSE_TWO_LINES)
        assert result.formatted_address == "350 5th Ave, Ste 3301, New York, NY 10118, USA"

    def test_missing_formatted_address_defaults_empty(self) -> None:
        data = {
            "result": {
                "address": {
                    "postalAddress": {
                        "regionCode": "US",
                        "addressLines": ["123 Main St"],
                    },
                },
            },
        }
        result = parse_response(data)
        assert result.formatted_address == ""


class TestParseResponseMessages:
    """Tests for validation messages from addressComponents."""

    def test_confirmed_components_produce_info_messages(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert len(result.messages) == 6
        assert all(m.type == "info" for m in result.messages)
        assert all(m.source == "google_maps" for m in result.messages)

    def test_confirmed_message_code_format(self) -> None:
        result = parse_response(VALID_RESPONSE_SINGLE_LINE)
        assert result.messages[0].code == "street_number.confirmed"
        assert result.messages[0].text == "Street number confirmed"

    def test_unconfirmed_component_produces_warning(self) -> None:
        result = parse_response(VALID_RESPONSE_UNCONFIRMED_COMPONENT)
        warning_messages = [m for m in result.messages if m.type == "warning"]
        assert len(warning_messages) == 1
        assert warning_messages[0].code == "street_number.unconfirmed_but_plausible"
        assert warning_messages[0].text == "Street number unconfirmed but plausible"

    def test_suspicious_component_produces_error(self) -> None:
        result = parse_response(VALID_RESPONSE_SUSPICIOUS_COMPONENT)
        error_messages = [m for m in result.messages if m.type == "error"]
        assert len(error_messages) == 1
        assert error_messages[0].code == "route.unconfirmed_and_suspicious"
        assert error_messages[0].text == "Route unconfirmed and suspicious"

    def test_missing_components_empty_messages(self) -> None:
        result = parse_response(VALID_RESPONSE_TWO_LINES)
        assert result.messages == []
