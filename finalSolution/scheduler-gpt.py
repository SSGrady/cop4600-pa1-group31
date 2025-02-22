# Steven Grady, Braden Voyles, Jovanny Rebollar, Dallas Moody, Kiyoshi Iwasaki, Dallas Moody
# COP4600 - PA1, Group 31

import sys
import os
import heapq
from collections import deque

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_time = burst
        self.start_time = None
        self.finish_time = None
        self.response_time = None
        self.wait_time = None
        self.turnaround_time = None


def parse_input(filename):
    if not os.path.isfile(filename):
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]

    process_count = 0
    run_for = 0
    scheduling_type = ''
    quantum = None
    processes = []

    for line in lines:
        parts = line.split()
        if not parts:
            continue

        if parts[0] == "processcount":
            process_count = int(parts[1])
        elif parts[0] == "runfor":
            run_for = int(parts[1])
        elif parts[0] == "use":
            scheduling_type = parts[1].lower()
        elif parts[0] == "quantum":
            quantum = int(parts[1])
        elif parts[0] == "process":
            name = parts[2]
            arrival = int(parts[4])
            burst = int(parts[6])
            processes.append(Process(name, arrival, burst))
        elif parts[0] == "end":
            break

    if scheduling_type == "rr" and quantum is None:
        print("Error: Missing quantum parameter when use is 'rr'")
        sys.exit(1)

    return scheduling_type, processes, quantum, run_for

def fcfs_scheduling(processes, run_for):
    processes.sort(key=lambda p: p.arrival)
    time = 0
    queue = deque()
    events = []
    executing = None

    while time < run_for:
        for p in processes:
            if p.arrival == time:
                events.append(f"Time {time:3} : {p.name} arrived")
                queue.append(p)

        if executing and executing.remaining_time == 0:
            events.append(f"Time {time:3} : {executing.name} finished")
            executing.finish_time = time
            executing = None

        if not executing and queue:
            executing = queue.popleft()
            executing.start_time = time
            executing.response_time = time - executing.arrival
            events.append(f"Time {time:3} : {executing.name} selected (burst {executing.burst:3})")

        if executing:
            executing.remaining_time -= 1
        else:
            events.append(f"Time {time:3} : Idle")

        time += 1

    events.append(f"Finished at time {run_for:3}")
    return events

def sjf_scheduling(processes, run_for):
    processes.sort(key=lambda p: p.arrival)  # Sort processes by arrival time
    ready_queue = []  # To hold processes in the ready queue
    time = 0
    events = []
    executing = None  # The current executing process
    process_index = 0  # To track which processes have arrived
    process_count = len(processes)

    finishedLogger = None

    while time < run_for:
        # Add arriving processes to the ready queue
        while process_index < process_count and processes[process_index].arrival == time:
            heapq.heappush(ready_queue, (processes[process_index].burst, process_index, processes[process_index]))
            events.append(f"Time {time:3} : {processes[process_index].name} arrived")
            process_index += 1
        
        if finishedLogger != None:
            events.append(f"Time {time:3} : {finishedLogger.name} finished")
            finishedLogger = None

        # Preempt the executing process if a new process with shorter burst arrives
        if executing and ready_queue and executing.remaining_time > ready_queue[0][2].remaining_time:
            # Preempt the executing process
            ready_queue.append((executing.remaining_time, process_index, executing))  # Re-insert the preempted process
            heapq.heapify(ready_queue)  # Re-heapify after inserting the preempted process
            executing = None

        # If no process is currently executing and there are processes in the ready queue, select the shortest job
        if not executing and ready_queue:
            _, _, executing = heapq.heappop(ready_queue)  # Select the shortest burst time process
            if executing.start_time is None:
                executing.start_time = time
                executing.response_time = time - executing.arrival
            events.append(f"Time {time:3} : {executing.name} selected (burst {executing.remaining_time:3})")

        # If a process is executing, continue to execute it until it finishes
        if executing:
            # Decrement the remaining burst time
            executing.remaining_time -= 1

            # If the process has finished, log the finish event **at the next time unit**
            if executing.remaining_time == 0:
                executing.finish_time = time + 1  # Process finishes at the next time unit
                finishedLogger = executing
                executing = None  # Set executing to None after finishing

        # Log idle time only if no process is executing and there are no processes in the ready queue
        elif not executing and not ready_queue:
            events.append(f"Time {time:3} : Idle")

        time += 1  # Increment the time at the end of the loop

    events.append(f"Finished at time {run_for:3}")
    return events



def round_robin_scheduling(processes, run_for, quantum):
    processes.sort(key=lambda p: p.arrival)
    queue = deque()
    time = 0
    events = []
    waiting_list = processes[:]

    while time < run_for:
        while waiting_list and waiting_list[0].arrival <= time:
            proc = waiting_list.pop(0)
            queue.append(proc)
            events.append(f"Time {time:3} : {proc.name} arrived")

        if queue:
            proc = queue.popleft()
            if proc.start_time is None:
                proc.start_time = time
                proc.response_time = time - proc.arrival
            exec_time = min(quantum, proc.remaining_time, run_for - time)
            events.append(f"Time {time:3} : {proc.name} selected (burst {proc.remaining_time:3})")
            proc.remaining_time -= exec_time
            new_time = time + exec_time

            while waiting_list and waiting_list[0].arrival <= new_time:
                next_proc = waiting_list.pop(0)
                queue.append(next_proc)
                events.append(f"Time {next_proc.arrival:3} : {next_proc.name} arrived")

            if proc.remaining_time > 0:
                queue.append(proc)
            else:
                proc.finish_time = new_time
                events.append(f"Time {new_time:3} : {proc.name} finished")
            time = new_time
        else:
            events.append(f"Time {time:3} : Idle")
            time += 1

    events.append(f"Finished at time {run_for:3}")
    return events

def write_output(filename, events, processes, scheduling_type, quantum=None):
    output_filename = filename.replace(".in", ".out")
    with open(output_filename, 'w') as file:
        file.write(f"{len(processes):3} processes\n")
        
        # Adjust the scheduling type display without extra line break
        if scheduling_type == "rr":
            file.write(f"Using Round-Robin\n")
            file.write(f"Quantum {quantum:3}\n\n")
        elif scheduling_type == "fcfs":
            file.write(f"Using First-Come First-Served\n")
        elif scheduling_type == "sjf":
            file.write(f"Using preemptive Shortest Job First\n")

        # Writing the events
        for event in events:
            file.write(event + "\n")

        file.write("\n")
        
        # Writing process statistics with consistent spacing
        for p in sorted(processes, key=lambda p: p.name):
            if p.finish_time is not None:
                p.turnaround_time = p.finish_time - p.arrival
                p.wait_time = p.turnaround_time - p.burst
                file.write(f"{p.name} wait {p.wait_time:3} turnaround {p.turnaround_time:3} response {p.response_time:3}\n")
            else:
                file.write(f"{p.name} did not finish\n")  # For unfinished processes

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    filename = sys.argv[1]
    scheduling_type, processes, quantum, run_for = parse_input(filename)

    # Scheduling based on type
    if scheduling_type == "rr":
        events = round_robin_scheduling(processes, run_for, quantum)
    elif scheduling_type == "fcfs":
        events = fcfs_scheduling(processes, run_for)
    elif scheduling_type == "sjf":
        events = sjf_scheduling(processes, run_for)
    else:
        print("Error: Unsupported scheduling type")
        sys.exit(1)

    write_output(filename, events, processes, scheduling_type, quantum)

if __name__ == "__main__":
    main()
