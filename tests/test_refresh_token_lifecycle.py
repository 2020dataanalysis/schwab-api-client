import unittest
from contextlib import nullcontext
from unittest.mock import Mock, patch

from schwab_client.oauth import OAuthManager


class TestRefreshTokenLifecycle(unittest.TestCase):

    def setUp(self):
        self.store = Mock()
        self.store.lock.side_effect = nullcontext

        self.oauth = OAuthManager(
            app_key="test-key",
            app_secret="test-secret",
            redirect_uri="https://127.0.0.1",
            token_store=self.store,
        )

        self.store.load.return_value = {
            "access_token": "old-access-token",
            "refresh_token": "original-refresh-token",
            "refresh_token_expiration_time": 2000000000,
        }

    def test_preserves_expiration_when_token_returned(self):
        with patch.object(
            self.oauth,
            "_post_token_request",
            return_value={
                "access_token": "new-access-token",
                "refresh_token": "returned-refresh-token",
                "expires_in": 1800,
            },
        ):
            result = self.oauth.refresh_token_flow()

        self.assertEqual(
            result["refresh_token"],
            "returned-refresh-token",
        )
        self.assertEqual(
            result["refresh_token_expiration_time"],
            2000000000,
        )
        self.store.save.assert_called_once_with(result)

    def test_preserves_token_when_omitted(self):
        with patch.object(
            self.oauth,
            "_post_token_request",
            return_value={
                "access_token": "new-access-token",
                "expires_in": 1800,
            },
        ):
            result = self.oauth.refresh_token_flow()

        self.assertEqual(
            result["refresh_token"],
            "original-refresh-token",
        )
        self.assertEqual(
            result["refresh_token_expiration_time"],
            2000000000,
        )
        self.store.save.assert_called_once_with(result)

    def test_unknown_expiration_remains_unknown(self):
        self.store.load.return_value.pop(
            "refresh_token_expiration_time"
        )

        with patch.object(
            self.oauth,
            "_post_token_request",
            return_value={
                "access_token": "new-access-token",
                "refresh_token": "returned-refresh-token",
                "expires_in": 1800,
            },
        ):
            result = self.oauth.refresh_token_flow()

        self.assertNotIn(
            "refresh_token_expiration_time",
            result,
        )


if __name__ == "__main__":
    unittest.main()
