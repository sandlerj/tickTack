# Handles the cache for tic tac minimax
import copy
def readFile(path):
  with open(path, "rt") as f:
    return f.read()

def writeFile(path, contents):
  with open(path, "wt") as f:
    f.write(contents)


CACHE_PATH = 'minimaxCache.txt'
TOKEN = '@'
DELINEATOR = '\n'

#decorator for rendering 2d result more nicely
def print2DArr(f):
  def g(*args):
    result = f(*args)
    for row in range(len(result)):
      print(result[row])
    return result
  return g

# rotates a non-jagged 2d array
# @print2DArr
def rotate2DArray(A):
  oldNumRows = len(A)
  oldNumCols = len(A[0])
  newNumRows = oldNumCols
  newNumCols = oldNumRows
  result = [[None for col in range(newNumCols)] for row in range(newNumRows)]
  for row in range(oldNumRows):
    for col in range(oldNumCols):
      newRow = col
      newCol = newNumCols - (row + 1)
      result[newRow][newCol] = A[row][col]
  return result


def return2D():
  return [[1,2,3],[4,5,6],[7,8,9]]

#mirrors 2d array, axis = 1 mirrors y, axis = 0 mirrors x 
def mirror2DArray(A, axis):
  numRows = len(A)
  numCols = len(A[0])
  result = [[None for col in range(numCols)] for row in range(numRows)]
  if (axis not in {0,1}):
    raise Exception('must define axis (see help(mirror2DArray)')
  for row in range(numRows):
    for col in range(numCols):
      if axis == 0:
        newRow = numRows - (row + 1)
        newCol = col
      if axis == 1:
        newRow = row
        newCol = numCols - (col + 1)
      result[newRow][newCol] = A[row][col]
  return result

def getTransforms(board):
  tmpBoard = copy.deepcopy(board)
  transforms = [tmpBoard]
  for _ in range(3):
    tmpBoard = rotate2DArray(tmpBoard)
    transforms.append(tmpBoard)
  mirror = mirror2DArray(tmpBoard, 1)
  transforms.append(mirror)
  for _ in range(3):
    mirror = rotate2DArray(mirror)
    transforms.append(mirror)
  return transforms


# Convert to set of strs
def transformsToStrSet(transforms):
  result = set()
  for board in transforms:
    boardStr = str(board)
    result.add(boardStr)
  return result

#returns dict of boards and scores, where key is board string and
# value is minimax score of a given board
# player should be the one we're maximizing for 
def readCache(player):
  try:
    contents = readFile(CACHE_PATH)
  except FileNotFoundError:
    contents = ''
  except:
    print('Cache was found but not read...')
    contents = ''
  lines = contents.splitlines()
  cache = dict()
  for line in lines:
    boardStr, score, maxi = line.split(TOKEN)
    score = int(score)
    if player != maxi:
      score *= -1
    cache[boardStr] = score
  return cache

def writeCacheDict(cacheDict, maxFor):
  newContents = ''
  for boardStr in cacheDict.keys():
    score = cacheDict[boardStr]
    newContents += boardStr + TOKEN + str(score) + TOKEN + maxFor + DELINEATOR
  try:
    writeFile(CACHE_PATH,  newContents)
  except Exception as e:
    print('ERROR: CACHE NOT UPDATED')


def addBoardsAndScore(cache, board, score):
  transformStrSet = transformsToStrSet(getTransforms(board))
  for boardStr in transformStrSet:
    cache[boardStr] = score