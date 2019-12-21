## AIs and helpers for ttt



import random, math
from collections import Counter
import minimaxCaching
from tickTackMain import execMove, hasWinner, gameOver, WINNING_LINES

def has_win_for_player(board, turn):
  for line in WINNING_LINES:
    lineContents = [board[coord[1]][coord[0]] for coord in line]
    if lineContents.count(turn) == 2 and lineContents.count(None) == 1:
      i = lineContents.index(None) #index of None in the line
      return line[i] # Coords of that None
  return None


def find_winning_moves_ai(board, turn):
  # see if there's a winning move
  #otherwise, return rand coords:
  coords = has_win_for_player(board, turn)
  if coords != None:
    return coords
  else:
    coords = random_ai(board, turn)
  return coords


def find_winning_and_blocking_moves_ai(board, turn):
  # see if there's a winning move
  #otherwise, return rand coords:
  opponent = 'O' if (turn == 'X') else 'X'
  coords = has_win_for_player(board, turn)
  blockingCoords = has_win_for_player(board, opponent)
  if coords != None:
    return coords
  elif blockingCoords != None:
    return blockingCoords
  else:
    return random_ai(board, turn)
  

def randCoords():
  return (random.randint(0,2), random.randint(0,2))

def random_ai(board, turn):
  #gets random move from "AI"
  while True:
    try:
      coords = randCoords()
      execMove(board, coords, turn)
      return coords
      break
    except:
      pass

def hooman_player(board, turn):
  return getMove()


# Chooses move which results in most bad options for opponent
# return move with most winning options assuming opponent makes mistake
def minimaxTiebreak(possibleMoves, board, turn, cache):
  opponent = 'O' if (turn == 'X') else 'X'
  scores = Counter()
  for move in possibleMoves:
    tmpBoard = execMove(board, move, turn)
    # Then for tmp board, count possible moves which lead to +10 minimax score
    possOppMoves = getLegalMoves(tmpBoard)
    for oppMove in possOppMoves:
      tmpTmpBoard = execMove(tmpBoard, oppMove, opponent)
      tmpScore = minimax_score(tmpTmpBoard, turn, turn, cache)
      if (tmpScore >= 10):
        # Increment if subsequent move leads to win
        scores[move] += 1
      elif tmpScore >= 0:
        # There may not be any 'winning' moves at this point, so initialize some
        # other 'non-losing' score at 0 to prevent index error below
        # but ensure it won't win out over a better move
        scores[move] += 0

  # return move with most winning options assuming opponent makes mistake
  # most_common returns list of tuples of move and '10 count'

  bestMove = scores.most_common(1)
  coords = bestMove[0][0]
  return coords



def minimax_score(board, current_player, maxFor, cache, alpha=-math.inf, beta=math.inf):
  # First, check if this board state has already been cached
  if cache != None:
      boardStr = str(board)
      if boardStr in cache:
        # Found the board, moving on
        return cache[boardStr]

  # Either not caching, or board has not been seen yet
  # Check if endstate ( base case)
  tmpWinner = hasWinner(board)
  if tmpWinner != False:
    if tmpWinner == maxFor:
      return 10
    else:
      return -10
  elif gameOver(board):
    return 0

  else: # Recursive call with alpha-beta pruning

    # All children of current node
    legal_moves = getLegalMoves(board)

    if current_player == maxFor:
      score = -math.inf
      for move in legal_moves:
        tmpBoard = execMove(board, move, current_player)
        otherPlayer = 'O' if (current_player == 'X') else 'X'
        tmpScore = minimax_score(tmpBoard, otherPlayer, maxFor, cache, alpha, beta)
        score = max(score, tmpScore)
        alpha = max(alpha, score)
        if alpha >= beta:
          break
      return score

    else:
      score = math.inf
      for move in legal_moves:
        tmpBoard = execMove(board, move, current_player)
        otherPlayer = maxFor
        tmpScore = minimax_score(tmpBoard, otherPlayer, maxFor, cache, alpha, beta)
        score = min(score, tmpScore)
        beta = min(beta, score)
        if alpha >= beta:
          break
      return score


def minimax_ai(board, turn, tieBreak=True, caching=True):
  # Will not function properly if board passed in is in game over state.

  moves = getLegalMoves(board)
  scoreMoves = []
  opponent = 'O' if (turn == 'X') else 'X'
  if caching:
    cache = minimaxCaching.readCache(turn)
  else:
    cache = None

  bestScore = -math.inf
  bestMove = []

  for move in moves:
    tmpBoard = execMove(board, move, turn)
    score = minimax_score(tmpBoard, opponent, turn, cache)
    if caching:
      minimaxCaching.addBoardsAndScore(cache, tmpBoard, score)
    if score > bestScore:
      bestScore = score
      bestMove = [move]
    elif score == bestScore:
      bestMove.append(move)
  ## Tie break
  if len(bestMove) > 1 and tieBreak:
    bestMove = minimaxTiebreak(bestMove, board, turn, cache)
  else:
    bestMove = bestMove[0]
  ##
  if caching:
    minimaxCaching.writeCacheDict(cache, turn)
  return bestMove

########################################################
#returns all legal moves on the board
def getLegalMoves(board):
  moves = []
  for row in range(len(board)):
    for col in range(len(board[row])):
      if board[row][col] == None:
        moves.append((col,row))
  return moves