#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Author: Long Chen
CISC 681 AI, HW1 pancake flipping with BFS and A* algorithms
"""


# In[2]:


# Global Variable
goalId = '1w2w3w4w'
# build a node class to be easy show result and search
class PancakeNode:
    def __init__(self, nodeId, g, h):
        self.nodeId = nodeId
        self.g = g
        self.h = h
    def show(self):
        return ('{0}, {1}, {2}'.format(self.nodeId, self.g, self.h))
# PancakeNode(goalId, 1,2).show()


# In[3]:


# in: a string sequence
# out: a list of four possible ways to flip, each of the pancakes has an ID number
#     that is consistent with their size followed by a letter “w” or “b”. 
#     The largest pancake has an ID of 4, the next largest 3, next 2, and the smallest 
#     has an ID of 1. The letter “w” refers to the unburnt (white) side is up, 
#     and “b” shows that the burnt side is up. 
#     e.g.expand('1w2b3w4b') = ['1b2b3w4b', '2w1b3w4b', '3b2w1b4b', '4w3b2w1b']
def expand(nodeId):
    sequence = []
    a = nodeId.replace('b','0')
    b = a.replace('w','1')
    one = list(map(int, list(b[:2])))
    two = list(map(int, list(b[2:4])))
    three = list(map(int, list(b[4:6])))
    four = list(map(int, list(b[6:])))
    s = [one] + [two] + [three] + [four]
    for i in range(1, 5):
        s_flip = s[:i]
        s_flip.reverse()
        newS = s_flip+s[i:]
        s[i-1][1] = 1 - s[i-1][1]
        new1 = sum(newS, [])
        new = new1[:]
        for j in range(0, 9):
            if j % 2 != 0:
                if new[j] == 0:
                    new[j] = 'b'
                else:
                    new[j] = 'w'        
        strS = "".join(map(str,new))
        sequence.append(strS)
    return sequence
# expand('1w2b3w4b')


# In[4]:


# BFS algorithm
#finds the shortest path between the start state and goal state
def bfs(nodeId): 
    #keep track of explored nodes
    visited = set()
    #keep track of all the path that the parent node expanded
    fringe = [[nodeId]]
    #keep looping until all nodes in the finge has been explored
    while fringe:
        #pop the first path from the fringe
        graph = fringe.pop(0)
        #get the last node from the path
        parent = graph[-1]
        #return path if start is the goal
        if parent == goalId:
            return graph
        #check whether the node has been visited or not, if yes, ignore it, if no, expand it
        elif parent not in visited:
            #expand the parent to four children(in this case, flip four times and produce four
            #different children)
            children = expand(parent)
            #go through all children that parent produced, construct a new path and put into queue
            for child in children:
                new_graph = list(graph)
                new_graph.append(child)
                fringe.append(new_graph)
                #return path if child is the goal
                if child == goalId:
                    return new_graph
            #mark node as explored
            visited.add(parent)
# print(bfs('4w2b3b1w'))        


# In[5]:


#heuristi funtion h(x)
#calculate the heuristic from goal state, which is 
# the ID of the largest pancake that is still out of place (e.g 1b2w3b4b h(x)=4)
def h_cost(nodeId):
    nodeId4 = nodeId[6:]
    nodeId3 = nodeId[4:6] 
    nodeId2 = nodeId[2:4] 
    nodeId1 = nodeId[:2]
    if nodeId4 != '4w':
        return 4
    elif nodeId3 != '3w':
        return 3
    elif nodeId2 != '2w':
        return 2
    elif nodeId1 != '1w':
        return 1
    else:
        return 0 
# h_cost('3w1b2b4w')


# In[6]:


#output function
#in: the visited node string list from algorithm
#out: still the same list but each element labeled the next flip position
def outPutGen(result):
    output = []
    if result == [goalId]:
        print(goalId)
    else:        
        for i in range(1, len(result)):
            children = []
            expansion = expand(result[i-1])
            inDex = expansion.index(result[i])
            if inDex == 0:
                parent = result[i-1][:2] + '|' + result[i-1][2:]
            elif inDex == 1:
                parent = result[i-1][:4] + '|' + result[i-1][4:]
            elif inDex == 2:
                parent = result[i-1][:6] + '|' + result[i-1][6:]
            elif inDex == 3:
                parent = result[i-1] + '|'
            children.append(parent)
            output.extend(children)
        output.append(goalId)
    print(output)


# In[7]:


#output function: this time show a three element tuple: node string, g cost, h cost
def outPut(result):
    output = []
    if result == [goalId]:
        print(goalId, 'g = 0', 'h = 0')
    else:        
        for i in range(1, len(result)):
            children = []
            expansion = expand(result[i-1])
            inDex = expansion.index(result[i])
            if inDex == 0:
                parent = result[i-1][:2] + '|' + result[i-1][2:]
                cost = 1
            elif inDex == 1:
                parent = result[i-1][:4] + '|' + result[i-1][4:]
                cost = 2
            elif inDex == 2:
                parent = result[i-1][:6] + '|' + result[i-1][6:]
                cost = 3
            elif inDex == 3:
                parent = result[i-1] + '|'
                cost = 4
            children.append(parent)
            children.append(cost)
            output.append(children)
        g = 0
        print('{0}, g = {1}, h = {2}'.format(output[0][0], 0, h_cost(output[0][0].replace('|', ''))))
        for i in range(1, len(output)):
            g += output[i-1][1]
            print('{0}, g = {1}, h = {2}'.format(output[i][0], g, h_cost(output[i][0].replace('|', ''))))
        print('{0}, g = {1}, h = {2}'.format(goalId, g+output[-1][1], 0))
# outPut(['1w2w3w4w'])


# In[8]:


#tie break function, used to break a tie if two string has the same total f cost
#when there is a tie between two nodes, replace “w” with 1 and “b” with 0 to obtain an eight-digit number. 
# After that pick the node with a larger numerical ID chosen.
# e.g.if there is a tie between 4b3w2b1b and 3w4w2b1b, 
#then 4b3w2b1b will be chosen as 40312010>31412010.
def tie_break(sequence):
    newSequence = []
    for i in range(len(sequence)):
        childReplaceW = sequence[i][2].replace('w', '1')
        childReplaceB = childReplaceW.replace('b', '0')
        newChild = childReplaceB
        newSequence.append(newChild)
    a = max(newSequence)
    return sequence[newSequence.index(a)]
# tie_break([(2, 0, '3b4w2b1b'),(3,0,'3w2w4b1b'), (1,5,'4w2b1w3b')])


# In[9]:


import heapq
def heapsort(iterable):
    h = []
    for value in iterable:
        heapq.heappush(h, value)
    return [heapq.heappop(h) for i in range(len(h))]


# In[10]:


#A* algorithm: use a priority queue to perform the repeated selection of minimum (estimated) cost nodes to expand.
#              At each step of the algorithm, the node with the lowest f(x) value is removed from the queue, 
#             the f and g values of its children are updated accordingly,
#             and these children are added to the queue.
#             The algorithm continues until a goal node has a lower f value than any node in the queue (or until the queue is empty)
#             The f value of the goal is then the cost of the shortest path, since h at the goal is zero in an admissible heuristic.
import heapq

def aStar(start):
    #the frontier is a set contains nodes that are ready to be explored
    frontier = set()
    #use min-heap as an auxilary list of the frontier, this contains the same elements but with
    #its g value and total cost. After each operation(eg pop or push), the min-heap still has the order
    #the 0 index element is the smallest cost 
    openHeap = []
    #contains the nodes those have been explored
    closedSet = set()
    cameFrom = dict()
    path = []
  #this is a trace path function, this function can show all the nodes that one path explored  
    def tracePath(cameFrom, node):            
        path = [node]
        while cameFrom.get(node):
            node = cameFrom[node]
            path.append(node)
        path.reverse()
        return path
    frontier.add(start)
    openHeap.append((h_cost(start), 0, start))
    while frontier:
        heapsort(openHeap)
        current = openHeap[0]
        #implement tie-break and pick the appropriate expand node
        if len(openHeap) > 1:
            for i in range(1, len(openHeap)):
                if openHeap[i][2] == current[2]:
                    current = tie_break([openHeap[i], current])
        heapq.heappop(openHeap)
        currentId = current[2]
        currentG = current[1]
        #if the start node is the goal node, return the goal node with g = 0 and f = 0
        if currentId == goalId:
            return tracePath(cameFrom,currentId)
        frontier.remove(currentId)
        closedSet.add(currentId)
        children = expand(currentId)
        #expand the parent and check all children, choose minimum cost node and put into the fontier
        for child in children:    
            g = currentG + (children.index(child)+1)
            newCost = g + h_cost(child)
            if child not in closedSet:
                if child not in frontier:
                    frontier.add(child)
                    heapq.heappush(openHeap, (newCost, g, child))
                elif child in frontier:
                    #if the node has already in the frontier, compare their cost, update to the smallest cost
                    temp_list = list(map(lambda x: x[2], openHeap))
                    indexChild = temp_list.index(child)
                    cost = openHeap[indexChild][0]
                    if newCost < cost:
                        openHeap.remove((cost, openHeap[indexChild][1], child))
                        heapq.heappush(openHeap, (newCost, g, child))
                cameFrom[child] = currentId

# aStar('1b2b3b4w')
        
        
            


# In[11]:


#---------------------------------------------------------------------------#
#Run the code
#userInput = input("Enter input here:")
#inputScan(userInput)
#---------------------------------------------------------------------------#
# if you want to see all the result from each algorithm,
# uncomment the  section below "result of each search"
# and comment out inputScan(userInput)


# In[12]:


#---------------------------------------------------------------------------#
#The input part: scan the input and call the consistent algorithm
def inputScan(nodeStr):
    if len(nodeStr) != 10:
        print('Wrong node input, please enter again!')
    else:
        nodeId = nodeStr[:8]
        algorithm = nodeStr[-1]
        if algorithm == 'b':
            print('Result of BFS:')
            print('**************************')
            result = bfs(nodeId)
            output = outPutGen(result)
        elif algorithm == 'a':
            print('Result of A*:')
            print('**************************')
            result = aStar(nodeId)
            output = outPut(result)
        else:
            print('Sorry, please only use A* or BFS algorithms!')
        return output
inputScan('4w2b3b1w-b')
    


# In[13]:


#Results of each search
#userInput = '4w2b3b1w'
#print('Result of BFS:')
#outPutGen(bfs(userInput))
#print('**************************************************************************')
#print('Result of A*:')
#outPut(aStar(userInput))


# In[ ]:





# In[ ]:




