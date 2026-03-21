"""Tests for address validation models."""

import pytest

from address_validation.models import AddressInput, NormalizedAddress


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
        assert address.country == "US"

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
                "regionCode": "US",
            },
        }


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
