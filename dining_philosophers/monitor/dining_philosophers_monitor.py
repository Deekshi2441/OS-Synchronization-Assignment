"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 4: Dining Philosophers Problem - 4 Philosophers (Monitor-Based)
================================================================================
Description:
    Demonstrates deadlock-free synchronization for 4 philosophers using
    a Monitor construct with Condition Variables (Signal-and-Continue discipline).
    
    Monitor Design:
        - Philosopher States:
            * THINKING: Philosopher is pondering and does not hold any forks.
            * HUNGRY: Philosopher wants to eat and is waiting for both forks.
            * EATING: Philosopher has acquired both adjacent forks and is eating.
        - Condition Variables:
            * `self_cond[4]`: An array of condition variables (one per philosopher).
              Philosopher i suspends on self_cond[i] if either neighbor is currently eating.
        - Procedures:
            * `pickup(i)`: Atomically attempts to acquire both forks; blocks if unavailable.
            * `putdown(i)`: Atomically releases both forks and tests adjacent neighbors.
            * `test(i)`: Core invariant checker. A philosopher only transitions to
              EATING if:
              (state[i] == HUNGRY and state[left] != EATING and state[right] != EATING)

    Deadlock and Starvation Analysis:
        - Deadlock Prevention: No philosopher can hold one fork and wait for the
          other indefinitely while preventing progress. Both forks are acquired
          simultaneously from the perspective of state transition.
        - Starvation: Tested when neighbors finish eating. In long runs, fair signaling
          or priority queues can prevent infinite bypass.

    Output:
        Executes concurrent threads, logs state transitions and fork allocations,
        and generates an interactive HTML simulation.
================================================================================
"""

import os
import sys
import time
import random
import threading
from typing import List, Dict, Any, Optional

# Ensure common visualizer can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.html_templates import generate_dp_html


PHILOSOPHER_NAMES = ["Aristotle (P0)", "Kant (P1)", "Spinoza (P2)", "Nietzsche (P3)"]
NUM_PHILOSOPHERS = 4


# ------------------------------------------------------------------------------
# Thread-Safe Execution Trace Recorder
# ------------------------------------------------------------------------------
class ExecutionTracer:
    """Thread-safe state recorder capturing event snapshots for visualization."""
    def __init__(self, start_time: float):
        self.start_time = start_time
        self.events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def record(self, philosopher_id: str, action: str, details: str,
               philosophers_state: List[Dict[str, Any]],
               forks_state: List[Optional[int]],
               held_forks: List[int]):
        with self._lock:
            elapsed_ms = int((time.time() - self.start_time) * 1000)
            snapshot = {
                "step": len(self.events),
                "timestamp_ms": elapsed_ms,
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
            f_str = ", ".join([f"F{i}:{('P' + str(o)) if o is not None else 'FREE'}" for i, o in enumerate(forks_state)])
            print(f"[{elapsed_ms:04d}ms] {philosopher_id:<4} | {action:<14} | {details} | [{f_str}]")


# ------------------------------------------------------------------------------
# Dining Philosophers Monitor Implementation
# ------------------------------------------------------------------------------
class DiningPhilosophersMonitor:
    """
    Monitor abstraction for 4 dining philosophers using condition variables.
    Enforces mutual exclusion on state transitions and eliminates circular waiting.
    """
    def __init__(self, tracer: ExecutionTracer):
        self.tracer = tracer
        self.num_philo = NUM_PHILOSOPHERS

        # Monitor synchronization primitives
        self._lock = threading.Lock()
        self.self_cond = [threading.Condition(self._lock) for _ in range(self.num_philo)]

        # Internal Monitor State
        self.state = ["THINKING"] * self.num_philo
        self.fork_owners: List[Optional[int]] = [None] * self.num_philo
        self.philo_forks = [[] for _ in range(self.num_philo)]
        self.meals_eaten = [0] * self.num_philo

        self.max_concurrent_eaters = 0

    def _left_neighbor(self, i: int) -> int:
        return (i + self.num_philo - 1) % self.num_philo

    def _right_neighbor(self, i: int) -> int:
        return (i + 1) % self.num_philo

    def _get_philosophers_snapshot(self) -> List[Dict[str, Any]]:
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
        """
        Check if philosopher i is hungry and neither neighbor is eating.
        If true, grants both forks atomically and signals condition variable.
        """
        left = self._left_neighbor(i)
        right = self._right_neighbor(i)

        if (self.state[i] == "HUNGRY" and
                self.state[left] != "EATING" and
                self.state[right] != "EATING"):
            self.state[i] = "EATING"
            self.meals_eaten[i] += 1

            # Allocate forks (left fork = i, right fork = (i+1)%4)
            left_fork = i
            right_fork = (i + 1) % self.num_philo
            self.fork_owners[left_fork] = i
            self.fork_owners[right_fork] = i
            self.philo_forks[i] = [left_fork, right_fork]

            current_eaters = sum(1 for s in self.state if s == "EATING")
            if current_eaters > self.max_concurrent_eaters:
                self.max_concurrent_eaters = current_eaters

            # Awaken waiting philosopher thread
            self.self_cond[i].notify()

    # --- Monitor Entry Procedure: pickup_forks ---
    def pickup_forks(self, i: int):
        with self._lock:
            self.state[i] = "HUNGRY"
            self.tracer.record(
                philosopher_id=f"P{i}",
                action="HUNGRY",
                details=f"P{i} called pickup_forks(). State = HUNGRY. Checking neighbors (L:P{self._left_neighbor(i)}, R:P{self._right_neighbor(i)}).",
                philosophers_state=self._get_philosophers_snapshot(),
                forks_state=self.fork_owners,
                held_forks=self.philo_forks[i]
            )

            # Test if forks are immediately available
            self._test(i)

            # If not yet eating, suspend on philosopher's private condition variable
            while self.state[i] != "EATING":
                self.tracer.record(
                    philosopher_id=f"P{i}",
                    action="WAITING",
                    details=f"P{i} blocked on condition variable self_cond[{i}]. One or both neighbors currently eating.",
                    philosophers_state=self._get_philosophers_snapshot(),
                    forks_state=self.fork_owners,
                    held_forks=self.philo_forks[i]
                )
                self.self_cond[i].wait()

            # Successfully eating
            left_fork = i
            right_fork = (i + 1) % self.num_philo
            self.tracer.record(
                philosopher_id=f"P{i}",
                action="EATING",
                details=f"P{i} awakened and entered EATING state! Holding F{left_fork} & F{right_fork}. (Meal #{self.meals_eaten[i]}).",
                philosophers_state=self._get_philosophers_snapshot(),
                forks_state=self.fork_owners,
                held_forks=self.philo_forks[i]
            )

    # --- Monitor Exit Procedure: putdown_forks ---
    def putdown_forks(self, i: int):
        with self._lock:
            left_fork = i
            right_fork = (i + 1) % self.num_philo

            self.fork_owners[left_fork] = None
            self.fork_owners[right_fork] = None
            self.philo_forks[i] = []
            self.state[i] = "THINKING"

            self.tracer.record(
                philosopher_id=f"P{i}",
                action="THINKING",
                details=f"P{i} called putdown_forks(). Released F{left_fork} and F{right_fork}. State = THINKING. Testing neighbors.",
                philosophers_state=self._get_philosophers_snapshot(),
                forks_state=self.fork_owners,
                held_forks=self.philo_forks[i]
            )

            # Test left and right neighbors to allow them to eat if waiting
            left = self._left_neighbor(i)
            right = self._right_neighbor(i)
            self._test(left)
            self._test(right)


# ------------------------------------------------------------------------------
# Philosopher Thread Routine
# ------------------------------------------------------------------------------
def philosopher_thread(p_id: int, monitor: DiningPhilosophersMonitor, meals_target: int):
    for _ in range(meals_target):
        # 1. Thinking
        time.sleep(random.uniform(0.08, 0.25))

        # 2. Pickup Forks (Blocks until both forks acquired)
        monitor.pickup_forks(p_id)

        # 3. Eating
        time.sleep(random.uniform(0.15, 0.3))

        # 4. Putdown Forks
        monitor.putdown_forks(p_id)


# ------------------------------------------------------------------------------
# Main Execution Entry Point
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  Dining Philosophers Problem (4 Philosophers) - Monitor Starting")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    monitor = DiningPhilosophersMonitor(tracer)

    meals_per_philosopher = 3
    threads = []

    for i in range(NUM_PHILOSOPHERS):
        t = threading.Thread(
            target=philosopher_thread,
            args=(i, monitor, meals_per_philosopher),
            name=f"Philosopher-{i}"
        )
        threads.append(t)

    random.shuffle(threads)
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    total_meals = sum(monitor.meals_eaten)
    print("-" * 70)
    print(f"Simulation completed. Total events: {len(tracer.events)}")
    print(f"Total Meals Consumed: {total_meals} (Target: {NUM_PHILOSOPHERS * meals_per_philosopher})")
    for i in range(NUM_PHILOSOPHERS):
        print(f"  Philosopher P{i} ({PHILOSOPHER_NAMES[i]}): {monitor.meals_eaten[i]} meals eaten")
    print(f"Max Concurrent Eaters Observed: {monitor.max_concurrent_eaters}")
    print("-" * 70)

    summary_stats = {
        "total_events": len(tracer.events),
        "total_meals_eaten": total_meals,
        "max_concurrent_eaters": f"{monitor.max_concurrent_eaters} (Optimal for N=4 is 2)",
        "deadlock_strategy": "Monitor with Condition Variables (Two-Fork Test)",
        "starvation_freedom": "Neighbor Testing on Release",
        "deadlock_explanation": (
            "A philosopher is only permitted to transition to EATING if both adjacent neighbors "
            "are currently not eating. Forks are acquired as an atomic pair inside the monitor, "
            "thereby eliminating the 'Hold and Wait' condition and preventing deadlock."
        )
    }

    output_dir = os.path.join(PROJECT_ROOT, "generated_html")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dining_philosophers_monitor.html")

    html_code = generate_dp_html(
        title="Dining Philosophers (4 Philosophers)",
        mechanism_type="Monitor with Condition Variables (Atomic Neighbor Test)",
        trace_data=tracer.events,
        summary_stats=summary_stats
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"SUCCESS: Generated HTML simulation at:\n  --> {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
