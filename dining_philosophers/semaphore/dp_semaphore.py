import threading
import time
import random
import json
import webbrowser
from pathlib import Path

# =========================================================
# DINING PHILOSOPHERS PROBLEM USING SEMAPHORES
# =========================================================

N = 4
MEALS_PER_PHILOSOPHER = 2

# One semaphore for each fork
forks = [threading.Semaphore(1) for _ in range(N)]

# Allow at most N-1 philosophers to compete for forks
room = threading.Semaphore(N - 1)

state_lock = threading.Lock()
event_lock = threading.Lock()

states = ["Thinking"] * N
fork_owner = [None] * N
meals_completed = [0] * N
events = []
event_number = 0
start_time = time.perf_counter()


# =========================================================
# RECORD EXECUTION EVENTS
# =========================================================

def record_event(message, event_type="info"):
    global event_number

    with state_lock:
        snapshot = {
            "states": states[:],
            "fork_owner": fork_owner[:],
            "meals_completed": meals_completed[:],
        }

    with event_lock:
        event_number += 1
        events.append({
            "number": event_number,
            "time": round(time.perf_counter() - start_time, 3),
            "message": message,
            "type": event_type,
            **snapshot,
        })


# =========================================================
# PHILOSOPHER THREAD
# =========================================================

def philosopher(i):
    left = i
    right = (i + 1) % N

    for meal in range(1, MEALS_PER_PHILOSOPHER + 1):

        with state_lock:
            states[i] = "Thinking"

        record_event(
            f"Philosopher {i + 1} is thinking before meal {meal}.",
            "thinking"
        )

        time.sleep(random.uniform(0.2, 0.6))

        with state_lock:
            states[i] = "Hungry / Waiting"

        record_event(
            f"Philosopher {i + 1} is hungry and requests "
            f"forks {left + 1} and {right + 1}.",
            "hungry"
        )

        # Enter the room semaphore
        room.acquire()

        record_event(
            f"Philosopher {i + 1} entered the room semaphore.",
            "room"
        )

        # Acquire left fork
        forks[left].acquire()

        with state_lock:
            fork_owner[left] = i
            states[i] = "Acquiring Forks"

        record_event(
            f"Philosopher {i + 1} acquired fork {left + 1}.",
            "acquire"
        )

        # Acquire right fork
        forks[right].acquire()

        with state_lock:
            fork_owner[right] = i
            states[i] = "Eating"

        record_event(
            f"Philosopher {i + 1} acquired fork {right + 1} "
            f"and starts eating meal {meal}.",
            "eat"
        )

        time.sleep(random.uniform(0.25, 0.55))

        with state_lock:
            meals_completed[i] += 1
            states[i] = "Releasing Forks"

        record_event(
            f"Philosopher {i + 1} finished meal {meal} "
            f"and is releasing the forks.",
            "release"
        )

        # Release right fork
        with state_lock:
            fork_owner[right] = None

        forks[right].release()

        record_event(
            f"Philosopher {i + 1} released fork {right + 1}.",
            "release"
        )

        # Release left fork
        with state_lock:
            fork_owner[left] = None

        forks[left].release()

        record_event(
            f"Philosopher {i + 1} released fork {left + 1}.",
            "release"
        )

        room.release()

        record_event(
            f"Philosopher {i + 1} released the room semaphore.",
            "room"
        )

    with state_lock:
        states[i] = "Finished"

    record_event(
        f"Philosopher {i + 1} completed all meals.",
        "finish"
    )


# =========================================================
# HTML VISUALIZATION GENERATOR
# =========================================================

def generate_html(event_data):

    output_file = Path(__file__).with_name(
        "dining_philosophers_semaphore.html"
    )

    page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dining Philosophers — Semaphores</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 22px;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #172033;
}

header {
    background: #172554;
    color: white;
    padding: 22px;
    border-radius: 14px;
    margin-bottom: 18px;
}

header p {
    line-height: 1.6;
}

.panel {
    background: white;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 3px 12px #0000000b;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
    gap: 10px;
}

.metric {
    background: #f8fafc;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

.metric span {
    display: block;
    color: #64748b;
    font-size: 13px;
    margin-bottom: 7px;
}

.metric strong {
    font-size: 23px;
}

button {
    padding: 10px 15px;
    margin: 4px;
    border: 0;
    border-radius: 8px;
    background: #1d4ed8;
    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #1e40af;
}

button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

input[type=range] {
    width: 100%;
    margin: 15px 0;
}

#eventMessage {
    font-size: 16px;
    line-height: 1.6;
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

.arena {
    position: relative;
    max-width: 720px;
    height: 540px;
    margin: 10px auto 0;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    overflow: hidden;
}

.table {
    position: absolute;
    width: 250px;
    height: 250px;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: #dbeafe;
    border: 9px solid #93c5fd;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-weight: bold;
    color: #1e3a8a;
    line-height: 1.5;
}

.phil {
    position: absolute;
    width: 155px;
    min-height: 82px;
    padding: 10px;
    border-radius: 12px;
    background: #e2e8f0;
    border: 2px solid #94a3b8;
    text-align: center;
    font-size: 13px;
    line-height: 1.45;
}

.phil strong {
    display: block;
    font-size: 15px;
    margin-bottom: 4px;
}

.p0 {
    left: 50%;
    top: 12px;
    transform: translateX(-50%);
}

.p1 {
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
}

.p2 {
    left: 50%;
    bottom: 12px;
    transform: translateX(-50%);
}

.p3 {
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
}

.fork {
    position: absolute;
    width: 105px;
    padding: 10px 5px;
    text-align: center;
    border-radius: 10px;
    background: #dcfce7;
    border: 2px solid #16a34a;
    font-size: 13px;
    font-weight: bold;
}

.f0 {
    left: calc(50% + 70px);
    top: calc(50% - 180px);
}

.f1 {
    right: calc(50% - 190px);
    top: calc(50% + 65px);
}

.f2 {
    left: calc(50% - 175px);
    top: calc(50% + 65px);
}

.f3 {
    left: calc(50% - 175px);
    top: calc(50% - 180px);
}

.thread-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
}

.thread {
    padding: 12px;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    background: #f8fafc;
}

.thread strong {
    display: block;
    margin-bottom: 7px;
}

#eventList {
    max-height: 390px;
    overflow-y: auto;
}

.event-row {
    border-left: 4px solid #94a3b8;
    padding: 10px 12px;
    margin: 7px 0;
    background: #f8fafc;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    line-height: 1.5;
    cursor: pointer;
    overflow-wrap: anywhere;
}

.event-row.current {
    background: #dbeafe;
    border-left-color: #2563eb;
}

.small {
    font-size: 13px;
    color: #64748b;
}

@media(max-width: 600px) {
    body {
        padding: 10px;
    }

    .arena {
        height: 610px;
    }

    .table {
        width: 180px;
        height: 180px;
    }

    .phil {
        width: 125px;
        font-size: 11px;
    }

    .f0 {
        left: calc(50% + 30px);
        top: calc(50% - 155px);
    }

    .f1 {
        right: calc(50% - 155px);
        top: calc(50% + 55px);
    }

    .f2 {
        left: calc(50% - 145px);
        top: calc(50% + 55px);
    }

    .f3 {
        left: calc(50% - 145px);
        top: calc(50% - 155px);
    }
}
</style>
</head>

<body>

<header>
    <h1>Dining Philosophers Problem — Semaphores</h1>
    <p>
        Four philosophers share four forks. Each fork is controlled
        by a semaphore, and a room semaphore allows at most three
        philosophers to compete for forks at once, preventing deadlock.
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
            <span>Eating now</span>
            <strong id="eating">0</strong>
        </div>
        <div class="metric">
            <span>Forks in use</span>
            <strong id="forksUsed">0 / 4</strong>
        </div>
        <div class="metric">
            <span>Total meals</span>
            <strong id="meals">0</strong>
        </div>
    </div>
</section>

<section class="panel">
    <h2>Dining table visualization</h2>
    <div class="arena">
        <div class="table">
            SHARED<br>DINING TABLE<br>
            <small>Semaphore control</small>
        </div>

        <div class="phil p0" id="p0"></div>
        <div class="phil p1" id="p1"></div>
        <div class="phil p2" id="p2"></div>
        <div class="phil p3" id="p3"></div>

        <div class="fork f0" id="f0"></div>
        <div class="fork f1" id="f1"></div>
        <div class="fork f2" id="f2"></div>
        <div class="fork f3" id="f3"></div>
    </div>

    <p class="small">
        Green forks are available; red forks are held by a philosopher.
        Philosopher cards show their state and meals completed.
    </p>
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

    <span id="eventType">Start</span>
    <h3 id="eventTitle">Waiting to begin</h3>
    <p id="eventMessage">
        Press Play or Next to inspect the execution.
    </p>
    <p class="small" id="eventTime"></p>
</section>

<section class="panel">
    <h2>Philosopher states</h2>
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

function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[c]));
}

function render() {
    const e = events[current];
    if (!e) return;

    document.getElementById("eventNumber").textContent =
        (current + 1) + " / " + events.length;

    document.getElementById("eating").textContent =
        e.states.filter(s => s === "Eating").length;

    document.getElementById("forksUsed").textContent =
        e.fork_owner.filter(x => x !== null).length + " / 4";

    document.getElementById("meals").textContent =
        e.meals_completed.reduce((a, b) => a + b, 0);

    e.states.forEach((s, i) => {
        const el = document.getElementById("p" + i);
        el.innerHTML =
            "<strong>Philosopher " + (i + 1) + "</strong>" +
            esc(s) + "<br>Meals: " + e.meals_completed[i];

        el.style.background =
            s === "Eating" ? "#bbf7d0" :
            s === "Hungry / Waiting" ? "#fef3c7" :
            s === "Acquiring Forks" ? "#fed7aa" :
            s === "Finished" ? "#ddd6fe" : "#e2e8f0";
    });

    e.fork_owner.forEach((owner, i) => {
        const el = document.getElementById("f" + i);
        el.innerHTML = "Fork " + (i + 1) + "<br>" +
            (owner === null ? "AVAILABLE" : "Held by P" + (owner + 1));

        el.style.background = owner === null ? "#dcfce7" : "#fee2e2";
        el.style.borderColor = owner === null ? "#16a34a" : "#dc2626";
    });

    document.getElementById("eventType").textContent = e.type;
    document.getElementById("eventTitle").textContent = "Event " + e.number;
    document.getElementById("eventMessage").textContent = e.message;
    document.getElementById("eventTime").textContent =
        "Elapsed time: " + e.time + " seconds";

    document.getElementById("progress").textContent =
        "Displaying event " + (current + 1) + " of " + events.length;

    document.getElementById("timeline").value = current;
    document.getElementById("playButton").disabled =
        current >= events.length - 1;

    document.getElementById("threadGrid").innerHTML =
        e.states.map((s, i) =>
            "<div class='thread'><strong>Philosopher " + (i + 1) +
            "</strong>" + esc(s) + "<br>Meals completed: " +
            e.meals_completed[i] + "</div>"
        ).join("");

    document.getElementById("eventList").innerHTML =
        events.map((x, i) =>
            "<div class='event-row " + (i === current ? "current" : "") +
            "' onclick='goTo(" + i + ")'><b>Event " + x.number +
            "</b> · " + x.time + "s<br>" + esc(x.message) + "</div>"
        ).join("");

    const selected = document.querySelector(".event-row.current");
    if (selected) selected.scrollIntoView({block: "nearest"});
}

function goTo(value) {
    pause();
    current = Math.max(0, Math.min(Number(value), events.length - 1));
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
    }, 800);
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
</html>"""

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

    print("=" * 60)
    print("DINING PHILOSOPHERS PROBLEM USING SEMAPHORES")
    print("=" * 60)
    print(f"Philosophers: {N}")
    print(f"Meals per philosopher: {MEALS_PER_PHILOSOPHER}")

    record_event(
        "Simulation started. Semaphore objects are ready.",
        "start"
    )

    threads = [
        threading.Thread(
            target=philosopher,
            args=(i,),
            name=f"Philosopher-{i + 1}"
        )
        for i in range(N)
    ]

    random.shuffle(threads)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    record_event(
        "Simulation completed. All philosophers finished.",
        "finish"
    )

    print("\nAll philosopher threads completed.")
    print(f"Total meals served: {sum(meals_completed)}")
    print(f"Total events recorded: {len(events)}")

    generate_html(events)
