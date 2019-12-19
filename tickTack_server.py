#########
# Tick Tack Server
# by Joseph Sandler
# adapted from sockets tutorials for 15-112 by Rohan Varma and Kyle Chin
#########

import socket
import threading
from queue import Queue
from tickTackAi import newBoard, isValid, execMove, gameOver, hasWinner

HOST = ""
PORT = 50003
BACKLOG = 2 # 2 players... it's tick tack toe.... (Could take 1 if playing server ai...)
CHUNK = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(BACKLOG)
print('awaiting connection')

def handleClient(client, serverChannel, cID, clientele, data):
  client.setblocking(1)
  msg = ""
  while True:
    try:
      msg += client.recv(CHUNK).decode("UTF-8")
      command = msg.split("\n")
      while (len(command) > 1):
        readyMsg = command[0]
        msg = "\n".join(command[1:]) #wouldn't it just be easier to say command = command[1:]
        serverChannel.put(str(cID) + " " + readyMsg)
        command = msg.split("\n")
    except:
      # something went wrong
      return

def sendToClient(msg, client, iD):
  client.send(msg.encode())
  print("> sent to", iD, msg[:-1])

def eventLoop(data, clientele, instruction, senderID, details):
  # not a true loop syntactically, but a loop is created by the exchange of events
  details = details.split()
  role, x, y = details[0], int(details[1]), int(details[2])
  data.board = execMove(data.board, (x,y), role) # maintain servers copy of board
  data.gameOver = gameOver(data.board)
  data.winner = hasWinner(data.board)
  details = " ".join(details)
  for cID in clientele:
    if cID != senderID:
      sendMsg = instruction + " " + senderID + " " + details + "\n"
      sendToClient(sendMsg, clientele[cID], cID)
      # also request move from this same other player
      # if you wanted to add Ai, add it here, getting move from ai and adding to server queue as a move made. Also will need to add flag to data indicating that we're playing against ai
      if not (data.gameOver or data.winner): # DeMorgan can eat my butt
        sendMsg = "inputRequest\n"
        sendToClient(sendMsg, clientele[cID], cID)
  if data.winner or data.gameOver:
    # checking if data.winner is truthy aka not False
    sendMsg = "gameOver "
    if data.winner:
      sendMsg += data.winner + "\n"
    else:
      #data.gameOver was true and no winner
      sendMsg += "draw\n"
    for cID in clientele:
      sendToClient(sendMsg, clientele[cID], cID)

def serverThread(clientele, serverChannel, data):
  while True:
    msg = serverChannel.get(True, None)
    print("msg recv: ", msg)
    msgList = msg.split(" ")
    senderID = msgList[0]
    instruction = msgList[1]
    details = " ".join(msgList[2:])
    if senderID == "server" and instruction == "startGame":
      # tell each client to start game
      for cID in clientele:
        playerRole = 'X' if (cID[-1] == '0') else 'O' if (cID[-1] == '1') \
                                                                      else None
      # assign roles
        sendMsg = instruction + " " + senderID + " " + playerRole + "\n"
        sendToClient(sendMsg, clientele[cID], cID)
      # send inputRequest event to X
      sendMsg = "inputRequest\n"
      sendToClient(sendMsg, clientele["player0"], "player0")
    

    if instruction == "madeMove":
      # creates event loop triggered by first request for a move
      eventLoop(data, clientele, instruction, senderID, details)

## Send other shit to other player, apparently not caught otherwise
    elif (details != ""): 
      # deal with move data, verify/validate
      #send to client, or reject
      for cID in clientele:
        if cID != senderID:
          sendMsg = instruction + " " + senderID + " " + details + "\n"
          sendToClient(sendMsg, clientele[cID], cID)
    print()
    serverChannel.task_done()



class Struct(object): pass
data = Struct()

clientele = dict()
playerNum = 0

serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel, data)).start() ########HOW DOES THREAD WORK
data.gameStarted = False

def init(data):
  data.gameStarted = True
  data.turn = False # (using as a switch for player 0/player 1, str(int(bool))
  data.board = newBoard()
  data.gameOver = False
  data.winner = False


while True:
  client, address = server.accept() #blocking call which waits for connection to server

  myID = "player" + str(playerNum)
  print(myID, playerNum)
  for cID in clientele:
    print(repr(cID), repr(playerNum))
    clientele[cID].send(("newPlayer %s\n" % myID).encode()) # sends newPlayer event with player to other player on server
    client.send(("newPlayer %s\n" % cID).encode()) # tells new player about other player
  clientele[myID] = client # add new player to dict of clients
  client.send(("myIDis %s\n" % myID).encode()) # lets client know what their name is on server
  print("connection reveived from %s at %s" % (myID, address))
  threading.Thread(target = handleClient, args = (client, serverChannel, myID, clientele, data)).start() # starts thread for client

  playerNum += 1
  if playerNum == 2 and not data.gameStarted:
    msg = "server startGame"
    serverChannel.put(msg)
    init(data)
