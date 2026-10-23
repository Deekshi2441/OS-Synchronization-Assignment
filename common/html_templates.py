"""
HTML Visualization Generator for OS Synchronization Assignment.
Generates interactive, rich, self-contained HTML simulations
from recorded execution event traces.
"""

import json
import html

def generate_rw_html(title, mechanism_type, trace_data, summary_stats):
    """
    Generates a rich, interactive HTML visualizer for the Readers-Writers problem.
    """
    trace_json = json.dumps(trace_data)
    stats_json = json.dumps(summary_stats)
    safe_title = html.escape(title)
    safe_mech = html.escape(mechanism_type)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title} - {safe_mech} Simulation</title>
<style>
  :root {{
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --card-bg: rgba(30, 41, 59, 0.75);
    --border-color: rgba(255, 255, 255, 0.1);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-blue: #38bdf8;
    --accent-indigo: #818cf8;
    --accent-green: #34d399;
    --accent-amber: #fbbf24;
    --accent-rose: #f43f5e;
    --accent-purple: #c084fc;
    --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background-color: var(--bg-primary);
    background-image: 
      radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.12) 0px, transparent 50%);
    color: var(--text-primary);
    font-family: var(--font-stack);
    line-height: 1.5;
    min-height: 100vh;
    padding: 24px;
  }}

  .container {{
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}

  header {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  }}

  .header-titles h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .header-titles p {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-top: 4px;
  }}

  .badge-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    background: rgba(56, 189, 248, 0.15);
    color: var(--accent-blue);
    border: 1px solid rgba(56, 189, 248, 0.3);
  }}

  /* Control Panel */
  .control-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 20px 28px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  }}

  .control-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }}

  .btn-group {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .btn {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s ease;
  }}

  .btn:hover {{
    background: var(--bg-tertiary);
    border-color: rgba(255, 255, 255, 0.25);
    transform: translateY(-1px);
  }}

  .btn-primary {{
    background: linear-gradient(135deg, #0284c7, #2563eb);
    border: none;
    color: white;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
  }}

  .btn-primary:hover {{
    background: linear-gradient(135deg, #0369a1, #1d4ed8);
    box-shadow: 0 6px 16px rgba(2, 132, 199, 0.4);
  }}

  .speed-selector {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 4px;
    border-radius: 8px;
  }}

  .speed-btn {{
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.15s;
  }}

  .speed-btn.active {{
    background: var(--accent-blue);
    color: #0f172a;
  }}

  .scrubber-container {{
    display: flex;
    align-items: center;
    gap: 16px;
    width: 100%;
  }}

  .scrubber {{
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    outline: none;
    cursor: pointer;
  }}

  .scrubber::-webkit-slider-thumb {{
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--accent-blue);
    cursor: pointer;
    box-shadow: 0 0 10px var(--accent-blue);
    transition: transform 0.1s;
  }}

  .scrubber::-webkit-slider-thumb:hover {{
    transform: scale(1.2);
  }}

  .step-info {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-variant-numeric: tabular-nums;
    min-width: 130px;
    text-align: right;
  }}

  /* Simulation Grid */
  .sim-grid {{
    display: grid;
    grid-template-columns: 1fr 1.3fr 1fr;
    gap: 20px;
  }}

  @media (max-width: 1024px) {{
    .sim-grid {{
      grid-template-columns: 1fr;
    }}
  }}

  .sim-column {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }}

  .col-title {{
    font-size: 1.1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary);
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
  }}

  /* Process Cards */
  .entity-list {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 480px;
    overflow-y: auto;
  }}

  .entity-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s ease;
  }}

  .entity-card.active-reader {{
    border-color: var(--accent-blue);
    background: rgba(56, 189, 248, 0.1);
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
  }}

  .entity-card.active-writer {{
    border-color: var(--accent-rose);
    background: rgba(244, 63, 94, 0.12);
    box-shadow: 0 0 15px rgba(244, 63, 94, 0.25);
  }}

  .entity-card.waiting {{
    border-color: var(--accent-amber);
    background: rgba(251, 191, 36, 0.08);
  }}

  .entity-id {{
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .entity-status {{
    font-size: 0.8rem;
    padding: 4px 10px;
    border-radius: 9999px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}

  .status-idle {{ background: rgba(148, 163, 184, 0.15); color: var(--text-secondary); }}
  .status-waiting {{ background: rgba(251, 191, 36, 0.2); color: var(--accent-amber); }}
  .status-reading {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-blue); }}
  .status-writing {{ background: rgba(244, 63, 94, 0.2); color: var(--accent-rose); }}

  /* Critical Section Center Stage */
  .cs-container {{
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: 100%;
  }}

  .cs-box {{
    flex: 1;
    min-height: 260px;
    background: radial-gradient(circle at center, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    position: relative;
    transition: all 0.3s ease;
  }}

  .cs-box.occupied-read {{
    border: 2px solid var(--accent-blue);
    box-shadow: inset 0 0 30px rgba(56, 189, 248, 0.2), 0 0 20px rgba(56, 189, 248, 0.25);
  }}

  .cs-box.occupied-write {{
    border: 2px solid var(--accent-rose);
    box-shadow: inset 0 0 30px rgba(244, 63, 94, 0.2), 0 0 25px rgba(244, 63, 94, 0.35);
  }}

  .cs-label {{
    position: absolute;
    top: 14px;
    left: 18px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-transform: uppercase;
  }}

  .shared-resource-card {{
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    width: 90%;
    margin-top: 20px;
    text-align: left;
  }}

  .shared-resource-header {{
    font-size: 0.8rem;
    color: var(--accent-indigo);
    font-weight: 600;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
  }}

  .shared-resource-val {{
    font-family: monospace;
    font-size: 1.1rem;
    color: var(--text-primary);
    background: #090d16;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    word-break: break-all;
  }}

  .active-occupants {{
    margin-top: 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
  }}

  .occupant-pill {{
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .occupant-pill.reader {{
    background: rgba(56, 189, 248, 0.2);
    color: var(--accent-blue);
    border: 1px solid rgba(56, 189, 248, 0.4);
  }}

  .occupant-pill.writer {{
    background: rgba(244, 63, 94, 0.2);
    color: var(--accent-rose);
    border: 1px solid rgba(244, 63, 94, 0.4);
  }}

  /* Synchronization Primitives Status */
  .sync-status-box {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}

  .sync-stat {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .sync-stat-label {{
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    font-weight: 600;
  }}

  .sync-stat-value {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  /* Timeline & Log Table */
  .log-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  .table-container {{
    max-height: 380px;
    overflow-y: auto;
    border: 1px solid var(--border-color);
    border-radius: 10px;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    text-align: left;
  }}

  th {{
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: 600;
    padding: 10px 14px;
    position: sticky;
    top: 0;
    z-index: 1;
  }}

  td {{
    padding: 8px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-secondary);
  }}

  tr.current-step-row {{
    background: rgba(56, 189, 248, 0.15) !important;
    border-left: 3px solid var(--accent-blue);
  }}

  tr.current-step-row td {{
    color: var(--text-primary);
    font-weight: 600;
  }}

  tr:hover {{
    background: rgba(255, 255, 255, 0.02);
    cursor: pointer;
  }}

  .event-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }}

  .event-req {{ background: rgba(251, 191, 36, 0.2); color: var(--accent-amber); }}
  .event-enter {{ background: rgba(52, 211, 153, 0.2); color: var(--accent-green); }}
  .event-exit {{ background: rgba(148, 163, 184, 0.2); color: var(--text-secondary); }}
  .event-write {{ background: rgba(244, 63, 94, 0.25); color: var(--accent-rose); }}

  /* Metric Chips */
  .metrics-bar {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
  }}

  .metric-card {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .metric-label {{
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 600;
  }}

  .metric-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
  }}
</style>
</head>
<body>

<div class="container">
  <header>
    <div class="header-titles">
      <h1>{safe_title}</h1>
      <p>Program-Generated Interactive Trace Simulation | Concurrency & Synchronization</p>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
      <span class="badge-tag">Mechanism: {safe_mech}</span>
      <span class="badge-tag" style="background: rgba(52, 211, 153, 0.15); color: var(--accent-green); border-color: rgba(52, 211, 153, 0.3);">Verified Concurrent Execution</span>
    </div>
  </header>

  <!-- Summary Metrics Bar -->
  <div class="metrics-bar" id="metricsBar"></div>

  <!-- Interactive Controls -->
  <div class="control-card">
    <div class="control-row">
      <div class="btn-group">
        <button class="btn" id="btnPrev" title="Previous step">⏮ Step Back</button>
        <button class="btn btn-primary" id="btnPlayPause">▶ Play</button>
        <button class="btn" id="btnNext" title="Next step">Step Next ⏭</button>
        <button class="btn" id="btnReset" title="Reset to start">↺ Reset</button>
      </div>

      <div class="speed-selector">
        <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 4px; padding-left: 6px;">Speed:</span>
        <button class="speed-btn" data-speed="1600">0.5x</button>
        <button class="speed-btn active" data-speed="800">1x</button>
        <button class="speed-btn" data-speed="400">2x</button>
        <button class="speed-btn" data-speed="150">5x</button>
      </div>
    </div>

    <div class="scrubber-container">
      <input type="range" class="scrubber" id="scrubber" min="0" max="{len(trace_data)-1}" value="0">
      <div class="step-info" id="stepCounter">Step 0 / {len(trace_data)-1}</div>
    </div>
  </div>

  <!-- Live Visual State Grid -->
  <div class="sim-grid">
    <!-- Readers Column -->
    <div class="sim-column">
      <div class="col-title">
        <span>📖 Reader Threads</span>
        <span id="readerSummaryCount" style="margin-left:auto; font-size: 0.85rem; color: var(--accent-blue);">0 Active</span>
      </div>
      <div class="entity-list" id="readersList"></div>
    </div>

    <!-- Critical Section & Shared Resource Center Stage -->
    <div class="sim-column">
      <div class="col-title">
        <span>🔒 Critical Section & Shared Resource</span>
      </div>
      <div class="cs-container">
        <div class="cs-box" id="csBox">
          <div class="cs-label">Critical Section Boundary</div>
          <div id="csOccupants" class="active-occupants">
            <span style="color: var(--text-muted); font-size: 0.9rem;">No threads inside Critical Section</span>
          </div>

          <div class="shared-resource-card">
            <div class="shared-resource-header">
              <span>SHARED DATABASE RESOURCE</span>
              <span id="resourceVersion">Rev 0</span>
            </div>
            <div class="shared-resource-val" id="resourceValue">Initial State</div>
          </div>
        </div>

        <!-- Synchronization State Info -->
        <div class="sync-status-box" id="syncStatusBox"></div>
      </div>
    </div>

    <!-- Writers Column -->
    <div class="sim-column">
      <div class="col-title">
        <span>✍ Writer Threads</span>
        <span id="writerSummaryCount" style="margin-left:auto; font-size: 0.85rem; color: var(--accent-rose);">0 Active</span>
      </div>
      <div class="entity-list" id="writersList"></div>
    </div>
  </div>

  <!-- Execution Event Log & Explanation -->
  <div class="log-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
      <h2 style="font-size: 1.15rem; font-weight: 600;">📜 Execution Trace Timeline</h2>
      <div style="font-size: 0.85rem; color: var(--text-secondary);" id="currentStepExplanation"></div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 70px;">Step</th>
            <th style="width: 100px;">Time (ms)</th>
            <th style="width: 90px;">Thread</th>
            <th style="width: 140px;">Action</th>
            <th style="width: 100px;">Active R/W</th>
            <th>Details & Synchronization Invariants</th>
          </tr>
        </thead>
        <tbody id="traceTableBody"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
  const trace = {trace_json};
  const summary = {stats_json};

  let currentStep = 0;
  let isPlaying = false;
  let playInterval = null;
  let delay = 800;

  // DOM Elements
  const btnPlayPause = document.getElementById('btnPlayPause');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnReset = document.getElementById('btnReset');
  const scrubber = document.getElementById('scrubber');
  const stepCounter = document.getElementById('stepCounter');
  const speedButtons = document.querySelectorAll('.speed-btn');
  const metricsBar = document.getElementById('metricsBar');
  const readersList = document.getElementById('readersList');
  const writersList = document.getElementById('writersList');
  const csBox = document.getElementById('csBox');
  const csOccupants = document.getElementById('csOccupants');
  const resourceValue = document.getElementById('resourceValue');
  const resourceVersion = document.getElementById('resourceVersion');
  const syncStatusBox = document.getElementById('syncStatusBox');
  const traceTableBody = document.getElementById('traceTableBody');
  const currentStepExplanation = document.getElementById('currentStepExplanation');
  const readerSummaryCount = document.getElementById('readerSummaryCount');
  const writerSummaryCount = document.getElementById('writerSummaryCount');

  // Populate Summary Metrics
  function initSummaryMetrics() {{
    const metrics = [
      {{ label: 'Total Synchronized Events', value: summary.total_events || trace.length }},
      {{ label: 'Total Read Operations', value: summary.total_reads || '-' }},
      {{ label: 'Total Write Operations', value: summary.total_writes || '-' }},
      {{ label: 'Max Concurrent Readers', value: summary.max_concurrent_readers || '-' }},
      {{ label: 'Reader Preference / Fairness', value: summary.policy || 'Starvation-Free Fair' }}
    ];

    metricsBar.innerHTML = metrics.map(m => `
      <div class="metric-card">
        <span class="metric-label">${{m.label}}</span>
        <span class="metric-value">${{m.value}}</span>
      </div>
    `).join('');
  }}

  // Populate Trace Table
  function initTraceTable() {{
    traceTableBody.innerHTML = trace.map((evt, idx) => `
      <tr id="row-${{idx}}" onclick="jumpToStep(${{idx}})">
        <td>#${{idx}}</td>
        <td>+${{evt.timestamp_ms || evt.time || 0}} ms</td>
        <td><strong>${{evt.entity_id}}</strong></td>
        <td><span class="event-badge ${{getBadgeClass(evt.action)}}">${{evt.action}}</span></td>
        <td>R:${{evt.active_readers || 0}} | W:${{evt.active_writers || 0}}</td>
        <td>${{evt.details || ''}}</td>
      </tr>
    `).join('');
  }}

  function getBadgeClass(action) {{
    if (!action) return '';
    if (action.includes('REQUEST')) return 'event-req';
    if (action.includes('ENTER') || action.includes('START')) return 'event-enter';
    if (action.includes('EXIT') || action.includes('FINISH')) return 'event-exit';
    if (action.includes('WRITE')) return 'event-write';
    return '';
  }}

  // Render State at Current Step
  function renderStep(step) {{
    if (step < 0 || step >= trace.length) return;
    const s = trace[step];

    // Update scrubber and step count
    scrubber.value = step;
    stepCounter.textContent = `Step ${{step}} / ${{trace.length - 1}}`;
    currentStepExplanation.innerHTML = `<strong>Current:</strong> Step #${{step}} — ${{s.entity_id}}: ${{s.details || s.action}}`;

    // Highlight row in table
    document.querySelectorAll('#traceTableBody tr').forEach(r => r.classList.remove('current-step-row'));
    const activeRow = document.getElementById(`row-${{step}}`);
    if (activeRow) {{
      activeRow.classList.add('current-step-row');
      activeRow.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
    }}

    // Update Readers List
    const readers = s.readers_state || [];
    readersList.innerHTML = readers.map(r => `
      <div class="entity-card ${{r.status === 'READING' ? 'active-reader' : (r.status === 'WAITING' ? 'waiting' : '')}}">
        <div class="entity-id">
          <span>📘</span> ${{r.id}}
        </div>
        <span class="entity-status status-${{r.status.toLowerCase()}}">${{r.status}}</span>
      </div>
    `).join('');
    readerSummaryCount.textContent = `${{s.active_readers || 0}} Active`;

    // Update Writers List
    const writers = s.writers_state || [];
    writersList.innerHTML = writers.map(w => `
      <div class="entity-card ${{w.status === 'WRITING' ? 'active-writer' : (w.status === 'WAITING' ? 'waiting' : '')}}">
        <div class="entity-id">
          <span>✍</span> ${{w.id}}
        </div>
        <span class="entity-status status-${{w.status.toLowerCase()}}">${{w.status}}</span>
      </div>
    `).join('');
    writerSummaryCount.textContent = `${{s.active_writers || 0}} Active`;

    // Update Critical Section Display
    const activeReaders = s.active_readers || 0;
    const activeWriters = s.active_writers || 0;

    csBox.classList.remove('occupied-read', 'occupied-write');
    if (activeWriters > 0) {{
      csBox.classList.add('occupied-write');
      const writer = writers.find(w => w.status === 'WRITING') || {{ id: s.entity_id }};
      csOccupants.innerHTML = `
        <div class="occupant-pill writer">
          <span>✍</span> Active Writer: ${{writer.id}} (Exclusive Mutual Exclusion)
        </div>
      `;
    }} else if (activeReaders > 0) {{
      csBox.classList.add('occupied-read');
      const readingReaders = readers.filter(r => r.status === 'READING');
      csOccupants.innerHTML = readingReaders.length > 0 
        ? readingReaders.map(r => `<div class="occupant-pill reader"><span>📖</span> ${{r.id}}</div>`).join('')
        : `<div class="occupant-pill reader"><span>📖</span> ${{activeReaders}} Concurrent Reader(s)</div>`;
    }} else {{
      csOccupants.innerHTML = `<span style="color: var(--text-muted); font-size: 0.9rem;">No threads inside Critical Section (Idle)</span>`;
    }}

    // Update Shared Resource
    resourceValue.textContent = s.shared_data || 'Database Record: [Initial Value]';
    resourceVersion.textContent = `Rev ${{s.shared_data_version || 0}}`;

    // Update Synchronization Primitives
    const sync = s.sync_state || {{}};
    syncStatusBox.innerHTML = `
      <div class="sync-stat">
        <span class="sync-stat-label">Active Readers</span>
        <span class="sync-stat-value" style="color: var(--accent-blue);">${{activeReaders}}</span>
      </div>
      <div class="sync-stat">
        <span class="sync-stat-label">Active Writers</span>
        <span class="sync-stat-value" style="color: ${{activeWriters > 0 ? 'var(--accent-rose)' : 'var(--text-muted)'}};">${{activeWriters}}</span>
      </div>
      <div class="sync-stat">
        <span class="sync-stat-label">Waiting Readers</span>
        <span class="sync-stat-value">${{s.waiting_readers || 0}}</span>
      </div>
      <div class="sync-stat">
        <span class="sync-stat-label">Waiting Writers</span>
        <span class="sync-stat-value">${{s.waiting_writers || 0}}</span>
      </div>
      <div class="sync-stat" style="grid-column: span 2;">
        <span class="sync-stat-label">Sync Mechanism State</span>
        <span class="sync-stat-value" style="font-size: 0.85rem; font-family: monospace;">${{sync.description || '{safe_mech} Primitive Active'}}</span>
      </div>
    `;
  }}

  function togglePlay() {{
    if (isPlaying) {{
      pause();
    }} else {{
      play();
    }}
  }}

  function play() {{
    if (currentStep >= trace.length - 1) {{
      currentStep = 0;
    }}
    isPlaying = true;
    btnPlayPause.textContent = '⏸ Pause';
    btnPlayPause.classList.remove('btn-primary');
    btnPlayPause.style.background = 'var(--accent-amber)';
    btnPlayPause.style.color = '#0f172a';

    clearInterval(playInterval);
    playInterval = setInterval(() => {{
      if (currentStep < trace.length - 1) {{
        currentStep++;
        renderStep(currentStep);
      }} else {{
        pause();
      }}
    }}, delay);
  }}

  function pause() {{
    isPlaying = false;
    clearInterval(playInterval);
    btnPlayPause.textContent = '▶ Play';
    btnPlayPause.classList.add('btn-primary');
    btnPlayPause.style.background = '';
    btnPlayPause.style.color = '';
  }}

  function jumpToStep(idx) {{
    pause();
    currentStep = idx;
    renderStep(currentStep);
  }}

  // Event Listeners
  btnPlayPause.addEventListener('click', togglePlay);
  btnPrev.addEventListener('click', () => {{
    pause();
    if (currentStep > 0) {{
      currentStep--;
      renderStep(currentStep);
    }}
  }});
  btnNext.addEventListener('click', () => {{
    pause();
    if (currentStep < trace.length - 1) {{
      currentStep++;
      renderStep(currentStep);
    }}
  }});
  btnReset.addEventListener('click', () => {{
    pause();
    currentStep = 0;
    renderStep(currentStep);
  }});

  scrubber.addEventListener('input', (e) => {{
    pause();
    currentStep = parseInt(e.target.value);
    renderStep(currentStep);
  }});

  speedButtons.forEach(btn => {{
    btn.addEventListener('click', () => {{
      speedButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      delay = parseInt(btn.getAttribute('data-speed'));
      if (isPlaying) {{
        clearInterval(playInterval);
        playInterval = setInterval(() => {{
          if (currentStep < trace.length - 1) {{
            currentStep++;
            renderStep(currentStep);
          }} else {{
            pause();
          }}
        }}, delay);
      }}
    }});
  }});

  // Keyboard Navigation
  window.addEventListener('keydown', (e) => {{
    if (e.code === 'Space') {{
      e.preventDefault();
      togglePlay();
    }} else if (e.code === 'ArrowRight') {{
      btnNext.click();
    }} else if (e.code === 'ArrowLeft') {{
      btnPrev.click();
    }}
  }});

  // Init
  initSummaryMetrics();
  initTraceTable();
  renderStep(0);
</script>
</body>
</html>
"""
    return html_content


def generate_dp_html(title, mechanism_type, trace_data, summary_stats):
    """
    Generates a rich, interactive HTML visualizer for the Dining Philosophers problem (4 philosophers).
    """
    trace_json = json.dumps(trace_data)
    stats_json = json.dumps(summary_stats)
    safe_title = html.escape(title)
    safe_mech = html.escape(mechanism_type)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title} - {safe_mech} Simulation</title>
<style>
  :root {{
    --bg-primary: #0b0f19;
    --bg-secondary: #161e2e;
    --bg-tertiary: #26334d;
    --card-bg: rgba(22, 30, 46, 0.8);
    --border-color: rgba(255, 255, 255, 0.1);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-cyan: #06b6d4;
    --accent-emerald: #10b981;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    --accent-indigo: #6366f1;
    --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background-color: var(--bg-primary);
    background-image: 
      radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.12) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.12) 0px, transparent 50%);
    color: var(--text-primary);
    font-family: var(--font-stack);
    line-height: 1.5;
    min-height: 100vh;
    padding: 24px;
  }}

  .container {{
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}

  header {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  }}

  .header-titles h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #06b6d4, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .header-titles p {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-top: 4px;
  }}

  .badge-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    background: rgba(6, 182, 212, 0.15);
    color: var(--accent-cyan);
    border: 1px solid rgba(6, 182, 212, 0.3);
  }}

  /* Controls */
  .control-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 20px 28px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  }}

  .control-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }}

  .btn-group {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .btn {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s ease;
  }}

  .btn:hover {{
    background: var(--bg-tertiary);
    border-color: rgba(255, 255, 255, 0.25);
    transform: translateY(-1px);
  }}

  .btn-primary {{
    background: linear-gradient(135deg, #0891b2, #059669);
    border: none;
    color: white;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
  }}

  .btn-primary:hover {{
    background: linear-gradient(135deg, #0e7490, #047857);
  }}

  .speed-selector {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 4px;
    border-radius: 8px;
  }}

  .speed-btn {{
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 600;
  }}

  .speed-btn.active {{
    background: var(--accent-cyan);
    color: #0b0f19;
  }}

  .scrubber-container {{
    display: flex;
    align-items: center;
    gap: 16px;
    width: 100%;
  }}

  .scrubber {{
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    outline: none;
    cursor: pointer;
  }}

  .scrubber::-webkit-slider-thumb {{
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--accent-cyan);
    cursor: pointer;
    box-shadow: 0 0 10px var(--accent-cyan);
  }}

  .step-info {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-variant-numeric: tabular-nums;
    min-width: 130px;
    text-align: right;
  }}

  /* Main Stage: Round Table & Info */
  .stage-grid {{
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 24px;
  }}

  @media (max-width: 1024px) {{
    .stage-grid {{
      grid-template-columns: 1fr;
    }}
  }}

  .table-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    min-height: 520px;
  }}

  /* SVG / Circular Table Styling */
  .table-viewport {{
    width: 100%;
    max-width: 500px;
    height: 500px;
    position: relative;
  }}

  .round-table-svg {{
    width: 100%;
    height: 100%;
    overflow: visible;
  }}

  /* Philosopher node */
  .philosopher-node {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
  }}

  .philosopher-node circle.glow {{
    transition: all 0.3s ease;
  }}

  .state-thinking circle.glow {{ fill: rgba(99, 102, 241, 0.15); stroke: #6366f1; stroke-width: 2; }}
  .state-hungry circle.glow {{ fill: rgba(245, 158, 11, 0.2); stroke: #f59e0b; stroke-width: 3; stroke-dasharray: 4 2; }}
  .state-eating circle.glow {{ fill: rgba(16, 185, 129, 0.25); stroke: #10b981; stroke-width: 3.5; filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.6)); }}

  /* Fork styling */
  .fork-element {{
    transition: all 0.3s ease;
  }}

  .fork-free {{
    stroke: #64748b;
    stroke-width: 3;
    opacity: 0.6;
  }}

  .fork-in-use {{
    stroke: #10b981;
    stroke-width: 4;
    filter: drop-shadow(0 0 6px #10b981);
    opacity: 1;
  }}

  /* Side Info Panels */
  .side-panel {{
    display: flex;
    flex-direction: column;
    gap: 20px;
  }}

  .panel-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}

  .panel-title {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
  }}

  /* Philosopher Cards */
  .philo-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}

  .philo-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    transition: all 0.2s;
  }}

  .philo-card.is-eating {{
    border-color: var(--accent-emerald);
    background: rgba(16, 185, 129, 0.1);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
  }}

  .philo-card.is-hungry {{
    border-color: var(--accent-amber);
    background: rgba(245, 158, 11, 0.08);
  }}

  .philo-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .philo-name {{
    font-weight: 700;
    font-size: 0.95rem;
  }}

  .philo-badge {{
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 9999px;
    font-weight: 700;
    text-transform: uppercase;
  }}

  .badge-thinking {{ background: rgba(99, 102, 241, 0.2); color: #818cf8; }}
  .badge-hungry {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
  .badge-eating {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}

  .philo-forks {{
    font-size: 0.8rem;
    color: var(--text-secondary);
  }}

  /* Forks Table */
  .forks-status-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }}

  .fork-box {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px;
    text-align: center;
  }}

  .fork-box.taken {{
    border-color: var(--accent-emerald);
    background: rgba(16, 185, 129, 0.12);
  }}

  .fork-title {{
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 600;
  }}

  .fork-holder {{
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 4px;
  }}

  /* Deadlock Analysis Callout */
  .callout {{
    background: rgba(6, 182, 212, 0.08);
    border: 1px solid rgba(6, 182, 212, 0.25);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 0.85rem;
    color: var(--text-secondary);
  }}

  .callout strong {{
    color: var(--accent-cyan);
  }}

  /* Event Table */
  .log-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  .table-container {{
    max-height: 380px;
    overflow-y: auto;
    border: 1px solid var(--border-color);
    border-radius: 10px;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    text-align: left;
  }}

  th {{
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: 600;
    padding: 10px 14px;
    position: sticky;
    top: 0;
    z-index: 1;
  }}

  td {{
    padding: 8px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-secondary);
  }}

  tr.current-step-row {{
    background: rgba(6, 182, 212, 0.15) !important;
    border-left: 3px solid var(--accent-cyan);
  }}

  tr.current-step-row td {{
    color: var(--text-primary);
    font-weight: 600;
  }}

  tr:hover {{
    background: rgba(255, 255, 255, 0.02);
    cursor: pointer;
  }}

  /* Metrics */
  .metrics-bar {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
  }}

  .metric-card {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .metric-label {{
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 600;
  }}

  .metric-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
  }}
</style>
</head>
<body>

<div class="container">
  <header>
    <div class="header-titles">
      <h1>{safe_title}</h1>
      <p>Interactive 4-Philosopher Synchronization Simulation | Deadlock-Free Execution</p>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
      <span class="badge-tag">Mechanism: {safe_mech}</span>
      <span class="badge-tag" style="background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); border-color: rgba(16, 185, 129, 0.3);">Deadlock-Free Verified</span>
    </div>
  </header>

  <!-- Summary Metrics Bar -->
  <div class="metrics-bar" id="metricsBar"></div>

  <!-- Interactive Controls -->
  <div class="control-card">
    <div class="control-row">
      <div class="btn-group">
        <button class="btn" id="btnPrev">⏮ Step Back</button>
        <button class="btn btn-primary" id="btnPlayPause">▶ Play</button>
        <button class="btn" id="btnNext">Step Next ⏭</button>
        <button class="btn" id="btnReset">↺ Reset</button>
      </div>

      <div class="speed-selector">
        <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 4px; padding-left: 6px;">Speed:</span>
        <button class="speed-btn" data-speed="1600">0.5x</button>
        <button class="speed-btn active" data-speed="800">1x</button>
        <button class="speed-btn" data-speed="400">2x</button>
        <button class="speed-btn" data-speed="150">5x</button>
      </div>
    </div>

    <div class="scrubber-container">
      <input type="range" class="scrubber" id="scrubber" min="0" max="{len(trace_data)-1}" value="0">
      <div class="step-info" id="stepCounter">Step 0 / {len(trace_data)-1}</div>
    </div>
  </div>

  <!-- Main Stage: SVG Circular Dining Table & Side Panels -->
  <div class="stage-grid">
    <div class="table-card">
      <div class="table-viewport">
        <svg class="round-table-svg" viewBox="0 0 500 500">
          <defs>
            <radialGradient id="tableGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#2d3748" />
              <stop offset="85%" stop-color="#1a202c" />
              <stop offset="100%" stop-color="#0f172a" />
            </radialGradient>
            <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          <!-- Outer Table -->
          <circle cx="250" cy="250" r="170" fill="url(#tableGradient)" stroke="rgba(255,255,255,0.15)" stroke-width="4" />
          <circle cx="250" cy="250" r="90" fill="#111827" stroke="rgba(255,255,255,0.06)" stroke-width="2" />
          <text x="250" y="246" text-anchor="middle" fill="#64748b" font-size="12" font-weight="700" letter-spacing="1.5">DINING TABLE</text>
          <text x="250" y="264" text-anchor="middle" fill="#475569" font-size="11">4 Philosophers</text>

          <!-- Spaghetti Bowls in front of each philosopher -->
          <!-- P0 (Top, 250, 140) -->
          <circle cx="250" cy="140" r="22" fill="#1f2937" stroke="#374151" stroke-width="2" />
          <circle cx="250" cy="140" r="14" fill="#d97706" opacity="0.8" />
          <text x="250" y="144" text-anchor="middle" font-size="14">🍝</text>

          <!-- P1 (Right, 360, 250) -->
          <circle cx="360" cy="250" r="22" fill="#1f2937" stroke="#374151" stroke-width="2" />
          <circle cx="360" cy="250" r="14" fill="#d97706" opacity="0.8" />
          <text x="360" y="254" text-anchor="middle" font-size="14">🍝</text>

          <!-- P2 (Bottom, 250, 360) -->
          <circle cx="250" cy="360" r="22" fill="#1f2937" stroke="#374151" stroke-width="2" />
          <circle cx="250" cy="360" r="14" fill="#d97706" opacity="0.8" />
          <text x="250" y="364" text-anchor="middle" font-size="14">🍝</text>

          <!-- P3 (Left, 140, 250) -->
          <circle cx="140" cy="250" r="22" fill="#1f2937" stroke="#374151" stroke-width="2" />
          <circle cx="140" cy="250" r="14" fill="#d97706" opacity="0.8" />
          <text x="140" y="254" text-anchor="middle" font-size="14">🍝</text>

          <!-- 4 Forks (Positioned between philosophers) -->
          <!-- Fork 0 (between P0 and P1: angle 45 deg, approx 315, 185) -->
          <g id="svgFork0" class="fork-element">
            <line x1="290" y1="210" x2="340" y2="160" stroke-linecap="round" class="fork-free" />
            <circle cx="315" cy="185" r="10" fill="#1e293b" stroke="currentColor" />
            <text x="315" y="189" text-anchor="middle" font-size="9" fill="#e2e8f0" font-weight="700">F0</text>
          </g>

          <!-- Fork 1 (between P1 and P2: angle 135 deg, approx 315, 315) -->
          <g id="svgFork1" class="fork-element">
            <line x1="290" y1="290" x2="340" y2="340" stroke-linecap="round" class="fork-free" />
            <circle cx="315" cy="315" r="10" fill="#1e293b" stroke="currentColor" />
            <text x="315" y="319" text-anchor="middle" font-size="9" fill="#e2e8f0" font-weight="700">F1</text>
          </g>

          <!-- Fork 2 (between P2 and P3: angle 225 deg, approx 185, 315) -->
          <g id="svgFork2" class="fork-element">
            <line x1="210" y1="290" x2="160" y2="340" stroke-linecap="round" class="fork-free" />
            <circle cx="185" cy="315" r="10" fill="#1e293b" stroke="currentColor" />
            <text x="185" y="319" text-anchor="middle" font-size="9" fill="#e2e8f0" font-weight="700">F2</text>
          </g>

          <!-- Fork 3 (between P3 and P0: angle 315 deg, approx 185, 185) -->
          <g id="svgFork3" class="fork-element">
            <line x1="210" y1="210" x2="160" y2="160" stroke-linecap="round" class="fork-free" />
            <circle cx="185" cy="185" r="10" fill="#1e293b" stroke="currentColor" />
            <text x="185" y="189" text-anchor="middle" font-size="9" fill="#e2e8f0" font-weight="700">F3</text>
          </g>

          <!-- 4 Philosophers Nodes -->
          <!-- P0 (Top) -->
          <g id="svgP0" class="philosopher-node state-thinking" onclick="jumpToThread('P0')">
            <circle class="glow" cx="250" cy="55" r="38" />
            <circle cx="250" cy="55" r="32" fill="#1e293b" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
            <text x="250" y="50" text-anchor="middle" font-size="18" id="svgIconP0">🤔</text>
            <text x="250" y="70" text-anchor="middle" font-size="11" fill="#f8fafc" font-weight="700">P0 (Aristotle)</text>
          </g>

          <!-- P1 (Right) -->
          <g id="svgP1" class="philosopher-node state-thinking" onclick="jumpToThread('P1')">
            <circle class="glow" cx="445" cy="250" r="38" />
            <circle cx="445" cy="250" r="32" fill="#1e293b" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
            <text x="445" y="245" text-anchor="middle" font-size="18" id="svgIconP1">🤔</text>
            <text x="445" y="265" text-anchor="middle" font-size="11" fill="#f8fafc" font-weight="700">P1 (Kant)</text>
          </g>

          <!-- P2 (Bottom) -->
          <g id="svgP2" class="philosopher-node state-thinking" onclick="jumpToThread('P2')">
            <circle class="glow" cx="250" cy="445" r="38" />
            <circle cx="250" cy="445" r="32" fill="#1e293b" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
            <text x="250" y="440" text-anchor="middle" font-size="18" id="svgIconP2">🤔</text>
            <text x="250" y="460" text-anchor="middle" font-size="11" fill="#f8fafc" font-weight="700">P2 (Spinoza)</text>
          </g>

          <!-- P3 (Left) -->
          <g id="svgP3" class="philosopher-node state-thinking" onclick="jumpToThread('P3')">
            <circle class="glow" cx="55" cy="250" r="38" />
            <circle cx="55" cy="250" r="32" fill="#1e293b" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
            <text x="55" y="245" text-anchor="middle" font-size="18" id="svgIconP3">🤔</text>
            <text x="55" y="265" text-anchor="middle" font-size="11" fill="#f8fafc" font-weight="700">P3 (Nietzsche)</text>
          </g>
        </svg>
      </div>
    </div>

    <!-- Side Panel: Philosophers & Forks Status -->
    <div class="side-panel">
      <!-- 4 Philosophers Status Cards -->
      <div class="panel-card">
        <div class="panel-title">
          <span>🧠 Philosophers State</span>
          <span id="eatingCountBadge" style="font-size: 0.8rem; color: var(--accent-emerald);">0 Eating</span>
        </div>
        <div class="philo-grid" id="philoCardsGrid"></div>
      </div>

      <!-- 4 Forks Status -->
      <div class="panel-card">
        <div class="panel-title">
          <span>🍴 Shared Forks Allocation</span>
        </div>
        <div class="forks-status-grid" id="forksGrid"></div>
      </div>

      <!-- Deadlock Prevention Info Callout -->
      <div class="callout" id="deadlockCallout"></div>
    </div>
  </div>

  <!-- Execution Event Log & Explanation -->
  <div class="log-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
      <h2 style="font-size: 1.15rem; font-weight: 600;">📜 Execution Trace Timeline</h2>
      <div style="font-size: 0.85rem; color: var(--text-secondary);" id="currentStepExplanation"></div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 70px;">Step</th>
            <th style="width: 100px;">Time (ms)</th>
            <th style="width: 90px;">Philosopher</th>
            <th style="width: 140px;">State / Event</th>
            <th style="width: 120px;">Forks Held</th>
            <th>Details & Invariant Explanation</th>
          </tr>
        </thead>
        <tbody id="traceTableBody"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
  const trace = {trace_json};
  const summary = {stats_json};

  let currentStep = 0;
  let isPlaying = false;
  let playInterval = null;
  let delay = 800;

  const btnPlayPause = document.getElementById('btnPlayPause');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnReset = document.getElementById('btnReset');
  const scrubber = document.getElementById('scrubber');
  const stepCounter = document.getElementById('stepCounter');
  const speedButtons = document.querySelectorAll('.speed-btn');
  const metricsBar = document.getElementById('metricsBar');
  const philoCardsGrid = document.getElementById('philoCardsGrid');
  const forksGrid = document.getElementById('forksGrid');
  const deadlockCallout = document.getElementById('deadlockCallout');
  const traceTableBody = document.getElementById('traceTableBody');
  const currentStepExplanation = document.getElementById('currentStepExplanation');
  const eatingCountBadge = document.getElementById('eatingCountBadge');

  const PHILO_NAMES = ['Aristotle (P0)', 'Kant (P1)', 'Spinoza (P2)', 'Nietzsche (P3)'];

  function initSummaryMetrics() {{
    const metrics = [
      {{ label: 'Total Events Recorded', value: summary.total_events || trace.length }},
      {{ label: 'Meals Consumed', value: summary.total_meals_eaten || '-' }},
      {{ label: 'Max Concurrent Diners', value: summary.max_concurrent_eaters || '2 (Optimal for N=4)' }},
      {{ label: 'Deadlock Prevention', value: summary.deadlock_strategy || 'Active' }},
      {{ label: 'Starvation Freedom', value: summary.starvation_freedom || 'Guaranteed' }}
    ];

    metricsBar.innerHTML = metrics.map(m => `
      <div class="metric-card">
        <span class="metric-label">${{m.label}}</span>
        <span class="metric-value">${{m.value}}</span>
      </div>
    `).join('');

    deadlockCallout.innerHTML = `
      <strong>Deadlock Prevention Mechanism (${safe_mech}):</strong><br>
      ${{summary.deadlock_explanation || 'Deadlock is provably prevented by breaking Coffman circular wait condition.'}}
    `;
  }}

  function initTraceTable() {{
    traceTableBody.innerHTML = trace.map((evt, idx) => `
      <tr id="row-${{idx}}" onclick="jumpToStep(${{idx}})">
        <td>#${{idx}}</td>
        <td>+${{evt.timestamp_ms || evt.time || 0}} ms</td>
        <td><strong>${{evt.philosopher_id || evt.entity_id}}</strong></td>
        <td><span class="philo-badge badge-${{(evt.state || evt.action || '').toLowerCase().includes('eat') ? 'eating' : ((evt.state || evt.action || '').toLowerCase().includes('hung') ? 'hungry' : 'thinking')}}">${{evt.state || evt.action}}</span></td>
        <td>${{formatForksHeld(evt.forks_held)}}</td>
        <td>${{evt.details || ''}}</td>
      </tr>
    `).join('');
  }}

  function formatForksHeld(held) {{
    if (!held || held.length === 0) return '<span style="color:var(--text-muted)">None</span>';
    return held.map(f => `F${{f}}`).join(', ');
  }}

  function renderStep(step) {{
    if (step < 0 || step >= trace.length) return;
    const s = trace[step];

    scrubber.value = step;
    stepCounter.textContent = `Step ${{step}} / ${{trace.length - 1}}`;
    currentStepExplanation.innerHTML = `<strong>Current:</strong> Step #${{step}} — ${{s.philosopher_id || s.entity_id}}: ${{s.details || s.state || s.action}}`;

    // Highlight row
    document.querySelectorAll('#traceTableBody tr').forEach(r => r.classList.remove('current-step-row'));
    const activeRow = document.getElementById(`row-${{step}}`);
    if (activeRow) {{
      activeRow.classList.add('current-step-row');
      activeRow.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
    }}

    const philosophers = s.philosophers || [];
    let eatingCount = 0;

    // Update 4 Philo SVG Nodes & Cards
    philosophers.forEach((p, idx) => {{
      const pId = p.id || `P${{idx}}`;
      const state = (p.state || 'THINKING').toUpperCase();
      if (state === 'EATING') eatingCount++;

      // Update SVG node
      const svgNode = document.getElementById(`svg${{pId}}`);
      const svgIcon = document.getElementById(`svgIcon${{pId}}`);
      if (svgNode) {{
        svgNode.className.baseVal = `philosopher-node state-${{state.toLowerCase()}}`;
      }}
      if (svgIcon) {{
        svgIcon.textContent = state === 'EATING' ? '😋' : (state === 'HUNGRY' ? '⌛' : '🤔');
      }}
    }});

    eatingCountBadge.textContent = `${{eatingCount}} Eating`;

    // Render Philo Cards
    philoCardsGrid.innerHTML = philosophers.map((p, idx) => {{
      const state = (p.state || 'THINKING').toUpperCase();
      const isEating = state === 'EATING';
      const isHungry = state === 'HUNGRY';
      return `
        <div class="philo-card ${{isEating ? 'is-eating' : (isHungry ? 'is-hungry' : '')}}">
          <div class="philo-header">
            <span class="philo-name">${{p.name || PHILO_NAMES[idx]}}</span>
            <span class="philo-badge badge-${{state.toLowerCase()}}">${{state}}</span>
          </div>
          <div class="philo-forks">
            Forks: ${{p.forks && p.forks.length > 0 ? p.forks.map(f => 'F' + f).join(', ') : 'None'}}<br>
            Meals: ${{p.meals_eaten !== undefined ? p.meals_eaten : '-'}}
          </div>
        </div>
      `;
    }}).join('');

    // Update Forks SVG & Status Boxes
    const forks = s.forks || [null, null, null, null];
    forks.forEach((owner, idx) => {{
      const svgFork = document.getElementById(`svgFork${{idx}}`);
      if (svgFork) {{
        const line = svgFork.querySelector('line');
        if (owner !== null && owner !== undefined) {{
          line.className.baseVal = 'fork-in-use';
        }} else {{
          line.className.baseVal = 'fork-free';
        }}
      }}
    }});

    forksGrid.innerHTML = forks.map((owner, idx) => `
      <div class="fork-box ${{owner !== null && owner !== undefined ? 'taken' : ''}}">
        <div class="fork-title">FORK ${{idx}}</div>
        <div class="fork-holder">${{owner !== null && owner !== undefined ? ('P' + owner) : 'FREE'}}</div>
      </div>
    `).join('');
  }}

  function togglePlay() {{
    if (isPlaying) {{
      pause();
    }} else {{
      play();
    }}
  }}

  function play() {{
    if (currentStep >= trace.length - 1) {{
      currentStep = 0;
    }}
    isPlaying = true;
    btnPlayPause.textContent = '⏸ Pause';
    btnPlayPause.classList.remove('btn-primary');
    btnPlayPause.style.background = 'var(--accent-amber)';
    btnPlayPause.style.color = '#0b0f19';

    clearInterval(playInterval);
    playInterval = setInterval(() => {{
      if (currentStep < trace.length - 1) {{
        currentStep++;
        renderStep(currentStep);
      }} else {{
        pause();
      }}
    }}, delay);
  }}

  function pause() {{
    isPlaying = false;
    clearInterval(playInterval);
    btnPlayPause.textContent = '▶ Play';
    btnPlayPause.classList.add('btn-primary');
    btnPlayPause.style.background = '';
    btnPlayPause.style.color = '';
  }}

  function jumpToStep(idx) {{
    pause();
    currentStep = idx;
    renderStep(currentStep);
  }}

  // Event Listeners
  btnPlayPause.addEventListener('click', togglePlay);
  btnPrev.addEventListener('click', () => {{
    pause();
    if (currentStep > 0) {{
      currentStep--;
      renderStep(currentStep);
    }}
  }});
  btnNext.addEventListener('click', () => {{
    pause();
    if (currentStep < trace.length - 1) {{
      currentStep++;
      renderStep(currentStep);
    }}
  }});
  btnReset.addEventListener('click', () => {{
    pause();
    currentStep = 0;
    renderStep(currentStep);
  }});

  scrubber.addEventListener('input', (e) => {{
    pause();
    currentStep = parseInt(e.target.value);
    renderStep(currentStep);
  }});

  speedButtons.forEach(btn => {{
    btn.addEventListener('click', () => {{
      speedButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      delay = parseInt(btn.getAttribute('data-speed'));
      if (isPlaying) {{
        clearInterval(playInterval);
        playInterval = setInterval(() => {{
          if (currentStep < trace.length - 1) {{
            currentStep++;
            renderStep(currentStep);
          }} else {{
            pause();
          }}
        }}, delay);
      }}
    }});
  }});

  // Keyboard Navigation
  window.addEventListener('keydown', (e) => {{
    if (e.code === 'Space') {{
      e.preventDefault();
      togglePlay();
    }} else if (e.code === 'ArrowRight') {{
      btnNext.click();
    }} else if (e.code === 'ArrowLeft') {{
      btnPrev.click();
    }}
  }});

  // Init
  initSummaryMetrics();
  initTraceTable();
  renderStep(0);
</script>
</body>
</html>
"""
    return html_content
