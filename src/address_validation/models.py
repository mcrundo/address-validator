"""Domain models for address validation."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AddressInput:
    """Inbound address to validate."""

    lines: list[str]
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""

    def to_google_request(self) -> dict[str, Any]:
        """Build the Google Maps Address Validation API request body."""
        address: dict[str, Any] = {"addressLines": self.lines}
        if self.country:
            address["regionCode"] = self.country
        if self.city:
            address["locality"] = self.city
        if self.state:
            address["administrativeArea"] = self.state
        if self.postal_code:
            address["postalCode"] = self.postal_code
        return {"address": address}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AddressInput":
        """Parse from the incoming request payload.

        Raises ValueError if required fields are missing or invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("address must be an object")

        lines = data.get("lines")
        if not lines or not isinstance(lines, list):
            raise ValueError("address.lines must be a non-empty array of strings")

        non_empty_lines = [line for line in lines if isinstance(line, str) and line.strip()]
        if not non_empty_lines:
            raise ValueError("address.lines must contain at least one non-empty string")

        return cls(
            lines=non_empty_lines,
            city=str(data.get("city", "")),
            state=str(data.get("state", "")),
            postal_code=str(data.get("postal_code", "")),
            country=str(data.get("country", "")),
        )


@dataclass(frozen=True, slots=True)
class RequestOptions:
    """Optional parameters forwarded to the Google Maps Address Validation API."""

    enable_usps_cass: bool = False
    previous_response_id: str = ""
    session_token: str = ""

    def to_google_params(self) -> dict[str, Any]:
        """Build the Google-level request fields (merged alongside ``address``)."""
        params: dict[str, Any] = {}
        if self.enable_usps_cass:
            params["enableUspsCass"] = True
        if self.previous_response_id:
            params["previousResponseId"] = self.previous_response_id
        if self.session_token:
            params["sessionToken"] = self.session_token
        return params

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RequestOptions":
        """Parse from the incoming ``options`` payload.

        Raises ValueError for invalid types.
        """
        if not isinstance(data, dict):
            raise ValueError("options must be an object")

        enable_usps_cass = data.get("enable_usps_cass", False)
        if not isinstance(enable_usps_cass, bool):
            raise ValueError("options.enable_usps_cass must be a boolean")

        previous_response_id = data.get("previous_response_id", "")
        if not isinstance(previous_response_id, str):
            raise ValueError("options.previous_response_id must be a string")

        session_token = data.get("session_token", "")
        if not isinstance(session_token, str):
            raise ValueError("options.session_token must be a string")

        return cls(
            enable_usps_cass=enable_usps_cass,
            previous_response_id=previous_response_id,
            session_token=session_token,
        )


@dataclass(frozen=True, slots=True)
class NormalizedAddress:
    """Validated and normalized address returned to the caller."""

    line1: str
    line2: str | None
    city: str
    state: str
    postal_code: str
    country: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidationMessage:
    """A single validation message derived from an address component."""

    source: str
    code: str
    text: str
    type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidationResults:
    """Validation metadata for an address."""

    granularity: str
    messages: list[ValidationMessage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "granularity": self.granularity,
            "messages": [m.to_dict() for m in self.messages],
        }


@dataclass(frozen=True, slots=True)
class ParsedResult:
    """Intermediate result from parsing a Google Maps API response."""

    address: NormalizedAddress
    is_valid: bool
    granularity: str
    messages: list[ValidationMessage]
    formatted_address: str


@dataclass(frozen=True, slots=True)
class ValidationResponse:
    """Top-level response envelope returned to the caller."""

    is_valid: bool
    address: NormalizedAddress
    validation_results: ValidationResults
    formatted_address: str
    original_address: dict[str, Any]
    original_response: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "address": self.address.to_dict(),
            "validation_results": self.validation_results.to_dict(),
            "formatted_address": self.formatted_address,
            "original_address": self.original_address,
            "original_response": self.original_response,
        }
