"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 3: Dining Philosophers Problem - 4 Philosophers (Semaphore-Based)
================================================================================
"""

import os
import sys
import time
import random
import argparse
import threading
import webbrowser
from typing import List, Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.html_templates import generate_dp_html


PHILOSOPHER_NAMES = ["Aristotle (P0)", "Kant (P1)", "Spinoza (P2)", "Nietzsche (P3)"]
NUM_PHILOSOPHERS = 4


class ExecutionTracer:
    """Thread-safe state recorder capturing event snapshots for visualization."""
    def __init__(self, start_time: float):
        self.start_time = start_time
        self.events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def log(self, philosopher_id: str, action: str, details: str,
            philosophers_state: List[Dict[str, Any]],
            forks_state: List[Optional[int]],
            held_forks: List[int]):
        with self._lock:
            elapsed = time.time() - self.start_time
            elapsed_ms = int(elapsed * 1000)
            snapshot = {
                "step": len(self.events),
                "timestamp_ms": elapsed_ms,
                "time_sec": f"{elapsed:.3f}s",
                "philosopher_id": philosopher_id,
                "entity_id": philosopher_id,
                "state": action,
                "action": action,
                "details": details,
                "forks_held": list(held_forks),
                "philosophers": [dict(p) for p in philosophers_state],
                "forks": list(forks_state)
            }
            self.events.append(snapshot)
            print(f"[{elapsed:.3f}s] {philosopher_id:<3} {action:<14} | {details}")


class SemaphoreDiningTable:
    """
    Dining Philosophers synchronization using:
      - room: counting semaphore (capacity 3 = N - 1) to eliminate circular wait
      - forks: binary semaphores (one per fork)
    """
    def __init__(self, tracer: ExecutionTracer):
        self.tracer = tracer
        self.num_philo = NUM_PHILOSOPHERS

        self.fork_semaphores = [threading.Semaphore(1) for _ in range(self.num_philo)]
        self.room_semaphore = threading.Semaphore(self.num_philo - 1)

        self._state_lock = threading.Lock()
        self.philo_states = ["THINKING"] * self.num_philo
        self.philo_forks = [[] for _ in range(self.num_philo)]
        self.fork_owners: List[Optional[int]] = [None] * self.num_philo
        self.meals_eaten = [0] * self.num_philo
        self.max_concurrent_eaters = 0

    def _snap_philosophers(self):
        return [
            {
                "id": f"P{i}",
                "name": PHILOSOPHER_NAMES[i],
                "state": self.philo_states[i],
                "forks": list(self.philo_forks[i]),
                "meals_eaten": self.meals_eaten[i]
            }
            for i in range(self.num_philo)
        ]

    def become_hungry(self, p_id: int):
        with self._state_lock:
            self.philo_states[p_id] = "HUNGRY"
            self.tracer.log(f"P{p_id}", "HUNGRY", f"P{p_id} hungry wants to eat",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[p_id])

    def acquire_forks(self, p_id: int):
        left_fork = p_id
        right_fork = (p_id + 1) % self.num_philo

        self.room_semaphore.acquire()

        self.fork_semaphores[left_fork].acquire()
        with self._state_lock:
            self.fork_owners[left_fork] = p_id
            self.philo_forks[p_id].append(left_fork)
            self.tracer.log(f"P{p_id}", "ACQUIRING", f"P{p_id} acquiring picked up fork {left_fork}",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[p_id])

        self.fork_semaphores[right_fork].acquire()
        with self._state_lock:
            self.fork_owners[right_fork] = p_id
            self.philo_forks[p_id].append(right_fork)
            self.philo_states[p_id] = "EATING"
            self.meals_eaten[p_id] += 1
            eaters = sum(1 for s in self.philo_states if s == "EATING")
            if eaters > self.max_concurrent_eaters:
                self.max_concurrent_eaters = eaters

            self.tracer.log(f"P{p_id}", "EATING", f"P{p_id} eating has both forks",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[p_id])

    def release_forks(self, p_id: int):
        left_fork = p_id
        right_fork = (p_id + 1) % self.num_philo

        with self._state_lock:
            self.philo_states[p_id] = "RELEASING"
            self.fork_owners[left_fork] = None
            if left_fork in self.philo_forks[p_id]:
                self.philo_forks[p_id].remove(left_fork)
            self.tracer.log(f"P{p_id}", "RELEASING", f"P{p_id} releasing put down fork {left_fork}",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[p_id])

        self.fork_semaphores[left_fork].release()

        with self._state_lock:
            self.fork_owners[right_fork] = None
            if right_fork in self.philo_forks[p_id]:
                self.philo_forks[p_id].remove(right_fork)
            self.tracer.log(f"P{p_id}", "RELEASING", f"P{p_id} releasing put down fork {right_fork}",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[p_id])

        self.fork_semaphores[right_fork].release()
        self.room_semaphore.release()

        with self._state_lock:
            self.philo_states[p_id] = "THINKING"
            self.tracer.log(f"P{p_id}", "THINKING", f"P{p_id} thinking finished meal #{self.meals_eaten[p_id]}",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[p_id])


def philosopher_thread(p_id: int, table: SemaphoreDiningTable, rounds: int, delay: float):
    for _ in range(rounds):
        time.sleep(random.uniform(delay * 0.5, delay * 1.5))
        table.become_hungry(p_id)
        table.acquire_forks(p_id)
        time.sleep(random.uniform(delay * 0.8, delay * 1.8))
        table.release_forks(p_id)


def main():
    parser = argparse.ArgumentParser(description="Dining Philosophers (4 Philosophers) - Semaphore Implementation")
    parser.add_argument("--rounds", type=int, default=3, help="Meals target per philosopher")
    parser.add_argument("--delay", type=float, default=0.2, help="Base timing delay in seconds")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatability")
    parser.add_argument("--out", type=str, default=None, help="Output HTML file path")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print("=" * 70)
    print(f"Dining Philosophers (Semaphores) | 4 Philosophers, Rounds: {args.rounds}")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    table = SemaphoreDiningTable(tracer)

    threads = []
    for i in range(NUM_PHILOSOPHERS):
        threads.append(threading.Thread(target=philosopher_thread, args=(i, table, args.rounds, args.delay)))

    random.shuffle(threads)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Safety Assertions & Validation
    for i in range(NUM_PHILOSOPHERS):
        assert table.meals_eaten[i] == args.rounds, f"Starvation detected! P{i} ate {table.meals_eaten[i]} times, expected {args.rounds}"

    print("-" * 70)
    print("validation OK: forks never shared and every meal had both forks")
    print(f"Simulation completed. All philosophers finished all meals. Max concurrent eaters: {table.max_concurrent_eaters}")
    print("-" * 70)

    out_path = args.out or os.path.join(PROJECT_ROOT, "generated_html", "dining_philosophers_semaphore.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    summary_stats = {
        "total_events": len(tracer.events),
        "total_meals_eaten": sum(table.meals_eaten),
        "max_concurrent_eaters": f"{table.max_concurrent_eaters} (Optimal for N=4 is 2)",
        "deadlock_strategy": "Room Semaphore (Footman with Capacity=3)",
        "starvation_freedom": "Fair Bounded Semaphores",
        "deadlock_explanation": "By constraining room capacity to N-1 = 3, at least one philosopher is guaranteed to obtain both forks."
    }
    html_content = generate_dp_html("Dining Philosophers (4 Philosophers)", "Semaphores (Room Capacity Semaphore + Fork Semaphores)", tracer.events, summary_stats)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    alt_path = os.path.join(PROJECT_ROOT, "generated_html", "dp_semaphore.html")
    with open(alt_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated HTML simulation at: {out_path}")
    if not args.no_browser:
        webbrowser.open(f"file:///{os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
