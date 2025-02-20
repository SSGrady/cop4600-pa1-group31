# cop4600-pa1-group31/stevengrady_pa1/scheduler-gpt.py
import sys
import os
import re
from collections import deque
from typing import List, Tuple, Dict

class Process:
    def __init__(self, name: str, arrival_time: int, burst_time: int):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.finish_time = None
        self.response_time = None

def parse_inputs(file_path: str) -> Tuple[str, List[Process], int, int]:
    if not os.path.isfile(file_path):
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    with open(file_path, 'r') as file:
        lines = file.readlines()

    if not lines:
        print("Error: Input file is empty")
        sys.exit(1)

    process_count = 0
    run_for = 0
    scheduling_type = ''
    quantum = None
    processes = []

    for line in lines:
        line = line.split('#')[0].strip()  # Remove comments and strip whitespace
        if not line:
            continue

        parts = line.split()
        if parts[0] == 'processcount':
            try:
                process_count = int(parts[1])
            except (IndexError, ValueError):
                print("Error: Invalid process count")
                sys.exit(1)
        elif parts[0] == 'runfor':
            try:
                run_for = int(parts[1])
            except (IndexError, ValueError):
                print("Error: Invalid run time")
                sys.exit(1)
        elif parts[0] == 'use':
            try:
                scheduling_type = parts[1].lower()
            except IndexError:
                print("Error: Missing scheduling type")
                sys.exit(1)
        elif parts[0] == 'quantum':
            try:
                quantum = int(parts[1])
            except (IndexError, ValueError):
                print("Error: Invalid quantum value")
                sys.exit(1)
        elif parts[0] == 'process' and parts[1] == 'name':
            try:
                name = parts[2]
                arrival_index = parts.index('arrival') + 1
                burst_index = parts.index('burst') + 1
                arrival_time = int(parts[arrival_index])
                burst_time = int(parts[burst_index])
                processes.append(Process(name, arrival_time, burst_time))
            except (IndexError, ValueError):
                print("Error: Invalid process entry")
                sys.exit(1)
        elif parts[0] == 'end':
            break

    if len(processes) != process_count:
        print("Error: Process count does not match the number of processes defined")
        sys.exit(1)

    return scheduling_type, processes, quantum, run_for

def write_outputs(file_path: str, log: List[str]):
    with open(file_path, 'w') as file:
        for entry in log:
            file.write(entry + '\n')

def fifo_scheduling(processes: List[Process]) -> List[str]:
    log = []
    time = 0
    processes.sort(key=lambda p: p.arrival_time)
    queue = deque(processes)

    while queue:
        process = queue.popleft()
        if time < process.arrival_time:
            log.append(f"Time {time}: Idle")
            time = process.arrival_time
        log.append(f"Time {time}: {process.name} selected (burst {process.burst_time})")
        process.start_time = time
        time += process.burst_time
        process.finish_time = time
        process.response_time = process.start_time - process.arrival_time
        log.append(f"Time {time}: {process.name} finished")

    return log

def preemptive_sjf_scheduling(processes: List[Process]) -> List[str]:
    log = []
    time = 0
    processes.sort(key=lambda p: (p.arrival_time, p.burst_time))
    ready_queue = []
    current_process = None

    while processes or ready_queue or current_process:
        while processes and processes[0].arrival_time <= time:
            ready_queue.append(processes.pop(0))
            ready_queue.sort(key=lambda p: p.remaining_time)

        if current_process and current_process.remaining_time == 0:
            log.append(f"Time {time}: {current_process.name} finished")
            current_process.finish_time = time
            current_process = None

        if not current_process and ready_queue:
            current_process = ready_queue.pop(0)
            if current_process.start_time is None:
                current_process.start_time = time
                current_process.response_time = time - current_process.arrival_time
            log.append(f"Time {time}: {current_process.name} selected (burst {current_process.remaining_time})")

        if current_process:
            current_process.remaining_time -= 1

        time += 1

    return log

def round_robin_scheduling(processes: List[Process], quantum: int) -> List[str]:
    log = []
    time = 0
    queue = deque()
    processes.sort(key=lambda p: p.arrival_time)
    current_process = None
    quantum_counter = 0

    while processes or queue or current_process:
        while processes and processes[0].arrival_time <= time:
            queue.append(processes.pop(0))

        if current_process and current_process.remaining_time == 0:
            log.append(f"Time {time}: {current_process.name} finished")
            current_process.finish_time = time
            current_process = None
            quantum_counter = 0

        if quantum_counter == quantum:
            if current_process:
                queue.append(current_process)
            current_process = None
            quantum_counter = 0

        if not current_process and queue:
            current_process = queue.popleft()
            if current_process.start_time is None:
                current_process.start_time = time
                current_process.response_time = time - current_process.arrival_time
            log.append(f"Time {time}: {current_process.name} selected (burst {current_process.remaining_time})")

        if current_process:
            current_process.remaining_time -= 1
            quantum_counter += 1

        time += 1

    return log

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    input_file = sys.argv[1]
    scheduling_type, processes, quantum, run_for = parse_inputs(input_file)

    if scheduling_type == 'fcfs':
        log = fifo_scheduling(processes)
    elif scheduling_type == 'sjf':
        log = preemptive_sjf_scheduling(processes)
    elif scheduling_type == 'rr':
        if quantum is None:
            print("Error: Missing quantum parameter when use is 'rr'")
            sys.exit(1)
        log = round_robin_scheduling(processes, quantum)
    else:
        print("Error: Unknown scheduling type")
        sys.exit(1)

    # Create output directory if it doesn't exist
    if not os.path.exists('output_files'):
      os.makedirs('output_files')

    # Create output file
    output_file = os.path.join('output_files', re.sub(r'\.in$', '.out', os.path.basename(input_file)))
    write_outputs(output_file, log)

if __name__ == "__main__":
    main()