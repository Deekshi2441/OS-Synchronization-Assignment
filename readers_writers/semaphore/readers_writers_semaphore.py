"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 1: Readers-Writers Problem (Semaphore-Based Implementation)
================================================================================
Description:
    Demonstrates classic synchronization between multiple concurrent readers
    and writer processes using semaphores.
    
    Shared Resource:
        A central dataset / database record containing a textual state and 
        monotonic revision counter.

    Synchronization Invariants:
        1. Mutual Exclusion: At most one writer can access the shared resource
           at any time, and no reader can access it while a writer is writing.
        2. Reader Concurrency: Arbitrary multiple readers may access the resource
           simultaneously without interference.
        3. Starvation Prevention: Implements a turnstile (service_queue) semaphore
           guaranteeing FIFO fairness and preventing writer starvation.

    Output:
        Executes concurrent threads, logs execution events with state snapshots,
        and generates an interactive visual simulation in HTML format.
================================================================================
"""

import os
import sys
import time
import random
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Ensure common visualizer can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.html_templates import generate_rw_html


# ------------------------------------------------------------------------------
# Shared Resource (Critical Section Target)
# ------------------------------------------------------------------------------
class SharedDatabase:
    """Represents the shared resource subject to concurrent read and write access."""
    def __init__(self):
        self.data: str = "Genesis Data: OS Kernel v1.0"
        self.revision: int = 0
        self.write_count: int = 0
        self.read_count: int = 0

    def read(self) -> str:
        self.read_count += 1
        return f"{self.data} (Rev {self.revision})"

    def write(self, new_val: str):
        self.revision += 1
        self.write_count += 1
        self.data = f"{new_val} [Rev {self.revision}]"


# ------------------------------------------------------------------------------
# Thread-Safe Execution Trace Recorder
# ------------------------------------------------------------------------------
class ExecutionTracer:
    """Thread-safe state recorder capturing event snapshots for visualization."""
    def __init__(self, start_time: float):
        self.start_time = start_time
        self.events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def record(self, entity_id: str, action: str, details: str,
               active_readers: int, active_writers: int,
               waiting_readers: int, waiting_writers: int,
               readers_state: List[Dict[str, str]],
               writers_state: List[Dict[str, str]],
               shared_data: str, shared_revision: int,
               sync_description: str):
        with self._lock:
            elapsed_ms = int((time.time() - self.start_time) * 1000)
            snapshot = {
                "step": len(self.events),
                "timestamp_ms": elapsed_ms,
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
                "shared_data_version": shared_revision,
                "sync_state": {
                    "description": sync_description,
                    "active_readers": active_readers,
                    "active_writers": active_writers
                }
            }
            self.events.append(snapshot)
            print(f"[{elapsed_ms:04d}ms] {entity_id:<4} | {action:<14} | R:{active_readers} W:{active_writers} | {details}")


# ------------------------------------------------------------------------------
# Semaphore Synchronization Manager
# ------------------------------------------------------------------------------
class SemaphoreSyncManager:
    """
    Implements starvation-free Readers-Writers synchronization via semaphores.
    Primitives:
        - mutex: protects reader_count updates (binary semaphore)
        - rw_mutex: protects shared resource access (binary semaphore)
        - turnstile: ensures FIFO fairness so writers are not starved by readers
    """
    def __init__(self, tracer: ExecutionTracer, db: SharedDatabase,
                 num_readers: int, num_writers: int):
        self.tracer = tracer
        self.db = db
        self.num_readers = num_readers
        self.num_writers = num_writers

        # Semaphores
        self.mutex = threading.Semaphore(1)
        self.rw_mutex = threading.Semaphore(1)
        self.turnstile = threading.Semaphore(1)

        # State tracking for visualization
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

    def _get_readers_snapshot(self):
        return [{"id": k, "status": v} for k, v in self.readers_status.items()]

    def _get_writers_snapshot(self):
        return [{"id": k, "status": v} for k, v in self.writers_status.items()]

    def reader_enter(self, reader_id: str):
        with self._state_lock:
            self.waiting_readers += 1
            self.readers_status[reader_id] = "WAITING"
            self.tracer.record(
                entity_id=reader_id,
                action="REQUEST_READ",
                details=f"{reader_id} requesting entry to read. Waiting on turnstile.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"turnstile=1, mutex=1, rw_mutex={'0 (LOCKED)' if self.active_readers > 0 or self.active_writers > 0 else '1 (FREE)'}"
            )

        # 1. Acquire turnstile to preserve order
        self.turnstile.acquire()

        # 2. Acquire mutex to update reader count
        self.mutex.acquire()
        with self._state_lock:
            self.active_readers += 1
            self.waiting_readers -= 1
            self.readers_status[reader_id] = "READING"
            if self.active_readers > self.max_concurrent_readers:
                self.max_concurrent_readers = self.active_readers

            # If first reader, lock resource from writers
            first_reader = (self.active_readers == 1)

        if first_reader:
            self.rw_mutex.acquire()

        self.mutex.release()
        self.turnstile.release()

        with self._state_lock:
            self.tracer.record(
                entity_id=reader_id,
                action="ENTER_CS",
                details=f"{reader_id} entered Critical Section. {'(First reader locked rw_mutex)' if first_reader else 'Joined concurrent readers.'}",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"rw_mutex held by Readers group ({self.active_readers} active)"
            )

    def reader_exit(self, reader_id: str, read_val: str):
        self.mutex.acquire()
        with self._state_lock:
            self.active_readers -= 1
            self.total_reads += 1
            self.readers_status[reader_id] = "IDLE"
            last_reader = (self.active_readers == 0)

        if last_reader:
            # Last reader releases resource lock for writers
            self.rw_mutex.release()

        self.mutex.release()

        with self._state_lock:
            self.tracer.record(
                entity_id=reader_id,
                action="EXIT_CS",
                details=f"{reader_id} exited Critical Section after reading '{read_val}'. {'(Last reader released rw_mutex)' if last_reader else ''}",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"rw_mutex {'FREE' if last_reader else 'HELD by remaining readers'}"
            )

    def writer_enter(self, writer_id: str):
        with self._state_lock:
            self.waiting_writers += 1
            self.writers_status[writer_id] = "WAITING"
            self.tracer.record(
                entity_id=writer_id,
                action="REQUEST_WRITE",
                details=f"{writer_id} requesting exclusive write access. Holding turnstile.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description="Writer waiting on rw_mutex"
            )

        # Acquire turnstile, then rw_mutex, then release turnstile
        self.turnstile.acquire()
        self.rw_mutex.acquire()
        self.turnstile.release()

        with self._state_lock:
            self.active_writers = 1
            self.waiting_writers -= 1
            self.writers_status[writer_id] = "WRITING"
            self.tracer.record(
                entity_id=writer_id,
                action="ENTER_CS",
                details=f"{writer_id} acquired exclusive rw_mutex and entered Critical Section.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"rw_mutex LOCKED exclusively by {writer_id}"
            )

    def writer_exit(self, writer_id: str, new_val: str):
        with self._state_lock:
            self.active_writers = 0
            self.total_writes += 1
            self.writers_status[writer_id] = "IDLE"

        self.rw_mutex.release()

        with self._state_lock:
            self.tracer.record(
                entity_id=writer_id,
                action="EXIT_CS",
                details=f"{writer_id} committed modification '{new_val}' and released rw_mutex.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description="rw_mutex released (FREE)"
            )


# ------------------------------------------------------------------------------
# Reader & Writer Thread Behaviors
# ------------------------------------------------------------------------------
def reader_thread(reader_id: str, manager: SemaphoreSyncManager, iterations: int):
    for i in range(iterations):
        time.sleep(random.uniform(0.05, 0.25))
        manager.reader_enter(reader_id)
        
        # Read from shared resource inside Critical Section
        val = manager.db.read()
        time.sleep(random.uniform(0.1, 0.25))  # simulate read work
        
        manager.reader_exit(reader_id, val)


def writer_thread(writer_id: str, manager: SemaphoreSyncManager, iterations: int):
    updates = [
        "Sensor Batch #104 Synchronized",
        "Memory Segment Table Rebalanced",
        "Page Fault Frequency Adjusted",
        "Security Token Ring Refreshed"
    ]
    for i in range(iterations):
        time.sleep(random.uniform(0.1, 0.35))
        manager.writer_enter(writer_id)

        # Write to shared resource inside Critical Section
        new_data = updates[(i + hash(writer_id)) % len(updates)]
        manager.db.write(new_data)
        time.sleep(random.uniform(0.15, 0.3))  # simulate write work

        manager.writer_exit(writer_id, new_data)


# ------------------------------------------------------------------------------
# Main Execution Entry Point
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  Readers-Writers Problem - Semaphore Implementation Starting")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    db = SharedDatabase()

    num_readers = 5
    num_writers = 2
    reader_iters = 3
    writer_iters = 3

    manager = SemaphoreSyncManager(tracer, db, num_readers, num_writers)

    # Launch threads
    threads = []
    for i in range(num_readers):
        r_id = f"R{i+1}"
        t = threading.Thread(target=reader_thread, args=(r_id, manager, reader_iters), name=r_id)
        threads.append(t)

    for j in range(num_writers):
        w_id = f"W{j+1}"
        t = threading.Thread(target=writer_thread, args=(w_id, manager, writer_iters), name=w_id)
        threads.append(t)

    # Shuffle to simulate unpredictable OS scheduler dispatch
    random.shuffle(threads)
    for t in threads:
        t.start()

    # Join threads
    for t in threads:
        t.join()

    print("-" * 70)
    print(f"Simulation completed. Total events: {len(tracer.events)}")
    print(f"Total Reads: {manager.total_reads} | Total Writes: {manager.total_writes}")
    print(f"Max Concurrent Readers: {manager.max_concurrent_readers}")
    print(f"Final Shared Data: {db.data}")
    print("-" * 70)

    # Generate HTML file
    summary_stats = {
        "total_events": len(tracer.events),
        "total_reads": manager.total_reads,
        "total_writes": manager.total_writes,
        "max_concurrent_readers": manager.max_concurrent_readers,
        "policy": "Starvation-Free Turnstile Semaphore"
    }

    output_dir = os.path.join(PROJECT_ROOT, "generated_html")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "readers_writers_semaphore.html")

    html_code = generate_rw_html(
        title="Readers-Writers Problem",
        mechanism_type="Semaphores (Turnstile + Mutex + RW_Mutex)",
        trace_data=tracer.events,
        summary_stats=summary_stats
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"SUCCESS: Generated HTML simulation at:\n  --> {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
