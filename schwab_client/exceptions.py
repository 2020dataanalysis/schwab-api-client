class SchwabClientError(Exception):
    pass


class SchwabAuthError(SchwabClientError):
    pass


class SchwabRequestError(SchwabClientError):
    pass
