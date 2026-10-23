"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 2: Readers-Writers Problem (Monitor-Based Implementation)
================================================================================
Description:
    Demonstrates Readers-Writers synchronization implemented via a Monitor
    construct with Condition Variables (Signal and Continue discipline).
    
    Monitor Abstraction:
        The `ReadersWritersMonitor` class encapsulates:
        - Internal State: active_readers, active_writers, waiting_readers, waiting_writers
        - Monitor Lock: An explicit internal lock guaranteeing mutual exclusion
          within monitor entry procedures.
        - Condition Variables:
            * `can_read`: Readers wait when a writer is active or waiting (writer priority).
            * `can_write`: Writers wait when any readers or another writer is active.

    Synchronization Invariants:
        1. Mutual Exclusion inside Monitor: Only one thread executes monitor logic at a time.
        2. Resource Invariant: (active_writers == 0 and active_readers >= 0) OR
                               (active_writers == 1 and active_readers == 0)
        3. Writer Starvation Prevention: New readers queue if a writer is waiting.

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
        self.data: str = "System Configuration v1.0 [Stable]"
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
# Monitor Implementation (Condition Variables)
# ------------------------------------------------------------------------------
class ReadersWritersMonitor:
    """
    Monitor abstraction for Readers-Writers with Writer Preference
    to ensure neither readers nor writers suffer starvation.
    """
    def __init__(self, tracer: ExecutionTracer, db: SharedDatabase,
                 num_readers: int, num_writers: int):
        self.tracer = tracer
        self.db = db
        self.num_readers = num_readers
        self.num_writers = num_writers

        # Monitor synchronization primitives
        self._lock = threading.Lock()
        self.can_read = threading.Condition(self._lock)
        self.can_write = threading.Condition(self._lock)

        # Monitor state variables
        self.active_readers = 0
        self.active_writers = 0
        self.waiting_readers = 0
        self.waiting_writers = 0

        # UI state tracking
        self.readers_status = {f"R{i+1}": "IDLE" for i in range(num_readers)}
        self.writers_status = {f"W{i+1}": "IDLE" for i in range(num_writers)}

        self.max_concurrent_readers = 0
        self.total_reads = 0
        self.total_writes = 0

    def _get_readers_snapshot(self):
        return [{"id": k, "status": v} for k, v in self.readers_status.items()]

    def _get_writers_snapshot(self):
        return [{"id": k, "status": v} for k, v in self.writers_status.items()]

    # --- Monitor Entry Procedure: start_read ---
    def start_read(self, reader_id: str):
        with self._lock:
            self.waiting_readers += 1
            self.readers_status[reader_id] = "WAITING"
            self.tracer.record(
                entity_id=reader_id,
                action="REQUEST_READ",
                details=f"{reader_id} called start_read(). Waiting if active_writers > 0 or waiting_writers > 0.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"Monitor: active_writers={self.active_writers}, waiting_writers={self.waiting_writers}"
            )

            # Wait while a writer is writing OR writers are waiting (prevents writer starvation)
            while self.active_writers > 0 or self.waiting_writers > 0:
                self.can_read.wait()

            self.waiting_readers -= 1
            self.active_readers += 1
            self.readers_status[reader_id] = "READING"
            if self.active_readers > self.max_concurrent_readers:
                self.max_concurrent_readers = self.active_readers

            self.tracer.record(
                entity_id=reader_id,
                action="ENTER_CS",
                details=f"{reader_id} granted read access. Total active readers: {self.active_readers}.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"Monitor: {self.active_readers} readers concurrently in CS"
            )

    # --- Monitor Exit Procedure: end_read ---
    def end_read(self, reader_id: str, read_val: str):
        with self._lock:
            self.active_readers -= 1
            self.total_reads += 1
            self.readers_status[reader_id] = "IDLE"

            # If last reader exiting and writers are waiting, signal one writer
            if self.active_readers == 0 and self.waiting_writers > 0:
                self.can_write.notify()
                signal_msg = "Last reader signaled can_write condition variable."
            elif self.active_readers == 0:
                self.can_read.notify_all()
                signal_msg = "Last reader signaled can_read condition variable."
            else:
                signal_msg = f"{self.active_readers} readers still active."

            self.tracer.record(
                entity_id=reader_id,
                action="EXIT_CS",
                details=f"{reader_id} finished read ('{read_val}'). {signal_msg}",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"Monitor: active_readers={self.active_readers}"
            )

    # --- Monitor Entry Procedure: start_write ---
    def start_write(self, writer_id: str):
        with self._lock:
            self.waiting_writers += 1
            self.writers_status[writer_id] = "WAITING"
            self.tracer.record(
                entity_id=writer_id,
                action="REQUEST_WRITE",
                details=f"{writer_id} called start_write(). Waiting if active_readers > 0 or active_writers > 0.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description=f"Monitor: active_readers={self.active_readers}, active_writers={self.active_writers}"
            )

            # Wait until no active readers and no active writer
            while self.active_readers > 0 or self.active_writers > 0:
                self.can_write.wait()

            self.waiting_writers -= 1
            self.active_writers = 1
            self.writers_status[writer_id] = "WRITING"

            self.tracer.record(
                entity_id=writer_id,
                action="ENTER_CS",
                details=f"{writer_id} granted exclusive write access via monitor.",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description="Monitor: Exclusive Writer lock active"
            )

    # --- Monitor Exit Procedure: end_write ---
    def end_write(self, writer_id: str, new_val: str):
        with self._lock:
            self.active_writers = 0
            self.total_writes += 1
            self.writers_status[writer_id] = "IDLE"

            # If other writers waiting, awaken one writer; otherwise awaken all waiting readers
            if self.waiting_writers > 0:
                self.can_write.notify()
                signal_msg = "Signaled waiting writer (can_write.notify())."
            else:
                self.can_read.notify_all()
                signal_msg = "Signaled all waiting readers (can_read.notify_all())."

            self.tracer.record(
                entity_id=writer_id,
                action="EXIT_CS",
                details=f"{writer_id} completed write '{new_val}'. {signal_msg}",
                active_readers=self.active_readers,
                active_writers=self.active_writers,
                waiting_readers=self.waiting_readers,
                waiting_writers=self.waiting_writers,
                readers_state=self._get_readers_snapshot(),
                writers_state=self._get_writers_snapshot(),
                shared_data=self.db.data,
                shared_revision=self.db.revision,
                sync_description="Monitor: Writer exited, lock free"
            )


# ------------------------------------------------------------------------------
# Thread Functions
# ------------------------------------------------------------------------------
def reader_thread(reader_id: str, monitor: ReadersWritersMonitor, iterations: int):
    for _ in range(iterations):
        time.sleep(random.uniform(0.05, 0.25))
        monitor.start_read(reader_id)

        # Critical Section: Read shared resource
        val = monitor.db.read()
        time.sleep(random.uniform(0.1, 0.25))

        monitor.end_read(reader_id, val)


def writer_thread(writer_id: str, monitor: ReadersWritersMonitor, iterations: int):
    updates = [
        "Thread Pool Resized to 16",
        "TLB Flush Completed",
        "Inode Table Synced to Disk",
        "Crypto Key Derivation Finished"
    ]
    for i in range(iterations):
        time.sleep(random.uniform(0.1, 0.35))
        monitor.start_write(writer_id)

        # Critical Section: Write shared resource
        new_val = updates[(i + hash(writer_id)) % len(updates)]
        monitor.db.write(new_val)
        time.sleep(random.uniform(0.15, 0.3))

        monitor.end_write(writer_id, new_val)


# ------------------------------------------------------------------------------
# Main Execution Entry Point
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  Readers-Writers Problem - Monitor Implementation Starting")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    db = SharedDatabase()

    num_readers = 5
    num_writers = 2
    reader_iters = 3
    writer_iters = 3

    monitor = ReadersWritersMonitor(tracer, db, num_readers, num_writers)

    threads = []
    for i in range(num_readers):
        r_id = f"R{i+1}"
        t = threading.Thread(target=reader_thread, args=(r_id, monitor, reader_iters), name=r_id)
        threads.append(t)

    for j in range(num_writers):
        w_id = f"W{j+1}"
        t = threading.Thread(target=writer_thread, args=(w_id, monitor, writer_iters), name=w_id)
        threads.append(t)

    random.shuffle(threads)
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("-" * 70)
    print(f"Simulation completed. Total events: {len(tracer.events)}")
    print(f"Total Reads: {monitor.total_reads} | Total Writes: {monitor.total_writes}")
    print(f"Max Concurrent Readers: {monitor.max_concurrent_readers}")
    print(f"Final Shared Data: {db.data}")
    print("-" * 70)

    summary_stats = {
        "total_events": len(tracer.events),
        "total_reads": monitor.total_reads,
        "total_writes": monitor.total_writes,
        "max_concurrent_readers": monitor.max_concurrent_readers,
        "policy": "Monitor with Writer Preference Condition Variables"
    }

    output_dir = os.path.join(PROJECT_ROOT, "generated_html")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "readers_writers_monitor.html")

    html_code = generate_rw_html(
        title="Readers-Writers Problem",
        mechanism_type="Monitor with Condition Variables (can_read, can_write)",
        trace_data=tracer.events,
        summary_stats=summary_stats
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"SUCCESS: Generated HTML simulation at:\n  --> {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
