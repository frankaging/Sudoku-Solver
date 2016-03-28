############################################################
# CIS 521: Homework 4
############################################################

student_name = "Zhengxuan Wu"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import math
import random
import time
import os
import Queue
import copy

############################################################
# Section 1: Sudoku
############################################################

fileDir = os.path.dirname(os.path.realpath('__file__'))

# tested
def sudoku_cells():
    cell = []
    for i in range(0,9):
        for j in range(0,9):
            cell.append((i,j))
    # print cell
    return cell
cell_temp = sudoku_cells()

# tested
def sudoku_arcs():
    arcs = []
    for key1 in cell_temp:
        for key2 in cell_temp:
            # first ensure they are not the same
            if key1 != key2:
                # if they are in same row or col
                if key1[0] == key2[0] or key1[1] == key2[1]:
                    arcs.append((key1,key2))
                # if they are in the same box
                elif math.floor(key1[0]/3) == math.floor(key2[0]/3) and \
                     math.floor(key1[1]/3) == math.floor(key2[1]/3):
                    arcs.append((key1,key2))
    return arcs

#sudoku_arcs()
# print ((4, 2), (5,2 )) in sudoku_arcs()

# tested
def read_board(path):
    board={}
    ind = 0
    filename = os.path.join(fileDir, path)
    filehandle = open(filename)
    cell_list = []
    for line in filehandle:
        line = line.rstrip().lstrip()
        cell_list.append(line)
    filehandle.close()
    for i in cell_list:
        for element in i:
            if element == '*':
                board[cell_temp[ind]] = set([1,2,3,4,5,6,7,8,9])
            else:
                board[cell_temp[ind]] = set([int(element)])
            ind +=1
    return board



class Sudoku(object):



    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()


    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        # print self.board[cell]
        return self.board[cell]

    def get_board(self):
        return self.board

    def print_board(self):
        # printing board for answer checking
        for i in range(0,9):
            temp = []
            for j in range(0,9):
                temp.extend(list(self.board[(i,j)]))
            print temp

    def remove_inconsistent_values(self, cell1, cell2):
        # justify that (cell1, cell2) is in the arcs list
            # condition: only 1 posiible sol in cell2
        set_cell1=self.get_values(cell1)
        set_cell2=self.get_values(cell2)
        if len(self.board[cell2]) == 1:
            for x in set_cell1:
                if x in set_cell2:
                    set_cell1.remove(x)
                    return True
            return False
        else:
            # not in arcs
            return False

    def get_arcs(self):
        '''for efficiency, we only add those arcs has constrain in it'''
        arcs = []
        for row in xrange(9):
            for col in xrange(9):
                # adding arcs in the same block
                for i in range((row/3)*3,((row/3)*3)+3):
                    for j in range((col/3)*3,((col/3)*3)+3):
                        if i != row or j != col:
                            if len(self.board[(i, j)]) == 1:
                                arcs.append(((row, col), (i, j)))
                # adding arcs in the same row
                for i in xrange(9):
                    if i not in range((row/3)*3,((row/3)*3)+3):
                        if len(self.board[(i, col)]) == 1:
                            arcs.append(((row, col), (i, col)))
                # adding arcs in the same col
                for j in xrange(9):
                    if j not in range((col/3)*3,((col/3)*3)+3):
                        if len(self.board[(row, j)]) == 1:
                            arcs.append(((row, col), (row, j)))
        return arcs

    def ac3_successor(self, queue, frontier):
        element = frontier[0]
        row = element[0]
        col = element[1]
        # Check in block
        for i in range((row/3)*3,((row/3)*3)+3):
            for j in range((col/3)*3,((col/3)*3)+3):
                if i != row or j != col:
                    if (i, j) != frontier[1]:
                        queue.append(((i, j), (row, col)))
        # Check for line
        # Vertical
        for i in xrange(9):
            if i not in range((row/3)*3,((row/3)*3)+3):
                if (i, col) != frontier[1]:
                    queue.append(((i, col), (row, col)))
        # Horizontal
        for j in xrange(9):
            if j not in range((col/3)*3,((col/3)*3)+3):
                if (row, j) != frontier[1]:
                    queue.append(((row, j), (row, col)))

    def infer_ac3(self):
        queue = []
        for element in self.get_arcs():
            queue.append(element)
        while queue !=[]:
            # get the first element of the queue
            frontier = queue.pop(0)
            if self.is_solved():
                self.print_board()
                return self
            if self.remove_inconsistent_values(frontier[0], frontier[1]):
                self.ac3_successor(queue, frontier)

    def is_in_block(self, value, element):
        block_row_start = (element[0]/3)*3
        block_col_start = (element[1]/3)*3
        for i in range(block_row_start, block_row_start+3):
            for j in range(block_col_start, block_col_start+3):
                if i != element[0] or j != element[1]:
                    if value in self.board[(i,j)]:
                        return True
        return False
    
    def is_in_row(self, value, element):
        for j in xrange(0,9):
            if j != element[1]:
                if value in self.board[(element[0],j)]:
                    return True
        return False

    def is_in_col(self, value, element):
        for i in xrange(0,9):
            if i != element[0]:
                if value in self.board[(i,element[1])]:
                    return True
        return False

    def infer_improved(self):
        # if it is not solved, we will continue to do the following
        running_time = 0
        converge_flag = False
        reduced = 1
        while reduced == 1:
            reduced = 0
            self.infer_ac3()
            if self.is_solved():
                # self.print_board()
                return self
            for i in xrange(0,9):
                for j in xrange(0,9):
                    element = (i,j)
                    if len(self.board[element]) > 1:
                        for value in self.board[element]:
                            # check if the value is not in anywhere in the block
                            if not self.is_in_block(value,element):
                                self.board[element] = set([value])
                                reduced = 1
                            # check if the value is not in anywhere in the row
                            if not self.is_in_row(value,element):
                                self.board[element] = set([value])
                                reduced = 1
                            # check if the value is not in anythere in the col
                            if not self.is_in_col(value,element):
                                self.board[element] = set([value])
                                reduced = 1
        return self

    # check is_solve function can be purely based on length because inside ac
    # we already make sure that every possible value in the set is satisfying
    # those necessary constrains
    def is_solved(self):
        '''check if it is solved, based on length'''
        for cell in self.CELLS:
            if len(self.board[cell]) != 1:
                return False
        return True

    def check_solvable(self):
        for cell in self.CELLS:
            if len(self.board[cell]) == 0:
                return False
        return True

    def infer_with_guessing(self):
        # stack dfs search among different choices of cells
        stack = []
        stack.append(self)
        # dfs search loop
        while stack != []:
            # pop out thef first element
            frontier = stack.pop()
            frontier.infer_improved()
            if frontier.is_solved():
                # frontier.print_board()
                self.board = frontier.board
                return frontier
            if frontier.check_solvable():
                next_cell = frontier.cell_choice()
                if next_cell != ():
                    for new_p in frontier.successor(next_cell):
                        stack.append(new_p)
        return self


    def cell_choice(self):
        '''a function that choose the most info-gain cell for board'''
        min = 10
        next_cell = ()
        for cell in self.CELLS:
        # traverse all cells to get the cell with min choices (not 1)
            if len(self.board[cell]) < min and len(self.board[cell]) > 1:
                if len(self.board[cell]) == 2:
                    return cell
                next_cell = cell
                min = len(self.board[cell])
        return next_cell

    def successor(self, next_cell):
        '''yield all the successor board based on the board and chossed cell'''
        board_copy = copy.deepcopy(self.board)
        potential_cand = list(self.board[next_cell])
        for i in potential_cand:
            board_copy[next_cell] = set([i])
            result_board = copy.deepcopy(board_copy)
            yield Sudoku(result_board)

#startTime = time.time()
#b = read_board("sudoku/hard2.txt")
#test_ob = Sudoku(b)
#test_ob.infer_with_guessing()
#test_ob.print_board()


#print time.time() - startTime

############################################################
# Section 2: Feedback
############################################################

feedback_question_1 = """
15 hrs
"""

feedback_question_2 = """
The guessing function
"""

feedback_question_3 = """
I love all of it !
"""
