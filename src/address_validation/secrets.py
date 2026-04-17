"""Secrets Manager helper — fetches secret values, cached per Lambda container."""

from functools import cache
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_secretsmanager.client import SecretsManagerClient


@cache
def _client() -> "SecretsManagerClient":
    return boto3.client("secretsmanager")


@cache
def get_secret(name: str) -> str:
    """Fetch a secret's string value from AWS Secrets Manager.

    Cached for the life of the Lambda container — warm invocations reuse
    the value without re-calling Secrets Manager. Rotated secrets propagate
    on the next cold start.
    """
    response = _client().get_secret_value(SecretId=name)
    return response["SecretString"]
