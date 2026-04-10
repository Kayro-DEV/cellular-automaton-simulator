
# Parallel Cellular Automaton Simulator

## Overview
This project implements a grid-based cellular automaton in Python that simulates 100 iterations of cell evolution based on custom rule sets. The system supports both serial and multiprocessing execution for performance optimization.

## Features
- File-based input/output for matrix data
- Custom rule engine using mathematical conditions (prime, Fibonacci, powers of two)
- Toroidal grid (wrap-around neighbors)
- Multiprocessing support for parallel execution

## Technologies
- Python
- Multiprocessing
- Algorithms & Data Structures

## How to Run
```bash
python final_project.py -i input.txt -o output.txt -p 4
