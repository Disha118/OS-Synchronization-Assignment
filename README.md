
# Operating Systems Programming Assignment

## Overview

This project implements four classic Operating Systems synchronization problems using Python multithreading. It demonstrates how semaphores and monitors can be used to coordinate multiple threads, manage shared resources, and prevent synchronization issues.

The project also includes HTML-based simulations to visualize thread execution, resource allocation, waiting states, and synchronization events.

## Objectives

- To understand process and thread synchronization.
- To implement the Readers-Writers problem using semaphores and monitors.
- To implement the Dining Philosophers problem using semaphores and monitors.
- To demonstrate mutual exclusion and race-condition prevention.
- To study deadlock prevention and starvation.
- To generate HTML simulations for visualizing execution events.

## Programs Included

### 1. Readers-Writers Problem Using Semaphores
Implements synchronization using semaphores and locks to control access to a shared database. Multiple readers can read simultaneously, while writers require exclusive access.

### 2. Readers-Writers Problem Using Monitors
Uses Python's `threading.Condition` to coordinate readers and writers and manage access to the shared database.

### 3. Dining Philosophers Problem Using Semaphores
Uses semaphores to control access to forks. A room semaphore limits the number of philosophers attempting to acquire forks simultaneously to help prevent deadlock.

### 4. Dining Philosophers Problem Using Monitors
Uses monitor-style synchronization with condition variables to coordinate philosophers and ensure that adjacent philosophers do not use the same fork simultaneously.

## Technologies Used

- **Programming Language:** Python
- **Threading:** Python `threading` module
- **Synchronization:** Semaphores, locks, condition variables
- **Visualization:** HTML, CSS, JavaScript
- **Supporting Modules:** `time`, `random`, `json`, `webbrowser`, and `pathlib`

## Project Structure

```text
Operating-Systems-Programming-Assignment/
│
├── readers_writers_semaphore.py
├── readers_writers_monitor.py
├── dining_philosophers_semaphore.py
├── dining_philosophers_monitor.py
│
├── readers_writers_semaphore.html
├── readers_writers_monitor.html
├── dining_philosophers_semaphore.html
├── dining_philosophers_monitor.html
│
├── README.md
└── Assignment_report.pdf
```

*Note: The structure above is a suggested layout. Adjust the filenames and folders to match the files actually present in your repository.*

## Requirements

- Python 3.10 or later recommended
- A modern web browser for viewing the HTML simulations

The Python programs use standard-library modules, so no additional Python packages are normally required.

## How to Run the Programs

Open a terminal in the project directory and run each Python file separately.

**Readers-Writers — Semaphore Solution**
```bash
python3 readers_writers_semaphore.py
```

**Readers-Writers — Monitor Solution**
```bash
python3 readers_writers_monitor.py
```

**Dining Philosophers — Semaphore Solution**
```bash
python3 dining_philosophers_semaphore.py
```

**Dining Philosophers — Monitor Solution**
```bash
python3 dining_philosophers_monitor.py
```

The programs execute the synchronization scenarios and record events according to their implementations. If the scripts generate HTML files automatically, open the generated files in a web browser to view the simulations.

## Key Concepts Demonstrated

- **Mutual Exclusion:** Preventing conflicting simultaneous access to shared resources.
- **Race Conditions:** Understanding problems caused by unsynchronized access to shared data.
- **Deadlock Prevention:** Using resource-management strategies to avoid circular waiting.
- **Starvation:** Understanding how a thread may wait indefinitely while other threads continue to make progress.
- **Thread Coordination:** Using semaphores, locks, and condition variables to manage concurrent execution.

## Observations

- Semaphores provide synchronization by controlling access to resources.
- Monitors combine shared-state protection with condition-based thread coordination.
- Multiple readers may access shared data concurrently when no writer is active.
- Writers require exclusive access to the shared database.
- Dining philosophers must coordinate fork usage to avoid conflicting access and deadlock.
- Thread execution order may vary between runs. Semaphores and condition variables do not inherently guarantee strict FIFO scheduling.

## AI Usage Disclosure

ChatGPT (OpenAI) was used as a supporting tool to understand synchronization concepts, assist with code development and debugging, explain program behavior, and prepare HTML-based simulations and documentation. The implementation and execution results were reviewed as part of the assignment.

## References

1. Silberschatz, A., Galvin, P. B., and Gagne, G., *Operating System Concepts*.
2. Downey, A. B., *The Little Book of Semaphores*: https://greenteapress.com/wp/semaphores/
3. Python Software Foundation, *threading — Thread-based parallelism*: https://docs.python.org/3/library/threading.html
4. Hoare, C. A. R., “Monitors: An Operating System Structuring Concept,” *Communications of the ACM*, 1974.
5. OpenAI, ChatGPT: https://chatgpt.com/

## Author

Operating Systems Programming Assignment

## License

This project was developed for educational and academic purposes.
