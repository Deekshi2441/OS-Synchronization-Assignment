"""
Builds Assignment_Report.pdf using ReportLab Platypus.
Includes complete assignment content, tables, code snippets,
and embedded simulation screenshots.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)

REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(REPORT_DIR, ".."))
PDF_PATH = os.path.join(REPORT_DIR, "Assignment_Report.pdf")
RW_IMG_PATH = os.path.join(PROJECT_ROOT, "screenshots", "readers_writers_semaphore.png")
DP_IMG_PATH = os.path.join(PROJECT_ROOT, "screenshots", "dining_philosophers_semaphore.png")

def generate_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=6,
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#f8fafc'),
        spaceBefore=4,
        spaceAfter=4
    )

    caption_style = ParagraphStyle(
        'ImgCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceBefore=4,
        spaceAfter=10
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("OPERATING SYSTEMS PROGRAMMING ASSIGNMENT REPORT", title_style))
    story.append(Paragraph("Classical Process Synchronization with Program-Generated HTML Simulation<br/>Readers-Writers Problem and Dining Philosophers Problem", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=14))

    # Declaration Callout Table
    decl_text = (
        "<b>Academic Integrity & Authorship Declaration:</b><br/>"
        "<i>&ldquo;I declare that I have personally tested and understood the submitted programs. "
        "I have disclosed the AI tools and external resources used in developing this assignment. "
        "I can explain the synchronization logic, generated HTML simulation, and modifications made to the code. "
        "I have not knowingly submitted another student’s work or unacknowledged third-party material as my own.&rdquo;</i><br/><br/>"
        "<b>Student:</b> [Student Full Name] &nbsp;|&nbsp; <b>USN:</b> [Student USN] &nbsp;|&nbsp; <b>Course:</b> Operating Systems (CS/IT)"
    )
    decl_p = Paragraph(decl_text, callout_style)
    decl_table = Table([[decl_p]], colWidths=[520])
    decl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(decl_table)
    story.append(Spacer(1, 14))

    # Section 1: Problem Statement
    story.append(Paragraph("1. Problem Statement and Synchronization Objectives", h1_style))
    story.append(Paragraph(
        "Modern operating systems coordinate concurrent processes to ensure reliable, conflict-free access to shared hardware and software resources. "
        "This project implements and evaluates four classical process synchronization solutions across two fundamental concurrency dilemmas:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Readers-Writers Problem:</b> Coordinates concurrent queries and modifications to a shared dataset. "
        "Multiple readers may concurrently inspect the data without interference, but writers must possess strictly exclusive mutual exclusion. "
        "The algorithms must prevent race conditions on reader counters and eliminate both reader and writer starvation.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>2. Dining Philosophers Problem (4 Philosophers):</b> Four philosophers sit around a circular table sharing four forks. "
        "Each philosopher requires both adjacent forks to eat. The synchronization logic must prevent catastrophic circular-wait deadlock "
        "and starvation while maximizing concurrent eating throughput (up to 2 concurrent diners for N=4).",
        bullet_style
    ))

    # Section 2: Readers-Writers
    story.append(Paragraph("2. Readers-Writers Implementations", h1_style))
    story.append(Paragraph("2.1 Semaphore-Based Solution (Starvation-Free Turnstile)", h2_style))
    story.append(Paragraph(
        "The semaphore solution utilizes three binary semaphores: <code>mutex</code> (protects atomic updates to <code>read_count</code>), "
        "<code>rw_mutex</code> (protects the critical section for writes), and <code>turnstile</code> (guarantees FIFO queueing). "
        "The first reader into the critical section acquires <code>rw_mutex</code>, while subsequent readers join concurrently. "
        "The last departing reader releases <code>rw_mutex</code>. Arriving writers hold the turnstile, ensuring subsequent readers queue "
        "and preventing writer starvation.",
        body_style
    ))

    story.append(Paragraph("2.2 Monitor-Based Solution (Condition Variables)", h2_style))
    story.append(Paragraph(
        "The monitor abstraction encapsulates internal synchronization state (<code>active_readers</code>, <code>active_writers</code>, "
        "<code>waiting_readers</code>, <code>waiting_writers</code>) within an explicit class. Mutual exclusion is enforced by an internal lock, "
        "and condition synchronization is handled via two condition variables: <code>can_read</code> and <code>can_write</code>. "
        "Writer preference is strictly enforced: arriving readers block in <code>start_read()</code> if any writer is active or waiting. "
        "Condition variable checks follow Mesa / Signal-and-Continue semantics within <code>while</code> loops.",
        body_style
    ))

    # Section 3: Dining Philosophers
    story.append(Paragraph("3. Dining Philosophers Implementations (4 Philosophers)", h1_style))
    story.append(Paragraph("3.1 Semaphore-Based Solution (Room Capacity Semaphore)", h2_style))
    story.append(Paragraph(
        "To prevent deadlock in the 4-philosopher table, we introduce a Footman / Room counting semaphore initialized to <code>N - 1 = 3</code>. "
        "At most 3 philosophers can enter the dining room to acquire forks simultaneously. "
        "<b>Mathematical Proof of Deadlock Freedom:</b> By the Pigeonhole Principle, distributing 4 shared forks among at most 3 diners "
        "guarantees that at least one philosopher will successfully acquire both adjacent forks and eat, breaking the circular wait condition.",
        body_style
    ))

    story.append(Paragraph("3.2 Monitor-Based Solution (Atomic Neighbor Testing)", h2_style))
    story.append(Paragraph(
        "The monitor encapsulates each philosopher's state (<code>THINKING</code>, <code>HUNGRY</code>, <code>EATING</code>) and private condition variables. "
        "In <code>pickup_forks(i)</code>, a philosopher only transitions to <code>EATING</code> if <code>(state[left] != EATING and state[right] != EATING)</code>. "
        "Both forks are claimed as an indivisible atomic action within the monitor lock, completely eliminating the Coffman Hold-and-Wait condition.",
        body_style
    ))

    story.append(PageBreak())

    # Section 4: Program-Generated Simulation Architecture
    story.append(Paragraph("4. Program-Generated HTML Simulation Architecture", h1_style))
    story.append(Paragraph(
        "In strict adherence to the assignment mandate, the HTML simulations are <b>directly generated from actual runtime execution data</b>. "
        "During execution, a thread-safe <code>ExecutionTracer</code> captures every state transition with millisecond timestamps, thread IDs, active counts, "
        "and resource states. When the threads complete, the program compiles the events into a self-contained, browser-viewable HTML file.",
        body_style
    ))

    # Screenshots
    if os.path.exists(RW_IMG_PATH):
        story.append(Paragraph("4.1 Readers-Writers Interactive Simulation", h2_style))
        story.append(Image(RW_IMG_PATH, width=500, height=270))
        story.append(Paragraph("Figure 1: Program-generated Readers-Writers simulation showing active concurrent readers and exclusive critical section status.", caption_style))

    if os.path.exists(DP_IMG_PATH):
        story.append(Paragraph("4.2 Dining Philosophers Interactive Simulation", h2_style))
        story.append(Image(DP_IMG_PATH, width=500, height=270))
        story.append(Paragraph("Figure 2: Program-generated Dining Philosophers simulation featuring dynamic circular SVG table, fork lines, and state badges.", caption_style))

    story.append(PageBreak())

    # Section 5: Comparative Evaluation
    story.append(Paragraph("5. Comparative Evaluation: Semaphores vs. Monitors", h1_style))
    comp_data = [
        ["Evaluation Dimension", "Semaphore-Based Approach", "Monitor-Based Approach"],
        ["Abstraction Level", "Low-level OS synchronization primitive", "High-level object-oriented abstraction"],
        ["Mutual Exclusion", "Explicitly acquired/released across blocks", "Implicitly guaranteed within monitor methods"],
        ["Signaling Semantics", "Stateful integer counters (P/V)", "Stateless notifications (notify / notify_all)"],
        ["Deadlock Vulnerability", "Higher risk of improper acquisition order", "Lower risk; atomic multi-resource tests"],
        ["Starvation Handling", "Requires FIFO turnstiles / ticket algorithms", "Condition variable queues with wait counts"],
        ["Code Maintainability", "Scattered acquire/release pairs", "Centralized, modular synchronization policies"]
    ]

    comp_table = Table(comp_data, colWidths=[130, 195, 195])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 14))

    # Section 6: Analysis of Concurrency Issues
    story.append(Paragraph("6. Analysis: Race Conditions, Mutual Exclusion, Deadlock & Starvation", h1_style))
    story.append(Paragraph(
        "<b>Race Conditions:</b> Prevented in all solutions by enclosing critical state variables (<code>read_count</code>, <code>fork_owners</code>) "
        "within binary semaphores or monitor locks. Runtime assertions verified that no concurrent writes or corruptions occurred.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Mutual Exclusion:</b> Verified across all execution runs. At no point did two writers access the shared resource simultaneously, "
        "nor did any reader access the resource while a writer was active. In Dining Philosophers, adjacent philosophers never held the same fork concurrently.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Deadlock Prevention:</b> Both the Footman counting semaphore and the monitor atomic neighbor test provably break Coffman's circular wait and hold-and-wait conditions.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Starvation Mitigation:</b> In Readers-Writers, turnstiles and writer-priority condition checks prevent indefinite reader barging. "
        "In Dining Philosophers, testing neighbors on fork release ensures waiting philosophers are promptly awakened.",
        body_style
    ))

    # Section 7: Viva Voce & Demonstration Summary
    story.append(Paragraph("7. Viva Voce & Demonstration Summary", h1_style))
    story.append(Paragraph(
        "All four programs can be executed live during evaluation via <code>python &lt;script_path&gt;</code>. "
        "Each program outputs real-time console event traces and automatically produces an interactive HTML simulation file. "
        "Evaluators can inspect the generated HTML files in any browser to verify thread states, examine critical section occupancy, "
        "and validate invariant compliance step by step.",
        body_style
    ))

    # Build document
    doc.build(story)
    print(f"Generated PDF report at: {PDF_PATH}")

if __name__ == "__main__":
    generate_pdf()
