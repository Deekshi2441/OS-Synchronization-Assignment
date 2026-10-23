"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 1: Readers-Writers Problem (Semaphore-Based Implementation)
================================================================================
"""

import os
import sys
import time
import random
import argparse
import threading
import webbrowser
from typing import List, Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.html_templates import generate_rw_html


class SharedDatabase:
    """Shared resource holding an integer counter subject to non-atomic read/modify/write."""
    def __init__(self, delay: float = 0.1):
        self.value: int = 0
        self.delay: float = delay
        self.data: str = "Counter: 0"
        self.revision: int = 0

    def read(self) -> int:
        v = self.value
        time.sleep(self.delay * 0.5)
        return v

    def write(self, writer_id: str) -> int:
        v = self.value
        time.sleep(self.delay)  # Deliberately non-atomic sleep
        self.value = v + 1
        self.revision = self.value
        self.data = f"Value={self.value} (updated by {writer_id})"
        return self.value


class ExecutionTracer:
    """Thread-safe event logger capturing state transitions for HTML simulation."""
    def __init__(self, start_time: float):
        self.start_time = start_time
        self.events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def log(self, entity_id: str, action: str, details: str,
            active_readers: int, active_writers: int,
            waiting_readers: int, waiting_writers: int,
            readers_state: List[Dict[str, str]],
            writers_state: List[Dict[str, str]],
            shared_data: str, shared_val: int,
            sync_desc: str):
        with self._lock:
            elapsed = time.time() - self.start_time
            elapsed_ms = int(elapsed * 1000)
            snapshot = {
                "step": len(self.events),
                "timestamp_ms": elapsed_ms,
                "time_sec": f"{elapsed:.3f}s",
                "entity_id": entity_id,
                "action": action,
                "details": details,
                "active_readers": active_readers,
                "active_writers": active_writers,
                "waiting_readers": waiting_readers,
                "waiting_writers": waiting_writers,
                "readers_state": [dict(r) for r in readers_state],
                "writers_state": [dict(w) for w in writers_state],
                "shared_data": shared_data,
                "shared_data_version": shared_val,
                "sync_state": {"description": sync_desc}
            }
            self.events.append(snapshot)
            state_str = "reading" if "READ" in action or action == "ENTER_CS" else ("writing" if "WRITE" in action or action == "ENTER_CS" else "idle")
            print(f"[{elapsed:.3f}s] {entity_id:<3} {action:<14} | R:{active_readers} W:{active_writers} | {details}")


class SemaphoreSyncManager:
    """
    Readers-Writers synchronization using:
      - resource_lock (rw_mutex): binary semaphore for critical section access
      - count_mutex: binary semaphore protecting active_readers
      - turnstile: gate preventing writer starvation
    """
    def __init__(self, tracer: ExecutionTracer, db: SharedDatabase,
                 num_readers: int, num_writers: int):
        self.tracer = tracer
        self.db = db
        self.num_readers = num_readers
        self.num_writers = num_writers

        self.resource_lock = threading.Semaphore(1)
        self.count_mutex = threading.Semaphore(1)
        self.turnstile = threading.Semaphore(1)

        self.active_readers = 0
        self.active_writers = 0
        self.waiting_readers = 0
        self.waiting_writers = 0
        self._state_lock = threading.Lock()

        self.readers_status = {f"R{i+1}": "IDLE" for i in range(num_readers)}
        self.writers_status = {f"W{i+1}": "IDLE" for i in range(num_writers)}

        self.max_concurrent_readers = 0
        self.total_reads = 0
        self.total_writes = 0

    def _readers_snap(self):
        return [{"id": k, "status": v} for k, v in self.readers_status.items()]

    def _writers_snap(self):
        return [{"id": k, "status": v} for k, v in self.writers_status.items()]

    def reader_enter(self, r_id: str):
        with self._state_lock:
            self.waiting_readers += 1
            self.readers_status[r_id] = "WAITING"
            self.tracer.log(r_id, "REQUEST_READ", f"{r_id} waiting requests read access",
                            self.active_readers, self.active_writers, self.waiting_readers, self.waiting_writers,
                            self._readers_snap(), self._writers_snap(), self.db.data, self.db.value, "turnstile queue")

        self.turnstile.acquire()
        self.count_mutex.acquire()

        with self._state_lock:
            self.active_readers += 1
            self.waiting_readers -= 1
            self.readers_status[r_id] = "READING"
            if self.active_readers > self.max_concurrent_readers:
                self.max_concurrent_readers = self.active_readers
            first = (self.active_readers == 1)

        if first:
            self.resource_lock.acquire()

        self.count_mutex.release()
        self.turnstile.release()

        with self._state_lock:
            self.tracer.log(r_id, "ENTER_CS", f"{r_id} reading entered CS, readers inside = {self.active_readers}",
                            self.active_readers, self.active_writers, self.waiting_readers, self.waiting_writers,
                            self._readers_snap(), self._writers_snap(), self.db.data, self.db.value, f"rw_mutex held by readers ({self.active_readers})")

    def reader_exit(self, r_id: str, read_val: int):
        self.count_mutex.acquire()
        with self._state_lock:
            self.active_readers -= 1
            self.total_reads += 1
            self.readers_status[r_id] = "IDLE"
            last = (self.active_readers == 0)

        if last:
            self.resource_lock.release()

        self.count_mutex.release()

        with self._state_lock:
            self.tracer.log(r_id, "EXIT_CS", f"{r_id} idle left CS, readers inside = {self.active_readers} (read value={read_val})",
                            self.active_readers, self.active_writers, self.waiting_readers, self.waiting_writers,
                            self._readers_snap(), self._writers_snap(), self.db.data, self.db.value, "rw_mutex free" if last else "readers remaining")

    def writer_enter(self, w_id: str):
        with self._state_lock:
            self.waiting_writers += 1
            self.writers_status[w_id] = "WAITING"
            self.tracer.log(w_id, "REQUEST_WRITE", f"{w_id} waiting requests write access",
                            self.active_readers, self.active_writers, self.waiting_readers, self.waiting_writers,
                            self._readers_snap(), self._writers_snap(), self.db.data, self.db.value, "holding turnstile, waiting on resource_lock")

        self.turnstile.acquire()
        self.resource_lock.acquire()
        self.turnstile.release()

        with self._state_lock:
            self.active_writers = 1
            self.waiting_writers -= 1
            self.writers_status[w_id] = "WRITING"
            self.tracer.log(w_id, "ENTER_CS", f"{w_id} writing entered CS (exclusive)",
                            self.active_readers, self.active_writers, self.waiting_readers, self.waiting_writers,
                            self._readers_snap(), self._writers_snap(), self.db.data, self.db.value, f"resource_lock exclusive held by {w_id}")

    def writer_exit(self, w_id: str, new_val: int):
        with self._state_lock:
            self.active_writers = 0
            self.total_writes += 1
            self.writers_status[w_id] = "IDLE"

        self.resource_lock.release()

        with self._state_lock:
            self.tracer.log(w_id, "EXIT_CS", f"{w_id} idle left CS, committed value = {new_val}",
                            self.active_readers, self.active_writers, self.waiting_readers, self.waiting_writers,
                            self._readers_snap(), self._writers_snap(), self.db.data, self.db.value, "resource_lock released (free)")


def reader_thread(r_id: str, manager: SemaphoreSyncManager, rounds: int, delay: float):
    for _ in range(rounds):
        time.sleep(random.uniform(delay * 0.5, delay * 1.5))
        manager.reader_enter(r_id)
        val = manager.db.read()
        time.sleep(random.uniform(delay * 0.4, delay * 1.0))
        manager.reader_exit(r_id, val)


def writer_thread(w_id: str, manager: SemaphoreSyncManager, rounds: int, delay: float):
    for _ in range(rounds):
        time.sleep(random.uniform(delay * 0.8, delay * 2.0))
        manager.writer_enter(w_id)
        val = manager.db.write(w_id)
        time.sleep(random.uniform(delay * 0.5, delay * 1.2))
        manager.writer_exit(w_id, val)


def main():
    parser = argparse.ArgumentParser(description="Readers-Writers Problem - Semaphore Implementation")
    parser.add_argument("--readers", type=int, default=4, help="Number of reader threads")
    parser.add_argument("--writers", type=int, default=2, help="Number of writer threads")
    parser.add_argument("--rounds", type=int, default=3, help="Rounds per thread")
    parser.add_argument("--delay", type=float, default=0.2, help="Base timing delay in seconds")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatability")
    parser.add_argument("--out", type=str, default=None, help="Output HTML file path")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print("=" * 70)
    print(f"Readers-Writers (Semaphores) | Readers: {args.readers}, Writers: {args.writers}, Rounds: {args.rounds}")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    db = SharedDatabase(delay=args.delay)
    manager = SemaphoreSyncManager(tracer, db, args.readers, args.writers)

    threads = []
    for i in range(args.readers):
        threads.append(threading.Thread(target=reader_thread, args=(f"R{i+1}", manager, args.rounds, args.delay)))
    for j in range(args.writers):
        threads.append(threading.Thread(target=writer_thread, args=(f"W{j+1}", manager, args.rounds, args.delay)))

    random.shuffle(threads)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Safety Assertions & Validation
    expected_val = args.writers * args.rounds
    assert db.value == expected_val, f"Race condition detected! Expected {expected_val}, got {db.value}"
    print("-" * 70)
    print(f"validation OK: final value equals writers x rounds ({db.value})")
    print(f"Simulation completed. Total events: {len(tracer.events)} | Max concurrent readers: {manager.max_concurrent_readers}")
    print("-" * 70)

    # Output HTML
    out_path = args.out or os.path.join(PROJECT_ROOT, "generated_html", "readers_writers_semaphore.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    summary_stats = {
        "total_events": len(tracer.events),
        "total_reads": manager.total_reads,
        "total_writes": manager.total_writes,
        "max_concurrent_readers": manager.max_concurrent_readers,
        "policy": "Starvation-Free Turnstile Semaphore"
    }
    html_content = generate_rw_html("Readers-Writers Problem", "Semaphores (Turnstile + Mutex + Resource Lock)", tracer.events, summary_stats)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Also mirror to rw_semaphore.html for reference compatibility
    alt_path = os.path.join(PROJECT_ROOT, "generated_html", "rw_semaphore.html")
    with open(alt_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated HTML simulation at: {out_path}")
    if not args.no_browser:
        webbrowser.open(f"file:///{os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
