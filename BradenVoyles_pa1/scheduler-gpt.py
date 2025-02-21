import sys
import re

class Process:
    def __init__(self, name, arrival, burst, index):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_time = burst
        self.start_time = None
        self.finish_time = None
        self.wait_time = None
        self.turnaround_time = None
        self.response_time = None
        self.index = index

def parse_input_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    process_count = None
    run_for = None
    algorithm = None
    processes = []
    process_index = 0
    
    for line in lines:
        line = line.strip()
        if line.startswith("processcount"):
            match = re.search(r"\d+", line)
            if match:
                process_count = int(match.group())
            else:
                print("Error: Missing parameter processcount.")
                sys.exit(1)
        elif line.startswith("runfor"):
            match = re.search(r"\d+", line)
            if match:
                run_for = int(match.group())
            else:
                print("Error: Missing parameter runfor.")
                sys.exit(1)
        elif line.startswith("use"):
            if "fcfs" in line:
                algorithm = "fcfs"
            else:
                print("Error: Only 'fcfs' algorithm is supported.")
                sys.exit(1)
        elif line.startswith("process name"):
            match = re.match(r"process name (\S+) arrival (\d+) burst (\d+)", line)
            if match:
                name, arrival, burst = match.groups()
                processes.append(Process(name, int(arrival), int(burst), process_index))
                process_index += 1
            else:
                print("Error: Missing parameter in process definition.")
                sys.exit(1)
        elif line == "end":
            break
    
    if process_count is None:
        print("Error: Missing parameter processcount.")
        sys.exit(1)
    if run_for is None:
        print("Error: Missing parameter runfor.")
        sys.exit(1)
    if algorithm is None:
        print("Error: Missing parameter use.")
        sys.exit(1)
    if len(processes) != process_count:
        print("Error: Mismatch between processcount and actual processes.")
        sys.exit(1)
    
    return process_count, run_for, algorithm, processes

def fcfs_scheduler(run_for, processes):
    processes.sort(key=lambda p: p.arrival)
    output = []
    time = 0
    queue = []
    executing = None

    output.append(f"{len(processes):3} processes")
    output.append("Using First-Come First-Served")
    
    while time < run_for:
        for process in processes:
            if process.arrival == time:
                output.append(f"Time {time:3} : {process.name} arrived")
                queue.append(process)

        if executing and executing.remaining_time == 0:
            output.append(f"Time {time:3} : {executing.name} finished")
            executing.finish_time = time
            executing = None

        if not executing and queue:
            executing = queue.pop(0)
            executing.start_time = time
            executing.response_time = time - executing.arrival
            output.append(f"Time {time:3} : {executing.name} selected (burst {executing.burst:3})")

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
            process.turnaround_time = process.finish_time - process.arrival
            process.wait_time = process.turnaround_time - process.burst
            output.append(f"{process.name} wait {process.wait_time:3} turnaround {process.turnaround_time:3} response {process.response_time:3}")
    
    return output

def write_output_file(input_filename, output):
    output_filename = input_filename.replace(".in", ".out")
    with open(output_filename, 'w') as file:
        for line in output:
            file.write(line + "\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    if not input_filename.endswith(".in"):
        print("Error: Input file must have a '.in' extension.")
        sys.exit(1)
    
    process_count, run_for, algorithm, processes = parse_input_file(input_filename)
    output = fcfs_scheduler(run_for, processes)
    write_output_file(input_filename, output)

if __name__ == "__main__":
    main()
