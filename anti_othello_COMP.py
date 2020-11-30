#!/usr/bin/env python3

import sys
from typing import List, Tuple
from copy import deepcopy
import time
from random import choices


GLOBAL_DEPTH = 4

ALPHA_BETA_DEPTH = 3
ALPHA_BETA_DEPTH_PLAYER_2 = 2
MAX_CHOICES = 8


def debug_print(*args):
  print(*args, file=sys.stderr, flush=True)

def xy_to_alphanum(pos):
  '''
  assumes 0-indexed coordinate
  '''
  x = pos % 8 + 1
  y = pos // 8 + 1

  return f'{chr(96 + x)}{y}'

def alphanum_to_xy(alpha, num):
  '''
  returns  0-indexed coordinates
  '''
  return (ord(alpha) - 96 - 1, int(num) - 1)

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
    def __init__(self, player: int):
        '''
        0 is black
        1 is white
        black plays first
        '''
        self.player = player

        self.won = False
        self.passed = False
        self.moves = 0

        self.static_player = player

        self.array = [None for i in range(64)]

        #self.array[27] = "b"
        #self.array[28] = "w"
        #self.array[35] = "w"
        #self.array[36] = "b"

        

        #based off of: http://play-othello.appspot.com/files/Othello.pdf
        self.weights = [
            -100, 20, -10, -5, -5, -10, 20, -100,
             20,  50,   2,  2,  2,  2,  50,   20,
            -10,   2,   1,  1,  1,  1,   2,  -10,
             -5,   2,   1,  1,  1,  1,   2,   -5,
             -5,   2,   1,  1,  1,  1,   2,   -5,
            -10,   2,   1,  1,  1,  1,   2,  -10,
             20,  50,   2,  2,  2,  2,  50,   20,
            -100, 20, -10, -5, -5, -10, 20, -100,
        ]

        self.neighbours_mapping = [
            [1, 8, 9], [0, 2, 9, 8, 10], [1, 3, 10, 9, 11], [2, 4, 11, 10, 12], [3, 5, 12, 11, 13], [4, 6, 13, 12, 14], [5, 7, 14, 13, 15], 
            [6, 15, 14], [0, 9, 16, 1, 17], [1, 8, 10, 17, 0, 2, 16, 18], [2, 9, 11, 18, 1, 3, 17, 19], [3, 10, 12, 19, 2, 4, 18, 20], 
            [4, 11, 13, 20, 3, 5, 19, 21], [5, 12, 14, 21, 4, 6, 20, 22], [6, 13, 15, 22, 5, 7, 21, 23], [7, 14, 23, 6, 22], [8, 17, 24, 9, 25], 
            [9, 16, 18, 25, 8, 10, 24, 26], [10, 17, 19, 26, 9, 11, 25, 27], [11, 18, 20, 27, 10, 12, 26, 28], [12, 19, 21, 28, 11, 13, 27, 29], 
            [13, 20, 22, 29, 12, 14, 28, 30], [14, 21, 23, 30, 13, 15, 29, 31], [15, 22, 31, 14, 30], [16, 25, 32, 17, 33], [17, 24, 26, 33, 16, 18, 32, 34], 
            [18, 25, 27, 34, 17, 19, 33, 35], [19, 26, 28, 35, 18, 20, 34, 36], [20, 27, 29, 36, 19, 21, 35, 37], [21, 28, 30, 37, 20, 22, 36, 38], 
            [22, 29, 31, 38, 21, 23, 37, 39], [23, 30, 39, 22, 38], [24, 33, 40, 25, 41], [25, 32, 34, 41, 24, 26, 40, 42], [26, 33, 35, 42, 25, 27, 41, 43], 
            [27, 34, 36, 43, 26, 28, 42, 44], [28, 35, 37, 44, 27, 29, 43, 45], [29, 36, 38, 45, 28, 30, 44, 46], [30, 37, 39, 46, 29, 31, 45, 47], 
            [31, 38, 47, 30, 46], [32, 41, 48, 33, 49], [33, 40, 42, 49, 32, 34, 48, 50], [34, 41, 43, 50, 33, 35, 49, 51], [35, 42, 44, 51, 34, 36, 50, 52], 
            [36, 43, 45, 52, 35, 37, 51, 53], [37, 44, 46, 53, 36, 38, 52, 54], [38, 45, 47, 54, 37, 39, 53, 55], [39, 46, 55, 38, 54], [40, 49, 56, 41, 57], 
            [41, 48, 50, 57, 40, 42, 56, 58], [42, 49, 51, 58, 41, 43, 57, 59], [43, 50, 52, 59, 42, 44, 58, 60], [44, 51, 53, 60, 43, 45, 59, 61], 
            [45, 52, 54, 61, 44, 46, 60, 62], [46, 53, 55, 62, 45, 47, 61, 63], [47, 54, 63, 46, 62], [48, 57, 49], [49, 56, 58, 48, 50], [50, 57, 59, 49, 51], 
            [51, 58, 60, 50, 52], [52, 59, 61, 51, 53], [53, 60, 62, 52, 54], [54, 61, 63, 53, 55], [55, 62, 54]
        ]

    def alphaBeta(self, node: List, depth: int, alpha: int, beta: int, maximizing: int) -> Tuple:
        '''
        maximizing = 0 gets best result for black
        maximizing = 1 gets best result for white
        '''

        choices = self.getPossibleMoves(node)
        boards = [self.move(i, node, maximizing) for i in choices] #ALSO TRY WITHOUT PUTTING MAXIMIZNG IN THERE THATS WHAT I DID BEFORE LOLZERS


        #If there are X or more choices, lower depth. this increases efficiency but decreases chances to get the best result
        if depth == ALPHA_BETA_DEPTH:
            if len(choices) >= MAX_CHOICES:
                depth -= 1
                debug_print(f"More than {MAX_CHOICES} choices, lowered depth")
            else:
                debug_print(f"Less then {MAX_CHOICES} choices, kept depth")
        
        #Basic alpha-beta pruning algorithim
        if depth == 0 or len(choices) == 0:
            return ([-self.scoring(node, maximizing), node]) #to negative or not to negative... that is the question

        if not maximizing:
            v = -float("inf")
            best_board = []
            best_choice = []
            for choice, board in zip(choices, boards):
                board_value = self.alphaBeta(board, depth-1, alpha, beta, 0)[0]
                if board_value > v:
                    v = board_value
                    best_board = board
                    best_choice = choice
                    
                alpha = max(alpha, v)
                
                if beta <= alpha:
                    break
            
        
        else:
            v = float("inf")
            best_board = []
            best_choice = []
            for choice, board in zip(choices, boards):
                board_value = self.alphaBeta(board, depth-1, alpha, beta, 1)[0]
                if board_value < v:
                    v = board_value
                    best_board = board
                    best_choice = choice\
                    


                beta = min(beta, v)
                if beta <= alpha:
                    break
        '''
        if depth == ALPHA_BETA_DEPTH:
            print("Total nodes: " + str(nodes))
            nodes = 0
        '''
        return ([v, best_board, best_choice])

    def convert_xy(self, x: int, y: int) -> int:
        return (x + y * 8)

    def convert_pos(self, pos: int) -> Tuple:
        #returns (x, y)
        return ((pos % 8), (pos // 8))

    def isValid(self, pos: int, board = None) -> bool: 
        '''
        :param x: 0-indexed coordinate
        :param y: 0-indexed coordinate
        :param pos: 0-indexed coordinate
        '''
        if board == None: board = self.array

        x = pos % 8
        y = pos // 8
        #Set player colour
        if self.player == 0:
            colour = 'b'
        else:
            colour = 'w'

        #if there is a piece in that position, it is not a valid move
        if board[pos] != None:
            return False

        else:
            #Generating a list of neighbors
            neighbours = self.neighbours_mapping[pos]

            #If there are no neigbours, it is an invalid move
            if not neighbours:
                return False

            else:
                valid = False
                for neighbour in neighbours:
                    neighX = neighbour % 8
                    neighY = neighbour // 8

                    if board[neighbour] == colour:
                        continue

                    else:
                        deltaX = neighX - x
                        deltaY = neighY - y
                        tempX = neighX
                        tempY = neighY

                        while 0 <= tempX <= 7 and 0 <= tempY <= 7:
                            if board[tempX + 8 * tempY] == None:
                                break
                            
                            if board[tempX + 8 * tempY] == colour:
                                return True
                            
                            tempX += deltaX
                            tempY += deltaY
            return valid

    def move(self, pos: int, temp_array = None, player = None) -> List:
        '''
        :param x: 0-indexed coordinate
        :param y: 0-indexed coordinate
        '''
        (x, y) = self.convert_pos(pos)
        
        if temp_array: array = deepcopy(temp_array)
        else: array = deepcopy(self.array)

        if player == None: player = self.player
        
        if player == 1: colour = 'w'
        else: colour = 'b'
            
        
        array[pos] = colour

        #get neighbours
        neighbours = self.neighbours_mapping[pos]
        
        #which tiles to convert
        convert = []
        for neighbour in neighbours:
            (neighX, neighY) = self.convert_pos(neighbour)
            
            if array[neighbour] != colour:
                path = []
                
                #Determine the direction to move in
                deltaX = neighX - x
                deltaY = neighY - y
                tempX = neighX
                tempY = neighY

                while 0 <= tempX <= 7 and 0 <= tempY <= 7:
                    temp_pos = self.convert_xy(tempX, tempY)
                    path.append(temp_pos)
                    value = array[temp_pos]

                    if value == None:
                        break
                
                    if value == colour:
                        for node in path:
                            convert.append(node)
                        break

                    tempX += deltaX
                    tempY += deltaY

        for node in convert:
            array[node] = colour

        return array

    def scoring(self, board, player:int, weights = None) -> int:
        '''
        :param board: array of a board
        :param player: 0 for player to be black and 1 for player to be black
        '''
        if not weights: weights = self.weights
        
        opponent = 1 - player
        
        
        score = 0
        for p, w in zip(board, weights):
            if p: p = 1 if p == 'w' else 0
            if p == player: score += p * w
            elif p == opponent: score -= p * w
        
        return score

    def getPossibleMoves(self, board = None) -> List:
        if not board: board = self.array
        moves = [pos for pos in range(64) if self.isValid(pos, board)]
        return moves

    def askForAIMove_COMP(self) -> str:
      self.player = self.static_player
      
      alpha_beta_result = self.alphaBeta(self.array, ALPHA_BETA_DEPTH, -float("inf"), float("inf"), 1)
      return xy_to_alphanum(alpha_beta_result[2])

    def getFinalMove_COMP(self, given_move: str, player: int) -> None:
        (x, y) = alphanum_to_xy(given_move[0], given_move[1])
        pos = self.convert_xy(x, y)
        self.player = player
        self.array = self.move(pos)
    




bw = input()
if bw == 'w': bw = 1
else: bw = 0
game = Game(0)



print('ok', flush=True)

line = '...'

while line and line != 'done':
  line = input()
  if line == 'get move':
    move = game.askForAIMove_COMP()
    print(move, flush=True)
  elif line[:4] == 'move':
    temp_player = 1 if line[5] == 'w' else 0
    move = line[7:9]
    game.getFinalMove_COMP(move, temp_player)

  else:
    pass
    #debug_print(line)






