"""Custom exceptions for address validation."""


class AddressValidationError(Exception):
    """Base exception for address validation failures."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.status_code = status_code


class InvalidInputError(AddressValidationError):
    """Raised when the request payload is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class UpstreamError(AddressValidationError):
    """Raised when the Google Maps API returns an error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=502)
