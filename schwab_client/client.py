from .market_data import MarketDataService
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

        self.market_data = MarketDataService(
            self
        )