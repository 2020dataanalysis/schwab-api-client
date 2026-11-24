import fcntl
import os

from contextlib import contextmanager
from pathlib import Path


@contextmanager
def token_lock(token_file):
    token_path = Path(token_file).resolve()

    lock_path = token_path.with_name(
        f"{token_path.name}.lock"
    )

    lock_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor = os.open(
        lock_path,
        os.O_CREAT | os.O_RDWR,
        0o600,
    )

    try:
        fcntl.flock(
            descriptor,
            fcntl.LOCK_EX,
        )

        yield

    finally:
        os.close(descriptor)
