"""Google Maps Address Validation API client."""

import httpx

from address_validation.exceptions import UpstreamError
from address_validation.models import AddressInput, RequestOptions

GOOGLE_API_URL = "https://addressvalidation.googleapis.com/v1:validateAddress"
DEFAULT_TIMEOUT = 10.0


def validate_address(
    address: AddressInput,
    *,
    api_key: str,
    options: RequestOptions | None = None,
) -> dict[str, object]:
    """Call the Google Maps Address Validation API.

    Returns the raw JSON response body on success.
    Raises UpstreamError on any failure.
    """
    body = address.to_google_request()
    if options:
        body.update(options.to_google_params())

    try:
        response = httpx.post(
            GOOGLE_API_URL,
            params={"key": api_key},
            json=body,
            timeout=DEFAULT_TIMEOUT,
        )
    except httpx.TimeoutException as exc:
        raise UpstreamError("Google Maps API request timed out") from exc
    except httpx.RequestError as exc:
        raise UpstreamError(f"Google Maps API request failed: {exc}") from exc

    if response.status_code != 200:
        raise UpstreamError(f"Google Maps API returned {response.status_code}: {response.text}")

    data: dict[str, object] = response.json()
    return data
