import json
from pathlib import Path


class JsonTokenStore:

    def __init__(self, token_file):
        self.token_file = Path(token_file)

    def load(self):
        if not self.token_file.exists():
            return None

        with open(self.token_file, "r") as file:
            return json.load(file)

    def save(self, token_data):
        self.token_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(self.token_file, "w") as file:
            json.dump(
                token_data,
                file,
                indent=2,
            )
