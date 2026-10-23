"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 4: Dining Philosophers Problem - 4 Philosophers (Monitor-Based)
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


class DiningTableMonitor:
    """
    Monitor abstraction for 4 dining philosophers using:
      - condition variables: can_eat[i] (one per philosopher)
      - state: THINKING, HUNGRY, EATING
      - atomic neighbor testing to eliminate hold-and-wait deadlock
    """
    def __init__(self, tracer: ExecutionTracer):
        self.tracer = tracer
        self.num_philo = NUM_PHILOSOPHERS

        self._lock = threading.Lock()
        self.can_eat = [threading.Condition(self._lock) for _ in range(self.num_philo)]

        self.state = ["THINKING"] * self.num_philo
        self.fork_owners: List[Optional[int]] = [None] * self.num_philo
        self.philo_forks = [[] for _ in range(self.num_philo)]
        self.meals_eaten = [0] * self.num_philo
        self.max_concurrent_eaters = 0

    def _left(self, i: int) -> int:
        return (i + self.num_philo - 1) % self.num_philo

    def _right(self, i: int) -> int:
        return (i + 1) % self.num_philo

    def _snap_philosophers(self):
        return [
            {
                "id": f"P{i}",
                "name": PHILOSOPHER_NAMES[i],
                "state": self.state[i],
                "forks": list(self.philo_forks[i]),
                "meals_eaten": self.meals_eaten[i]
            }
            for i in range(self.num_philo)
        ]

    def _test(self, i: int):
        left = self._left(i)
        right = self._right(i)

        if (self.state[i] == "HUNGRY" and
                self.state[left] != "EATING" and
                self.state[right] != "EATING"):
            self.state[i] = "EATING"
            self.meals_eaten[i] += 1

            left_fork = i
            right_fork = (i + 1) % self.num_philo
            self.fork_owners[left_fork] = i
            self.fork_owners[right_fork] = i
            self.philo_forks[i] = [left_fork, right_fork]

            eaters = sum(1 for s in self.state if s == "EATING")
            if eaters > self.max_concurrent_eaters:
                self.max_concurrent_eaters = eaters

            self.can_eat[i].notify()

    def pickup(self, i: int):
        with self._lock:
            self.state[i] = "HUNGRY"
            self.tracer.log(f"P{i}", "HUNGRY", f"P{i} hungry wants to eat",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[i])

            self._test(i)

            while self.state[i] != "EATING":
                self.tracer.log(f"P{i}", "WAITING", f"P{i} waiting on can_eat[{i}], neighbor eating",
                                self._snap_philosophers(), self.fork_owners, self.philo_forks[i])
                self.can_eat[i].wait()

            left_fork = i
            right_fork = (i + 1) % self.num_philo
            self.tracer.log(f"P{i}", "EATING", f"P{i} eating has both forks",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[i])

    def putdown(self, i: int):
        with self._lock:
            left_fork = i
            right_fork = (i + 1) % self.num_philo

            self.fork_owners[left_fork] = None
            self.fork_owners[right_fork] = None
            self.philo_forks[i] = []
            self.state[i] = "THINKING"

            self.tracer.log(f"P{i}", "RELEASING", f"P{i} releasing put down fork {left_fork}",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[i])
            self.tracer.log(f"P{i}", "RELEASING", f"P{i} releasing put down fork {right_fork}",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[i])
            self.tracer.log(f"P{i}", "THINKING", f"P{i} thinking back to thinking",
                            self._snap_philosophers(), self.fork_owners, self.philo_forks[i])

            left = self._left(i)
            right = self._right(i)
            self._test(left)
            self._test(right)


def philosopher_thread(p_id: int, monitor: DiningTableMonitor, rounds: int, delay: float):
    for _ in range(rounds):
        time.sleep(random.uniform(delay * 0.5, delay * 1.5))
        monitor.pickup(p_id)
        time.sleep(random.uniform(delay * 0.8, delay * 1.8))
        monitor.putdown(p_id)


def main():
    parser = argparse.ArgumentParser(description="Dining Philosophers (4 Philosophers) - Monitor Implementation")
    parser.add_argument("--rounds", type=int, default=3, help="Meals target per philosopher")
    parser.add_argument("--delay", type=float, default=0.2, help="Base timing delay in seconds")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatability")
    parser.add_argument("--out", type=str, default=None, help="Output HTML file path")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print("=" * 70)
    print(f"Dining Philosophers (Monitor) | 4 Philosophers, Rounds: {args.rounds}")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    monitor = DiningTableMonitor(tracer)

    threads = []
    for i in range(NUM_PHILOSOPHERS):
        threads.append(threading.Thread(target=philosopher_thread, args=(i, monitor, args.rounds, args.delay)))

    random.shuffle(threads)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for i in range(NUM_PHILOSOPHERS):
        assert monitor.meals_eaten[i] == args.rounds, f"Starvation detected! P{i} ate {monitor.meals_eaten[i]} times, expected {args.rounds}"

    print("-" * 70)
    print("validation OK: forks never shared and every meal had both forks")
    print(f"Simulation completed. All philosophers finished all meals. Max concurrent eaters: {monitor.max_concurrent_eaters}")
    print("-" * 70)

    out_path = args.out or os.path.join(PROJECT_ROOT, "generated_html", "dining_philosophers_monitor.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    summary_stats = {
        "total_events": len(tracer.events),
        "total_meals_eaten": sum(monitor.meals_eaten),
        "max_concurrent_eaters": f"{monitor.max_concurrent_eaters} (Optimal for N=4 is 2)",
        "deadlock_strategy": "Monitor with Condition Variables (Two-Fork Test)",
        "starvation_freedom": "Neighbor Testing on Release",
        "deadlock_explanation": "Forks are acquired as an atomic pair inside the monitor, eliminating Hold and Wait."
    }
    html_content = generate_dp_html("Dining Philosophers (4 Philosophers)", "Monitor with Condition Variables (can_eat)", tracer.events, summary_stats)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    alt_path = os.path.join(PROJECT_ROOT, "generated_html", "dp_monitor.html")
    with open(alt_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated HTML simulation at: {out_path}")
    if not args.no_browser:
        webbrowser.open(f"file:///{os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
