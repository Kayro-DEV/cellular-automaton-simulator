"""
Parallel Cellular Automaton Simulator

A Python program that reads a grid-based matrix from a file and simulates
100 iterations of cellular evolution using rule-based transformations.
Supports both serial and multiprocessing execution.
"""



import argparse
import os
import sys
import multiprocessing


#Data Retrieval - This function will parse and verify the command line arguments
def parse_arguments():
    #these will parse the command line arguments using argparse
    parser = argparse.ArgumentParser(description = "Parallel Cellular Automaton Simulator with Multiprocessing")

    parser.add_argument("-i", dest="input_path", required=True, help ="This is the path to the starting ceullar matrix file")

    parser.add_argument("-o", dest="output_path", required=True, help ="This is the path to the output ceullar matrix file")

    parser.add_argument("-p", dest="number_processes", required=False, type=int, default=1, help ="This is the number of processes to use for the simulation")



    #this will check if the input file exists if it does not it will print an error and exit
    args = parser.parse_args()

    if not os.path.isfile(args.input_path):
        print(f"Error: this input file does not exist. File: {args.input_path}", file=sys.stderr)
        sys.exit(1)

    #this will now check the output directory exists, exits after printing an error if nonexistent
    output_directory = os.path.dirname(args.output_path)

    if output_directory == "":
        output_directory = "."

    if not os.path.isdir(output_directory):
        print(f"Error: the output directory does not exist. Directory: {output_directory}", file=sys.stderr)
        sys.exit(1)
    
    #Final validation, validate the number of processes and ensure it is a positive integer, exits after printing an error if invalid number

    if args.number_processes <= 0: 
        print("Error: -p needs to be a positive integer that is greater than 0 ", file=sys.stderr)
        sys.exit(1)
    
    #return the parsed arugments
    return args.input_path, args.output_path, args.number_processes



def read_input_matrix(input_path):
    """
This function will read the input matrix from the given file path 
Then it will return a 2d list of the characters representing the matrix grid

It will exit with an error message if the file is not formatted properly(not all rows are the same length or invalid characters are present)

"""
    
    #this trys to open the file and goves an error if it cannot be opened
    try:
        with open(input_path, 'r') as file:
            datalines = file.readlines()
    except OSError as e:
        print(f"Error: Could not open input file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # This removes the whitespaces and empty lines
    matrix = []
    for line in datalines:
        stripped = line.strip()
        if stripped == "":
            continue
        matrix.append(stripped)

    # This checks if the matrix is empty
    if not matrix:
        print(f"Error: Input file '{input_path}' has no matrix data.", file=sys.stderr)
        sys.exit(1)

    # this checks if it is a rectangle shape 
    num_columns = len(matrix[0])
    if num_columns == 0:
        print(f"Error: First row of matrix is empty. File: {input_path}", file=sys.stderr)
        sys.exit(1)

    for row_index, row in enumerate(matrix):
        if len(row) != num_columns:
            print(
                f"Error: Matrix is not rectangular. "
                f"Row 0 has length {num_columns}, but row {row_index} has length {len(row)}.",
                file=sys.stderr
            )
            sys.exit(1)

    #these are the allowed characters
    allowed_characters = {'O', 'o', 'X', 'x', '.'}

    matrix_2d = []

    #THIS WILL TELLS US IF THERE ARE INVALID CHARACTERS OR NOT.
    for row_index, row in enumerate(matrix):
        row_list = []
        for col_index, char in enumerate(row):
            if char not in allowed_characters:
                print(
                    f"Error: Invalid character '{char}' at row {row_index}, column {col_index}.",
                    file=sys.stderr
                )
                sys.exit(1)
            row_list.append(char)
        matrix_2d.append(row_list)

    return matrix_2d

def write_output_matrix(output_path, matrix):

    """
    This function will write the matrix to the outputfle that is provided

    it will give an error message if it cannot be opened or written into
    """

    try:
        with open(output_path, 'w') as file:
            for row in matrix:

                line = ''.join(row)

                file.write(line + '\n')
    except OSError as e:
        print(f"Error: Cannot write output to a output file '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)

def get_around_sum(matrix, row, col):
    """This function will get the vlaue of the 8 surroudning cells 
apply the rules and build a matrix"""

    num_rows = len(matrix)
    num_cols = len(matrix[0])

    offsets = [(-1, -1),(-1, 0),(-1, 1),(0, -1),(0, 1),(1, -1),(1, 0),(1, 1)]
    charactervalue = { 'O': 3, 'o': 1, '.':0, 'x': -1, 'X': -3}

    total = 0

    for (drow,dcol) in offsets:
        aroundrow = (row + drow) % num_rows
        aroundcol = (col + dcol) % num_cols

        around_character = matrix[aroundrow][aroundcol]
        total += charactervalue[around_character]

    return total

#NUMBER FUNCTIONS (2 POWER, PRIME, FIBONACCI)

def power2(n):
    return n in {1,2,4,8,16}

def primal(n):
    return n in {2,3,5,7,11,13,17,19,23}

def fibonacci(n):
    return abs(n) in {0,1,2,3,5,8,13,21}

def trafalgar_law(cell, neighobouring_sum):
    """This function takes a cell and changes it according to the rules."""

    # living o
    if cell == 'O':
        if power2(neighobouring_sum):
            return '.'
        elif neighobouring_sum < 10:
            return 'o'
        else:
            return 'O'

    # weakling o
    elif cell == 'o':
        if neighobouring_sum <= 0:
            return '.'
        elif neighobouring_sum > 6:
            return 'O'
        else:
            return 'o'

    # deadge cell .
    elif cell == '.':
        if primal(neighobouring_sum):
            return 'o'
        elif primal(abs(neighobouring_sum)):
            return 'x'
        else:
            return '.'
    # living x

    elif cell == 'x':
        if neighobouring_sum >= 1:
            return '.'
        elif neighobouring_sum < -6:
            return 'X'
        else:
            return 'x'
        
    # healthly x
    elif cell == 'X':
        if fibonacci(neighobouring_sum):
            return '.'
        elif neighobouring_sum > -10:
            return 'x'
        else:
            return 'X'
        
    #if it is invalid return cell
    return cell

def row_parrallel(args):
    """This will let us do multiprocessing on rows
    
    args used: tuple matrix row_index
    this will also return a new row after applying the rules
    """

    matrix, row_index = args
    number_columns = len(matrix[0])
    new_row = [None for _ in range(number_columns)]

    for cols in range(number_columns):
        arounding_sum = get_around_sum(matrix, row_index, cols)
        current_cell = matrix[row_index][cols]
        new_row[cols] = trafalgar_law(current_cell, arounding_sum)
    return new_row



def simulation_steps(matrix):
    """This just does the rules cell once and returns new matrix the next function will loop it 100 times"""

    number_rows = len(matrix)
    number_columns = len(matrix[0])

    new_matrix = [[None for _ in range(number_columns)] for _ in range(number_rows)]


    #loop through the cells and apply the rules from my law function
    for rows in range(number_rows):
        for cols in range(number_columns):
            arounding_sum = get_around_sum(matrix, rows, cols)
            current_cell = matrix[rows][cols]
            new_matrix[rows][cols] = trafalgar_law(current_cell, arounding_sum)

    #return the matrix
    return new_matrix

def simulation_steps_parallel(matrix, number_processes):
    """This is basically the same as simulation steps but for multiprocessing :D
    so awesome"""

    number_rows = len(matrix)

    proccess = min(number_processes, number_rows)

    args_list = [(matrix, row_index) for row_index in range(number_rows)]

    with multiprocessing.Pool(processes=proccess) as pool:
        new_rows = pool.map(row_parrallel, args_list)
    
    return new_rows


def the_100_simulator(initial_matrix, number_steps = 100, number_processes=1):
    """This runs it 100 times (number steps amount) and retusn the final matrix"""

    current_matrix = initial_matrix

    for _ in range(number_steps):
        if number_processes == 1:
            current_matrix = simulation_steps(current_matrix)
        else:
            current_matrix = simulation_steps_parallel(current_matrix, number_processes)
    return current_matrix



#this is the end
"""Main function that will run everything"""
def main():


    #step 2 parse arguments
    input_path, output_path, number_processes = parse_arguments()
    #step 3 read intial / starting matrix
    matrix = read_input_matrix(input_path)
    #step 4 run the 100 step simulation
    final_matrix = the_100_simulator(matrix, number_steps=100, number_processes=number_processes)
    #step 5 write the output matrix to the output file
    write_output_matrix(output_path, final_matrix)



if __name__ == "__main__":
    main()
    
