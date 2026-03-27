"""Realistic Google Maps Address Validation API response fixtures."""

from typing import Any

VALID_RESPONSE_SINGLE_LINE: dict[str, Any] = {
    "result": {
        "verdict": {
            "inputGranularity": "PREMISE",
            "validationGranularity": "PREMISE",
            "geocodeGranularity": "PREMISE",
            "addressComplete": True,
        },
        "address": {
            "formattedAddress": "1600 Amphitheatre Pkwy, Mountain View, CA 94043-1351, USA",
            "postalAddress": {
                "revision": 0,
                "regionCode": "US",
                "languageCode": "en",
                "postalCode": "94043-1351",
                "administrativeArea": "CA",
                "locality": "Mountain View",
                "addressLines": ["1600 Amphitheatre Pkwy"],
            },
            "addressComponents": [
                {
                    "componentName": {"text": "1600", "languageCode": "en"},
                    "componentType": "street_number",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "Amphitheatre Pkwy", "languageCode": "en"},
                    "componentType": "route",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "Mountain View", "languageCode": "en"},
                    "componentType": "locality",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "CA", "languageCode": "en"},
                    "componentType": "administrative_area_level_1",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "94043-1351", "languageCode": "en"},
                    "componentType": "postal_code",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "US", "languageCode": "en"},
                    "componentType": "country",
                    "confirmationLevel": "CONFIRMED",
                },
            ],
        },
        "geocode": {
            "location": {"latitude": 37.4220656, "longitude": -122.0862784},
            "plusCode": {"globalCode": "849VCWC8+W5"},
        },
    },
    "responseId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
}

VALID_RESPONSE_TWO_LINES: dict[str, Any] = {
    "result": {
        "verdict": {
            "inputGranularity": "SUB_PREMISE",
            "validationGranularity": "SUB_PREMISE",
            "geocodeGranularity": "PREMISE",
            "addressComplete": True,
        },
        "address": {
            "formattedAddress": "350 5th Ave, Ste 3301, New York, NY 10118, USA",
            "postalAddress": {
                "revision": 0,
                "regionCode": "US",
                "languageCode": "en",
                "postalCode": "10118",
                "administrativeArea": "NY",
                "locality": "New York",
                "addressLines": ["350 5th Ave", "Ste 3301"],
            },
        },
    },
    "responseId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
}

RESPONSE_MISSING_POSTAL_ADDRESS: dict[str, Any] = {
    "result": {
        "address": {
            "formattedAddress": "Unknown",
        },
    },
}

RESPONSE_EMPTY_ADDRESS_LINES: dict[str, Any] = {
    "result": {
        "address": {
            "postalAddress": {
                "regionCode": "US",
                "addressLines": [],
            },
        },
    },
}

RESPONSE_MISSING_RESULT: dict[str, Any] = {
    "responseId": "no-result",
}

VALID_RESPONSE_UNCONFIRMED_COMPONENT: dict[str, Any] = {
    "result": {
        "verdict": {
            "inputGranularity": "PREMISE",
            "validationGranularity": "ROUTE",
            "geocodeGranularity": "ROUTE",
            "addressComplete": False,
        },
        "address": {
            "formattedAddress": "Amphitheatre Pkwy, Mountain View, CA 94043, USA",
            "postalAddress": {
                "revision": 0,
                "regionCode": "US",
                "languageCode": "en",
                "postalCode": "94043",
                "administrativeArea": "CA",
                "locality": "Mountain View",
                "addressLines": ["Amphitheatre Pkwy"],
            },
            "addressComponents": [
                {
                    "componentName": {"text": "9999", "languageCode": "en"},
                    "componentType": "street_number",
                    "confirmationLevel": "UNCONFIRMED_BUT_PLAUSIBLE",
                },
                {
                    "componentName": {"text": "Amphitheatre Pkwy", "languageCode": "en"},
                    "componentType": "route",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "Mountain View", "languageCode": "en"},
                    "componentType": "locality",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "CA", "languageCode": "en"},
                    "componentType": "administrative_area_level_1",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "94043", "languageCode": "en"},
                    "componentType": "postal_code",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "US", "languageCode": "en"},
                    "componentType": "country",
                    "confirmationLevel": "CONFIRMED",
                },
            ],
        },
    },
    "responseId": "c3d4e5f6-a7b8-9012-cdef-123456789012",
}

VALID_RESPONSE_SUSPICIOUS_COMPONENT: dict[str, Any] = {
    "result": {
        "verdict": {
            "inputGranularity": "PREMISE",
            "validationGranularity": "OTHER",
            "geocodeGranularity": "OTHER",
            "addressComplete": False,
        },
        "address": {
            "formattedAddress": "123 Fake St, Springfield, IL 62704, USA",
            "postalAddress": {
                "revision": 0,
                "regionCode": "US",
                "languageCode": "en",
                "postalCode": "62704",
                "administrativeArea": "IL",
                "locality": "Springfield",
                "addressLines": ["123 Fake St"],
            },
            "addressComponents": [
                {
                    "componentName": {"text": "123", "languageCode": "en"},
                    "componentType": "street_number",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "Fake St", "languageCode": "en"},
                    "componentType": "route",
                    "confirmationLevel": "UNCONFIRMED_AND_SUSPICIOUS",
                },
                {
                    "componentName": {"text": "Springfield", "languageCode": "en"},
                    "componentType": "locality",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "IL", "languageCode": "en"},
                    "componentType": "administrative_area_level_1",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "62704", "languageCode": "en"},
                    "componentType": "postal_code",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "US", "languageCode": "en"},
                    "componentType": "country",
                    "confirmationLevel": "CONFIRMED",
                },
            ],
        },
    },
    "responseId": "d4e5f6a7-b8c9-0123-def0-234567890123",
}

GOOGLE_ERROR_RESPONSE_403: dict[str, Any] = {
    "error": {
        "code": 403,
        "message": "The caller does not have permission",
        "status": "PERMISSION_DENIED",
    },
}
