#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Long Chen
# CISC681 hw4 2020S

import random

# Settings - you may alternative the settings including the dimensions of the board
ROW = 4
COLUMN = 4
STATE_SPACE = ROW * COLUMN
START_STATE = 2
ITERATIONS = 10000
LIVING_REWARD = -0.1
DISCOUNT_RATE = 0.2
LEARNING_RATE = 0.1
END_REWARD = 100
FORBIDDEN_REWARD = -100
EPSILON = 0.1

# get user inputs
uInput = input("Please enter input here:")
userInput = list(uInput.split(" "))
endLoc1 = int(userInput[0])
endLoc2 = int(userInput[1])
forbiddenLoc = int(userInput[2])
wallLoc = int(userInput[3])


# In[2]:


# states are held in a maze array
grideWorld = []
# initialize the grideWorld with 12 states
# state = [stateSequence, availableActions, qValues, isEnd, isForbidden, isWall]
for i in range(1, STATE_SPACE + 1):
    # availableActions = [[stateSequence, NESW]...]
    # qValues = [N, E, S, W]
    state = [i, [[0, 'N'], [0, 'E'], [0, 'S'], [0, 'W']], [0, 0, 0, 0], False, False, False]
    grideWorld.append(state)

# assign the donut, forbidden and wall locations
grideWorld[endLoc1 - 1][3] = True
grideWorld[endLoc1 - 1][1] = ['exit']
grideWorld[endLoc1 - 1][2] = [0]
grideWorld[endLoc2 - 1][3] = True
grideWorld[endLoc2 - 1][1] = ['exit']
grideWorld[endLoc2 - 1][2] = [0]
grideWorld[forbiddenLoc - 1][4] = True
grideWorld[forbiddenLoc - 1][1] = ['exit']
grideWorld[forbiddenLoc - 1][2] = [0]
grideWorld[wallLoc - 1][5] = True


# justify the wall location to see if the going state is a wall.
# if it's not a wall, update the available actions for the current state
def isThisWall(stateSequence, direction):
    if direction == 'N':
        if grideWorld[stateSequence - 1 + COLUMN][5] == False:
            grideWorld[stateSequence - 1][1][0][0] = stateSequence + COLUMN
    elif direction == 'E':
        if grideWorld[stateSequence - 1 + 1][5] == False:
            grideWorld[stateSequence - 1][1][1][0] = stateSequence + 1
    elif direction == 'S':
        if grideWorld[stateSequence - 1 - COLUMN][5] == False:
            grideWorld[stateSequence - 1][1][2][0] = stateSequence - COLUMN
    elif direction == 'W':
        if grideWorld[stateSequence - 1 - 1][5] == False:
            grideWorld[stateSequence - 1][1][3][0] = stateSequence - 1
           



# In[3]:


for state in grideWorld:
    if state[3] != True and state[4] != True and state[5] != True:
        # square is at the four corners, can go to 2 different states based on their location
        if state[0] in [1, COLUMN, (ROW - 1) * COLUMN + 1, ROW * COLUMN]:
            if state[0] % COLUMN == 1:
                # under an action - if the going state is not wall,
                # isThisWall() will add this action to availableActions
                # same functionality if similar coding block occurs in this loop
                isThisWall(state[0], 'E')
                # lower left corner
                if state[0] == 1:
                    isThisWall(state[0], 'N')
                # upper left corner
                elif state[0] == (ROW - 1) * COLUMN + 1:
                    isThisWall(state[0], 'S')
            elif state[0] % COLUMN == 0:
                isThisWall(state[0], 'W')
                # lower right corner
                if state[0] == COLUMN:
                    isThisWall(state[0], 'N')
                # upper right corner
                elif state[0] == ROW * COLUMN:
                    isThisWall(state[0], 'S')
        # square is along the south edge, excluding the lower left and lower right corners, having three actions - N, E, W
        elif state[0] in range(2, (COLUMN - 1) + 1):
            for direction in ['N', 'E', 'W']:
                isThisWall(state[0], direction)
        # square is along the north edge, excluding the upper left and lower right corners, having three actions - E, S, W
        elif state[0] in range((ROW - 1) * COLUMN + 1 + 1, (ROW * COLUMN) - 1 + 1):
            for direction in ['E', 'S', 'W']:
                isThisWall(state[0], direction)
        # square is along the west edge, excluding the upper left and lower left corners, having three actions - N, E, S
        elif state[0] in range(1 * COLUMN + 1, (ROW - 2) * COLUMN + 1 + 1, COLUMN):
            for direction in ['N', 'E', 'S']:
                isThisWall(state[0], direction)
        # square is along the east edge, excluding the upper right and lower right corners, having three actions - N, S, W
        elif state[0] in range(2 * COLUMN, (ROW - 1) * COLUMN + 1, COLUMN):
            for direction in ['N', 'S', 'W']:
                isThisWall(state[0], direction)
        # square is not on the edge, having four actions - N, E, S, W
        else:
            for direction in ['N', 'E', 'S', 'W']:
                isThisWall(state[0], direction)

# print(grideWorld)


# In[4]:


# based on the Q-values of the current state, calculate the best action
# if epsilon falls into the probability then a random action is chosen
def bestAction(qValues, epsilon):
    direction = qValues.index(max(qValues))
    if direction == 0:
        action = 'N'
    elif direction == 1:
        action = 'E'
    elif direction == 2:
        action = 'S'
    else:
        action = 'W'
    probability = random.uniform(0, 1)
    if probability <= epsilon:
        return random.choice(['N', 'E', 'S', 'W'])
    return action


# the function updates the Q-values for the current state and
# return the going state based on the action received from bestAction()
def updateQValAndReturnGoingState(state, action):
    if len(state[1])!= 1:
        if action == 'N':
            qValueIndex = 0
        elif action == 'E':
            qValueIndex = 1
        elif action == 'S':
            qValueIndex = 2
        elif action == 'W':
            qValueIndex = 3
        for actionItem in state[1]:
            if actionItem[1] == action:
                goingState = actionItem[0]
       
        if goingState == 0:
#     this means the going state is either a wall or boundary
#     in this case, the agent bounces back, which means s' = s
#     the max Q value of the going state becomes its own max Q value
            goingStateMaxQVal = max(state[2])
        else:
            goingStateMaxQVal = max(grideWorld[goingState - 1][2])
        state[2][qValueIndex] = (1 - LEARNING_RATE) * state[2][qValueIndex] + LEARNING_RATE * (LIVING_REWARD + DISCOUNT_RATE * goingStateMaxQVal)
        return goingState


# update the value of the exit states - end or forbidden
def updateValExitStates(state):
    if state[3] == True:
        exitReward = END_REWARD
    elif state[4] == True:
        exitReward = FORBIDDEN_REWARD
    state[2][0] = (1 - LEARNING_RATE) * state[2][0] + LEARNING_RATE * (exitReward)

    # start Q learning
i = 0
sequence = START_STATE
while i < ITERATIONS:
    state = grideWorld[sequence - 1]
    epsilon = EPSILON
    while state[3] != True and state[4] != True:
        # not the exit state, update Q values and go to the next state
        action = bestAction(state[2], epsilon)
        sequence = updateQValAndReturnGoingState(state, action)
        state = grideWorld[sequence - 1]
    updateValExitStates(state)
    sequence = START_STATE
    i += 1
#   reach exit state, update value and restart if iteration is still on going


# In[5]:


# OUTPUT1 - print the optimal policy
def printOptimal():
    print('')
    print("Q-values after", ITERATIONS, "iterations:\n")
    for state in grideWorld:
        if state[3] == False and state[4] == False and state[5] == False:
            availableActions = []
            for actionItem in state[1]:
                if actionItem[1] == 'N':
                    availableActions.append(['↑', state[2][0]])
                elif actionItem[1] == 'E':
                    availableActions.append(['→', state[2][1]])
                elif actionItem[1] == 'S':
                    availableActions.append(['↓', state[2][2]])
                elif actionItem[1] == 'W':
                    availableActions.append(['←', state[2][3]])
            action, qVal = max(availableActions, key=lambda item: item[1])
            print(state[0], ' ', action)
# OUTPUT2 - print the Q-values of the designated state
def printQVals(stateSequence):
    print("")
    print("Q-values after", ITERATIONS, "iterations:\n")
    print("State", stateSequence, "has optimal Q-values:")
    if len(grideWorld[stateSequence - 1][2])>1:
        print('↑ ', "%.2f"%(grideWorld[stateSequence - 1][2][0]))
        print('→ ', "%.2f"%(grideWorld[stateSequence - 1][2][1]))
        print('↓ ', "%.2f"%(grideWorld[stateSequence - 1][2][2]))
        print('← ', "%.2f"%(grideWorld[stateSequence - 1][2][3]))
    else:
        print('exit ', "%.2f"%(grideWorld[stateSequence - 1][2][0]))


# In[6]:


# debug - print the Q values of every state
# for state in grideWorld:
#     print(state[0], state[2])

# output based on the input arguments
if len(userInput) == 5:
    printOptimal()
else:
    stateSequence = int(userInput[5])
    printQVals(stateSequence)


# In[ ]:




