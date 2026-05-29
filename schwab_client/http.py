import requests

from .config import DEFAULT_TIMEOUT_SECONDS
from .exceptions import SchwabRequestError


class SchwabHttpClient:

    def __init__(
        self,
        token_provider,
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    ):
        self.token_provider = token_provider
        self.timeout_seconds = timeout_seconds

    def get(
        self,
        base_url,
        endpoint,
        params=None,
    ):
        token = self.token_provider.get_access_token()

        response = requests.get(
            f"{base_url}{endpoint}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            params=params,
            timeout=self.timeout_seconds,
        )

        if response.status_code >= 400:
            raise SchwabRequestError(
                f"GET {endpoint} failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json()
