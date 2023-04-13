import pickle
import networkx as nx
import math
import numpy as np

class NavChoice():
    
    def __init__(self, current, tovisit, path, dist, choices):
        '''
        current: which point am I on currently?
        tovisit: which points do I need to visit?
        path: how did I get here?
        dist: how much distance did I travel to get here?
        choices: which waypoints did I visit in order to get here?
        '''
        self.current=current
        self.tovisit=tovisit
        self.path=path
        self.dist=dist
        self.choices=choices
        self.to={}
    
    def exploreopts(self, graph):
        '''
        find the path to each waypoint and calculate the cost for each option
        
        graph: the roadmap.
        
        returns a list of the options and their costs, and whether all waypoints have been visited.
        format is [waypoint, cost, done?]
        '''
        
        costs=[]
        
        for waypoint in self.tovisit:
            #print(f"from {self.current} to {waypoint}")
            # check cache - does astar path already exist?
            if str(self.current)+str(waypoint) in cache:
                # we have this exact computation
                cachelabel=str(self.current)+str(waypoint)
                path=cache[cachelabel]["path"]
                dist=cache[cachelabel]["dist"]
            elif str(waypoint)+str(self.current) in cache:
                # we have the inverse of this computation
                cachelabel=str(waypoint)+str(self.current)
                path=cache[cachelabel]["path"]
                # reverse list
                path=[path[i] for i in range(len(path)-1, -1, -1)]
                dist=cache[cachelabel]["dist"]
            else:
                path=nx.astar_path(graph, self.current, waypoint, heuristic=distance)
                
                # convert into floats
                path=[(float(i[0]),float(i[1])) for i in path]
                
                # find how long the path is
                dist=0
                for i in range(len(path)-1):
                    dist+=distance(path[i], path[i+1])

                # save result to cache.
                cachelabel=str(self.current)+str(waypoint)
                cache[cachelabel]={}
                cache[cachelabel]["path"]=path
                cache[cachelabel]["dist"]=dist
            
            wpchoice=NavChoice(waypoint,
                               [i for i in self.tovisit if i != waypoint],
                               self.path+path,
                               self.dist+dist,
                               self.choices+[waypoint])
            
            self.to[str(waypoint)]=wpchoice
            costs.append([wpchoice.choices, wpchoice.dist, len(wpchoice.tovisit)==0])
            
        return costs

def distance(p1,p2):
    '''
    L2 norm
    '''
    #return np.linalg.norm(np.array(p2)-np.array(p1))
    #return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

'''
def exploreopts(graph, pathdict):
    pathdict["to"]={}
    for waypoint in pathdict["tovisit"]:
        print(f"starting with {pathdict['start']} and {waypoint}")
        path=nx.astar_path(graph, pathdict["start"], waypoint, heuristic=distance)
        
        path=[(float(i[0]),float(i[1])) for i in path]
        #print(f"path: {path}")
        
        dist=0
        for i in range(len(path)-1):
            dist+=distance(path[i], path[i+1])
        #print(dist)
        
        pathdict["to"][str(waypoint)]={}
        pathdict["to"][str(waypoint)]["start"]=waypoint
        pathdict["to"][str(waypoint)]["tovisit"]=[i for i in pathdict["tovisit"] if i != waypoint]
        pathdict["to"][str(waypoint)]["path"]=path
        pathdict["to"][str(waypoint)]["dist"]=dist
#'''
        
def getpathdict(tree, route):
    '''
    get a node in the tree.
    
    tree: the root of the navigation tree. NavChoice object.
    route: a list with the names of each waypoint to go to.
    '''
    current=tree
    for i in route:
        current=current.to[str(i)]
    return current


# load the roadmap file
with open("roadmap.pickle", "rb") as f:
    graph=pickle.load(f)

# load the waypoints file
with open('foreground_centroids.txt', 'r') as f:
    waypoints = [tuple(map(float, line.split())) for line in f]
# add starting point into the waypoints as well as the last element
startingpoint=(0,0)
waypoints.append(startingpoint)

# we need to connect all waypoints to the graph nodes they are closest to.
nodecoords=list(graph.nodes())

# store closest node to each one here
closest=[[waypoint, distance(waypoint,nodecoords[0]), nodecoords[0]] for waypoint in waypoints]

for node in graph.nodes():
    for j,waypoint in enumerate(closest):
        # if this node is closer to the waypoint, add it as closest
        newdist=distance(waypoint[0], node)
        if newdist < waypoint[1]:
            closest[j]=[waypoint[0], newdist, node]

# add waypoints to graph. index them as negative.
for waypoint in closest:
    graph.add_node(waypoint[0])
    graph.add_edge(waypoint[2], waypoint[0])

# visualize new graph
'''
from matplotlib import pyplot as plt
import cv2
plt.figure()
img = cv2.imread("map_framed.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = img//240
plt.imshow(img)

nodecoords={i:i for i in graph.nodes()}
nx.draw(graph, nodecoords)
#'''

# to cache results of each astar operation.
cache={}

# do a djikstra search to find the order in which to visit the waypoints
navtree=NavChoice(startingpoint, waypoints[:-1], [], 0, [])

toexplore=navtree
pending=[]
while True:
    # check all options of the current node to explore
    pending+=toexplore.exploreopts(graph)
    # check if any of the options have completed the task
    completed=[i for i in pending if i[2]]
    if len(completed):
        break
    # sort by distance
    pending.sort(key=lambda x: x[1])
    # cull the last 10% of the list (they probably aren't the right choice anyway)
    # this parameter can be increased to get better results. 100 (cull 1%) finds a shorter path, but takes a few seconds to find it.
    todel=len(pending)//10
    if todel:
        del pending[-todel:]
        #print(f"deleted {todel} elements")
    # get the object for the lowest cost option
    toexplore=getpathdict(navtree, pending.pop(0)[0])

print(completed)
