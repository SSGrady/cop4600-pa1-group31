# COP 4600 PA1 - Group 31 Schedulers

## Introduction
This project implements various CPU scheduling algorithms as part of the OS's Programming Assignment 1. It includes implementations of 
1. First-Come, First Serve (FCFS) ✅
2. Pre-emptive Shortest Job First (SJF) ✅ 
3. Round-Robin (RR) scheduling ✅ 

## Requirements

- Python 3.x

## Clone with SSH
To clone this repo, use the following command
```
git clone git@github.com:SSGrady/cop4600-pa1-group31.git
```

## Running the Scheduler
To run the scheduler you wish to test out, execute the `scheduler-gpt.py` script from `finalSolution/` alongside your chosen input file as the arguments

```
cd cop4600-pa1-group31/
python3 finalSolution/scheduler-gpt.py pa1-testfiles-1/<inputFile>.in
```

All outputs are dynamically generated and stored in the `outputs` directory

e.g., input

```
python3 finalSolution/scheduler-gpt.py pa1-testfiles-1/c5-fcfs.in
```
## Validation
Take your new output file and compare it to the existing unit case
```
# continuing with our previous example
diff output_files/c5-fcfs.out pa1-testfiles-1/c5-fcfs.out
```
