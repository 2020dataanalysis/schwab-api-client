import multiprocessing
import tempfile
import time
import unittest

from pathlib import Path
from unittest.mock import patch

from schwab_client.oauth import OAuthManager
from schwab_client.token_store import JsonTokenStore


def request_token(token_file, counter, barrier, results):
    store = JsonTokenStore(token_file)

    oauth = OAuthManager(
        app_key="test-key",
        app_secret="test-secret",
        redirect_uri="https://127.0.0.1",
        token_store=store,
    )

    def mock_refresh(*args, **kwargs):
        with counter.get_lock():
            counter.value += 1

        time.sleep(0.3)

        return {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 1800,
        }

    with patch.object(
        oauth,
        "_post_token_request",
        side_effect=mock_refresh,
    ):
        barrier.wait(timeout=10)
        results.put(oauth.get_access_token())


class TestConcurrentRefresh(unittest.TestCase):

    def test_only_one_process_refreshes(self):
        context = multiprocessing.get_context("spawn")

        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "tokens.json"
            store = JsonTokenStore(token_file)

            store.save({
                "access_token": "expired-token",
                "refresh_token": "original-refresh-token",
                "access_token_expiration_time": 0,
                "refresh_token_expiration_time": 9999999999,
            })

            counter = context.Value("i", 0)
            barrier = context.Barrier(4)
            results = context.Queue()

            processes = [
                context.Process(
                    target=request_token,
                    args=(
                        token_file,
                        counter,
                        barrier,
                        results,
                    ),
                )
                for _ in range(4)
            ]

            try:
                for process in processes:
                    process.start()

                for process in processes:
                    process.join(timeout=15)
                    self.assertEqual(process.exitcode, 0)

                self.assertEqual(counter.value, 1)

                for _ in processes:
                    self.assertEqual(
                        results.get(timeout=2),
                        "new-access-token",
                    )

                self.assertEqual(
                    store.load()["refresh_token"],
                    "new-refresh-token",
                )

            finally:
                for process in processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()

                results.close()
                results.join_thread()


if __name__ == "__main__":
    unittest.main()
