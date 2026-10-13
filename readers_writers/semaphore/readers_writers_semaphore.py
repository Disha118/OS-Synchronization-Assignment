
import threading
import time
import json
import random
import html
import webbrowser
from pathlib import Path

# =========================================================
# READERS-WRITERS PROBLEM USING SEMAPHORES
# =========================================================

# Synchronization tools
resource = threading.Semaphore(1)
reader_count_lock = threading.Lock()
state_lock = threading.Lock()

# Shared variables
reader_count = 0
active_readers = 0
active_writer = None
waiting_readers = 0
waiting_writers = 0

# Simulated shared database
database_value = 100
version = 0

# Execution history for the HTML visualization
events = []
event_number = 0


def record_event(message, event_type="info"):
    """Save a snapshot of the system after an execution event."""
    global event_number

    with state_lock:
        event_number += 1

        events.append({
            "number": event_number,
            "time": round(time.perf_counter() - start_time, 3),
            "message": message,
            "type": event_type,
            "reader_count": reader_count,
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
    global reader_count, active_readers, waiting_readers

    record_event(
        f"Reader {reader_id} has been created and is ready.",
        "info"
    )

    # Each reader performs three reading operations
    for attempt in range(1, 4):

        with state_lock:
            waiting_readers += 1

        record_event(
            f"Reader {reader_id}, operation {attempt}: "
            f"requests permission to read.",
            "request"
        )

        # Protect the reader counter
        with reader_count_lock:

            reader_count += 1

            record_event(
                f"Reader {reader_id}: reader count increased "
                f"to {reader_count}.",
                "lock"
            )

            # The first reader locks the shared resource
            if reader_count == 1:
                record_event(
                    f"Reader {reader_id}: first reader detected. "
                    f"Requesting the resource semaphore.",
                    "request"
                )

                resource.acquire()

                record_event(
                    f"Reader {reader_id}: acquired the resource "
                    f"semaphore. Writers cannot enter.",
                    "lock"
                )

            with state_lock:
                waiting_readers -= 1
                active_readers += 1

        record_event(
            f"Reader {reader_id} starts reading operation "
            f"{attempt}. Multiple readers may read together.",
            "read"
        )

        # Simulate reading from the shared database
        time.sleep(random.uniform(0.15, 0.4))

        value_read = database_value
        current_version = version

        record_event(
            f"Reader {reader_id} completed operation {attempt}: "
            f"read database value {value_read}, "
            f"version {current_version}.",
            "read"
        )

        # Finish reading and update reader counter
        with reader_count_lock:

            with state_lock:
                active_readers -= 1

            reader_count -= 1

            record_event(
                f"Reader {reader_id} finished reading. "
                f"Reader count is now {reader_count}.",
                "lock"
            )

            # The last reader releases the resource
            if reader_count == 0:
                resource.release()

                record_event(
                    f"Reader {reader_id}: last reader has left. "
                    f"Resource semaphore released; a writer may enter.",
                    "release"
                )

        # Pause before the next read operation
        time.sleep(random.uniform(0.1, 0.25))

    record_event(
        f"Reader {reader_id} completed all three reading operations.",
        "finish"
    )


# =========================================================
# WRITER THREAD
# =========================================================

def writer(writer_id):
    global active_writer, waiting_writers
    global database_value, version

    record_event(
        f"Writer {writer_id} has been created and is ready.",
        "info"
    )

    # Each writer performs two writing operations
    for attempt in range(1, 3):

        with state_lock:
            waiting_writers += 1

        record_event(
            f"Writer {writer_id}, operation {attempt}: "
            f"requests exclusive access to the database.",
            "request"
        )

        record_event(
            f"Writer {writer_id} is waiting for the resource semaphore.",
            "wait"
        )

        # Only one writer or group of readers can hold the resource
        resource.acquire()

        with state_lock:
            waiting_writers -= 1
            active_writer = writer_id

        record_event(
            f"Writer {writer_id} acquired the semaphore. "
            f"Exclusive writing access granted.",
            "lock"
        )

        record_event(
            f"Writer {writer_id} starts writing operation {attempt}.",
            "write"
        )

        # Simulate updating the shared database
        time.sleep(random.uniform(0.25, 0.5))

        old_value = database_value
        database_value += random.randint(5, 20)
        version += 1

        record_event(
            f"Writer {writer_id} updated the database from "
            f"{old_value} to {database_value}. "
            f"Database version is now {version}.",
            "write"
        )

        record_event(
            f"Writer {writer_id} completed writing operation {attempt}.",
            "write"
        )

        with state_lock:
            active_writer = None

        # Release the shared resource
        resource.release()

        record_event(
            f"Writer {writer_id} released the resource semaphore. "
            f"Other threads may now proceed.",
            "release"
        )

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
        "readers_writers_semaphore.html"
    )

    data_json = json.dumps(event_data)

    page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Readers-Writers Semaphore Visualization</title>

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

h1, h2 {
    margin-top: 0;
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
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
    border-radius: 10px;
    background: #dcfce7;
    color: #166534;
    font-weight: bold;
    margin-top: 12px;
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
    font-size: 18px;
    line-height: 1.7;
    overflow-wrap: anywhere;
}

#eventType {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    padding: 6px 10px;
    border-radius: 20px;
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
    max-height: 420px;
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
    line-height: 1.5;
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
    <h1>Readers-Writers Problem</h1>
    <p>
        Synchronization using a binary semaphore and a reader-count lock.
        Multiple readers may access the database together, but a writer
        needs exclusive access.
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
        Move the slider to inspect individual execution events.
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
    <p class="small">
        Select an event to inspect that point in the execution.
    </p>
    <div id="eventList"></div>
</section>



<script>
const events = EVENT_DATA;

let current = 0;
let timer = null;

const readerIds = [1, 2, 3, 4, 5, 6];
const writerIds = [1, 2, 3];

function inferThreadState(id, type, message, writer) {
    if (type === "finish" && message.includes("Reader " + id + " ")) {
        return "Finished";
    }

    if (message.includes("Reader " + id + " starts reading")) {
        return "Reading";
    }

    if (message.includes("Reader " + id + " completed operation")) {
        return "Read completed";
    }

    if (message.includes("Reader " + id + " requests")) {
        return "Requesting access";
    }

    if (message.includes("Reader " + id + ", operation")) {
        return "Requesting access";
    }

    if (message.includes("Reader " + id + " is waiting")) {
        return "Waiting";
    }

    if (message.includes("Reader " + id + " completed all")) {
        return "Finished";
    }

    if (message.includes("Writer " + id + " starts writing")) {
        return "Writing";
    }

    if (message.includes("Writer " + id + " updated")) {
        return "Writing completed";
    }

    if (message.includes("Writer " + id + " acquired")) {
        return "Has exclusive access";
    }

    if (message.includes("Writer " + id + " is waiting")) {
        return "Waiting for resource";
    }

    if (message.includes("Writer " + id + " released")) {
        return "Resource released";
    }

    if (message.includes("Writer " + id + " completed both")) {
        return "Finished";
    }

    return "Ready / not active";
}

function renderThreads(e) {
    const grid = document.getElementById("threadGrid");
    let output = "";

    readerIds.forEach(id => {
        let state = inferThreadState(
            id, e.type, e.message, false
        );

        // The snapshot is authoritative for currently active readers.
        if (e.active_readers > 0 &&
            e.message.includes("Reader " + id + " starts reading")) {
            state = "Reading";
        }

        output += `
            <div class="thread">
                <strong>Reader ${id}</strong>
                <div class="state">${state}</div>
            </div>`;
    });

    writerIds.forEach(id => {
        let state = inferThreadState(
            id, e.type, e.message, true
        );

        if (e.active_writer === id) {
            state = "Writing / exclusive access";
        }

        output += `
            <div class="thread">
                <strong>Writer ${id}</strong>
                <div class="state">${state}</div>
            </div>`;
    });

    grid.innerHTML = output;
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
            "Shared resource: Held exclusively by Writer " +
            e.active_writer;
        resource.style.background = "#fee2e2";
        resource.style.color = "#991b1b";
    } else if (e.active_readers > 0) {
        resource.textContent =
            "Shared resource: Held by " +
            e.active_readers + " active reader(s)";
        resource.style.background = "#dbeafe";
        resource.style.color = "#1e40af";
    } else {
        resource.textContent = "Shared resource: Available";
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

function renderEventList() {
    const list = document.getElementById("eventList");

    list.innerHTML = events.map((e, i) => `
        <div class="event-row ${i === current ? "current" : ""}"
             onclick="goTo(${i})">
            <b>Event ${e.number}</b>
            · ${e.time}s
            <br>
            ${escapeHtml(e.message)}
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

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, ch => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[ch]);
}

function goTo(value) {
    pause();
    current = Number(value);
    current = Math.max(0, Math.min(current, events.length - 1));
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

    page = page.replace("EVENT_DATA", data_json)
    output_file.write_text(page, encoding="utf-8")

    print("\nHTML visualization created successfully!")
    print(f"File location: {output_file.resolve()}")
    print(f"Total recorded events: {len(event_data)}")

    # Automatically open the HTML visualization
    webbrowser.open(output_file.resolve().as_uri())


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    start_time = time.perf_counter()

    print("=" * 60)
    print("READERS-WRITERS PROBLEM USING SEMAPHORES")
    print("=" * 60)
    print("Readers: 6")
    print("Writers: 3")
    print("Reading operations per reader: 3")
    print("Writing operations per writer: 2")
    print("Starting concurrent execution...\n")

    # Record the initial state
    record_event(
        "Simulation started. The shared database is available.",
        "start"
    )

    threads = []

    # Create six reader threads
    for reader_id in range(1, 7):
        thread = threading.Thread(
            target=reader,
            args=(reader_id,),
            name=f"Reader-{reader_id}"
        )
        threads.append(thread)

    # Create three writer threads
    for writer_id in range(1, 4):
        thread = threading.Thread(
            target=writer,
            args=(writer_id,),
            name=f"Writer-{writer_id}"
        )
        threads.append(thread)

    # Start all threads
    random.shuffle(threads)

    for thread in threads:
        thread.start()

    # Wait until every thread finishes
    for thread in threads:
        thread.join()

    record_event(
        "Simulation finished. All readers and writers have completed.",
        "finish"
    )

    print("\nAll threads completed successfully.")
    print(f"Final database value: {database_value}")
    print(f"Final database version: {version}")
    print(f"Total events recorded: {len(events)}")

    # Generate HTML from the actual execution trace
    generate_html(events)
