
import threading
import time
import random
import json
import webbrowser
from pathlib import Path

# =========================================================
# READERS-WRITERS PROBLEM USING A MONITOR
# =========================================================

# A monitor combines a lock and condition variable.
monitor = threading.Condition()

# Shared resource state
active_readers = 0
active_writer = None
waiting_readers = 0
waiting_writers = 0

# Shared database
database_value = 100
version = 0

# Execution history
events = []
event_number = 0
start_time = time.perf_counter()


# =========================================================
# RECORD EXECUTION EVENTS
# =========================================================

def record_event(message, event_type="info"):
    """Record a consistent snapshot of the monitor state."""
    global event_number

    # Condition uses an RLock by default, so this can also
    # be called safely while the monitor is already acquired.
    with monitor:
        event_number += 1

        events.append({
            "number": event_number,
            "time": round(time.perf_counter() - start_time, 3),
            "message": message,
            "type": event_type,
            "active_readers": active_readers,
            "active_writer": active_writer,
            "waiting_readers": waiting_readers,
            "waiting_writers": waiting_writers,
            "database_value": database_value,
            "version": version
        })


# =========================================================
# READER THREAD
# =========================================================

def reader(reader_id):
    global active_readers, waiting_readers

    record_event(
        f"Reader {reader_id} thread created and ready.",
        "info"
    )

    # Every reader performs 3 reading operations
    for attempt in range(1, 4):

        with monitor:
            waiting_readers += 1

            record_event(
                f"Reader {reader_id}, operation {attempt}: "
                f"requests permission to read.",
                "request"
            )

            # Writer-priority monitor policy:
            # Readers wait if a writer is active OR waiting.
            while active_writer is not None or waiting_writers > 0:
                record_event(
                    f"Reader {reader_id} waits because a writer "
                    f"is active or waiting. Condition.wait() releases "
                    f"the monitor lock while waiting.",
                    "wait"
                )

                monitor.wait()

                record_event(
                    f"Reader {reader_id} woke up and rechecked "
                    f"the monitor conditions.",
                    "wake"
                )

            waiting_readers -= 1
            active_readers += 1

            record_event(
                f"Reader {reader_id} enters the reading section. "
                f"Active readers: {active_readers}.",
                "read"
            )

        # Read outside the monitor lock.
        # Other readers can read at the same time.
        time.sleep(random.uniform(0.2, 0.45))

        with monitor:
            value_read = database_value
            current_version = version

            record_event(
                f"Reader {reader_id}, operation {attempt}: "
                f"read value {value_read} at database version "
                f"{current_version}.",
                "read"
            )

            active_readers -= 1

            record_event(
                f"Reader {reader_id} leaves the reading section. "
                f"Active readers remaining: {active_readers}.",
                "release"
            )

            # When the last reader exits, waiting writers may proceed.
            if active_readers == 0:
                record_event(
                    "No active readers remain. Notifying threads "
                    "waiting on the monitor condition.",
                    "notify"
                )
                monitor.notify_all()

        time.sleep(random.uniform(0.1, 0.25))

    record_event(
        f"Reader {reader_id} completed all 3 reading operations.",
        "finish"
    )


# =========================================================
# WRITER THREAD
# =========================================================

def writer(writer_id):
    global active_writer, waiting_writers
    global database_value, version

    record_event(
        f"Writer {writer_id} thread created and ready.",
        "info"
    )

    # Every writer performs 2 writing operations
    for attempt in range(1, 3):

        with monitor:
            waiting_writers += 1

            record_event(
                f"Writer {writer_id}, operation {attempt}: "
                f"requests exclusive database access.",
                "request"
            )

            # A writer must wait until there are no active readers
            # and no other active writer.
            while active_writer is not None or active_readers > 0:
                record_event(
                    f"Writer {writer_id} waits because the resource "
                    f"is currently in use. Condition.wait() releases "
                    f"the monitor lock while waiting.",
                    "wait"
                )

                monitor.wait()

                record_event(
                    f"Writer {writer_id} woke up and rechecked "
                    f"the monitor conditions.",
                    "wake"
                )

            waiting_writers -= 1
            active_writer = writer_id

            record_event(
                f"Writer {writer_id} enters the writing section "
                f"with exclusive access.",
                "write"
            )

        # Simulate database modification outside the monitor lock.
        # The active_writer flag prevents readers and other writers
        # from entering while this writer works.
        time.sleep(random.uniform(0.3, 0.55))

        with monitor:
            old_value = database_value
            database_value += random.randint(5, 20)
            version += 1

            record_event(
                f"Writer {writer_id}, operation {attempt}: "
                f"database updated from {old_value} to "
                f"{database_value}; version is now {version}.",
                "write"
            )

            active_writer = None

            record_event(
                f"Writer {writer_id} leaves the writing section "
                f"and releases exclusive access.",
                "release"
            )

            record_event(
                "Writer finished. Notifying all threads waiting "
                "on the monitor condition.",
                "notify"
            )

            monitor.notify_all()

        time.sleep(random.uniform(0.1, 0.25))

    record_event(
        f"Writer {writer_id} completed both writing operations.",
        "finish"
    )


# =========================================================
# HTML VISUALIZATION GENERATOR
# =========================================================

def generate_html(event_data):
    output_file = Path(__file__).with_name(
        "readers_writers_monitor.html"
    )

    page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Readers-Writers Monitor Visualization</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 24px;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #172033;
}

header {
    background: #172554;
    color: white;
    padding: 24px;
    border-radius: 14px;
    margin-bottom: 20px;
}

header p {
    line-height: 1.6;
}

.panel {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 3px 12px #0000000b;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px;
}

.metric {
    background: #f8fafc;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

.metric span {
    display: block;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 8px;
}

.metric strong {
    font-size: 25px;
    overflow-wrap: anywhere;
}

#resource {
    padding: 16px;
    margin-top: 12px;
    border-radius: 10px;
    font-weight: bold;
}

button {
    padding: 10px 16px;
    margin: 4px;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
    background: #1d4ed8;
    color: white;
    font-weight: bold;
}

button:hover {
    background: #1e40af;
}

button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

input[type="range"] {
    width: 100%;
    margin: 16px 0;
}

#eventMessage {
    font-size: 17px;
    line-height: 1.7;
    overflow-wrap: anywhere;
}

#eventType {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 20px;
    background: #dbeafe;
    color: #1e40af;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}

.thread-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
}

.thread {
    padding: 14px;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    background: #f8fafc;
}

.thread strong {
    display: block;
    margin-bottom: 8px;
}

.thread .state {
    font-size: 13px;
    line-height: 1.5;
}

#eventList {
    max-height: 450px;
    overflow-y: auto;
}

.event-row {
    border-left: 4px solid #94a3b8;
    padding: 10px 12px;
    margin: 8px 0;
    background: #f8fafc;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    line-height: 1.5;
    overflow-wrap: anywhere;
    cursor: pointer;
}

.event-row.current {
    background: #dbeafe;
    border-left-color: #2563eb;
}

.small {
    color: #64748b;
    font-size: 13px;
}

.explanation li {
    margin: 10px 0;
    line-height: 1.6;
}

@media (max-width: 600px) {
    body {
        padding: 12px;
    }
}
</style>
</head>

<body>

<header>
    <h1>Readers-Writers Problem — Monitor</h1>
    <p>
        This simulation uses Python's threading.Condition to
        coordinate reader and writer threads. A monitor lock
        protects shared state, and condition variables allow
        threads to wait until access is safe.
    </p>
    <p id="progress">Loading execution...</p>
</header>

<section class="panel">
    <h2>System status</h2>

    <div class="grid">
        <div class="metric">
            <span>Current event</span>
            <strong id="eventNumber">0</strong>
        </div>

        <div class="metric">
            <span>Active readers</span>
            <strong id="activeReaders">0</strong>
        </div>

        <div class="metric">
            <span>Waiting readers</span>
            <strong id="waitingReaders">0</strong>
        </div>

        <div class="metric">
            <span>Waiting writers</span>
            <strong id="waitingWriters">0</strong>
        </div>

        <div class="metric">
            <span>Database value</span>
            <strong id="databaseValue">100</strong>
        </div>

        <div class="metric">
            <span>Database version</span>
            <strong id="version">0</strong>
        </div>
    </div>

    <div id="resource">Shared resource: Available</div>
    <p id="writerStatus">Active writer: None</p>
</section>

<section class="panel">
    <h2>Execution controls</h2>

    <button id="playButton" onclick="play()">Play</button>
    <button onclick="pause()">Pause</button>
    <button onclick="previous()">Previous</button>
    <button onclick="next()">Next</button>
    <button onclick="reset()">Reset</button>

    <input id="timeline" type="range" min="0" max="0"
           value="0" oninput="goTo(this.value)">

    <p class="small">
        Use the slider or event history to inspect execution step by step.
    </p>

    <span id="eventType">Start</span>
    <h3 id="eventTitle">Waiting to begin</h3>
    <p id="eventMessage">Press Play or Next to inspect the execution.</p>
    <p class="small" id="eventTime"></p>
</section>

<section class="panel">
    <h2>Thread activity</h2>
    <div class="thread-grid" id="threadGrid"></div>
</section>

<section class="panel">
    <h2>Execution event history</h2>
    <div id="eventList"></div>
</section>


<script>
const events = EVENT_DATA;

let current = 0;
let timer = null;

const readerIds = [1, 2, 3, 4, 5, 6];
const writerIds = [1, 2, 3];

function threadState(id, isWriter, e) {
    const m = e.message;

    if (isWriter && e.active_writer === id) {
        return "Writing / exclusive access";
    }

    if (!isWriter && m.includes("Reader " + id + " enters the reading")) {
        return "Reading";
    }

    if (!isWriter && m.includes("Reader " + id + ", operation")) {
        if (m.includes("requests permission")) return "Requesting access";
        if (m.includes("read value")) return "Reading completed";
    }

    if (m.includes((isWriter ? "Writer " : "Reader ") + id +
                   " completed")) {
        return "Finished";
    }

    if (m.includes((isWriter ? "Writer " : "Reader ") + id +
                   " waits")) {
        return "Waiting on condition";
    }

    if (m.includes((isWriter ? "Writer " : "Reader ") + id +
                   " woke up")) {
        return "Awake; checking condition";
    }

    if (isWriter && m.includes("Writer " + id + " enters the writing")) {
        return "Writing";
    }

    if (isWriter && m.includes("Writer " + id + ", operation")) {
        return "Requesting access";
    }

    if (m.includes((isWriter ? "Writer " : "Reader ") + id +
                   " leaves the")) {
        return "Leaving resource";
    }

    return "Ready / not active";
}

function renderThreads(e) {
    const grid = document.getElementById("threadGrid");
    let output = "";

    readerIds.forEach(id => {
        output += `
            <div class="thread">
                <strong>Reader ${id}</strong>
                <div class="state">${threadState(id, false, e)}</div>
            </div>`;
    });

    writerIds.forEach(id => {
        output += `
            <div class="thread">
                <strong>Writer ${id}</strong>
                <div class="state">${threadState(id, true, e)}</div>
            </div>`;
    });

    grid.innerHTML = output;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, ch => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[ch]);
}

function renderEventList() {
    const list = document.getElementById("eventList");

    list.innerHTML = events.map((e, i) => `
        <div class="event-row ${i === current ? "current" : ""}"
             onclick="goTo(${i})">
            <b>Event ${e.number}</b> · ${e.time}s
            <br>${escapeHtml(e.message)}
        </div>
    `).join("");

    const selected = list.querySelector(".current");

    if (selected) {
        selected.scrollIntoView({
            block: "nearest",
            behavior: "auto"
        });
    }
}

function render() {
    const e = events[current];
    if (!e) return;

    document.getElementById("eventNumber").textContent =
        `${current + 1} / ${events.length}`;

    document.getElementById("activeReaders").textContent =
        e.active_readers;

    document.getElementById("waitingReaders").textContent =
        e.waiting_readers;

    document.getElementById("waitingWriters").textContent =
        e.waiting_writers;

    document.getElementById("databaseValue").textContent =
        e.database_value;

    document.getElementById("version").textContent = e.version;

    const resource = document.getElementById("resource");

    if (e.active_writer !== null) {
        resource.textContent =
            "Resource: Held exclusively by Writer " + e.active_writer;
        resource.style.background = "#fee2e2";
        resource.style.color = "#991b1b";
    } else if (e.active_readers > 0) {
        resource.textContent =
            "Resource: Shared by " + e.active_readers + " reader(s)";
        resource.style.background = "#dbeafe";
        resource.style.color = "#1e40af";
    } else {
        resource.textContent = "Resource: Available";
        resource.style.background = "#dcfce7";
        resource.style.color = "#166534";
    }

    document.getElementById("writerStatus").textContent =
        "Active writer: " +
        (e.active_writer === null ? "None" : e.active_writer);

    document.getElementById("eventType").textContent = e.type;
    document.getElementById("eventTitle").textContent =
        "Event " + e.number;

    document.getElementById("eventMessage").textContent = e.message;

    document.getElementById("eventTime").textContent =
        "Elapsed time: " + e.time + " seconds";

    document.getElementById("progress").textContent =
        "Displaying event " + (current + 1) +
        " of " + events.length;

    document.getElementById("timeline").value = current;
    document.getElementById("playButton").disabled =
        current >= events.length - 1;

    renderThreads(e);
    renderEventList();
}

function goTo(value) {
    pause();
    current = Math.max(
        0, Math.min(Number(value), events.length - 1)
    );
    render();
}

function next() {
    pause();
    if (current < events.length - 1) {
        current++;
        render();
    }
}

function previous() {
    pause();
    if (current > 0) {
        current--;
        render();
    }
}

function reset() {
    pause();
    current = 0;
    render();
}

function play() {
    pause();

    if (current >= events.length - 1) {
        current = 0;
        render();
    }

    timer = setInterval(() => {
        if (current >= events.length - 1) {
            pause();
            return;
        }

        current++;
        render();
    }, 900);
}

function pause() {
    if (timer !== null) {
        clearInterval(timer);
        timer = null;
    }
}

document.getElementById("timeline").max = events.length - 1;
render();
</script>

</body>
</html>
"""

    page = page.replace("EVENT_DATA", json.dumps(event_data))
    output_file.write_text(page, encoding="utf-8")

    print("\nHTML visualization generated successfully!")
    print(f"Location: {output_file.resolve()}")
    print(f"Total events recorded: {len(event_data)}")

    webbrowser.open(output_file.resolve().as_uri())


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    start_time = time.perf_counter()

    print("=" * 60)
    print("READERS-WRITERS PROBLEM USING A MONITOR")
    print("=" * 60)
    print("Readers: 6")
    print("Writers: 3")
    print("Read operations per reader: 3")
    print("Write operations per writer: 2")
    print("Starting execution...\n")

    record_event(
        "Simulation started. Monitor is ready.",
        "start"
    )

    threads = []

    # Create 6 reader threads
    for reader_id in range(1, 7):
        threads.append(
            threading.Thread(
                target=reader,
                args=(reader_id,),
                name=f"Reader-{reader_id}"
            )
        )

    # Create 3 writer threads
    for writer_id in range(1, 4):
        threads.append(
            threading.Thread(
                target=writer,
                args=(writer_id,),
                name=f"Writer-{writer_id}"
            )
        )

    # Randomize start order to demonstrate concurrency
    random.shuffle(threads)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    record_event(
        "Simulation completed. All reader and writer threads finished.",
        "finish"
    )

    print("\nAll threads completed.")
    print(f"Final database value: {database_value}")
    print(f"Final database version: {version}")
    print(f"Total events: {len(events)}")

    generate_html(events)
