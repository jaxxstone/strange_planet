# strange planet program
# rule: 2 species contribute by 1 each to produce qty 2 of the next specie (in m>3 this should allow for all comb)
# v15b - inc to v15a -jgraph +neo4j. Neo (user: neo4j, pass: test)
# initial combinations set produced based on: https://docs.python.org/2/library/itertools.html
# logical graph implemented based on: http://interactivepython.org/runestone/static/pythonds/Graphs/Implementation.html
# Neo4j and python integration based on: http://nicolewhite.github.io/neo4j-jupyter/hello-world.html
from itertools import combinations
from itertools import combinations_with_replacement
import numpy as np
import pandas as pd
import copy
from py2neo import authenticate, Graph
from py2neo import Node, Relationship, NodeSelector
from py2neo import Graph as PGraph
import jgraph
from neo4jrestclient.client import GraphDatabase

# used by simple logical graph construct
class Vertex:
    def __init__(self,key):
        self.id = key
        self.connectedTo = {}

    def addNeighbor(self,nbr,weight=0):
        self.connectedTo[nbr] = weight

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

    def getConnections(self):
        return self.connectedTo.keys()

    def getId(self):
        return self.id

    def getWeight(self,nbr):
        return self.connectedTo[nbr]

# simple logical graph construct, gets job done    
class GraphI:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self,f,t,cost=0):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t], cost)

    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values())

def add_to_final_struct(g, out, out1):
    out1p = [int(e) for e in out1]
    outp = [int(e) for e in out]
    parent_node ='-'.join(str(e) for e in outp) # if n has more than single digit replace '' with '-' on this and next line
    child_node = '-'.join(str(e) for e in (sorted((out1p), reverse=True)))    
    if (g.getVertex(parent_node) == None):
        g.addVertex(parent_node)
        
    parnt = g.getVertex(parent_node)
    if (g.getVertex(child_node) == None):
        g.addVertex(child_node)
    chld = g.getVertex(child_node)
    # this is for neo, need to find out what makes sense to keep parent and child the same node
#    parnt = Node("Parent", name=parent_node)
    reps = 0
    for parnt in g:
        if chld in parnt.getConnections():
            reps = parnt.getWeight(chld) # getting number of repeated trips or connections from parent to child
    # need to make increment instead of 1 in the line below
    g.addEdge(parent_node, child_node, reps+1)  

    # add relationship to external db table from here or outside of subroutine

    return 0

#############################################################################
## **** MAIN ****
#############################################################################

n = int(input ("Enter the total number of individuals: ")) # number of people
m = int(input("Enter the number of species: ")) # number of groups

lst = range(n, -1, -1)
alist = []
# need to replace the following 5 lines with the iterative construct as further below
# complexity of python comb_with_repl is O(r * (n! / (r! (n - r)!))), discussed at the link below
# see: http://stackoverflow.com/questions/20764926/combinations-without-using-itertools-combinations
for comb in combinations_with_replacement(lst,m):
    if sum(comb) == n:
        alist.append(comb)        
print (alist)
total_combinations = len(alist)
print ("Number of combinations: ", total_combinations)

g = GraphI() # logical attempt, v9

# set up authentication parameters
authenticate("localhost:7474", "neo4j", "test")

# connect to authenticated graph database, v10 of program
graph = Graph("http://localhost:7474/db/data/")
db = GraphDatabase("http://localhost:7474/db/data/") # this is using REST Client, testing
graph.delete_all()

row_cnt = 0

for comb in alist:
    count = 0
    # next For and If constructs take care of MUST_FAIL case where there is less than 2 species on the planet
    for i in range(m):
        if (comb[i] == 0):
            count = count + 1
    if (count >= m-1):
        print ("Must fail: ", comb) # need to add "must_fail" combination to db table from here
        must_fail = [int(e) for e in comb]
        p_must_fail ='-'.join(str(e) for e in must_fail) # for more than single digit n, change '' to '-' as separator
        if (g.getVertex(p_must_fail) == None):
            g.addVertex(p_must_fail)
        temp = ','.join(map(str, comb))
        row_cnt = row_cnt + 1
        
    else: # there are at least 2 elements !=0, so they can produce child
        out = np.zeros(m)
        for i in range (m):
            if (comb[i] != 0):
                out[i] = comb[i]
        print ("parent: ", out)
        temp = ','.join(map(str, comb))
        row_cnt = row_cnt + 1

        # decrement value of j-th element (first working value in the tuple) - line 63
        for i in range(m):
            if (out[i] != 0):
                #out1 = np.zeros(m)
                out1 = copy.deepcopy(out)
                out1[i] = out[i] - 1
                for j in range(i+1, m):
                    if (out[j] != 0): #line 65 pseudocode
                        out1[j] = out[j] - 1
                        out2 = copy.deepcopy(out1)
                        for k in range(m):
                            if (i != k and j != k):
                                out1[k] = out[k] + 2
                                print ("\tchild: ", out1)
                                add_to_final_struct(g, out, out1) # call to subrotine, check complexity
                                out1 = copy.deepcopy(out2)
                    else:
                        break
                    #out1 = sorted(out1, reverse=True) # need to sort outside of the loop, in add_to_final_struct
                    out1 = copy.deepcopy(out)
                    if (j != m-1):
                        out1[i] = out[i] - 1

from scripts.vis import draw
options = {"State": "name"}

v_arr = []
print (sorted(g.getVertices(), reverse=True)) # printing all vertices in order

query = """
MATCH (p:State)
WHERE p.name = {name}
RETURN p
"""

relship = """
START n=node(*), m=node(*)  
where exists(n.name) and exists(m.name) 
and n.name = {prev_state} 
and m.name = {next_state} 
create (n)-[:MOVES_TO]->(m)
"""

for v in g:
    v_curr = str(v.getId())
    x_curr = Node("State", name = v_curr) # jupyter try
    graph.create(x_curr) # jupyter try  
    
for v in g:
    v_curr = str(v.getId())
    x_curr = graph.run(query, name = v_curr) # jupyter try
    for w in v.getConnections():
        print("( %s, %s , %s )" % (v.getId(), w.getId(), v.getWeight(w))) # printing all relationships
        w_curr = str(w.getId())
        y_curr = graph.run(query, name = w_curr) # jupyter try
        graph.run(relship, prev_state = v_curr, next_state = w_curr)
          
draw(graph, options)
