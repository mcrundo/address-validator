"""Tests for the API key authorizer Lambda."""

import pytest

from address_validation.authorizer import handler


@pytest.fixture(autouse=True)
def _set_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_KEY_SECRET_NAME", "address-validation/test/api-key")
    monkeypatch.setattr(
        "address_validation.authorizer.get_secret",
        lambda _name: "test-secret-key-abc123",
    )


def _make_event(api_key: str | None = None) -> dict:
    """Build a minimal API Gateway v2 authorizer event."""
    headers: dict[str, str] = {}
    if api_key is not None:
        headers["x-api-key"] = api_key
    return {"headers": headers}


class TestAuthorizerSuccess:
    def test_valid_key(self) -> None:
        result = handler(_make_event("test-secret-key-abc123"), None)
        assert result["isAuthorized"] is True

    def test_valid_key_is_exact_match(self) -> None:
        result = handler(_make_event("test-secret-key-abc123"), None)
        assert result["isAuthorized"] is True


class TestAuthorizerRejection:
    def test_wrong_key(self) -> None:
        result = handler(_make_event("wrong-key"), None)
        assert result["isAuthorized"] is False

    def test_empty_key(self) -> None:
        result = handler(_make_event(""), None)
        assert result["isAuthorized"] is False

    def test_missing_header(self) -> None:
        result = handler(_make_event(), None)
        assert result["isAuthorized"] is False

    def test_no_headers_at_all(self) -> None:
        result = handler({"headers": {}}, None)
        assert result["isAuthorized"] is False

    def test_missing_secret_name_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("API_KEY_SECRET_NAME")
        result = handler(_make_event("test-secret-key-abc123"), None)
        assert result["isAuthorized"] is False

    def test_secret_fetch_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def raise_(_name: str) -> str:
            raise RuntimeError("boom")

        monkeypatch.setattr("address_validation.authorizer.get_secret", raise_)
        result = handler(_make_event("test-secret-key-abc123"), None)
        assert result["isAuthorized"] is False

    def test_key_with_extra_whitespace(self) -> None:
        result = handler(_make_event(" test-secret-key-abc123 "), None)
        assert result["isAuthorized"] is False
