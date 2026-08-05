import json
import tempfile
import threading
import unittest
from pathlib import Path

from schwab_client.token_store import JsonTokenStore


class JsonTokenStoreTests(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.token_path = self.directory / "refresh_token.json"
        self.store = JsonTokenStore(self.token_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_missing_file_returns_none(self):
        self.assertFalse(self.store.exists())
        self.assertIsNone(self.store.load())
        self.assertIsNone(self.store.get_access_token())
        self.assertIsNone(self.store.get_refresh_token())

    def test_save_and_load(self):
        expected = {
            "access_token": "access-123",
            "refresh_token": "refresh-456",
            "access_token_expiration_time": 1234567890,
        }

        self.store.save(expected)

        self.assertTrue(self.store.exists())
        self.assertEqual(self.store.load(), expected)
        self.assertEqual(
            self.store.get_access_token(),
            "access-123",
        )
        self.assertEqual(
            self.store.get_refresh_token(),
            "refresh-456",
        )

        with open(
            self.token_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.assertEqual(json.load(file), expected)

    def test_repeated_save_leaves_no_temporary_files(self):
        for number in range(100):
            self.store.save(
                {
                    "access_token": f"access-{number}",
                    "refresh_token": f"refresh-{number}",
                }
            )

        temporary_files = list(
            self.directory.glob(
                f".{self.token_path.name}.*.tmp"
            )
        )

        self.assertEqual(temporary_files, [])
        self.assertEqual(
            self.store.get_access_token(),
            "access-99",
        )

    def test_concurrent_reads_never_see_invalid_json(self):
        self.store.save(
            {
                "access_token": "initial-access",
                "refresh_token": "initial-refresh",
            }
        )

        errors = []
        stop_reading = threading.Event()

        def writer():
            try:
                for number in range(1000):
                    self.store.save(
                        {
                            "access_token": f"access-{number}",
                            "refresh_token": f"refresh-{number}",
                            "sequence": number,
                        }
                    )
            except Exception as error:
                errors.append(error)
            finally:
                stop_reading.set()

        def reader():
            try:
                while not stop_reading.is_set():
                    data = self.store.load()

                    if not isinstance(data, dict):
                        raise AssertionError(
                            f"Expected dictionary, received {data!r}"
                        )

                    if "access_token" not in data:
                        raise AssertionError(
                            f"Missing access token: {data!r}"
                        )
            except Exception as error:
                errors.append(error)
                stop_reading.set()

        writer_thread = threading.Thread(target=writer)
        reader_threads = [
            threading.Thread(target=reader)
            for _ in range(4)
        ]

        for thread in reader_threads:
            thread.start()

        writer_thread.start()
        writer_thread.join()

        for thread in reader_threads:
            thread.join()

        self.assertEqual(errors, [])

        final_data = self.store.load()
        self.assertEqual(final_data["sequence"], 999)


if __name__ == "__main__":
    unittest.main()
