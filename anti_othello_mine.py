
'''
CODE HEAVILY INSPIRED FROM JOHN FISH'S OTHELLO PROGRAM
'''

from typing import List
from copy import deepcopy
import time
from random import choices

GLOBAL_DEPTH = 3
ALPHA_BETA_DEPTH = 3



def hms_string(sec_elapsed: int) -> str:
    """
    Gets time in Hour:Minutes:Seconds
    :param sec_elapsed: seconds elapsed
    :return: Hour:Minutes:Seconds
    """
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

class Game(object):
    def __init__(self, player = None):
        '''
        0 is black
        1 is white
        black plays first
        '''
        if player:
            self.player = player
        else:
            self.player = int(input("Input 0 for black and 1 for white: "))
        self.won = False
        self.passed = False
        self.moves = 0

        self.array = []
        
        for column in range(8):
            self.array.append([])
            for row in range(8):
                self.array[column].append(None)

        self.array[3][3] = "w"
        self.array[3][4] = "b"
        self.array[4][3] = "b"
        self.array[4][4] = "w"

        #based off of: http://play-othello.appspot.com/files/Othello.pdf
        self.squares_to_values_mapping = { # [[x, y], [x, y]... ] : value 
            -100: [[0, 0], [7, 0], [0, 7], [7, 7]], #corner
            20: [[1, 0], [0, 1], [6, 0], [7, 1], [0, 6], [1, 7], [6, 7], [7, 6]],  #adjacent_linear
            50: [[1, 1], [6, 1], [1, 6], [6, 6]], #adjacent_diagonal
            -10: [[2, 0], [5, 0], [0, 2], [0, 5], [7, 2], [7, 5], [2, 7], [5, 7]], #side_outer
            -5: [[3, 0], [4, 0], [0, 3], [0, 4], [7, 3], [7, 4], [3, 7], [4, 7]], #side_inner
            1: [[1, 2], [1, 3], [1, 4], [1, 5], [6, 2], [6, 3], [6, 4], [6, 5], [1, 2], [1, 3], [1, 4], [1, 5], [7, 2], [7, 3], [7, 4], [7, 5]], #inner_4x4_walls_excluding_diagonals
        }
        
    def minimax(self, node, depth, maximizing):
        
        boards = []
        choices = []
        
        for x in range(8):
            for y in range(8):
                if self.isValid(x, y):
                    test = self.move(x, y, node)
                    boards.append(test)
                    choices.append([x, y])
        
        if depth == 0 or len(choices) == 0:
            return ([self.scoring(node, maximizing), node])
        
        if not maximizing:
            best_value = -float("inf")
            best_board = []
            for board in boards:
                val = self.minimax(board, depth-1, 0)[0]
                if val > best_value:
                    best_value = val
                    best_board = board
            
            return ([best_value, best_board])
        
        else:
            bestValue = float("inf")
            bestBoard = []
            for board in boards:
                val = self.minimax(board, depth-1, 1)[0]
                if val < bestValue:
                    bestValue = val
                    bestBoard = board
            
            return ([bestValue, bestBoard])

    def alphaBeta(self, node, depth, alpha, beta, maximizing):
        boards = []
        choices = []
        
        for x in range(8):
            for y in range(8):
                if self.isValid(x, y):
                    test = self.move(x, y, node)
                    boards.append(test)
                    choices.append([x, y])
        
        if depth == 0 or len(choices) == 0:
            return ([self.scoring(node, maximizing), node])

        if not maximizing:
            v = -float("inf")
            best_board = []
            best_choice = []
            for board in boards:
                board_value = self.alphaBeta(board, depth-1, alpha, beta, 0)[0]
                if board_value > v:
                    v = board_value
                    best_board = board
                    best_choice = choices[boards.index(board)]
                alpha = max(alpha, v)
                
                if beta <= alpha:
                    break
            return ([v, best_board, best_choice])
        
        else:
            v = float("inf")
            best_board = []
            best_choice = []
            for board in boards:
                board_value = self.alphaBeta(board, depth-1, alpha, beta, 1)[0]
                if board_value < v:
                    v = board_value
                    best_board = board
                    best_choice = choices[boards.index(board)]

                beta = min(beta, v)
                if beta <= alpha:
                    break
            return ([v, best_board, best_choice])

    def isValid(self, x: int, y: int) -> bool: 
        '''
        :param x: 0-indexed coordinate
        :param y: 0-indexed coordinate
        '''
        
        #Set player colour
        if self.player == 0:
            colour = 'b'
        else:
            colour = 'w'

        #if there is a piece in that position, it is not a valid move
        if self.array[y][x] != None:
            return False

        else:
            #Generating a list of neighbors
            neighbour = False
            neighbours = []
            for i in range(max(0, x-1), min(x+2, 8)):
                for j in range(max(0, y-1), min(y+2, 8)):
                    if self.array[j][i] != None:
                        neighbour = True
                        neighbours.append([i, j])

            #If there are no neigbours, it is an invalid move
            if not neighbour:
                return False

            else:
                #Iterating through neighbours to determine if at least one line is formed
                valid = False
                for neighbour in neighbours:
                    neighX = neighbour[0]
                    neighY = neighbour[1]

                    #if the neighbour colour is equal to your colour, it doesn't form a line
                    if self.array[neighY][neighX] == colour:
                        continue

                    else:
                        #Determine the direction of the line
                        deltaX = neighX - x
                        deltaY = neighY - y
                        tempX = neighX
                        tempY = neighY

                        while 0 <= tempX <= 7 and 0 <= tempY <= 7:
                            #If an empty space, no line is formed

                            if self.array[tempY][tempX] == None:
                                break

                            if self.array[tempY][tempX] == colour:
                                valid = True
                                break

                            #Move the index according to the direction of the line
                            tempX += deltaX
                            tempY += deltaY
                return valid

    def move(self, x: int, y: int, temp_array = None):
        '''
        :param x: 0-indexed coordinate
        :param y: 0-indexed coordinate
        '''
        
        if temp_array:
            array = deepcopy(temp_array)
        else:
            array = deepcopy(self.array)

        if self.player == 1:
            colour = 'w'
        else:
            colour = 'b'
        
        array[y][x] = colour

        #determine neighbours
        neighbours = []
        for i in range(max(0, x-1), min(x+2, 8)):
            for j in range(max(0, y-1), min(y+2, 8)):
                if self.array[j][i] != None:
                    neighbours.append([i, j])
        
        #which tiles to convert
        convert = []
        for neighbour in neighbours:
            neighX = neighbour[0]
            neighY = neighbour[1]
            if array[neighY][neighX] != colour:
                path = []
                
                #Determine the direction to move in
                deltaX = neighX - x
                deltaY = neighY - y
                tempX = neighX
                tempY = neighY

                while 0 <= tempX <= 7 and 0 <= tempY <= 7:
                    path.append([tempX, tempY])
                    value = array[tempY][tempX]

                    if value == None:
                        break
                
                    if value == colour:
                        for node in path:
                            convert.append(node)
                        break

                    tempX += deltaX
                    tempY += deltaY

        for node in convert:
            array[node[1]][node[0]] = colour

        return array

    def scoring(self, board: List, player: int) -> int:
        '''
        :param board: array of a board
        :param player: 0 for player to be black and 1 for player to be black
        '''

        #Set player and opponent colour
        if self.player == 0:
            colour = 'b'
            opponent = 'w'
        else:
            colour = 'w'
            opponent = 'b'
        score = 0
        #iterate through all the vals
        for x in range(8):
            for y in range(8):
                add = -1
                for value in self.squares_to_values_mapping:
                    if [x, y] in self.squares_to_values_mapping[value]:
                        add = value
                        break
                
                if board[y][x] == colour:
                        score += add
                
                elif board[y][x] == opponent:
                    score -= add
        
        return score

    def passTest(self) -> bool:        
        for x in range(8):
            for y in range(8):
                if self.isValid(x, y): return True

        return False

    def getPossibleMoves(self) -> List:
        moves = []
        for x in range(8):
            for y in range(8):
                if self.isValid(x, y): moves.append([x, y])

        return moves

    def askForMove(self) -> List:
        x = int(input('What X coordinate would you like to play? '))
        y = int(input('What Y coordinate would you like to play? '))
        if self.isValid(x - 1, y - 1):
            return (x - 1, y - 1)
        else:
            print('Not a valid move.')
            return self.askForMove()

    def playGame(self):  
        while not self.won:
            print ('_______________Moves: {}________________'.format(self.moves), flush = True)
            print(self, flush = True)
            print('\n', flush = True)

            valid_moves = self.getPossibleMoves()

            if not valid_moves:
                if self.passed:
                    self.won = True
                else:
                    self.passed = True
                
                self.player = 1 - self.player
                print("NO POSSIBLE MOVES, PASSED TO PLAYER " + str(self.player), flush = True)
                continue

            else: 
                self.passed = False

            if self.player == 0:
                print("Black's turn |", flush = True) 
                (x, y) = self.askForMove()  
                self.array = self.move(x, y)

            else:
                print("White's turn |", flush = True)
                minimaxResult = self.minimax(self.array, GLOBAL_DEPTH, 1)
                self.array = minimaxResult[1]

            self.player = 1 - self.player

        print("Game Over", flush = True)

    def playGame_AI(self):
        
        black_overtime = 0
        white_overtime = 0

        while not self.won:
            print ('_______________Moves: {}________________'.format(self.moves), flush = True)
            print(self, flush = True)
            print('\n', flush = True)

            valid_moves = self.getPossibleMoves()

            if not valid_moves:
                if self.passed:
                    self.won = True
                else:
                    self.passed = True
                
                self.player = 1 - self.player
                print("NO POSSIBLE MOVES, PASSED TO PLAYER " + str(self.player), flush = True)
                continue

            else: 
                self.passed = False

            start_time = time.time()

            if self.player == 0:
                
                print("Black's turn", flush = True)
                alpha_beta_result = self.alphaBeta(self.array, ALPHA_BETA_DEPTH, -float("inf"), float("inf"), 1)
                self.array = alpha_beta_result[1]
                elapsed_time = time.time() - start_time
                if elapsed_time > 1: black_overtime += 1

            else:
                print("White's turn |", flush = True)
                minimaxResult = self.minimax(self.array, GLOBAL_DEPTH, 1)
                self.array = minimaxResult[1]
                elapsed_time = time.time() - start_time
                if elapsed_time > 1: white_overtime += 1
            
            print("Elapsed Time: {}".format(hms_string(elapsed_time)), flush = True)
            #sleep(15)
            self.player = 1 - self.player
            self.moves += 1

        print("Game Over", flush = True)
        print('\n\n', flush = True)
        print('Black over time: ' + str(black_overtime), flush = True)
        print('White over time: ' + str(white_overtime), flush = True)

    def __str__(self):
        my_string = ''
        for column in self.array:
            my_string += str(['-' if i == None else i for i in column])
            my_string += '\n'
        return my_string



game = Game()
game.playGame_AI()