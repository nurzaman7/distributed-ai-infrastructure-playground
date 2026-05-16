from __future__ import annotations

from time import sleep


def stream_tokens(text: str, delay_sec: float = 0.01):
    for tok in text.split():
        sleep(delay_sec)
        yield tok
