from typing import List
from copy import deepcopy
import time
from random import choices
from os import sys

GLOBAL_DEPTH = 4

ALPHA_BETA_DEPTH = 4
ALPHA_BETA_DEPTH_PLAYER_2 = 2
MAX_CHOICES = 8

nodes = 0
def debug_print(*args):
  print(*args, file=sys.stderr, flush=True)

def xy_to_alphanum(x, y):
  '''
  assumes non 0-indexed coordinates
  '''
  # Instead of '96', it's nicer to write 'ord('a')-1'.
  # The reason is improved understanding --- even I don't know
  # ASCII codes by heart.
  #
  # An alternative would be:
  # return '#abcdefgh'[x] + '#12345678'[y]
  return f'{chr(96 + x)}{y}'

def alphanum_to_xy(alpha, num):
  '''
  returns non 0-indexed coordinates
  '''
  return (ord(alpha) - 96, int(num))

def hms_string(sec_elapsed: int) -> str:
    # When you get code from somewhere else, please include attribution!
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
        
        # General note on this sort of fallback: doing IO (input/output) in constructors
        # is generally frowned upon.  In this case, it _might_ do IO.  It's just better
        # code organization for this conditional to live outside (the conditional itself
        # is fine, it should just live elsewhere).
        if player:
            self.player = player
        else:
            self.player = int(input("Input 0 for black and 1 for white: "))

        self.won = False
        self.passed = False
        self.moves = 0
        
        self.static_player = player

        # Faster, and easier to copy, would be a single array 64 elements long,
        # with helper methods to get/set:
        #
        # self.array = 64 * [None]
        # ...
        # def get(self, x, y):
        #   # One-indexed version:
        #   return self.array[(x-1) + 64 * (y-1)]
        #   # Zero-indexed version (a hint why programmers like zero-indexing):
        #   return self.array[x + 64 * y]
        self.array = []
        
        for column in range(8):
            self.array.append([])
            for _ in range(8):
                self.array[column].append(None)

        # Don't initialize these moves!!! The first moves will be sent to you
        # when the game starts!
        self.array[3][3] = "b"
        self.array[3][4] = "w"
        self.array[4][3] = "w"
        self.array[4][4] = "b"

        # Using a faster board representation will likely be a bigger win than
        # memoization
        self.scoring_memoization = {} #repr(board): [blacks_score, whites_score]

        #based off of: http://play-othello.appspot.com/files/Othello.pdf
        # Good job w/ attribution!
        
        # A few notes:
        # 1. This makes it hard to look up score by position.  It also makes it hard to tell all elements are covered
        # 2. Style-wise, if you're not going to mutate, a tuple is better.
        self.squares_to_values_mapping = { # [[x, y], [x, y]... ] : value 
            -100: [[0, 0], [7, 0], [0, 7], [7, 7]], #corner
            20: [[1, 0], [0, 1], [6, 0], [7, 1], [0, 6], [1, 7], [6, 7], [7, 6]],  #adjacent_linear
            50: [[1, 1], [6, 1], [1, 6], [6, 6]], #adjacent_diagonal
            -10: [[2, 0], [5, 0], [0, 2], [0, 5], [7, 2], [7, 5], [2, 7], [5, 7]], #side_outer
            -5: [[3, 0], [4, 0], [0, 3], [0, 4], [7, 3], [7, 4], [3, 7], [4, 7]], #side_inner
            1: [[1, 2], [1, 3], [1, 4], [1, 5], [6, 2], [6, 3], [6, 4], [6, 5], [1, 2], [1, 3], [1, 4], [1, 5], [7, 2], [7, 3], [7, 4], [7, 5]], #inner_4x4_walls_excluding_diagonals
        }
        
    def minimax(self, node, depth, maximizing):
        # I'm skipping this, since you said the alpha-beta was newer
        
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
        '''
        maximizing = 0 gets best result for black
        maximizing = 1 gets best result for white
        '''
        
        # You should add some comments/documentation on you "nodes" global  I don't fully follow what it's meant to do.
        global nodes

        boards = []
        choices = []
        
        # Slightly cleaner to move this into a helper function.  It could return
        # a list of tuples like [(move, board), ...]
        #Finds all valid moves
        for x in range(8):
            for y in range(8):
                if self.isValid(x, y):
                    test = self.move(x, y, node)
                    boards.append(test)
                    choices.append([x, y]) #0 indexed coordinates
                    nodes += 1

        #If there are X or more choices, lower depth. this increases efficiency but decreases chances to get the best result
        if depth == ALPHA_BETA_DEPTH:
            if len(choices) >= MAX_CHOICES:
                depth -= 1
                debug_print(f"More than {MAX_CHOICES} choices, lowered depth")
            else:
                debug_print(f"Less then {MAX_CHOICES} choices, kept depth")
        
        #Basic alpha-beta pruning algorithim
        if depth == 0 or len(choices) == 0:
            return ([-self.scoring(node, maximizing), node])

        # Instead of repeating this twice, you can negate scores as you descend, and
        # always maximize.  For minimax, you also have to do something to alpha,beta
        # (hint: it's not bad)
        if not maximizing:
            v = -float("inf")
            best_board = []
            best_choice = []
            for board in boards:
                board_value = self.alphaBeta(board, depth-1, alpha, beta, 0)[0]
                if board_value > v:
                    v = board_value
                    best_board = board
                    # This (calling 'index') is slow.  It's a linear search.
                    best_choice = choices[boards.index(board)]

                # If you already have the if statement, you could just put alpha = v indented in the body above
                alpha = max(alpha, v)
                
                if beta <= alpha:
                    break
            
        
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
        '''
        if depth == ALPHA_BETA_DEPTH:
            print("Total nodes: " + str(nodes))
            nodes = 0
        '''
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
            
        # In Python, "None" is falsey, and non-empty strings are truthy,
        # so you can just write:
        # if self.array[x][y]: return False

        #if there is a piece in that position, it is not a valid move
        if self.array[y][x] != None:
            return False

        else:
            # You search for non-empty neighbors, then you search for
            # lines in the direction of each.
            #
            # Interestingly, the code for the non-empty neighbor is very
            # much like the code searching along the line, so you could simplify
            # a little.  Optional
           
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

            # Read about something called an "early return" (or "early exit").  It's just a nicer pattern for
            # cases like this that keeps your indentation more under control.
            #
            # Example:
            #
            # if BAD:
            #   return None
            # else:
            #   do
            #   a bunch
            #   of stuff...
            #
            # Can be written:
            #
            # if BAD:
            #   return None
            # do
            # a bunch
            # of stuff
            #
            # It also makes it more obvious that the else-case is really the intended flow,
            # and the if-case is the exception
            else:
                #Iterating through neighbours to determine if at least one line is formed
                
                # The way I write this (I don't compute neighbors either):
                #
                # for dx,dy in [(1,0), (1,1), (0,1), (-1,1), ...]:
                #   ...
                #   for k in range(8):
                #     xk, yk = x + k*dx, y + k*dy
                #     if not (0 <= xk < 8) or not (0 <= yk < 8): break
                #     ...
                
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

    # It's good that you use type annotations.  But annotate return types
    # too --- and it helps to note that this returns a new board, rather
    # than modifying the existing one in-place.
    def move(self, x: int, y: int, temp_array = None, player = None):
        '''
        :param x: 0-indexed coordinate
        :param y: 0-indexed coordinate
        '''
        
        # Pythonic alternative:
        # array = deepcopy(temp_array or self.array)
        
        if temp_array:
            array = deepcopy(temp_array)
        else:
            array = deepcopy(self.array)

        # Pythonic convention: compare to None with "is":
        # if player is None:
        if player == None:
          player = self.player

        # Pythonic alternative:
        # colour = 'w' if player == 1 else 'b'
        if player == 1:
            colour = 'w'
        else:
            colour = 'b'
        
        array[y][x] = colour

        # Ahhhh!  You should find a way to factor this out.  It's a complicated
        # and important piece of code.... and you've essentially written out the
        # logic twice!  That makes it twice as hard to fix if something goes
        # wrong.
        
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
        
        # If you store the board as a flat array, and store the scoring weights in the
        # same structure, then you can replace the ENTIRE function with:
        # score = 0
        # for p,w in zip(board, weights):
        #   if p == player: score += p*w
        #   elif p == oppoenent: score -= p*w
        # return score
        #
        # That should run similarly fast to calling repr(board), and hence make
        # memoization not worth it.

        brepr = repr(board)

        if brepr in self.scoring_memoization:
            return self.scoring_memoization[brepr][player]

        black_score = 0
        white_score = 0
        
        #iterate through all the vals
        for x in range(8):
            for y in range(8):
                add = -1
                for value in self.squares_to_values_mapping:
                    if [x, y] in self.squares_to_values_mapping[value]:
                        add = value
                        break
                
                if board[y][x] == 'b':
                    black_score += add
                    white_score -= add
                
                elif board[y][x] == 'w':
                    black_score -= add
                    white_score += add
        self.scoring_memoization[brepr] = [black_score, white_score]

        return [black_score, white_score][player]

    def passTest(self) -> bool:        
        # Alternative:
        # return any(self.isValid(x,y) for x in range(8) for y in range(8))
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
                minimax_result = self.minimax(self.array, GLOBAL_DEPTH, 1)
                self.array = minimax_result[1]
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

    def askForAIMove_COMP(self):
      self.player = self.static_player
      
      alpha_beta_result = self.alphaBeta(self.array, ALPHA_BETA_DEPTH, -float("inf"), float("inf"), 1)
      return xy_to_alphanum(alpha_beta_result[2][0]+1, alpha_beta_result[2][1]+1)

    def getFinalMove_COMP(self, given_move: str, player: int):
        (x, y) = alphanum_to_xy(given_move[0], given_move[1])
        self.player = player
        self.array = self.move(x, y)
    
    def __str__(self):
        my_string = ''
        for column in self.array:
            my_string += str(['-' if i == None else i for i in column])
            my_string += '\n'
        return my_string




#game = Game(1)
#game.playGame_AI()

game = Game(1)
print(game.askForAIMove_COMP())

