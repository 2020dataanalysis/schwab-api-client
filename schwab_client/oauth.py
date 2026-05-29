class OAuthManager:

    def __init__(
        self,
        app_key,
        app_secret,
        redirect_uri,
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    def authorization_code_flow(self):
        raise NotImplementedError

    def refresh_token_flow(self):
        raise NotImplementedError
