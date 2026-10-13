
import threading
import time
import random
import json
import webbrowser
from pathlib import Path

# ============================================================
# Q4: DINING PHILOSOPHERS USING MONITORS
# ============================================================

N = 4
MEALS_PER_PHILOSOPHER = 2

THINKING = "Thinking"
HUNGRY = "Hungry / Waiting"
ACQUIRING = "Acquiring Forks"
EATING = "Eating"
FINISHED = "Finished"

# Monitor: lock + condition variable
monitor = threading.Condition()

states = [THINKING] * N
fork_owner = [None] * N
meals_completed = [0] * N

events = []
event_lock = threading.Lock()
start_time = time.time()


def record_event(message):
    """Record a snapshot of the current shared state."""
    with monitor:
        snapshot = {
            "states": states.copy(),
            "fork_owner": fork_owner.copy(),
            "meals": meals_completed.copy()
        }

    with event_lock:
        events.append({
            "number": len(events) + 1,
            "time": round(time.time() - start_time, 2),
            "message": message,
            **snapshot
        })


def left_fork(i):
    return i


def right_fork(i):
    return (i + 1) % N


def can_eat(i):
    left_neighbor = (i - 1) % N
    right_neighbor = (i + 1) % N

    return (
        states[left_neighbor] != EATING
        and states[right_neighbor] != EATING
    )


def take_forks(i):
    with monitor:
        states[i] = HUNGRY
        record_event(f"Philosopher {i} is hungry and waiting")

        while not can_eat(i):
            monitor.wait()

        states[i] = ACQUIRING
        fork_owner[left_fork(i)] = i
        fork_owner[right_fork(i)] = i
        record_event(f"Philosopher {i} acquired both forks")

        states[i] = EATING
        record_event(f"Philosopher {i} started eating")


def put_forks(i):
    with monitor:
        fork_owner[left_fork(i)] = None
        fork_owner[right_fork(i)] = None
        states[i] = THINKING

        record_event(f"Philosopher {i} released both forks")

        monitor.notify_all()
        record_event("Monitor notified waiting philosophers")


def philosopher(i):
    for meal in range(MEALS_PER_PHILOSOPHER):
        with monitor:
            states[i] = THINKING

        record_event(f"Philosopher {i} is thinking")
        time.sleep(random.uniform(0.3, 0.7))

        take_forks(i)
        time.sleep(random.uniform(0.4, 0.8))

        with monitor:
            meals_completed[i] += 1

        record_event(f"Philosopher {i} completed meal {meal + 1}")
        put_forks(i)

    with monitor:
        states[i] = FINISHED

    record_event(f"Philosopher {i} finished all meals")


def generate_html(event_data):
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dining Philosophers - Monitor Simulation</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    font-family: Arial, sans-serif;
    background: #eff6ff;
    color: #172554;
}

.container {
    max-width: 1000px;
    margin: auto;
}

header {
    text-align: center;
    margin-bottom: 20px;
}

header h1 {
    color: #1d4ed8;
}

header p {
    color: #526581;
}

.panel {
    background: white;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 4px 16px #17255410;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

.stat {
    text-align: center;
    padding: 12px;
    background: #dbeafe;
    border-radius: 10px;
}

.stat strong {
    display: block;
    font-size: 22px;
    color: #1d4ed8;
    margin-top: 5px;
}

.arena {
    position: relative;
    width: min(100%, 620px);
    aspect-ratio: 1;
    margin: 15px auto;
}

.table {
    position: absolute;
    width: 43%;
    height: 43%;
    top: 28.5%;
    left: 28.5%;
    border-radius: 50%;
    background: #dbeafe;
    border: 5px solid #93c5fd;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    text-align: center;
    font-weight: bold;
    color: #1e40af;
}

.table small {
    margin-top: 8px;
    font-weight: normal;
}

.philosopher {
    position: absolute;
    width: 29%;
    min-height: 78px;
    padding: 10px 4px;
    border: 2px solid #93c5fd;
    border-radius: 12px;
    background: white;
    text-align: center;
    z-index: 2;
}

.name {
    font-weight: bold;
    margin-bottom: 8px;
}

.state {
    font-size: 12px;
    line-height: 1.4;
}

.p0 { top: 0; left: 35.5%; }
.p1 { top: 35.5%; right: 0; }
.p2 { bottom: 0; left: 35.5%; }
.p3 { top: 35.5%; left: 0; }

.fork {
    position: absolute;
    min-width: 76px;
    padding: 8px 4px;
    border: 2px solid #86efac;
    border-radius: 9px;
    background: #dcfce7;
    color: #166534;
    text-align: center;
    font-size: 12px;
    z-index: 3;
}

.fork.busy {
    background: #ffedd5;
    border-color: #fdba74;
    color: #9a3412;
}

.f0 { top: 23%; right: 22%; }
.f1 { bottom: 23%; right: 22%; }
.f2 { bottom: 23%; left: 22%; }
.f3 { top: 23%; left: 22%; }

.thinking {
    background: #dbeafe;
    border-color: #60a5fa;
}

.hungry {
    background: #fef3c7;
    border-color: #fbbf24;
}

.acquiring {
    background: #ffedd5;
    border-color: #fb923c;
}

.eating {
    background: #dcfce7;
    border-color: #4ade80;
}

.finished {
    background: #ede9fe;
    border-color: #a78bfa;
}

.legend {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
}

.legend span {
    background: #f3f4f6;
    padding: 7px;
    border-radius: 7px;
}

.current-event {
    min-height: 44px;
    font-weight: bold;
    line-height: 1.5;
    color: #1d4ed8;
}

.controls {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 12px 0;
}

button {
    border: 0;
    border-radius: 8px;
    padding: 10px 14px;
    background: #2563eb;
    color: white;
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

input[type=range] {
    width: 100%;
    accent-color: #2563eb;
}

.progress {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    font-size: 12px;
    color: #526581;
}

.meal-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.meal {
    text-align: center;
    padding: 12px;
    background: #dbeafe;
    border-radius: 10px;
}

.meal strong {
    display: block;
    font-size: 22px;
    color: #1d4ed8;
    margin-top: 5px;
}

.history-item {
    padding: 10px 12px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    border-radius: 6px;
    background: #eff6ff;
    font-size: 13px;
    line-height: 1.5;
}

.history-item.active {
    background: #dbeafe;
    border-left-color: #1d4ed8;
    font-weight: bold;
}

@media (max-width: 520px) {
    body { padding: 8px; }
    .panel { padding: 10px; }
    .philosopher { width: 32%; min-height: 68px; }
    .p0, .p2 { left: 34%; }
    .state { font-size: 10px; }
    .fork { min-width: 58px; font-size: 10px; }
    .f0, .f1 { right: 12%; }
    .f2, .f3 { left: 12%; }
    .stats { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<div class="container">

<header>
<h1>Dining Philosophers Problem</h1>
<p>Monitor Synchronization | Four Philosophers | Four Forks</p>
</header>

<section class="panel stats">
    <div class="stat">
        <strong id="eventNumber">0</strong>
        Current Event
    </div>
    <div class="stat">
        <strong id="eatingCount">0</strong>
        Philosophers Eating
    </div>
    <div class="stat">
        <strong id="availableForks">4</strong>
        Available Forks
    </div>
</section>

<section class="panel">
<h2>Simulation</h2>

<div class="arena">
    <div class="table">
        DINING TABLE
        <small>Monitor control</small>
    </div>

    <div class="philosopher p0" id="p0">
        <div class="name">Philosopher 0</div>
        <div class="state">Thinking</div>
    </div>

    <div class="philosopher p1" id="p1">
        <div class="name">Philosopher 1</div>
        <div class="state">Thinking</div>
    </div>

    <div class="philosopher p2" id="p2">
        <div class="name">Philosopher 2</div>
        <div class="state">Thinking</div>
    </div>

    <div class="philosopher p3" id="p3">
        <div class="name">Philosopher 3</div>
        <div class="state">Thinking</div>
    </div>

    <div class="fork f0" id="f0">Fork 0<br>Available</div>
    <div class="fork f1" id="f1">Fork 1<br>Available</div>
    <div class="fork f2" id="f2">Fork 2<br>Available</div>
    <div class="fork f3" id="f3">Fork 3<br>Available</div>
</div>

<div class="legend">
    <span>Thinking</span>
    <span>Hungry / Waiting</span>
    <span>Acquiring Forks</span>
    <span>Eating</span>
    <span>Finished</span>
</div>
</section>

<section class="panel">
<h2>Simulation Controls</h2>

<div class="current-event" id="message">
    Ready to begin simulation.
</div>

<div class="controls">
    <button onclick="previousEvent()">Previous</button>
    <button onclick="togglePlay()" id="playButton">Play</button>
    <button onclick="nextEvent()">Next</button>
    <button onclick="resetSimulation()">Reset</button>
</div>

<input type="range" id="timeline" min="0" max="0" value="0">

<div class="progress">
    <span id="progressText">Event 0 of 0</span>
    <span id="timeText">Time: 0.00 s</span>
</div>
</section>

<section class="panel">
<h2>Execution History</h2>
<div id="historyList"></div>
</section>

<section class="panel">
<h2>Meals Completed</h2>

<div class="meal-grid">
    <div class="meal">Philosopher 0<strong id="m0">0</strong></div>
    <div class="meal">Philosopher 1<strong id="m1">0</strong></div>
    <div class="meal">Philosopher 2<strong id="m2">0</strong></div>
    <div class="meal">Philosopher 3<strong id="m3">0</strong></div>
</div>
</section>

</div>

<script>
const events = EVENT_DATA;

let current = 0;
let playing = false;
let timer = null;

const classes = {
    "Thinking": "thinking",
    "Hungry / Waiting": "hungry",
    "Acquiring Forks": "acquiring",
    "Eating": "eating",
    "Finished": "finished"
};

function renderHistory() {
    const historyList = document.getElementById("historyList");

    historyList.innerHTML = events.map((event, index) => `
        <div class="history-item ${index === current ? "active" : ""}">
            <strong>Event ${event.number}</strong>
            — ${Number(event.time).toFixed(2)} s
            <br>
            ${event.message}
        </div>
    `).join("");
}

function render(index) {
    if (!events.length) return;

    current = Math.max(0, Math.min(index, events.length - 1));

    const e = events[current];

    document.getElementById("eventNumber").textContent = e.number;
    document.getElementById("message").textContent = e.message;

    document.getElementById("timeText").textContent =
        "Time: " + Number(e.time).toFixed(2) + " s";

    document.getElementById("progressText").textContent =
        "Event " + (current + 1) + " of " + events.length;

    document.getElementById("timeline").value = current;

    let eating = 0;
    let available = 0;

    e.states.forEach((state, i) => {
        const p = document.getElementById("p" + i);

        p.className =
            "philosopher p" + i + " " +
            (classes[state] || "thinking");

        p.querySelector(".state").textContent = state;

        document.getElementById("m" + i).textContent = e.meals[i];

        if (state === "Eating") {
            eating++;
        }
    });

    e.fork_owner.forEach((owner, i) => {
        const f = document.getElementById("f" + i);

        if (owner === null || owner === undefined) {
            f.className = "fork f" + i;
            f.innerHTML = "Fork " + i + "<br>Available";
            available++;
        } else {
            f.className = "fork f" + i + " busy";
            f.innerHTML =
                "Fork " + i + "<br>Philosopher " + owner;
        }
    });

    document.getElementById("eatingCount").textContent = eating;
    document.getElementById("availableForks").textContent = available;

    renderHistory();
}

function pause() {
    playing = false;
    clearInterval(timer);
    document.getElementById("playButton").textContent = "Play";
}

function nextEvent() {
    if (current < events.length - 1) {
        render(current + 1);
    } else {
        pause();
    }
}

function previousEvent() {
    pause();

    if (current > 0) {
        render(current - 1);
    }
}

function togglePlay() {
    if (playing) {
        pause();
        return;
    }

    if (current >= events.length - 1) {
        current = -1;
    }

    playing = true;
    document.getElementById("playButton").textContent = "Pause";

    timer = setInterval(() => {
        if (current >= events.length - 1) {
            pause();
            return;
        }

        render(current + 1);
    }, 900);
}

function resetSimulation() {
    pause();
    render(0);
}

const timeline = document.getElementById("timeline");

timeline.max = Math.max(0, events.length - 1);

timeline.addEventListener("input", () => {
    pause();
    render(Number(timeline.value));
});

render(0);
</script>

</body>
</html>"""

    html = html.replace("EVENT_DATA", json.dumps(event_data))

    output = Path("dining_philosophers_monitor.html").resolve()
    output.write_text(html, encoding="utf-8")

    print("HTML simulation created:", output)
    webbrowser.open(output.as_uri())


def main():
    global start_time

    start_time = time.time()
    record_event("Simulation started")

    threads = [
        threading.Thread(target=philosopher, args=(i,))
        for i in range(N)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    record_event("All philosophers completed their meals")

    generate_html(events)


if __name__ == "__main__":
    main()
