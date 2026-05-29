from .token_service import TokenService


class SchwabClient:

    def __init__(
        self,
        credentials_path=None,
        token_path=None,
    ):
        self.token_service = TokenService(
            credentials_path=credentials_path,
            token_path=token_path,
        )

    def get_quote(
        self,
        symbol,
    ):
        raise NotImplementedError

    def get_price_history(
        self,
        symbol,
    ):
        raise NotImplementedError

    def get_market_hours(
        self,
    ):
        raise NotImplementedError
