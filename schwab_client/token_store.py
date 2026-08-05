import json
import os
import tempfile
from pathlib import Path


class JsonTokenStore:

    def __init__(
        self,
        token_file,
    ):
        self.token_file = Path(token_file)

    def exists(self):
        return self.token_file.exists()

    def load(self):
        if not self.exists():
            return None

        with open(
            self.token_file,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def save(
        self,
        token_data,
    ):
        self.token_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=self.token_file.parent,
            prefix=f".{self.token_file.name}.",
            suffix=".tmp",
        )

        temporary_path = Path(temporary_name)

        try:
            with os.fdopen(
                file_descriptor,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    token_data,
                    file,
                    indent=2,
                )
                file.flush()
                os.fsync(file.fileno())

            os.replace(
                temporary_path,
                self.token_file,
            )
        except Exception:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass

            raise

    def get_access_token(self):
        data = self.load()

        if not data:
            return None

        return data.get("access_token")

    def get_refresh_token(self):
        data = self.load()

        if not data:
            return None

        return data.get("refresh_token")
