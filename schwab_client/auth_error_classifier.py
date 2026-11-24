from .exceptions import (
    SchwabAuthError,
    SchwabReauthorizationRequired,
    SchwabAuthTemporaryError,
    SchwabAuthRateLimitError,
    SchwabAuthConfigurationError,
)


def classify_auth_error(response):
    status = response.status_code

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    error = payload.get("error")

    message = f"OAuth token request failed: HTTP {status}"

    if status == 429:
        exception = SchwabAuthRateLimitError(message)
        exception.retry_after = response.headers.get(
            "Retry-After"
        )
        return exception

    if status == 408 or 500 <= status <= 599:
        return SchwabAuthTemporaryError(message)

    if error == "invalid_grant":
        return SchwabReauthorizationRequired(message)

    if error in (
        "invalid_client",
        "unauthorized_client",
        "unsupported_grant_type",
        "invalid_scope",
    ):
        return SchwabAuthConfigurationError(message)

    if error in (
        "temporarily_unavailable",
        "server_error",
    ):
        return SchwabAuthTemporaryError(message)

    return SchwabAuthError(message)
