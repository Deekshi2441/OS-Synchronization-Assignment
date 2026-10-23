# Academic References and Citations

The conceptual models, synchronization algorithms, and software abstractions implemented in this repository are based on the following established computer science literature, standards, and references:

---

## 1. Classical Textbooks & Foundations
1. **Silberschatz, A., Galvin, P. B., & Gagne, G.** (2018).  
   *Operating System Concepts* (10th ed.). Hoboken, NJ: John Wiley & Sons.  
   - **Chapter 6:** Synchronization Tools (Semaphores, Monitors, Condition Variables).
   - **Chapter 7:** Synchronization Examples (Classical Problems of Synchronization: Readers-Writers, Dining Philosophers).
   - **Chapter 8:** Deadlocks (Coffman Conditions, Prevention, Avoidance, and Detection).

2. **Tanenbaum, A. S., & Bos, H.** (2015).  
   *Modern Operating Systems* (4th ed.). Boston, MA: Pearson.  
   - Comprehensive discussion of mutual exclusion primitives, Hoare vs. Mesa monitor semantics, and asymmetric dining philosopher solutions.

3. **Downey, A. B.** (2016).  
   *The Little Book of Semaphores* (Version 2.2.1). Green Tea Press.  
   - **Section 4.2:** Readers-Writers problem, reader-preference, writer-preference, and no-starve turnstile patterns.
   - **Section 4.4:** Dining Philosophers problem, footman/room capacity solution, and asymmetric ordering proof.

---

## 2. Foundational Research Papers
4. **Dijkstra, E. W.** (1965).  
   *Cooperating Sequential Processes*. Technological University Eindhoven. Reprinted in F. Genuys (Ed.), *Programming Languages*, Academic Press, 1968, pp. 43–112.  
   - Original formulation of the semaphore abstraction (`P` and `V` operations) and the Dining Philosophers dilemma.

5. **Hoare, C. A. R.** (1974).  
   *Monitors: An Operating System Structuring Concept*. *Communications of the ACM*, 17(10), 549–557.  
   - Formulation of the monitor construct, condition variables, and wait/signal scheduling disciplines.

6. **Courtois, P. J., Heymans, F., & Parnas, D. L.** (1971).  
   *Concurrent Control with "Readers" and "Writers"*. *Communications of the ACM*, 14(10), 667–668.  
   - Canonical solutions for the first and second Readers-Writers problems.

7. **Coffman, E. G., Elphick, M. J., & Shoshani, A.** (1971).  
   *System Deadlocks*. *ACM Computing Surveys*, 3(2), 67–78.  
   - Formulation of the four necessary conditions for deadlock: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.

---

## 3. Technology Documentation & Standards
8. **Python Software Foundation.** (2024).  
   *Python 3.12/3.13/3.14 Documentation: `threading` — Thread-based parallelism*.  
   Available online: `https://docs.python.org/3/library/threading.html`  
   - Specifications for `threading.Semaphore`, `threading.Lock`, and `threading.Condition`.

9. **World Wide Web Consortium (W3C).** (2023).  
   *Scalable Vector Graphics (SVG) 2 Specification*.  
   Available online: `https://www.w3.org/TR/SVG2/`  
   - Interactive DOM and SVG element rendering for circular table geometry.

---

## 4. AI Tool Disclosure
10. **Google DeepMind.** (2024).  
    *Gemini 3.8 Flash (High)* via Antigravity IDE Assistant.  
    - Used for pair-programming, scaffolding data pipelines, generating SVG templates, and formatting reports.
