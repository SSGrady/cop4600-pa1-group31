# Steven Grady, Braden Voyles, Jovanny Rebollar, Dallas Moody, Kiyoshi Iwasaki, Dallas Moody
# COP4600 - PA1, Group 31

import sys
import os
import re
import heapq
from typing import List, Tuple

class Process:
    def __init__(self, name: str, arrival_time: int, burst_time: int, index: int = None):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.finish_time = None
        self.response_time = None
        self.index = index 

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
    process_index = 0

    for line in lines:
        line = line.split('#')[0].strip()
        if not line:
            continue

        parts = line.split()
        if parts[0] == 'processcount':
            process_count = int(parts[1])
        elif parts[0] == 'runfor':
            run_for = int(parts[1])
        elif parts[0] == 'use':
            scheduling_type = parts[1].lower()
        elif parts[0] == 'quantum':
            quantum = int(parts[1])
        elif parts[0] == 'process' and parts[1] == 'name':
            name = parts[2]
            arrival_time = int(parts[4])
            burst_time = int(parts[6])
            processes.append(Process(name, arrival_time, burst_time, process_index))  # Add index
            process_index += 1
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

def preemptive_sjf_scheduling(processes: List[Process], run_for: int) -> List[str]:
    log = []
    time = 0
    processes.sort(key=lambda p: p.arrival_time)
    ready_queue = []
    current_process = None
    process_index = 0
    process_count = len(processes)

    log.append(f"{process_count} processes")
    log.append("Using preemptive Shortest Job First")
    log.append("")

    while time < run_for:
        # Check if current process has finished
        if current_process and current_process.remaining_time == 0:
            log.append(f"Process {current_process.name} finished at time {time}")
            current_process = None

        # Add arriving processes to ready queue
        while process_index < process_count and processes[process_index].arrival_time == time:
            new_process = processes[process_index]
            heapq.heappush(ready_queue, (new_process.remaining_time, new_process.arrival_time, new_process.name, new_process))
            log.append(f"Process {new_process.name} arrives at time {time}")
            process_index += 1

        # Select next process from ready queue
        if ready_queue:
            next_process_tuple = heapq.heappop(ready_queue)
            next_process = next_process_tuple[3]

            # Preempt if a shorter job is available
            if current_process and next_process.remaining_time < current_process.remaining_time:
                heapq.heappush(ready_queue, (current_process.remaining_time, current_process.arrival_time, current_process.name, current_process))
                if next_process.start_time is None:
                    next_process.start_time = time
                    next_process.response_time = time - next_process.arrival_time
                if not current_process or current_process.name != next_process.name:
                    log.append(f"Process {next_process.name} selected at time {time}")
                current_process = next_process
            elif not current_process:
                if next_process.start_time is None:
                    next_process.start_time = time
                    next_process.response_time = time - next_process.arrival_time
                if not current_process or current_process.name != next_process.name:
                    log.append(f"Process {next_process.name} selected at time {time}")
                current_process = next_process
            else:
                heapq.heappush(ready_queue, (next_process.remaining_time, next_process.arrival_time, next_process.name, next_process))

        # Execute the current process
        if current_process:
            current_process.remaining_time -= 1
        elif not ready_queue and process_index >= process_count:
            log.append(f"CPU idle at time {time}")
            time += 1
            continue

        time += 1

    log.append(f"Finished at time {run_for}")
    return log

def fcfs_scheduler(processes: List[Process], run_for: int) -> List[str]:
    processes.sort(key=lambda p: p.arrival_time)
    output = []
    time = 0
    queue = []
    executing = None

    output.append(f"{len(processes):3} processes")
    output.append("Using First-Come First-Served")

    while time < run_for:
        for process in processes:
            if process.arrival_time == time:
                output.append(f"Time {time:3} : {process.name} arrived")
                queue.append(process)

        if executing and executing.remaining_time == 0:
            output.append(f"Time {time:3} : {executing.name} finished")
            executing.finish_time = time
            executing = None

        if not executing and queue:
            executing = queue.pop(0)
            executing.start_time = time
            executing.response_time = time - executing.arrival_time
            output.append(f"Time {time:3} : {executing.name} selected (burst {executing.burst_time:3})")

        if executing:
            executing.remaining_time -= 1
        else:
            output.append(f"Time {time:3} : Idle")

        time += 1

    output.append(f"Finished at time {run_for:3}")

    processes.sort(key=lambda p: p.index)
    output.append("")
    for process in processes:
        if process.finish_time is None:
            output.append(f"{process.name} did not finish")
        else:
            turnaround_time = process.finish_time - process.arrival_time
            wait_time = turnaround_time - process.burst_time
            output.append(f"{process.name} wait {wait_time:3} turnaround {turnaround_time:3} response {process.response_time:3}")

    return output

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    input_file = sys.argv[1]
    scheduling_type, processes, quantum, run_for = parse_inputs(input_file)

    if scheduling_type == 'sjf':
        log = preemptive_sjf_scheduling(processes, run_for)
    elif scheduling_type == 'fcfs':
        log = fcfs_scheduler(processes, run_for)
    else:
        print("Error: Unsupported scheduling type")
        sys.exit(1)

    if not os.path.exists('output_files'):
        os.makedirs('output_files')

    output_file = os.path.join('output_files', re.sub(r'\.in$', '.out', os.path.basename(input_file)))
    write_outputs(output_file, log)

if __name__ == "__main__":
    main()
