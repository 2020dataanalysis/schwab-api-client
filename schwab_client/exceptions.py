class SchwabClientError(Exception):
    pass


class SchwabAuthError(SchwabClientError):
    pass


class SchwabReauthorizationRequired(SchwabAuthError):
    pass


class SchwabAuthTemporaryError(SchwabAuthError):
    pass


class SchwabAuthRateLimitError(SchwabAuthTemporaryError):
    pass


class SchwabAuthConfigurationError(SchwabAuthError):
    pass


class SchwabRequestError(SchwabClientError):
    pass
