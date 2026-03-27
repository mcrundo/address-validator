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
    country: str = "US"

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
            country=str(data.get("country", "US")),
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
