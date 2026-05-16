from __future__ import annotations

from queue import Queue, Empty, Full
from threading import Thread, Event, Lock

from core.storage.jsonl_store import JSONLStore


class AsyncQueueWriter:
    def __init__(self, store: JSONLStore, max_size: int = 10000, batch_size: int = 100) -> None:
        self.store = store
        self.batch_size = batch_size
        self.q: Queue[dict] = Queue(maxsize=max_size)
        self.stop_event = Event()
        self.thread: Thread | None = None

        self.lock = Lock()
        self.enqueued_total = 0
        self.dropped_total = 0
        self.written_total = 0
        self.flush_batches_total = 0
        self.errors_total = 0

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=3)

    def enqueue(self, record: dict) -> bool:
        try:
            self.q.put_nowait(record)
            with self.lock:
                self.enqueued_total += 1
            return True
        except Full:
            with self.lock:
                self.dropped_total += 1
            return False

    def metrics(self) -> dict:
        with self.lock:
            return {
                "queue_depth": self.q.qsize(),
                "enqueued_total": self.enqueued_total,
                "dropped_total": self.dropped_total,
                "written_total": self.written_total,
                "flush_batches_total": self.flush_batches_total,
                "errors_total": self.errors_total,
            }

    def _run(self) -> None:
        batch: list[dict] = []
        while not self.stop_event.is_set() or not self.q.empty():
            try:
                batch.append(self.q.get(timeout=0.2))
            except Empty:
                pass
            if not batch:
                continue
            if len(batch) >= self.batch_size or self.stop_event.is_set() or self.q.empty():
                self._flush(batch)
                batch.clear()

    def _flush(self, batch: list[dict]) -> None:
        try:
            for row in batch:
                self.store.append(row)
            with self.lock:
                self.written_total += len(batch)
                self.flush_batches_total += 1
        except Exception:
            with self.lock:
                self.errors_total += 1
