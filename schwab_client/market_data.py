from .config import MARKET_DATA_BASE_URL


class MarketDataService:

    def __init__(
        self,
        http_client,
    ):
        self.http = http_client

    def get_quote(
        self,
        symbol,
    ):
        return self.http.get(
            MARKET_DATA_BASE_URL,
            f"/{symbol.upper()}/quotes",
        )

    def get_quotes(
        self,
        symbols,
    ):
        if isinstance(symbols, list):
            symbols = ",".join(
                symbol.upper()
                for symbol in symbols
            )

        return self.http.get(
            MARKET_DATA_BASE_URL,
            "/quotes",
            params={
                "symbols": symbols,
            },
        )

    def get_movers(
        self,
        symbol_id="EQUITY_ALL",
        sort="VOLUME",
        frequency=0,
    ):
        return self.http.get(
            MARKET_DATA_BASE_URL,
            f"/movers/{symbol_id}",
            params={
                "sort": sort,
                "frequency": frequency,
            },
        )

    def get_market_hours(
        self,
        markets="equity",
        date=None,
    ):
        params = {
            "markets": markets,
        }

        if date is not None:
            params["date"] = date

        return self.http.get(
            MARKET_DATA_BASE_URL,
            "/markets",
            params=params,
        )

    def get_price_history(
        self,
        symbol,
        period_type="day",
        period=10,
        frequency_type="minute",
        frequency=1,
        start_date=None,
        end_date=None,
        need_extended_hours_data=True,
        need_previous_close=True,
    ):
        params = {
            "symbol": symbol.upper(),
            "periodType": period_type,
            "period": period,
            "frequencyType": frequency_type,
            "frequency": frequency,
            "needExtendedHoursData": need_extended_hours_data,
            "needPreviousClose": need_previous_close,
        }

        if start_date is not None:
            params["startDate"] = start_date

        if end_date is not None:
            params["endDate"] = end_date

        return self.http.get(
            MARKET_DATA_BASE_URL,
            "/pricehistory",
            params=params,
        )