import unittest
from contextlib import nullcontext
from unittest.mock import Mock, patch

from schwab_client.exceptions import SchwabAuthError
from schwab_client.oauth import OAuthManager


class TestOAuthLifecycle(unittest.TestCase):

    def setUp(self):
        self.store = Mock()
        self.store.lock.side_effect = nullcontext
        self.oauth = OAuthManager(
            app_key="test-key",
            app_secret="test-secret",
            redirect_uri="https://127.0.0.1",
            token_store=self.store,
        )

    def test_valid_token_does_not_refresh(self):
        self.store.load.return_value = {
            "access_token": "valid-token",
            "access_token_expiration_time": 9999999999,
        }

        with patch.object(
            self.oauth, "_refresh_token_unlocked"
        ) as refresh:
            token = self.oauth.get_access_token()

        self.assertEqual(token, "valid-token")
        refresh.assert_not_called()

    def test_expired_token_refreshes(self):
        self.store.load.side_effect = [
            {"access_token_expiration_time": 0},
            {"access_token_expiration_time": 0},
            {"access_token": "refreshed-token"},
        ]

        with patch.object(
            self.oauth, "_refresh_token_unlocked"
        ) as refresh:
            token = self.oauth.get_access_token()

        self.assertEqual(token, "refreshed-token")
        refresh.assert_called_once()

    def test_refresh_failure_never_prompts(self):
        self.store.load.return_value = {
            "access_token_expiration_time": 0,
        }

        with (
            patch.object(
                self.oauth,
                "_refresh_token_unlocked",
                side_effect=SchwabAuthError("Refresh rejected"),
            ),
            patch.object(
                self.oauth,
                "interactive_authorization_code_flow",
            ) as interactive,
            patch("builtins.input") as user_input,
        ):
            with self.assertRaisesRegex(
                SchwabAuthError, "Refresh rejected"
            ):
                self.oauth.get_access_token()

        interactive.assert_not_called()
        user_input.assert_not_called()

    def test_missing_access_token_raises_auth_error(self):
        self.store.load.return_value = {
            "access_token_expiration_time": 9999999999,
        }

        with self.assertRaisesRegex(
            SchwabAuthError, "No access token available"
        ):
            self.oauth.get_access_token()


    def test_another_process_already_refreshed(self):
        valid_token = {
            "access_token": "updated-token",
            "access_token_expiration_time": 9999999999,
        }

        self.store.load.side_effect = [
            {"access_token_expiration_time": 0},
            valid_token,
            valid_token,
        ]

        with patch.object(
            self.oauth, "_refresh_token_unlocked"
        ) as refresh:
            token = self.oauth.get_access_token()

        self.assertEqual(token, "updated-token")
        self.store.lock.assert_called_once()
        refresh.assert_not_called()

if __name__ == "__main__":
    unittest.main()
