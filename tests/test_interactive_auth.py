import unittest
from unittest.mock import MagicMock, patch

from schwab_client.oauth import OAuthManager
from schwab_client.exceptions import (
    SchwabAuthError,
    SchwabReauthorizationRequired,
    SchwabAuthTemporaryError,
    SchwabAuthConfigurationError,
    SchwabAuthRateLimitError,
)


class TestInteractiveAuth(unittest.TestCase):

    def make_manager(self, interactive_auth):
        manager = OAuthManager(
            app_key="test",
            app_secret="test",
            redirect_uri="https://127.0.0.1",
            token_store=MagicMock(),
            interactive_auth=interactive_auth,
        )

        manager.is_access_token_valid = MagicMock(
            return_value=False
        )

        manager.token_store.load.return_value = {
            "access_token": "test-access-token"
        }

        manager._refresh_token_unlocked = MagicMock(
            side_effect=SchwabReauthorizationRequired(
                "Refresh rejected"
            )
        )

        manager.interactive_authorization_code_flow = (
            MagicMock()
        )

        return manager

    @patch("sys.stdin.isatty", return_value=True)
    def test_interactive_recovery(self, _):
        manager = self.make_manager(True)

        self.assertEqual(
            manager.get_access_token(),
            "test-access-token",
        )

        manager.interactive_authorization_code_flow.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    def test_unknown_auth_error_recovery(self, _):
        manager = self.make_manager(True)

        manager._refresh_token_unlocked.side_effect = (
            SchwabAuthError("HTTP 400")
        )

        manager.get_access_token()

        manager.interactive_authorization_code_flow.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    def test_disabled_interactive_recovery(self, _):
        manager = self.make_manager(False)

        with self.assertRaises(SchwabReauthorizationRequired):
            manager.get_access_token()

        manager.interactive_authorization_code_flow.assert_not_called()

    @patch("sys.stdin.isatty", return_value=False)
    def test_no_terminal_available(self, _):
        manager = self.make_manager(True)

        with self.assertRaises(SchwabReauthorizationRequired):
            manager.get_access_token()

        manager.interactive_authorization_code_flow.assert_not_called()

    @patch("sys.stdin.isatty", return_value=True)
    def test_non_authorization_failures_never_prompt(self, _):
        for error_type in (
            SchwabAuthTemporaryError,
            SchwabAuthConfigurationError,
            SchwabAuthRateLimitError,
        ):
            with self.subTest(error_type=error_type):
                manager = self.make_manager(True)

                manager._refresh_token_unlocked.side_effect = (
                    error_type("Test failure")
                )

                with self.assertRaises(error_type):
                    manager.get_access_token()

                manager.interactive_authorization_code_flow.assert_not_called()


if __name__ == "__main__":
    unittest.main()
