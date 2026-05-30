import json
from pathlib import Path

from schwab_client import SchwabClient


BASE_DIR = Path(__file__).resolve().parents[1]

CREDENTIALS_FILE = (
    BASE_DIR / "private" / "credentials.json"
)

TOKEN_FILE = (
    BASE_DIR / "private" / "refresh_token.json"
)


def load_credentials():
    with open(CREDENTIALS_FILE, "r") as file:
        return json.load(file)


def main():
    credentials = load_credentials()

    client = SchwabClient(
        app_key=credentials["app_key"],
        app_secret=credentials["app_secret"],
        redirect_uri=credentials["redirect_uri"],
        token_file=TOKEN_FILE,
    )

    data = client.market_data.get_price_history(
        symbol="TSLA",
        period_type="day",
        period=10,
        frequency_type="minute",
        frequency=1,
        need_extended_hours_data=True,
        need_previous_close=True,
    )

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
