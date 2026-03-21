"""Parse Google Maps Address Validation API responses into normalized addresses."""

from typing import Any

from address_validation.exceptions import UpstreamError
from address_validation.models import NormalizedAddress


def parse_response(data: dict[str, Any]) -> NormalizedAddress:
    """Extract a NormalizedAddress from a Google Maps Address Validation API response.

    The response structure we care about:
        {
            "result": {
                "address": {
                    "postalAddress": {
                        "regionCode": "US",
                        "postalCode": "94043-1351",
                        "administrativeArea": "CA",
                        "locality": "Mountain View",
                        "addressLines": [
                            "1600 Amphitheatre Pkwy"
                        ]
                    }
                }
            }
        }

    addressLines may have 1 or 2 entries (line1, line2).
    """
    try:
        postal_address = data["result"]["address"]["postalAddress"]
    except (KeyError, TypeError) as exc:
        raise UpstreamError("Unexpected response structure from Google Maps API") from exc

    address_lines: list[str] = postal_address.get("addressLines", [])

    if not address_lines:
        raise UpstreamError("Google Maps API returned no address lines")

    return NormalizedAddress(
        line1=address_lines[0],
        line2=address_lines[1] if len(address_lines) > 1 else None,
        city=postal_address.get("locality", ""),
        state=postal_address.get("administrativeArea", ""),
        postal_code=postal_address.get("postalCode", ""),
        country=postal_address.get("regionCode", ""),
    )
