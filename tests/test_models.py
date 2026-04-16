"""Tests for address validation models."""

import pytest

from address_validation.models import (
    AddressInput,
    NormalizedAddress,
    RequestOptions,
    ValidationMessage,
    ValidationResponse,
    ValidationResults,
)


class TestAddressInput:
    def test_from_dict_valid(self) -> None:
        data = {
            "lines": ["1600 Amphitheatre Parkway"],
            "city": "Mountain View",
            "state": "CA",
            "postal_code": "94043",
            "country": "US",
        }
        address = AddressInput.from_dict(data)
        assert address.lines == ["1600 Amphitheatre Parkway"]
        assert address.city == "Mountain View"
        assert address.state == "CA"
        assert address.postal_code == "94043"
        assert address.country == "US"

    def test_from_dict_lines_only(self) -> None:
        address = AddressInput.from_dict({"lines": ["123 Main St"]})
        assert address.lines == ["123 Main St"]
        assert address.city == ""
        assert address.country == ""

    def test_from_dict_strips_empty_lines(self) -> None:
        address = AddressInput.from_dict({"lines": ["123 Main St", "", "  "]})
        assert address.lines == ["123 Main St"]

    def test_from_dict_missing_lines(self) -> None:
        with pytest.raises(ValueError, match=r"address\.lines must be a non-empty array"):
            AddressInput.from_dict({"city": "Test"})

    def test_from_dict_empty_lines(self) -> None:
        with pytest.raises(ValueError, match=r"address\.lines must be a non-empty array"):
            AddressInput.from_dict({"lines": []})

    def test_from_dict_all_blank_lines(self) -> None:
        with pytest.raises(ValueError, match="at least one non-empty string"):
            AddressInput.from_dict({"lines": ["", "  "]})

    def test_from_dict_lines_not_a_list(self) -> None:
        with pytest.raises(ValueError, match=r"address\.lines must be a non-empty array"):
            AddressInput.from_dict({"lines": "not a list"})

    def test_from_dict_not_a_dict(self) -> None:
        with pytest.raises(ValueError, match="address must be an object"):
            AddressInput.from_dict("not a dict")  # type: ignore[arg-type]

    def test_to_google_request_full(self) -> None:
        address = AddressInput(
            lines=["1600 Amphitheatre Parkway"],
            city="Mountain View",
            state="CA",
            postal_code="94043",
            country="US",
        )
        request = address.to_google_request()
        assert request == {
            "address": {
                "addressLines": ["1600 Amphitheatre Parkway"],
                "regionCode": "US",
                "locality": "Mountain View",
                "administrativeArea": "CA",
                "postalCode": "94043",
            },
        }

    def test_to_google_request_minimal(self) -> None:
        address = AddressInput(lines=["123 Main St"])
        request = address.to_google_request()
        assert request == {
            "address": {
                "addressLines": ["123 Main St"],
            },
        }


class TestRequestOptions:
    def test_from_dict_defaults(self) -> None:
        options = RequestOptions.from_dict({})
        assert options.enable_usps_cass is False
        assert options.previous_response_id == ""
        assert options.session_token == ""

    def test_from_dict_all_fields(self) -> None:
        options = RequestOptions.from_dict(
            {
                "enable_usps_cass": True,
                "previous_response_id": "resp-123",
                "session_token": "token-abc",
            }
        )
        assert options.enable_usps_cass is True
        assert options.previous_response_id == "resp-123"
        assert options.session_token == "token-abc"

    def test_from_dict_not_a_dict(self) -> None:
        with pytest.raises(ValueError, match="options must be an object"):
            RequestOptions.from_dict("bad")  # type: ignore[arg-type]

    def test_from_dict_invalid_enable_usps_cass_type(self) -> None:
        with pytest.raises(ValueError, match="enable_usps_cass must be a boolean"):
            RequestOptions.from_dict({"enable_usps_cass": "yes"})

    def test_from_dict_invalid_previous_response_id_type(self) -> None:
        with pytest.raises(ValueError, match="previous_response_id must be a string"):
            RequestOptions.from_dict({"previous_response_id": 123})

    def test_from_dict_invalid_session_token_type(self) -> None:
        with pytest.raises(ValueError, match="session_token must be a string"):
            RequestOptions.from_dict({"session_token": True})

    def test_from_dict_ignores_unknown_fields(self) -> None:
        options = RequestOptions.from_dict({"enable_usps_cass": True, "unknown_field": "ignored"})
        assert options.enable_usps_cass is True

    def test_to_google_params_empty(self) -> None:
        options = RequestOptions()
        assert options.to_google_params() == {}

    def test_to_google_params_all_set(self) -> None:
        options = RequestOptions(
            enable_usps_cass=True,
            previous_response_id="resp-123",
            session_token="token-abc",
        )
        assert options.to_google_params() == {
            "enableUspsCass": True,
            "previousResponseId": "resp-123",
            "sessionToken": "token-abc",
        }

    def test_to_google_params_partial(self) -> None:
        options = RequestOptions(enable_usps_cass=True)
        params = options.to_google_params()
        assert params == {"enableUspsCass": True}
        assert "previousResponseId" not in params
        assert "sessionToken" not in params


class TestNormalizedAddress:
    def test_to_dict(self) -> None:
        address = NormalizedAddress(
            line1="1600 Amphitheatre Pkwy",
            line2=None,
            city="Mountain View",
            state="CA",
            postal_code="94043-1351",
            country="US",
        )
        assert address.to_dict() == {
            "line1": "1600 Amphitheatre Pkwy",
            "line2": None,
            "city": "Mountain View",
            "state": "CA",
            "postal_code": "94043-1351",
            "country": "US",
        }

    def test_to_dict_with_line2(self) -> None:
        address = NormalizedAddress(
            line1="350 5th Ave",
            line2="Ste 3301",
            city="New York",
            state="NY",
            postal_code="10118",
            country="US",
        )
        result = address.to_dict()
        assert result["line2"] == "Ste 3301"

    def test_frozen(self) -> None:
        address = NormalizedAddress(
            line1="x", line2=None, city="x", state="x", postal_code="x", country="x"
        )
        with pytest.raises(AttributeError):
            address.line1 = "y"  # type: ignore[misc]


class TestValidationMessage:
    def test_to_dict(self) -> None:
        msg = ValidationMessage(
            source="google_maps",
            code="street_number.confirmed",
            text="Street number confirmed",
            type="info",
        )
        assert msg.to_dict() == {
            "source": "google_maps",
            "code": "street_number.confirmed",
            "text": "Street number confirmed",
            "type": "info",
        }


class TestValidationResults:
    def test_to_dict(self) -> None:
        msg = ValidationMessage(
            source="google_maps",
            code="route.confirmed",
            text="Route confirmed",
            type="info",
        )
        results = ValidationResults(granularity="premise", messages=[msg])
        assert results.to_dict() == {
            "granularity": "premise",
            "messages": [
                {
                    "source": "google_maps",
                    "code": "route.confirmed",
                    "text": "Route confirmed",
                    "type": "info",
                },
            ],
        }

    def test_to_dict_empty_messages(self) -> None:
        results = ValidationResults(granularity="unknown")
        assert results.to_dict() == {
            "granularity": "unknown",
            "messages": [],
        }


class TestValidationResponse:
    def test_to_dict(self) -> None:
        address = NormalizedAddress(
            line1="1600 Amphitheatre Pkwy",
            line2=None,
            city="Mountain View",
            state="CA",
            postal_code="94043-1351",
            country="US",
        )
        msg = ValidationMessage(
            source="google_maps",
            code="street_number.confirmed",
            text="Street number confirmed",
            type="info",
        )
        original_address = {
            "lines": ["1600 Amphitheatre Parkway"],
            "city": "Mountain View",
            "state": "CA",
            "postal_code": "94043",
            "country": "US",
        }
        original_response = {"result": {"verdict": {"addressComplete": True}}}
        response = ValidationResponse(
            is_valid=True,
            address=address,
            validation_results=ValidationResults(granularity="premise", messages=[msg]),
            formatted_address="1600 Amphitheatre Pkwy, Mountain View, CA 94043-1351, USA",
            original_address=original_address,
            original_response=original_response,
        )
        result = response.to_dict()
        assert result["is_valid"] is True
        assert result["address"]["line1"] == "1600 Amphitheatre Pkwy"
        assert result["validation_results"]["granularity"] == "premise"
        assert len(result["validation_results"]["messages"]) == 1
        assert (
            result["formatted_address"]
            == "1600 Amphitheatre Pkwy, Mountain View, CA 94043-1351, USA"
        )
        assert result["original_address"]["lines"] == ["1600 Amphitheatre Parkway"]
        assert result["original_response"] == original_response
