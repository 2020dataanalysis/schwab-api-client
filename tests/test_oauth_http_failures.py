import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

import requests

from schwab_client.oauth import OAuthManager
from schwab_client.token_store import JsonTokenStore
from schwab_client.exceptions import (
    SchwabAuthError,
    SchwabReauthorizationRequired,
    SchwabAuthTemporaryError,
    SchwabAuthRateLimitError,
    SchwabAuthConfigurationError,
)


class TestOAuthHttpFailures(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

        self.store = JsonTokenStore(
            Path(self.directory.name) / "tokens.json"
        )

        self.original_tokens = {
            "access_token": "expired-token",
            "refresh_token": "original-refresh-token",
            "access_token_expiration_time": 0,
            "refresh_token_expiration_time": 9999999999,
        }

        self.store.save(self.original_tokens)

        self.oauth = OAuthManager(
            app_key="test-key",
            app_secret="test-secret",
            redirect_uri="https://127.0.0.1",
            token_store=self.store,
        )

    def assert_failure(self, exception_type, **mock_options):
        with patch(
            "schwab_client.oauth.requests.post",
            **mock_options,
        ) as post, patch("builtins.input") as prompt:

            with self.assertRaises(exception_type):
                self.oauth.get_access_token()

            prompt.assert_not_called()
            post.assert_called_once()

        self.assertEqual(
            self.store.load(),
            self.original_tokens,
        )

    def make_response(self, status, payload=None):
        response = Mock()
        response.status_code = status
        response.json.return_value = payload or {}
        response.headers = {}
        return response

    def test_invalid_grant(self):
        self.assert_failure(
            SchwabReauthorizationRequired,
            return_value=self.make_response(
                400, {"error": "invalid_grant"}
            ),
        )

    def test_invalid_client(self):
        self.assert_failure(
            SchwabAuthConfigurationError,
            return_value=self.make_response(
                401, {"error": "invalid_client"}
            ),
        )

    def test_server_unavailable(self):
        self.assert_failure(
            SchwabAuthTemporaryError,
            return_value=self.make_response(503),
        )

    def test_rate_limit(self):
        self.assert_failure(
            SchwabAuthRateLimitError,
            return_value=self.make_response(429),
        )

    def test_network_timeout(self):
        self.assert_failure(
            SchwabAuthTemporaryError,
            side_effect=requests.exceptions.Timeout(),
        )

    def test_connection_error(self):
        self.assert_failure(
            SchwabAuthTemporaryError,
            side_effect=requests.exceptions.ConnectionError(),
        )

    def test_tls_error(self):
        self.assert_failure(
            SchwabAuthConfigurationError,
            side_effect=requests.exceptions.SSLError(),
        )

    def test_invalid_json(self):
        response = self.make_response(200)
        response.json.side_effect = ValueError()

        self.assert_failure(
            SchwabAuthTemporaryError,
            return_value=response,
        )

    def test_missing_refresh_token(self):
        self.store.save({
            "access_token_expiration_time": 0,
        })

        with patch(
            "schwab_client.oauth.requests.post"
        ) as post:

            with self.assertRaises(
                SchwabReauthorizationRequired
            ):
                self.oauth.get_access_token()

            post.assert_not_called()

    def test_unknown_http_error(self):
        self.assert_failure(
            SchwabAuthError,
            return_value=self.make_response(400),
        )


if __name__ == "__main__":
    unittest.main()
