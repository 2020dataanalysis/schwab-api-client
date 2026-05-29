from pathlib import Path


class TokenService:

    def __init__(
        self,
        credentials_path=None,
        token_path=None,
    ):
        self.credentials_path = (
            Path(credentials_path)
            if credentials_path
            else None
        )

        self.token_path = (
            Path(token_path)
            if token_path
            else None
        )

    def load_token(self):
        raise NotImplementedError

    def save_token(self):
        raise NotImplementedError

    def refresh_token(self):
        raise NotImplementedError

    def access_token(self):
        raise NotImplementedError
