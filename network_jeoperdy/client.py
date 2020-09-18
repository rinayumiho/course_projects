#!/usr/bin/env python
# coding: utf-8

# In[1]:


from socket import *
from time import ctime
import signal, os


# In[2]:


CM_SUBSCRIBE = 10
CM_NEW_ROUND = 11
CM_CATEGORY = 12
CM_CATEGORY_RECV = 13
CM_RING = 14
CM_ANSWER = 15
CM_ANSWER_SHOW = 16
SPLIT = "::"

SM_WELCOME = 10
SM_NEW_GAME = 11
SM_NEW_ROUND = 12
SM_CATEGORY = 13
SM_QUESTION = 14
SM_RING_CLIENT = 15
SM_ANSWER = 16

JOINING_GAME = 0
GAME_IN_PROGRESS = 1
ROUND_IN_PROGRESS = 2
CATEGORY_SELECTED = 3
DISPLAY_QUESTION = 4
WAIT_FOR_ANSWER = 5
ANSWER_SHOW = 6

PlayerId = -1
PlayerName = ""
timeout = 60
PointsPerQues = -1
CateNames = []
PlayerState = JOINING_GAME

def readMsg(msg):
    global PlayerId
    global PlayerName
    global PlayerState
    global CateNames
    global timeout
    global PointsPerQues
    field = msg.split(SPLIT)
    RecvMsg = int(field[0])    
    if RecvMsg == SM_WELCOME and PlayerState == JOINING_GAME:
        print("Please enter your name:")
        PlayerName = input("Name: ")
        PlayerState = GAME_IN_PROGRESS
        msg = str(CM_SUBSCRIBE) + SPLIT + PlayerName + SPLIT + "#"
    
    if RecvMsg == SM_NEW_GAME and PlayerState == GAME_IN_PROGRESS:
        NumOfPlayers = int(field[1])
        PlayersNames = field[2].split(",")
        NumOfCategories = int(field[3])
        CateNames = field[4].split(",")
        PointsPerQues = int(field[5])
        timeout = int(field[6])
        print("Hello, everyone! Are you ready? Game Start!")
        print("These are basic informations for our players:")
        print("**********"*6)
        print("There are %d players in the game:" % NumOfPlayers)
        for i, playername in enumerate(PlayersNames):
            print("Player: %s, Id: %d" % (playername, i+1))
        print("%d categories:" % NumOfCategories)
        for i, categoryname in enumerate(CateNames):
            print("Category number - %d: %s" % (i, categoryname))
        print("Each category has two questions and each question worth %d points" % PointsPerQues)
        print("You have %d seconds to ring the bell if you know the answer" % timeout)
        PlayerId = PlayersNames.index(PlayerName) + 1
        PlayerState = ROUND_IN_PROGRESS
        msg = str(CM_NEW_ROUND) + SPLIT + str(PlayerId) + SPLIT + "#"
    if RecvMsg == SM_NEW_ROUND and PlayerState in (ROUND_IN_PROGRESS, ANSWER_SHOW):
        ClientId = int(field[1])
        print("Let's start a new round!")
        print("**********"*6)
        if ClientId == PlayerId:
            print("Please select a category:")
            CateId = input("Category: ")
            msg = str(CM_CATEGORY) + SPLIT + CateId + SPLIT + str(PlayerId)
        else:
            print("Wait for Player %d select" % ClientId)
            print("----------"*6)
            msg = str(CM_CATEGORY) + SPLIT + "-1" + SPLIT + str(PlayerId)
        PlayerState = CATEGORY_SELECTED
    if RecvMsg == SM_CATEGORY and PlayerState == CATEGORY_SELECTED:
        CateId = int(field[1])
        CateName = CateNames[CateId]
        print("In this round, the selected category is: %s" % CateName)
        PlayerState = DISPLAY_QUESTION
        msg = str(CM_CATEGORY_RECV) + SPLIT + str(CateId) + SPLIT + "#"
    if RecvMsg == SM_QUESTION and PlayerState == DISPLAY_QUESTION:
        question = field[1]
        print("The question is: %s" % question)
        print("(If you know the answer, press the ring button quickly\n and remember you have 60 seconds to ring the bell).")
        print("$$$$$$$$$$"*6)
        print("Timer start!")
        print("**********"*6)
        class TimeoutError(Exception):
            pass
        def interrupted(signum, frame):
            raise TimeoutError
        signal.signal(signal.SIGALRM, interrupted)
        signal.alarm(60)
        try:
            answer = input("Please ring the bell(enter your ID: 1 or 2) if you know the answer: ")
        except TimeoutError:
            print("\ntimeout!")
            answer = "-1"
        signal.alarm(0)  # 读到输入的话重置信号
        if answer != "-1":
            PlayerState = DISPLAY_QUESTION
            msg = str(CM_RING) + SPLIT + answer + SPLIT + "#"
        else:
            PlayerState = WAIT_FOR_ANSWER
            msg = str(CM_RING) + SPLIT + "#" + SPLIT + "#"
    if RecvMsg == SM_RING_CLIENT and PlayerState == DISPLAY_QUESTION:
        RingPlayerId = int(field[1])
        if PlayerId == RingPlayerId:
            print("**********"*6)
            print("Congratulations! player-%d get the chance to answer this question." % PlayerId)
            print("**********"*6)
            answer = input("Please show your answer: (if you don't know the answer, please enter 'no')")
            PlayerState = ANSWER_SHOW
            msg = str(CM_ANSWER) + SPLIT + answer + SPLIT + "#"
        else:
            print("**********"*6)
            print("Sorry, player %s ring the bell first and you need to wait, you cannot answer the question..." % RingPlayerId)
            PlayerState = ANSWER_SHOW
            msg = str(CM_ANSWER) + SPLIT + "#" + SPLIT + "#"
    if RecvMsg == SM_ANSWER and PlayerState == ANSWER_SHOW:
        PlayerAnswer = field[1]
        CorrAnswer = field[2]
        print("Player's answer is: %s and the correct answer is: %s" % (PlayerAnswer, CorrAnswer))
        print("**********"*6)
        if PlayerAnswer == CorrAnswer:
            print("Good job! Win %s points!" % PointsPerQues)
        else:
            print("Sorry! Wrong answer!")
        PlayerState = ANSWER_SHOW
        msg = str(CM_ANSWER_SHOW) + SPLIT + "#" + SPLIT + "#"
    return msg
       


# In[5]:


serverName = '127.0.0.1'
serverPort = 33333
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
while True:
    msg = clientSocket.recv(1024).decode()
    outmsg = readMsg(msg)
    clientSocket.send(outmsg.encode())
clientSocket.close()


