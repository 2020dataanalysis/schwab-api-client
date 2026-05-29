class MarketDataService:

    def __init__(
        self,
        client,
    ):
        self.client = client

    def get_quote(
        self,
        symbol,
    ):
        raise NotImplementedError

    def get_quotes(
        self,
        symbols,
    ):
        raise NotImplementedError

    def get_movers(
        self,
        index="EQUITY_ALL",
    ):
        raise NotImplementedError

    def get_market_hours(
        self,
        markets=None,
    ):
        raise NotImplementedError

    def get_price_history(
        self,
        symbol,
    ):
        raise NotImplementedError
