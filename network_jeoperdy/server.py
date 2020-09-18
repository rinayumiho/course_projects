#!/usr/bin/env python
# coding: utf-8

# In[3]:


import select
import socket
import queue
import random


# In[9]:


CM_SUBSCRIBE = 10
CM_NEW_ROUND = 11
CM_CATEGORY = 12
CM_CATEGORY_RECV = 13
CM_RING = 14
CM_ANSWER = 15
CM_ANSWER_SHOW = 16

SPLIT = "::"
MIN_PLAYERS = 2

SM_WELCOME = 10
SM_NEW_GAME = 11
SM_NEW_ROUND = 12
SM_CATEGORY = 13
SM_QUESTION = 14
SM_RING_CLIENT = 15
SM_ANSWER = 16

COLLECT_SUBSCRIBTIONS = 0
GAME_IN_PROGRESS = 1
ROUND_IN_PROGRESS = 2
WAIT_RING = 3
WAIT_FOR_RING = 4
WAIT_FOR_CM_ANSWER = 5
ANSWER_SHOW = 6


# In[10]:


PlayerNames = []
Categories = ["Science", "History"]
Answers = [["100 degree C", "High energy matter"],["07/28/1941", "05/23"]]
Questions = [["What is the boiling point of water?", "What is dark matter?"],["When did the first world war start?", "What's the date of 'Memorial Day'"]]
RingIds = []
SelectCate = -1
SelectQues = -1
SelectPlayerId = -1
PlayerAnswer = ""
PointsPerQues = 200
timeout = 60
ServerState = COLLECT_SUBSCRIBTIONS

def readMsg(msg, socketP):
    global PlayerNames
    global Categories
    global Answers
    global SelectCate
    global SelectQues
    global SelectPlayerId
    global Questions
    global RingIds
    global PlayerAnswer
    global ServerState

    field = msg.split(SPLIT)
    RecvMsg = int(field[0])
    msgSent = ""
    if RecvMsg == CM_SUBSCRIBE and ServerState == COLLECT_SUBSCRIBTIONS:
        if len(PlayerNames) < 2:
            player = {}
            player["Name"] = field[1]
            player["Socket"] = socketP
            PlayerNames.append(player)
        if len(PlayerNames) == 2:
            msgSent = str(SM_NEW_GAME) + SPLIT + str(len(PlayerNames)) + SPLIT
            for i, player in enumerate(PlayerNames):
                if i == 0:
                    msgSent = msgSent + player["Name"] + ","
                elif i == 1:
                    msgSent += player["Name"]
            msgSent = msgSent + SPLIT + str(len(Categories)) + SPLIT
            for i, category in enumerate(Categories):
                if i == 0:
                    msgSent = msgSent + category + ","
                elif i == 1:
                    msgSent += category
            msgSent = msgSent + SPLIT + str(PointsPerQues) + SPLIT + str(timeout)
            ServerState = GAME_IN_PROGRESS
    if RecvMsg in (CM_NEW_ROUND, CM_ANSWER_SHOW) and ServerState in (GAME_IN_PROGRESS, ANSWER_SHOW):
        SelectPlayerId = random.randint(1, 2)
        msgSent = str(SM_NEW_ROUND) + SPLIT + str(SelectPlayerId)
        ServerState = ROUND_IN_PROGRESS
    if RecvMsg == CM_CATEGORY and ServerState == ROUND_IN_PROGRESS and int(field[1]) != -1:
        SelectCate = int(field[1])
        SelectQues = random.randint(0, len(Questions[SelectCate])-1)
        msgSent = str(SM_CATEGORY) + SPLIT + str(SelectCate)
        ServerState = WAIT_RING
    if RecvMsg == CM_CATEGORY_RECV and ServerState == WAIT_RING:
        msgSent = str(SM_QUESTION) + SPLIT + Questions[SelectCate][SelectQues]
        ServerState = WAIT_FOR_RING
    if RecvMsg == CM_RING and ServerState == WAIT_FOR_RING:
        RingIds.append(int(field[1]))
        if len(RingIds) == len(PlayerNames):
            msgSent = str(SM_RING_CLIENT) + SPLIT + str(RingIds[0])
            ServerState = WAIT_FOR_CM_ANSWER
    if RecvMsg == CM_ANSWER and ServerState == WAIT_FOR_CM_ANSWER:
        if field[1] != "#":
            PlayerAnswer = field[1]
            msgSent = str(SM_ANSWER) + SPLIT + PlayerAnswer + SPLIT + Answers[SelectCate][SelectQues]
            RingIds = []
            ServerState = ANSWER_SHOW

    return msgSent   



def playerId(socketP):
    global PlayerNames
    for i, player in enumerate(PlayerNames):
        if socketP == player["Socket"]:
            return i
        


# In[15]:


# Create a TCP/IP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)

# Bind the socket to the port
server_address = ('127.0.0.1', 33333)
print('starting up on %s port %s' % server_address)
server.bind(server_address)

# Listen for incoming connections
server.listen(3)

# Sockets from which we expect to read
inputs = [server]

# Sockets to which we expect to write
# deal with the message which we expect to send
outputs = []

# Outgoing message queues (socket: Queue)
message_queues = {}

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

  # Handle inputs
  # 循环判断是否有客户端连接进来, 当有客户端连接进来时select 将触发
    for s in readable:
    # 判断当前触发的是不是服务端对象, 当触发的对象是服务端对象时,说明有新客户端连接进来了
    # 表示有新用户来连接
        if s is server:
      # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
            print('connection from', client_address)
      # this is connection not server
            connection.setblocking(0)
      # 将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
            inputs.append(connection)

      # Give the connection a queue for data we want to send
      # 为连接的客户端单独创建一个消息队列，用来保存客户端发送的消息
            message_queues[connection] = queue.Queue()
            m = str(SM_WELCOME) + SPLIT + "Hello!"
            msg = m.encode()
            message_queues[connection].put(msg)
            if connection not in outputs:
                outputs.append(connection)
        else:
      # 有老用户发消息, 处理接受
      # 由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(input_list), 客户端发送消息将触发
      # 所以判断是否是客户端对象触发
            data = s.recv(1024)
      # 客户端未断开
            if data:
        # A readable client socket has data
#                 print('received "%s" from %s' % (data.decode(), s.getpeername()))
                msg = readMsg(data.decode(), s).encode()
#                 print('sent "%s"'% msg.decode())
                for player in PlayerNames:
                    s1 = player["Socket"]
        # 将收到的消息放入到相对应的socket客户端的消息队列中
                    message_queues[s1].put(msg)
        # Add output channel for response
        # 将需要进行回复操作socket放到output 列表中, 让select监听
                    if s1 not in outputs:
                        outputs.append(s1) 
            else:
        # 客户端断开了连接, 将客户端的监听从input列表中移除
        # Interpret empty result as closed connection
                print('closing', client_address)
        # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                try:
                    del PlayerNames[playerId(s)]
                except:
                    pass
                del message_queues[s]

  # Handle outputs
  # 如果现在没有客户端请求, 也没有客户端发送消息时, 开始对发送消息列表进行处理, 是否需要发送消息
  # 存储哪个客户端发送过消息
    for s in writable:
        try:
      # 如果消息队列中有消息,从消息队列中获取要发送的消息
            msg = message_queues[s].get_nowait()
            print('sent "%s"' % (msg).decode())
        except queue.Empty:
      # 客户端连接断开了
#             print("%s" % (s.getpeername()))
            outputs.remove(s)
        else:
      # print("sending %s to %s " % (send_data, s.getpeername))
      # print("send something")
            s.send(msg)
      # del message_queues[s]
      # writable.remove(s)
      # print("Client %s disconnected" % (client_address))

  # # Handle "exceptional conditions"
  # 处理异常的情况
    for s in exceptional:
        print('exception condition on %s' % (s.getpeername()))
    # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

    # Remove message queue
        del message_queues[s]
server.close()


# In[ ]:




