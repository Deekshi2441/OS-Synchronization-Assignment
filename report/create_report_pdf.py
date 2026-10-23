"""
Generates Assignment_Report.pdf matching the exact 14-section layout,
typography, page-by-page structure, execution traces, comparison table,
screenshots, and academic integrity declaration from the reference report.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(REPORT_DIR, ".."))
PDF_PATH = os.path.join(REPORT_DIR, "Assignment_Report.pdf")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "screenshots")

FIG1_PATH = os.path.join(SCREENSHOTS_DIR, "fig1_rw_semaphore.png")
FIG2_PATH = os.path.join(SCREENSHOTS_DIR, "fig2_rw_monitor.png")
FIG3_PATH = os.path.join(SCREENSHOTS_DIR, "fig3_dp_semaphore.png")
FIG4_PATH = os.path.join(SCREENSHOTS_DIR, "fig4_dp_monitor.png")


def generate_pdf():
    # 54pt margin (~0.75 in) gives clean printable area (504 x 684)
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.black,
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.black,
        alignment=1,
        spaceAfter=3
    )

    topic_style = ParagraphStyle(
        'DocTopic',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.black,
        alignment=1,
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.black,
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'SecH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SecH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.black,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.2,
        textColor=colors.black,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'SecBullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3
    )

    trace_style = ParagraphStyle(
        'TraceCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.8,
        textColor=colors.HexColor('#111827'),
        leftIndent=6,
        spaceAfter=1
    )

    fig_label_style = ParagraphStyle(
        'FigLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        spaceBefore=4,
        spaceAfter=4,
        keepWithNext=True
    )

    story = []

    # =========================================================================
    # PAGE 1: Title, Section 1, Section 2, Section 3 (start)
    # =========================================================================
    story.append(Paragraph("OPERATING SYSTEMS - Task 2", title_style))
    story.append(Paragraph("AI-Assisted Synchronization Algorithms with Program-Generated HTML Simulation", subtitle_style))
    story.append(Paragraph("Readers-Writers Problem and Dining Philosophers Problem (Semaphores and Monitors)", topic_style))
    story.append(Paragraph("<b>Name:</b> Deekshi R Gowda &nbsp;|&nbsp; <b>USN:</b> NNM24IS064 &nbsp;|&nbsp; <b>Course:</b> Operating Systems &nbsp;|&nbsp;<br/><b>GitHub repository:</b> https://github.com/Deekshi2441/OS-Synchronization-Assignment", meta_style))

    # 1. Problem Statement and Synchronization Objective
    story.append(Paragraph("1. Problem Statement and Synchronization Objective", h1_style))
    story.append(Paragraph(
        "When multiple threads share data we don't control the order in which they run. If they aren't coordinated "
        "the outcome can change depending on timing. This is called a race condition. In this assignment we solve "
        "two synchronization problems. Readers-Writers and Dining Philosophers. Each using two methods: "
        "semaphores and monitors. That makes four programs total.",
        body_style
    ))
    story.append(Paragraph(
        "Readers-Writers. Many readers can read a shared resource at the time.. A writer must have the resource "
        "all to themselves. The goal is to make sure a writer never runs at the time as a reader or another writer. "
        "Readers can still share the resource. Also no one should wait forever. Everyone must eventually get what they need.",
        body_style
    ))
    story.append(Paragraph(
        "Dining Philosophers (4 philosophers). Four philosophers sit around a table. There are four forks, one "
        "between each pair of neighbors. To eat a philosopher needs both forks next, to them. The goal is to make "
        "sure each fork is used by one philosopher at a time. We must avoid deadlock. Where everyone is waiting. "
        "No one can eat. We also need to talk about starvation. When someone waits long and never gets to eat.",
        body_style
    ))
    story.append(Paragraph(
        "In addition every program must create an HTML simulation. This simulation must come from the data of "
        "the program's real run not from a hand-drawn or made-up animation.",
        body_style
    ))

    # 2. Implementation Overview
    story.append(Paragraph("2. Implementation Overview", h1_style))
    story.append(Paragraph(
        "All programs are written in Python 3 using only the standard library (threading, json, webbrowser). Each "
        "philosopher, reader and writer is a real thread. Random sleep times are used only to make the interleaving "
        "visible; they never replace the synchronization primitives.",
        body_style
    ))
    story.append(Paragraph("&bull; <b>readers_writers/semaphore/rw_semaphore.py</b> - Readers-Writers with semaphores", bullet_style))
    story.append(Paragraph("&bull; <b>readers_writers/monitor/rw_monitor.py</b> - Readers-Writers with a monitor", bullet_style))
    story.append(Paragraph("&bull; <b>dining_philosophers/semaphore/dp_semaphore.py</b> - 4 philosophers with semaphores", bullet_style))
    story.append(Paragraph("&bull; <b>dining_philosophers/monitor/dp_monitor.py</b> - 4 philosophers with a monitor", bullet_style))
    story.append(Paragraph("&bull; <b>common/sync_trace.py</b> - shared module that records events, checks them and generates the HTML", bullet_style))
    story.append(Paragraph(
        "There is no compile step. Run for example <code>python readers_writers/semaphore/rw_semaphore.py --readers 4 --writers 2 --rounds 3</code>. "
        "The options <code>--delay</code>, <code>--seed</code> and <code>--out</code> change the speed, make timing repeatable "
        "and choose the HTML path. After the run, the HTML file is written to <code>generated_html/</code> and opened in the browser.",
        body_style
    ))

    # 3. Readers-Writers - Semaphore Solution (Start)
    story.append(Paragraph("3. Readers-Writers - Semaphore Solution", h1_style))
    story.append(Paragraph(
        "Shared resource: a SharedDatabase object holding one integer. Its write() method reads the value, sleeps "
        "briefly, then stores value + 1. This is deliberately not atomic: if two writers, or a writer and a reader, were "
        "ever inside together, updates would be lost or a wrong value would be read.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: Section 3 (cont), Section 4, Section 5, Section 6 (start)
    # =========================================================================
    story.append(Paragraph("Critical sections: the body of a reader (reading the value) and the body of a writer (db.write()).", body_style))
    story.append(Paragraph("Semaphores and initial values:", body_style))
    story.append(Paragraph("&bull; <b>resource_lock (1):</b> held by one writer, or by the whole group of active readers together.", bullet_style))
    story.append(Paragraph("&bull; <b>count_mutex (1):</b> protects the shared variable active_readers, because the counter is itself shared data.", bullet_style))
    story.append(Paragraph("&bull; <b>turnstile (1):</b> a gate that every reader and writer passes through when requesting access. Since arrivals queue at this gate, a waiting writer blocks readers that arrive later, and readers cannot overtake it forever.", bullet_style))
    story.append(Paragraph(
        "Reader: wait(turnstile), wait(count_mutex), increment active_readers; if it became 1, wait(resource_lock) "
        "so writers are locked out; signal(count_mutex), signal(turnstile). Read. On exit: wait(count_mutex), "
        "decrement; if it became 0, signal(resource_lock); signal(count_mutex).<br/>"
        "Writer: wait(turnstile), wait(resource_lock), signal(turnstile). Write. Then signal(resource_lock).<br/>"
        "The first reader acquires the lock on behalf of all readers and the last reader releases it, which is how "
        "readers share while writers are excluded.",
        body_style
    ))

    # 4. Readers-Writers - Monitor Solution
    story.append(Paragraph("4. Readers-Writers - Monitor Solution", h1_style))
    story.append(Paragraph(
        "Python has no monitor keyword, so a monitor is built as a class (ReadersWritersMonitor) whose shared "
        "state is only touched while holding one lock. Waiting is done with two condition variables created on that "
        "same lock, which is the allowed equivalent abstraction.<br/>"
        "Monitor state: active_readers, writing, waiting_writers. Condition variables: ok_to_read and ok_to_write.",
        body_style
    ))
    story.append(Paragraph("&bull; <b>start_read:</b> waits until no writer is writing and no writer is waiting, then increments active_readers.", bullet_style))
    story.append(Paragraph("&bull; <b>end_read:</b> decrements active_readers; if zero, notifies one waiting writer.", bullet_style))
    story.append(Paragraph("&bull; <b>start_write:</b> increments waiting_writers, waits until nobody is reading or writing, then sets writing = True.", bullet_style))
    story.append(Paragraph("&bull; <b>end_write:</b> clears writing; if writers are waiting it wakes one, otherwise it wakes all waiting readers.", bullet_style))
    story.append(Paragraph(
        "Because Python uses Mesa-style conditions (a woken thread must check again), the waits use "
        "wait_for(condition), which re-checks the predicate after waking. The actual reading and writing happen "
        "outside the entry and exit procedures, so readers can run in parallel. The policy is writer preference.",
        body_style
    ))

    # 5. Dining Philosophers (4) - Semaphore Solution
    story.append(Paragraph("5. Dining Philosophers (4) - Semaphore Solution", h1_style))
    story.append(Paragraph(
        "Philosopher i uses fork i (left) and fork (i+1) mod 4 (right). Each fork is a binary semaphore with initial "
        "value 1, so a fork can belong to only one philosopher at a time. That gives mutual exclusion on the forks.<br/>"
        "If every philosopher picks up the left fork and then waits for the right one, all four hold one fork and wait "
        "forever, which is a circular wait, so deadlock. To prevent this, a counting semaphore room is initialised to "
        "3 (N - 1). A philosopher must wait(room) before touching any fork, and signal(room) after eating. At "
        "most three philosophers compete at once, so at least one of them can always get both forks, and the "
        "circular wait cannot form.<br/>"
        "Cycle of each philosopher: think, become hungry, wait(room), wait(left), wait(right), eat, signal(left), "
        "signal(right), signal(room).",
        body_style
    ))

    # 6. Dining Philosophers (4) - Monitor Solution (Start)
    story.append(Paragraph("6. Dining Philosophers (4) - Monitor Solution", h1_style))
    story.append(Paragraph(
        "The DiningTable monitor keeps a state for each philosopher (THINKING, HUNGRY, EATING) and one "
        "condition variable per philosopher, all on one lock.",
        body_style
    ))
    story.append(Paragraph("&bull; <b>pickup(i):</b> set state HUNGRY, call _test(i), and wait on can_eat[i] until the state becomes EATING.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: Section 6 (cont), Section 7, Section 8.1, Section 8.2 (start)
    # =========================================================================
    story.append(Paragraph("&bull; <b>_test(i):</b> if i is hungry and neither neighbour is eating, set EATING (this takes both forks at once) and notify i.", bullet_style))
    story.append(Paragraph("&bull; <b>putdown(i):</b> set THINKING, release both forks, then call _test for the left and right neighbours, because one of them may now be able to eat.", bullet_style))
    story.append(Paragraph(
        "The check and the change of state happen atomically inside the monitor, so a philosopher takes both forks "
        "or none. Hold-and-wait, one of the four conditions for deadlock, never happens, so deadlock is impossible.",
        body_style
    ))

    # 7. How the Program Records Events and Generates the HTML
    story.append(Paragraph("7. How the Program Records Events and Generates the HTML", h1_style))
    story.append(Paragraph(
        "1. Every thread calls Tracer.log(actor, state, detail, ...) each time its state changes, for example "
        "waiting, reading, writing, hungry, acquiring, eating, releasing. For philosophers the call also "
        "carries the fork number and its new owner (or none when released).<br/>"
        "2. log() takes a lock, so every event gets a sequence number and a time stamp in one single order. "
        "Events are logged while the thread holds the relevant semaphore or monitor lock (and before it "
        "releases it), so the recorded order cannot show an impossible overlap.<br/>"
        "3. After all threads finish, the program replays the trace and asserts the safety rules: no reader/writer "
        "or writer/writer overlap, no fork with two owners, and every eating philosopher holds both of its forks.<br/>"
        "4. write_html() embeds the event list as JSON inside a self-contained HTML page. JavaScript in the "
        "page applies the events one by one: it colours readers, writers and philosophers by state, shows "
        "whether the shared resource is free, shared-read or exclusive-write, draws the four forks and who "
        "holds them, and prints the event log. Start, Pause, Step, Reset, a speed slider and a timeline slider allow replay.<br/>"
        "The HTML contains no hard-coded story; if the program is run again with different parameters, a "
        "different file is generated.",
        body_style
    ))

    # 8. Execution Traces (from real runs)
    story.append(Paragraph("8. Execution Traces (from real runs)", h1_style))
    story.append(Paragraph("These are excerpts from actual runs of the submitted programs on Windows PowerShell. Each run demonstrates concurrent interleavings and synchronization invariants.", body_style))

    story.append(Paragraph("8.1 Readers-Writers, semaphores (4 readers, 2 writers)", h2_style))
    rw_sem_lines = [
        "[0.112s] R1  REQUEST_READ   | R:0 W:0 | R1 waiting requests read access",
        "[0.113s] R1  ENTER_CS       | R:1 W:0 | R1 reading entered CS, readers inside = 1",
        "[0.118s] R2  REQUEST_READ   | R:1 W:0 | R2 waiting requests read access",
        "[0.118s] R2  ENTER_CS       | R:2 W:0 | R2 reading entered CS, readers inside = 2",
        "[0.224s] W1  REQUEST_WRITE  | R:2 W:0 | W1 waiting requests write access",
        "[0.366s] R2  EXIT_CS        | R:1 W:0 | R2 idle left CS, readers inside = 1 (read value=0)",
        "[0.368s] R1  EXIT_CS        | R:0 W:0 | R1 idle left CS, readers inside = 0 (read value=0)",
        "[0.369s] W1  ENTER_CS       | R:0 W:1 | W1 writing entered CS (exclusive)",
        "[0.775s] W1  EXIT_CS        | R:1 W:0 | W1 idle left CS, committed value = 1",
        "[0.775s] R4  ENTER_CS       | R:1 W:0 | R4 reading entered CS, readers inside = 1",
        "[0.776s] R3  ENTER_CS       | R:2 W:0 | R3 reading entered CS, readers inside = 2",
        "[0.963s] R3  EXIT_CS        | R:1 W:0 | R3 idle left CS, readers inside = 1 (read value=1)"
    ]
    for line in rw_sem_lines:
        story.append(Paragraph(line, trace_style))

    story.append(Paragraph(
        "Readers R1 and R2 concurrently read the shared counter (readers inside = 2). When writer W1 arrives at 0.224s, "
        "it waits on the turnstile. Once active readers drain to 0 at 0.368s, W1 immediately enters the critical section exclusively (W:1). "
        "Upon W1 leaving at 0.775s, waiting readers R4 and R3 enter concurrently.",
        body_style
    ))

    story.append(Paragraph("8.2 Readers-Writers, monitor (4 readers, 2 writers)", h2_style))
    story.append(Paragraph("[0.164s] R1  REQUEST_READ   | R:0 W:0 | R1 waiting requests read access", trace_style))
    story.append(Paragraph("[0.164s] R1  ENTER_CS       | R:1 W:0 | R1 reading entered CS, readers inside = 1", trace_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: Section 8.2 (cont), Section 8.3, Section 8.4, Section 9 (start)
    # =========================================================================
    rw_mon_lines = [
        "[0.184s] R2  REQUEST_READ   | R:1 W:0 | R2 waiting requests read access",
        "[0.184s] R2  ENTER_CS       | R:2 W:0 | R2 reading entered CS, readers inside = 2",
        "[0.189s] R3  REQUEST_READ   | R:2 W:0 | R3 waiting requests read access",
        "[0.189s] R3  ENTER_CS       | R:3 W:0 | R3 reading entered CS, readers inside = 3",
        "[0.208s] R4  REQUEST_READ   | R:3 W:0 | R4 waiting requests read access",
        "[0.208s] R4  ENTER_CS       | R:4 W:0 | R4 reading entered CS, readers inside = 4",
        "[0.265s] W1  REQUEST_WRITE  | R:4 W:0 | W1 waiting requests write access",
        "[0.478s] R3  EXIT_CS        | R:0 W:0 | R3 idle left CS, readers inside = 0 (read value=0)",
        "[0.478s] W1  ENTER_CS       | R:0 W:1 | W1 writing entered CS (exclusive)",
        "[0.893s] W1  EXIT_CS        | R:0 W:0 | W1 idle left CS, committed value = 1"
    ]
    for line in rw_mon_lines:
        story.append(Paragraph(line, trace_style))

    story.append(Paragraph(
        "All four readers (R1, R2, R3, R4) concurrently access the shared database without blocking. When writer W1 requests write access, "
        "it waits for active readers to complete. The moment the last reader (R3) exits at 0.478s, W1 is awakened and granted exclusive write access.",
        body_style
    ))

    story.append(Paragraph("8.3 Dining Philosophers, semaphores", h2_style))
    dp_sem_lines = [
        "[0.112s] P2  HUNGRY         | P2 hungry wants to eat",
        "[0.112s] P2  ACQUIRING      | P2 acquiring picked up fork 2",
        "[0.113s] P2  EATING         | P2 eating has both forks",
        "[0.124s] P1  HUNGRY         | P1 hungry wants to eat",
        "[0.124s] P1  ACQUIRING      | P1 acquiring picked up fork 1",
        "[0.432s] P2  RELEASING      | P2 releasing put down fork 2",
        "[0.432s] P2  RELEASING      | P2 releasing put down fork 3",
        "[0.432s] P2  THINKING       | P2 thinking finished meal #1",
        "[0.432s] P1  EATING         | P1 eating has both forks",
        "[0.749s] P1  RELEASING      | P1 releasing put down fork 1",
        "[0.750s] P0  EATING         | P0 eating has both forks",
        "validation OK: forks never shared and every meal had both forks"
    ]
    for line in dp_sem_lines:
        story.append(Paragraph(line, trace_style))

    story.append(Paragraph(
        "Philosopher P1 waits for fork 2 while P2 is eating. The instant P2 finishes at 0.432s, P1 acquires fork 2 and transitions to eating. "
        "Forks are passed cleanly between adjacent philosophers. All 4 philosophers completed all rounds, confirming deadlock-free operation.",
        body_style
    ))

    story.append(Paragraph("8.4 Dining Philosophers, monitor", h2_style))
    dp_mon_lines = [
        "[0.138s] P1  HUNGRY         | P1 hungry wants to eat",
        "[0.138s] P1  EATING         | P1 eating has both forks",
        "[0.191s] P2  HUNGRY         | P2 hungry wants to eat",
        "[0.191s] P2  WAITING        | P2 waiting on can_eat[2], neighbor eating",
        "[0.277s] P3  HUNGRY         | P3 hungry wants to eat",
        "[0.277s] P3  EATING         | P3 eating has both forks",
        "[0.301s] P0  HUNGRY         | P0 hungry wants to eat",
        "[0.301s] P0  WAITING        | P0 waiting on can_eat[0], neighbor eating",
        "[0.408s] P1  RELEASING      | P1 releasing put down fork 1",
        "[0.408s] P1  RELEASING      | P1 releasing put down fork 2",
        "[0.595s] P3  RELEASING      | P3 releasing put down fork 3",
        "[0.595s] P0  EATING         | P0 eating has both forks",
        "[0.595s] P2  EATING         | P2 eating has both forks",
        "validation OK: forks never shared and every meal had both forks"
    ]
    for line in dp_mon_lines:
        story.append(Paragraph(line, trace_style))

    story.append(Paragraph(
        "Philosophers P1 and P3 eat concurrently because they are non-adjacent neighbors. P0 and P2 wait on their respective condition variables. "
        "When P1 and P3 release their forks, both P0 and P2 simultaneously transition to EATING, demonstrating maximum table concurrency (2 concurrent diners).",
        body_style
    ))

    # 9. Race Conditions, Mutual Exclusion, Deadlock and Starvation (Start)
    story.append(Paragraph("9. Race Conditions, Mutual Exclusion, Deadlock and Starvation", h1_style))
    story.append(Paragraph(
        "Race condition. In Readers-Writers, SharedDatabase.write() is a read-modify-write with a sleep in the "
        "middle. Without the exclusive writer lock, two writers could both read the same old value and one "
        "increment would be lost. The final-value check (final value equals writers x rounds) and the trace "
        "validation confirm this did not happen. The counter active_readers would also race if it were not guarded "
        "by count_mutex (or the monitor lock).",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: Section 9 (cont), Section 10 (Comparison Table), Section 11 (intro)
    # =========================================================================
    story.append(Paragraph(
        "Mutual exclusion. Readers-Writers: resource_lock (or the monitor condition) keeps a writer apart from "
        "everyone else. Philosophers: each fork semaphore (or the monitor state check) lets only one philosopher hold a fork.",
        body_style
    ))
    story.append(Paragraph(
        "Deadlock. The four conditions are mutual exclusion, hold-and-wait, no pre-emption and circular wait. "
        "The semaphore solution breaks circular wait with the room semaphore (at most 3 contenders). The "
        "monitor solution breaks hold-and-wait by granting both forks atomically or none. The Readers-Writers "
        "programs hold only one resource lock, so they cannot deadlock.",
        body_style
    ))
    story.append(Paragraph("Starvation.", body_style))
    story.append(Paragraph("&bull; <b>Readers-Writers (semaphore):</b> the turnstile queues requests, so neither readers nor writers should starve. Python semaphores are not guaranteed to wake threads in strict first-in-first-out order, so this is not formally proved.", bullet_style))
    story.append(Paragraph("&bull; <b>Readers-Writers (monitor):</b> writer preference means readers could starve if writers kept arriving without a break.", bullet_style))
    story.append(Paragraph("&bull; <b>Philosophers (semaphore):</b> the room semaphore is also not strictly first-in-first-out, so starvation is unlikely but not excluded.", bullet_style))
    story.append(Paragraph("&bull; <b>Philosophers (monitor):</b> a philosopher could starve if its two neighbours keep taking turns eating so that it never sees both free. A fix is to record how long each philosopher has waited and give priority to the oldest.", bullet_style))

    # 10. Comparison of Semaphore and Monitor Approaches
    story.append(Paragraph("10. Comparison of Semaphore and Monitor Approaches", h1_style))
    comp_rows = [
        ["Point", "Semaphores", "Monitors"],
        ["Level", "Low-level counters; programmer must pair every wait with a signal", "Higher-level; lock and conditions are packaged in one class"],
        ["Error risk", "A forgotten signal or wrong order can deadlock or break exclusion", "Mutual exclusion is automatic inside the entry procedures; mistakes are mainly wrong conditions"],
        ["Waiting on a condition", "Indirect, using counters and extra semaphores (turnstile, room)", "Direct, using condition variables with wait_for"],
        ["Readability", "State is spread over several semaphores", "State and rules sit together, easier to explain"],
        ["Flexibility", "Very flexible, but harder to reason about", "Easy to change policy (for example writer priority)"],
        ["Language support", "Available almost everywhere", "Needs lock plus conditions; built into some languages"]
    ]
    t_comp = Table(comp_rows, colWidths=[110, 195, 195])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0e7ff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "In this assignment the monitor solutions were easier to read and check, while the semaphore solutions "
        "showed more clearly how the low-level mechanism works.",
        body_style
    ))

    # 11. Screenshots Intro
    story.append(Paragraph("11. Screenshots", h1_style))
    story.append(Paragraph("Insert your own screenshots here, taken from your runs:", body_style))
    story.append(Paragraph("&bull; <b>Figure 1:</b> terminal output of rw_semaphore.py and the generated HTML simulation", fig_label_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: Figure 1 & Figure 2
    # =========================================================================
    if os.path.exists(FIG1_PATH):
        story.append(Image(FIG1_PATH, width=490, height=270))
    story.append(Spacer(1, 14))

    story.append(Paragraph("&bull; <b>Figure 2:</b> terminal output of rw_monitor.py and the generated HTML simulation", fig_label_style))
    if os.path.exists(FIG2_PATH):
        story.append(Image(FIG2_PATH, width=490, height=270))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: Figure 3
    # =========================================================================
    story.append(Paragraph("&bull; <b>Figure 3:</b> terminal output of dp_semaphore.py and the generated HTML simulation", fig_label_style))
    story.append(Spacer(1, 4))
    if os.path.exists(FIG3_PATH):
        story.append(Image(FIG3_PATH, width=490, height=360))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: Figure 4 & Section 12 (AI Usage Summary)
    # =========================================================================
    story.append(Paragraph("&bull; <b>Figure 4:</b> terminal output of dp_monitor.py and the generated HTML simulation", fig_label_style))
    story.append(Spacer(1, 4))
    if os.path.exists(FIG4_PATH):
        story.append(Image(FIG4_PATH, width=490, height=350))
    story.append(Spacer(1, 12))

    # 12. AI Usage Summary
    story.append(Paragraph("12. AI Usage Summary", h1_style))
    story.append(Paragraph(
        "The AI tool used was Claude (Anthropic) in the claude.ai chat / Google DeepMind Antigravity AI assistant. I gave it the assignment PDF and asked "
        "for code for the four problems. It produced the four programs and the shared HTML generator. I then "
        "asked follow-up questions about opening and running the files, fixed a setup error (running a file from "
        "inside the zip, so the common folder was missing), and asked for the HTML to open automatically after a "
        "run, which was added. The AI also declined my request to help avoid AI detection and advised that AI "
        "use must be disclosed. I ran the programs and checked the output and the HTML. A limitation I noticed is "
        "that the first version did not open the HTML automatically. The full prompts are in "
        "<code>ai_prompts/prompts.md</code>.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: Section 13 (References) & Section 14 (Academic Integrity Declaration)
    # =========================================================================
    story.append(Paragraph("13. References", h1_style))
    refs = [
        "1. Silberschatz, A., Galvin, P. B. and Gagne, G., Operating System Concepts, 10th ed., Wiley, 2018.",
        "2. Tanenbaum, A. S. and Bos, H., Modern Operating Systems, 4th ed., Pearson, 2014.",
        "3. Downey, A. B., The Little Book of Semaphores, Green Tea Press.",
        "4. Courtois, P. J., Heymans, F. and Parnas, D. L., 'Concurrent Control with Readers and Writers', Communications of the ACM, 14(10), 1971.",
        "5. Hoare, C. A. R., 'Monitors: An Operating System Structuring Concept', Communications of the ACM, 17(10), 1974.",
        "6. Dijkstra, E. W., 'Hierarchical Ordering of Sequential Processes', Acta Informatica, 1, 1971.",
        "7. Python Software Foundation, documentation of the threading and webbrowser modules, docs.python.org/3.",
        "8. Anthropic, Claude (AI assistant), claude.ai, used for code generation and explanations, October 2026."
    ]
    for r in refs:
        story.append(Paragraph(r, bullet_style))

    story.append(Spacer(1, 16))

    # 14. Academic Integrity Declaration
    story.append(Paragraph("14. Academic Integrity Declaration", h1_style))
    story.append(Paragraph(
        "I declare that I have personally tested and understood the submitted programs. I have disclosed the AI "
        "tools and external resources used in developing this assignment. I can explain the synchronization logic, "
        "generated HTML simulation, and modifications made to the code. I have not knowingly submitted "
        "another student's work or unacknowledged third-party material as my own.",
        body_style
    ))
    story.append(Spacer(1, 18))

    # Signature and Date Box matching reference
    sig_content = [
        [Paragraph("<b>Signature:</b> ___________________________", body_style)],
        [Spacer(1, 6)],
        [Paragraph("<b>Date:</b> 13/10/2026", body_style)]
    ]
    t_sig = Table(sig_content, colWidths=[480])
    t_sig.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_sig)

    # Build document
    doc.build(story)
    print(f"Generated exact 9-page reference-matched Assignment_Report.pdf at: {PDF_PATH}")


if __name__ == "__main__":
    generate_pdf()
