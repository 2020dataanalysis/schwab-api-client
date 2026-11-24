import unittest

from unittest.mock import Mock

from schwab_client.auth_error_classifier import (
    classify_auth_error,
)
from schwab_client.exceptions import (
    SchwabAuthError,
    SchwabReauthorizationRequired,
    SchwabAuthTemporaryError,
    SchwabAuthRateLimitError,
    SchwabAuthConfigurationError,
)


class TestAuthErrorClassifier(unittest.TestCase):

    def make_response(self, status, payload=None):
        response = Mock()
        response.status_code = status
        response.json.return_value = payload or {}
        response.headers = {}
        return response

    def test_invalid_grant(self):
        response = self.make_response(
            400, {"error": "invalid_grant"}
        )

        self.assertIsInstance(
            classify_auth_error(response),
            SchwabReauthorizationRequired,
        )

    def test_configuration_errors(self):
        for error in (
            "invalid_client",
            "unauthorized_client",
            "unsupported_grant_type",
            "invalid_scope",
        ):
            with self.subTest(error=error):
                response = self.make_response(
                    400, {"error": error}
                )

                self.assertIsInstance(
                    classify_auth_error(response),
                    SchwabAuthConfigurationError,
                )

    def test_temporary_http_errors(self):
        for status in (408, 500, 502, 503, 504):
            with self.subTest(status=status):
                response = self.make_response(status)

                self.assertIsInstance(
                    classify_auth_error(response),
                    SchwabAuthTemporaryError,
                )

    def test_temporary_oauth_errors(self):
        for error in (
            "temporarily_unavailable",
            "server_error",
        ):
            with self.subTest(error=error):
                response = self.make_response(
                    400, {"error": error}
                )

                self.assertIsInstance(
                    classify_auth_error(response),
                    SchwabAuthTemporaryError,
                )

    def test_rate_limit(self):
        response = self.make_response(429)
        response.headers["Retry-After"] = "60"

        exception = classify_auth_error(response)

        self.assertIsInstance(
            exception,
            SchwabAuthRateLimitError,
        )
        self.assertEqual(exception.retry_after, "60")

    def test_unknown_error(self):
        response = self.make_response(401)

        self.assertIs(
            type(classify_auth_error(response)),
            SchwabAuthError,
        )

    def test_invalid_json(self):
        response = self.make_response(400)
        response.json.side_effect = ValueError()

        self.assertIs(
            type(classify_auth_error(response)),
            SchwabAuthError,
        )

    def test_non_dictionary_response(self):
        response = self.make_response(
            400, ["unexpected"]
        )

        self.assertIs(
            type(classify_auth_error(response)),
            SchwabAuthError,
        )

    def test_sensitive_data_not_exposed(self):
        response = self.make_response(
            400,
            {
                "error": "invalid_grant",
                "error_description": "secret-token-value",
            },
        )

        exception = classify_auth_error(response)

        self.assertNotIn(
            "secret-token-value",
            str(exception),
        )


if __name__ == "__main__":
    unittest.main()
