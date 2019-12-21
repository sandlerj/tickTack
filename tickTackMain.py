# Tick tack toe engine
# Joseph Sandler
# Created following guides of Robert Heaton

import copy, random, time, math
from collections import Counter
import minimaxCaching
from tickTackAI import *

#(x,y)'s of the 8 possible wins

WINNING_LINES = [[(0,0), (1,0), (2,0)],
                  [(0,1),(1,1),(2,1)],
                  [(0,2),(1,2),(2,2)],
                  [(0,0),(0,1),(0,2)],
                  [(1,0),(1,1),(1,2)],
                  [(2,0),(2,1),(2,2)],
                  [(0,0),(1,1),(2,2)],
                  [(0,2),(1,1),(2,0)]]

# produce new board
def newBoard(n=3):
  return [[None]*n for _ in range(n)]

#loop until win conditions have been met
# ie, check for winning conditions

# #print board
def render(board):
  print("   0   1   2")
  print(" - "*(len(board[0]) + 2))
  for row in range(len(board)):
    print(str(row) + "|", end='')
    for col in range(len(board[row])):
      if board[row][col] == None:
        print(" " + " " + " |", end="")
      else:
        print(" " + board[row][col] + " |", end="")    
    print();print()
  print(" - "*(len(board[0]) + 2))


#get next move
def getMove(coords=None):
  if coords == None or type(coords) != tuple or coords[0]<0 or coords[1] < 0 or\
  coords[0] > 2 or coords[1] > 2 :
    x=input("What is your x input? (0-2):")
    y=input("What is your y input? (0-2):")
    try:
      coords = (int(x),int(y))
    except:
      # print('Invalid input')
      coords = getMove()
  while not isValid(coords):
    # print('Invalid Move')
    coords = getMove()
  return coords


def isValid(coords):
  for num in coords:
    if not (0 <= num <= 2):
      return False
  return True

#put move on board
def execMove(board, coords, player):
  #takes coords of move as (x,y) and deals appropriately
  if board[coords[1]][coords[0]] != None:
    raise Exception('Illegal move: Space occupied')
  else:
    newBoard = copy.deepcopy(board)
    newBoard[coords[1]][coords[0]] = player
    return newBoard


#check for winner, if yes, exit

#if no moves can be made, call draw
def countNonNone(L, count=0):
  #recursively counts all non-none values in a nested array
  
  for item in L: #base case lol?
    if type(item) != list and item != None:
      count += 1
    elif type(item) == list:
      count = countNonNone(item, count)
  return count

#check if board full:
def gameOver(board):
  if countNonNone(board) == 9: # we counted and there are 9 items that aren't None on the board
    return True
  else:
    return False

def hasWinner(board):
  #checks if board has winner
  for line in WINNING_LINES:
    #check each line for a winner
    coords1, coords2, coords3 = line
    if board[coords1[1]][coords1[0]] == None:
      continue #not a winning line
    elif board[coords1[1]][coords1[0]] == board[coords2[1]][coords2[0]] == \
    board[coords3[1]][coords3[0]]:
    #return winner if exists
      return board[coords1[1]][coords1[0]]
  return False





def run(AI=None, AI2=None, AI2Role=None, renderTurns=False):
  # print('Now playing tic-tac-toe')
  board = newBoard()
  xTurn = True
  game_Over = False
  if AI != None:
    #get PC
    if AI2Role == None:
      inp = input('Choose "X" or "O":')
    else:
      inp = AI2Role
    if inp == 'X':
      playerTurn = True
      
    elif inp == 'O':
      playerTurn = False
      
    else:
      raise Exception('Invalid Input')

  while not game_Over: 
    if renderTurns:
      render(board)
    game_Over = gameOver(board)
    if game_Over:
      if renderTurns:
        print('Draw!')
      break
    turn = 'X' if xTurn else 'O'
    if renderTurns:
      print(turn + "'s turn")

    if AI == None:
      move = find_winning_and_blocking_moves_ai(board, turn)
      board = execMove(board, move, turn)
    else:
      if playerTurn:
        if AI2 == None:
          board = execMove(board, getMove(), turn)
        else:
          coords = AI2(board, turn)
          board = execMove(board, coords, turn)
      else:
        coords = AI(board, turn)
        board = execMove(board,coords, turn)
      playerTurn = not playerTurn
    

    xTurn = not xTurn
    winner = hasWinner(board)
    if winner != False:
      if renderTurns:
        render(board)
        print('The winner is: ' + winner)
      return winner
      break







##
def test():
  def testHasWinner():
    # print('Testing hasWinner....', end='')
    board1 = [[None] * 3] * 3
    assert(hasWinner(board1) == False)
    board2 = [['O', None, 'X'],
              [None, 'O', None],
              ['X', None, 'O']]
    assert(hasWinner(board2) == 'O')
    board3 = [['O', 'X', 'X'],
              [None, None, 'O'],
              ['X', None, 'O']]
    assert(hasWinner(board3) == False)
    board4 = [['O', 'O', 'X'],
              ['O', None, 'X'],
              ['X', 'X', 'O']]
    assert(hasWinner(board4) == False)
    # print('Passed.')

  testHasWinner()
  def cacheTest(player):
    cache = minimaxCaching.readCache(player)
    print("All of the printed lines are incorrect cachings:")
    for key in cache:
      board = eval(key)
      score = minimax_score(board, player, player, None)
      
      try:    
        assert(score == cache[key])
      except:
        print(score, key, cache[key])
  for player in ["X","O"]:
    cacheTest(player)

import time
def playSelfNTimes(n):
  results = []
  start = time.time()
  for _ in range(n):
    results.append(run())
  wins = Counter(results)
  print(wins)
  print(time.time() - start)

def playNGames(player1, player2, n):
  n //= 2
  results = []
  start = time.time()
  for _ in range(n):
    # print('Game', _, 'of', str(n-1))
    #playes two games for each n (which was divided in half), trading start role
    # print('\tRound 1: %s as "O", %s as "X"' % (player1.__name__, player2.__name__))
    winner1 = run(AI=player1, AI2=player2, AI2Role='X')
    if winner1 == 'X':
      results.append(player2.__name__)
    elif winner1 == 'O':
      results.append(player1.__name__)
    else:
      results.append(None)
    # print('\tRound 1 winner:', winner1)
    # trade off starting role
    # print('\tRound 2: %s as "X", %s as "O"' % (player1.__name__, player2.__name__))
    winner2 = run(AI=player1, AI2=player2, AI2Role='O')
    if winner2 == 'O':
      results.append(player2.__name__)
    elif winner2 == 'X':
      results.append(player1.__name__)
    else:
      results.append(None)
    # print('\tRound 2 winner:', winner2)
  wins = Counter(results)
  print('Players:', player1.__name__, player2.__name__)
  print('\t',wins)
  print('\t runtime:',time.time()-start)

def isInt(s):
  try:
    int(s)
  except:
    return False
  return True

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    mainFunc = sys.argv[1]
    allFuncs = dir()
    try:
      if mainFunc in allFuncs:
        mainFunc = eval(mainFunc)
        argStr = sys.argv[2:]
        args = list(map(lambda x: eval(x) if x in allFuncs else int(x) if isInt(x) else x, argStr))
        print(args)
        mainFunc(*args)
      else:
        raise Exception
    except Exception as e:
      print('Proper usage: python testingTIckTack.py func arg1 arg2...')
      raise e
  else:
    #playNGames(minimax_ai, find_winning_moves_ai, 10)
    pass