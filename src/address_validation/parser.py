"""Parse Google Maps Address Validation API responses."""

from typing import Any

from address_validation.exceptions import UpstreamError
from address_validation.models import NormalizedAddress, ParsedResult, ValidationMessage

_CONFIRMATION_TYPE_MAP: dict[str, str] = {
    "CONFIRMED": "info",
    "UNCONFIRMED_BUT_PLAUSIBLE": "warning",
    "UNCONFIRMED_AND_SUSPICIOUS": "error",
}

_CONFIRMATION_LABEL_MAP: dict[str, str] = {
    "CONFIRMED": "confirmed",
    "UNCONFIRMED_BUT_PLAUSIBLE": "unconfirmed but plausible",
    "UNCONFIRMED_AND_SUSPICIOUS": "unconfirmed and suspicious",
}

_COMPONENT_TYPE_LABELS: dict[str, str] = {
    "street_number": "Street number",
    "route": "Route",
    "locality": "Locality",
    "administrative_area_level_1": "State",
    "postal_code": "Postal code",
    "country": "Country",
    "subpremise": "Unit",
    "premise": "Premise",
}


def parse_response(data: dict[str, Any]) -> ParsedResult:
    """Extract a ParsedResult from a Google Maps Address Validation API response.

    The required structure for address extraction:
        data["result"]["address"]["postalAddress"]

    Optional structures extracted when present:
        data["result"]["verdict"]           -> is_valid, granularity
        data["result"]["address"]["formattedAddress"]   -> formatted_address
        data["result"]["address"]["addressComponents"]  -> messages
    """
    try:
        postal_address = data["result"]["address"]["postalAddress"]
    except (KeyError, TypeError) as exc:
        raise UpstreamError("Unexpected response structure from Google Maps API") from exc

    address_lines: list[str] = postal_address.get("addressLines", [])

    if not address_lines:
        raise UpstreamError("Google Maps API returned no address lines")

    address = NormalizedAddress(
        line1=address_lines[0],
        line2=address_lines[1] if len(address_lines) > 1 else None,
        city=postal_address.get("locality", ""),
        state=postal_address.get("administrativeArea", ""),
        postal_code=postal_address.get("postalCode", ""),
        country=postal_address.get("regionCode", ""),
    )

    result = data.get("result", {})
    verdict = result.get("verdict", {})
    address_data = result.get("address", {})

    is_valid = verdict.get("addressComplete", False)
    granularity = verdict.get("validationGranularity", "unknown").lower()
    formatted_address = address_data.get("formattedAddress", "")
    components = address_data.get("addressComponents", [])
    messages = _build_messages(components)

    return ParsedResult(
        address=address,
        is_valid=is_valid,
        granularity=granularity,
        messages=messages,
        formatted_address=formatted_address,
    )


def _build_messages(components: list[dict[str, Any]]) -> list[ValidationMessage]:
    """Build validation messages from Google's addressComponents."""
    messages: list[ValidationMessage] = []
    for component in components:
        component_type = component.get("componentType", "unknown")
        confirmation_level = component.get("confirmationLevel", "CONFIRMED")

        code = f"{component_type}.{confirmation_level.lower()}"
        label = _COMPONENT_TYPE_LABELS.get(
            component_type, component_type.replace("_", " ").title()
        )
        confirmation_label = _CONFIRMATION_LABEL_MAP.get(
            confirmation_level, confirmation_level.lower()
        )
        text = f"{label} {confirmation_label}"
        msg_type = _CONFIRMATION_TYPE_MAP.get(confirmation_level, "info")

        messages.append(
            ValidationMessage(source="google_maps", code=code, text=text, type=msg_type)
        )
    return messages
