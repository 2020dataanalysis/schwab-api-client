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

    def _headers(self):
        return {
            "Authorization": (
                f"Bearer {self.token_provider.get_access_token()}"
            ),
            "Accept": "application/json",
        }

    def get(
        self,
        base_url,
        endpoint,
        params=None,
    ):
        response = requests.get(
            f"{base_url}{endpoint}",
            headers=self._headers(),
            params=params,
            timeout=self.timeout_seconds,
        )

        return self._handle_response(
            response,
            method="GET",
            endpoint=endpoint,
        )

    def post(
        self,
        base_url,
        endpoint,
        json_data=None,
    ):
        response = requests.post(
            f"{base_url}{endpoint}",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
            },
            json=json_data,
            timeout=self.timeout_seconds,
        )

        return self._handle_response(
            response,
            method="POST",
            endpoint=endpoint,
        )

    def put(
        self,
        base_url,
        endpoint,
        json_data=None,
    ):
        response = requests.put(
            f"{base_url}{endpoint}",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
            },
            json=json_data,
            timeout=self.timeout_seconds,
        )

        return self._handle_response(
            response,
            method="PUT",
            endpoint=endpoint,
        )

    def delete(
        self,
        base_url,
        endpoint,
    ):
        response = requests.delete(
            f"{base_url}{endpoint}",
            headers=self._headers(),
            timeout=self.timeout_seconds,
        )

        return self._handle_response(
            response,
            method="DELETE",
            endpoint=endpoint,
        )

    def _handle_response(
        self,
        response,
        method,
        endpoint,
    ):
        if response.status_code >= 400:
            raise SchwabRequestError(
                f"{method} {endpoint} failed: "
                f"{response.status_code} {response.text}"
            )

        if response.status_code == 204:
            return None

        if not response.text:
            return None

        return response.json()