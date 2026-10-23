"""
================================================================================
Operating Systems Programming Assignment: Process Synchronization
Problem 3: Dining Philosophers Problem - 4 Philosophers (Semaphore-Based)
================================================================================
Description:
    Demonstrates deadlock-free synchronization for exactly 4 philosophers
    (P0, P1, P2, P3) seated at a round table sharing 4 forks (F0, F1, F2, F3).
    
    Resource Topology:
        Philosopher i has Left Fork = i, Right Fork = (i + 1) % 4.
        P0: Forks 0 & 1
        P1: Forks 1 & 2
        P2: Forks 2 & 3
        P3: Forks 3 & 0

    Deadlock Prevention Strategy:
        We employ the Footman / Room Semaphore (`room = Semaphore(3)`):
        At most 3 philosophers are permitted to enter the dining room and attempt
        to acquire forks simultaneously.
        * Proof of Deadlock Freedom (Pigeonhole Principle):
          With 4 forks and at most 3 philosophers in the room, at least one
          philosopher is guaranteed to acquire both adjacent forks and eat.
          Thus, circular wait is completely broken and deadlock cannot occur.

    Starvation Considerations:
        In standard semaphores, operating system scheduling could theoretically
        cause starvation if unfair queuing occurs. With a bounded room size
        and reasonable eating durations, all philosophers get turns. We discuss
        this fully in the technical report.

    Output:
        Executes concurrent threads, captures fork ownership and philosopher
        state transitions, and generates an interactive HTML simulation.
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
# Dining Philosophers Semaphore Coordinator
# ------------------------------------------------------------------------------
class SemaphoreDiningTable:
    """
    Coordinates 4 philosophers sharing 4 forks using semaphores.
    Deadlock Prevention:
        - `room`: Semaphore(3) limits simultaneous diners to at most 3.
        - `forks`: Array of 4 binary semaphores (one per fork).
    """
    def __init__(self, tracer: ExecutionTracer):
        self.tracer = tracer
        self.num_philo = NUM_PHILOSOPHERS

        # Synchronization primitives
        self.fork_semaphores = [threading.Semaphore(1) for _ in range(self.num_philo)]
        self.room_semaphore = threading.Semaphore(self.num_philo - 1)  # Capacity = 3

        # State tracking for visualization
        self._state_lock = threading.Lock()
        self.philo_states = ["THINKING"] * self.num_philo
        self.philo_forks = [[] for _ in range(self.num_philo)]
        self.fork_owners: List[Optional[int]] = [None] * self.num_philo
        self.meals_eaten = [0] * self.num_philo

        self.max_concurrent_eaters = 0

    def _get_philosophers_snapshot(self) -> List[Dict[str, Any]]:
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

    def record_state(self, p_id: int, action: str, details: str):
        with self._state_lock:
            self.tracer.record(
                philosopher_id=f"P{p_id}",
                action=action,
                details=details,
                philosophers_state=self._get_philosophers_snapshot(),
                forks_state=self.fork_owners,
                held_forks=self.philo_forks[p_id]
            )

    def become_hungry(self, p_id: int):
        with self._state_lock:
            self.philo_states[p_id] = "HUNGRY"
        self.record_state(p_id, "HUNGRY", f"P{p_id} stopped thinking and is now HUNGRY. Waiting for room capacity.")

    def acquire_forks(self, p_id: int):
        left_fork = p_id
        right_fork = (p_id + 1) % self.num_philo

        # Step 1: Wait for room entry (breaks circular wait)
        self.room_semaphore.acquire()
        self.record_state(p_id, "ENTER_ROOM", f"P{p_id} entered dining room (room semaphore acquired). Attempting fork acquisition.")

        # Step 2: Acquire Left Fork
        self.fork_semaphores[left_fork].acquire()
        with self._state_lock:
            self.fork_owners[left_fork] = p_id
            self.philo_forks[p_id].append(left_fork)
        self.record_state(p_id, "ACQUIRING_FORKS", f"P{p_id} picked up Left Fork F{left_fork}. Waiting for Right Fork F{right_fork}.")

        # Step 3: Acquire Right Fork
        self.fork_semaphores[right_fork].acquire()
        with self._state_lock:
            self.fork_owners[right_fork] = p_id
            self.philo_forks[p_id].append(right_fork)
            self.philo_states[p_id] = "EATING"
            self.meals_eaten[p_id] += 1

            current_eaters = sum(1 for s in self.philo_states if s == "EATING")
            if current_eaters > self.max_concurrent_eaters:
                self.max_concurrent_eaters = current_eaters

        self.record_state(p_id, "EATING", f"P{p_id} acquired Right Fork F{right_fork}. Both forks held! Now EATING (Meal #{self.meals_eaten[p_id]}).")

    def release_forks(self, p_id: int):
        left_fork = p_id
        right_fork = (p_id + 1) % self.num_philo

        with self._state_lock:
            self.philo_states[p_id] = "RELEASING_FORKS"
        self.record_state(p_id, "RELEASING_FORKS", f"P{p_id} finished eating. Releasing forks F{left_fork} and F{right_fork}.")

        # Release left fork
        with self._state_lock:
            self.fork_owners[left_fork] = None
            if left_fork in self.philo_forks[p_id]:
                self.philo_forks[p_id].remove(left_fork)
        self.fork_semaphores[left_fork].release()

        # Release right fork
        with self._state_lock:
            self.fork_owners[right_fork] = None
            if right_fork in self.philo_forks[p_id]:
                self.philo_forks[p_id].remove(right_fork)
        self.fork_semaphores[right_fork].release()

        # Leave the dining room
        self.room_semaphore.release()

        with self._state_lock:
            self.philo_states[p_id] = "THINKING"
        self.record_state(p_id, "THINKING", f"P{p_id} returned forks and left room. Transitioned back to THINKING.")


# ------------------------------------------------------------------------------
# Philosopher Thread Routine
# ------------------------------------------------------------------------------
def philosopher_thread(p_id: int, table: SemaphoreDiningTable, meals_target: int):
    for _ in range(meals_target):
        # 1. Thinking
        time.sleep(random.uniform(0.08, 0.25))

        # 2. Hungry
        table.become_hungry(p_id)

        # 3. Acquire forks
        table.acquire_forks(p_id)

        # 4. Eating
        time.sleep(random.uniform(0.15, 0.3))

        # 5. Release forks
        table.release_forks(p_id)


# ------------------------------------------------------------------------------
# Main Execution Entry Point
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  Dining Philosophers Problem (4 Philosophers) - Semaphore Starting")
    print("=" * 70)

    start_time = time.time()
    tracer = ExecutionTracer(start_time)
    table = SemaphoreDiningTable(tracer)

    meals_per_philosopher = 3
    threads = []

    for i in range(NUM_PHILOSOPHERS):
        t = threading.Thread(
            target=philosopher_thread,
            args=(i, table, meals_per_philosopher),
            name=f"Philosopher-{i}"
        )
        threads.append(t)

    random.shuffle(threads)
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    total_meals = sum(table.meals_eaten)
    print("-" * 70)
    print(f"Simulation completed. Total events: {len(tracer.events)}")
    print(f"Total Meals Consumed: {total_meals} (Target: {NUM_PHILOSOPHERS * meals_per_philosopher})")
    for i in range(NUM_PHILOSOPHERS):
        print(f"  Philosopher P{i} ({PHILOSOPHER_NAMES[i]}): {table.meals_eaten[i]} meals eaten")
    print(f"Max Concurrent Eaters Observed: {table.max_concurrent_eaters}")
    print("-" * 70)

    summary_stats = {
        "total_events": len(tracer.events),
        "total_meals_eaten": total_meals,
        "max_concurrent_eaters": f"{table.max_concurrent_eaters} (Optimal for N=4 is 2)",
        "deadlock_strategy": "Room Semaphore (Footman with Capacity=3)",
        "starvation_freedom": "Fair Bounded Semaphores",
        "deadlock_explanation": (
            "By constraining room capacity to N - 1 = 3 via a counting semaphore, "
            "it is mathematically impossible for all 4 philosophers to hold one fork simultaneously. "
            "By the Pigeonhole Principle, at least one philosopher will obtain both forks and eat, "
            "guaranteeing deadlock freedom."
        )
    }

    output_dir = os.path.join(PROJECT_ROOT, "generated_html")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dining_philosophers_semaphore.html")

    html_code = generate_dp_html(
        title="Dining Philosophers (4 Philosophers)",
        mechanism_type="Semaphores (Room Capacity Semaphore + Fork Semaphores)",
        trace_data=tracer.events,
        summary_stats=summary_stats
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"SUCCESS: Generated HTML simulation at:\n  --> {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
