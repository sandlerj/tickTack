#########
# Tick-tack client
# by Joseph Sandler
# Based on sockets tutorial by Rohan Varma and Kyle Chin for 15-112 at CMU
#########

import socket
import threading
from queue import Queue

HOST = "127.0.0.1"
PORT = 50003
CHUNK = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST, PORT))
print("connected to server")

def handlerServerMsg(server, serverMsg):
  server.setblocking(1)
  msg=""
  command=""
  while True:
    msg += server.recv(CHUNK).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

from tickTackAi import render, getMove, newBoard, isValid, execMove, gameOver, hasWinner


def init(data):
  data.board = newBoard()

def sendToServer(msg):
  server.send(msg.encode())
  print('> sent to server:', msg[:-1] )

def inputRequest(data):
  while True:
    coords = getMove()
    try:
      data.board = execMove(data.board, coords, data.role)
      break
    except:
      print("Your input was invalid, probably playing on an invalid space.\nTry again")
  render(data.board)
  print("Sending move to server.")
  sendMsg = "madeMove " + data.role + " " + \
                          str(coords[0]) + " " + str(coords[1]) + "\n"
  sendToServer(sendMsg)

def doMessage(data, msg):
  command = msg.split()
  instruction= command[0]
  if instruction == "startGame":
    init(data)
    data.role = command[2]
    print('Now playing tick-tack-toe with someone somewhere')
    print("Playing as:", data.role)
    render(data.board)
  elif instruction == "inputRequest":
    inputRequest(data)
    
  elif instruction == "madeMove":
    senderID, senderRole, coords = command[1], command[2],\
                                        (int(command[3]), int(command[4]))
    print('Move made by', senderID, 'playing as', senderRole)
    # should have been pre-validated, im going to be lazy and just execute the
    #   move on local board
    data.board = execMove(data.board, coords, senderRole)
    render(data.board)
  elif instruction == "gameOver":
    print("Game over")
    condition = command[1]
    if condition == 'draw':
      print('No one wins')
    else:
      print(condition, 'is the winner')
    render(data.board)

def run(serverMsg=None, server=None):
  class Struct(object): pass
  data = Struct()
  data.gameStarted = False
  init(data)

  while True:
    while (serverMsg.qsize() > 0):
      msg = serverMsg.get(False)
      try:
        print("received: ", msg, "\n")
        doMessage(data, msg)
      except Exception as error:
        print("failed:", error)
      serverMsg.task_done()

serverMsg = Queue(100)
threading.Thread(target = handlerServerMsg, args = (server, serverMsg)).start()

run(serverMsg, server)
