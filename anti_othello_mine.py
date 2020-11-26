

'''
CODE HEAVILY INSPIRED FROM JOHN FISH'S OTHELLO PROGRAM
'''

from typing import List
from copy import deepcopy
from time import sleep
from random import choices

GLOBAL_DEPTH = 3
ALPHA_BETA_DEPTH = 4


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
        score = 0
        corner_val = 25
        adjacent_val = 5
        side_val = 5
        #set scoring vals

        #Set player and opponent colour
        if self.player == 0:
            colour = 'b'
            opponent = 'w'
        else:
            colour = 'w'
            opponent = 'b'

        #iterate through all the vals
        for x in range(8):
            for y in range(8):
                #Normal tiles worth -1
                add = -1

                #Adjacent to corners are worth -3
                if (x == 0 and y == 1) or (x == 1 and 0 <= y <= 1):
                    
                    if board[0][0] == colour:
                        add = side_val
                    else:
                        add = -adjacent_val

                elif (x == 0 and y == 6) or (x == 1 and 6 <= y <= 7):     
                    if board[0][7] == colour:
                        add = side_val
                    else:
                        add = -adjacent_val
                
                elif (x==7 and y==6) or (x==6 and 6<=y<=7):
                    if board[7][7] == colour:
                        add = side_val
                    
                    else:
                        add = -adjacent_val
                
                elif (x == 0 and 1 < y < 6) or (x == 7 and 1 < y < 6) or (y == 0 and 1 < x < 6) or (y == 7 and 1 < x < 6):
                    add = side_val
                
                elif (x == 0 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 0) or (x == 7 and y == 7):
                    add = corner_val

                if board[x][y] == colour:
                    score += add
                
                elif board[x][y] == opponent:
                    score -= add
        
        return score

    def passTest(self) -> bool:        
        for x in range(8):
            for y in range(8):
                if self.isValid(x, y): return True

        return False

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
            print(board, flush = True)
            print('\n', flush = True)

            if not self.passTest():
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
        while not self.won:
            print ('_______________Moves: {}________________'.format(self.moves))
            print(board)
            print('\n')

            if not self.passTest():
                if self.passed:
                    self.won = True
                else:
                    self.passed = True
                
                self.player = 1 - self.player
                print("NO POSSIBLE MOVES, PASSED TO PLAYER " + str(self.player))
                continue

            else: 
                self.passed = False

            if self.player == 0:
                print("Black's turn") 
                alpha_beta_result = self.alphaBeta(self.array, ALPHA_BETA_DEPTH, -float("inf"), float("inf"), 1)
                self.array = alpha_beta_result[1]

            else:
                print("White's turn |")
                minimaxResult = self.minimax(self.array, GLOBAL_DEPTH, 1)
                self.array = minimaxResult[1]
            #sleep(15)
            self.player = 1 - self.player
            self.moves += 1
        print("Game Over")

    def __str__(self):
        my_string = ''
        for column in self.array:
            my_string += str(['-' if i == None else i for i in column])
            my_string += '\n'
        return my_string



game = Game()
game.playGame_AI()