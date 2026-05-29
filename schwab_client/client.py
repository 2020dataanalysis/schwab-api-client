from .http import SchwabHttpClient
from .market_data import MarketDataService
from .oauth import OAuthManager
from .token_store import JsonTokenStore


class SchwabClient:

    def __init__(
        self,
        app_key,
        app_secret,
        redirect_uri,
        token_file,
    ):
        self.token_store = JsonTokenStore(
            token_file
        )

        self.oauth = OAuthManager(
            app_key=app_key,
            app_secret=app_secret,
            redirect_uri=redirect_uri,
            token_store=self.token_store,
        )

        self.http = SchwabHttpClient(
            token_provider=self.oauth
        )

        self.market_data = MarketDataService(
            http_client=self.http
        )