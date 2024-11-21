from contextlib import contextmanager
from typing import Generator

from django.dispatch import Signal


@contextmanager
def disconnect_all_signals(signal: Signal) -> Generator[None, None, None]:
    """
    Disconnects all handlers for the specified signal within the context.

    Args:
        signal (Signal): The Django signal to modify (e.g., post_save).

    Yields:
        None: Allows the signal modification to be temporary within the context.
    """
    original_receivers = signal.receivers[:]
    signal.receivers = []  # Disconnect all receivers

    try:
        yield
    finally:
        signal.receivers = original_receivers  # Restore all receivers
