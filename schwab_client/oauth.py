import base64
import time
from urllib.parse import unquote

import requests

from .config import TOKEN_URL, AUTHORIZATION_URL, DEFAULT_TIMEOUT_SECONDS
from .exceptions import SchwabAuthError


class OAuthManager:

    def __init__(
        self,
        app_key,
        app_secret,
        redirect_uri,
        token_store,
        token_url=TOKEN_URL,
        authorization_url=AUTHORIZATION_URL,
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.token_store = token_store
        self.token_url = token_url
        self.authorization_url = authorization_url
        self.timeout_seconds = timeout_seconds

    def build_authorization_url(self):
        return (
            f"{self.authorization_url}"
            f"?client_id={self.app_key}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
        )

    def extract_authorization_code(
        self,
        callback_url,
    ):
        code_index = callback_url.find("code=")
        session_index = callback_url.find("&session=")

        if code_index == -1:
            raise SchwabAuthError(
                "Authorization code not found in callback URL."
            )

        if session_index == -1:
            raw_code = callback_url[
                code_index + len("code="):
            ]
        else:
            raw_code = callback_url[
                code_index + len("code="):session_index
            ]

        return unquote(raw_code)

    def authorization_code_flow(
        self,
        callback_url,
    ):
        code = self.extract_authorization_code(
            callback_url
        )

        response = self._post_token_request(
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )

        token_data = self._with_expiration_times(
            response
        )

        self.token_store.save(
            token_data
        )

        return token_data

    def refresh_token_flow(self):
        token_data = self.token_store.load()

        if not token_data:
            raise SchwabAuthError(
                "No token data available for refresh."
            )

        refresh_token = token_data.get(
            "refresh_token"
        )

        if not refresh_token:
            raise SchwabAuthError(
                "No refresh token available."
            )

        response = self._post_token_request(
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

        refreshed = self._with_expiration_times(
            response
        )

        self.token_store.save(
            refreshed
        )

        return refreshed

    def is_access_token_valid(self):
        token_data = self.token_store.load()

        if not token_data:
            return False

        expiration_time = token_data.get(
            "access_token_expiration_time"
        )

        if not expiration_time:
            return False

        return int(time.time()) < expiration_time

    def interactive_authorization_code_flow(self):
        print("Refresh token failed. Starting authorization-code flow.")
        print("Please visit the following URL and authorize the application:")
        print(self.build_authorization_url())

        callback_url = input(
            "Paste the FULL callback URL from your browser's address bar "
            "(the one that starts with https://127.0.0.1/):\n> "
        ).strip()

        return self.authorization_code_flow(
            callback_url
        )

    def get_access_token(self):
        if not self.is_access_token_valid():
            try:
                self.refresh_token_flow()
            except SchwabAuthError as e:
                print(f"REFRESH TOKEN FAILED DETAILS: {e}")
                self.interactive_authorization_code_flow()

        token_data = self.token_store.load()

        if not token_data:
            raise SchwabAuthError(
                "No token data available."
            )

        return token_data["access_token"]

    def _post_token_request(
        self,
        data,
    ):
        credentials = (
            f"{self.app_key}:{self.app_secret}"
        )

        encoded_credentials = base64.b64encode(
            credentials.encode()
        ).decode()

        response = requests.post(
            self.token_url,
            headers={
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=data,
            timeout=self.timeout_seconds,
        )

        if response.status_code >= 400:
            raise SchwabAuthError(
                f"OAuth token request failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json()

    def _with_expiration_times(
        self,
        token_data,
    ):
        now = int(time.time())

        token_data["access_token_expiration_time"] = (
            now + int(token_data["expires_in"])
        )

        if "refresh_token" in token_data:
            token_data["refresh_token_expiration_time"] = (
                now + 60 * 60 * 24 * 7
            )

        return token_data