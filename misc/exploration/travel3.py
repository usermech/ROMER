import math
import cv2
import numpy as np
from matplotlib import pyplot as plt

class Graph:
    def __init__(self, graph_dict=None):
        if graph_dict is None:
            graph_dict = {}
        self.__graph_dict = graph_dict
    
    # function to add a node to the graph
    def add_node(self, node):
        if node not in self.__graph_dict:
            self.__graph_dict[node] = []
    
    # function to add an edge to the graph
    def add_edge(self, edge):
        edge = set(edge)
        (node1, node2) = tuple(edge)
        if node1 in self.__graph_dict:
            self.__graph_dict[node1].append(node2)
        else:
            self.__graph_dict[node1] = [node2]

    def make_undirected(self):
        '''
        If node A is connected to node B, then node B is also connected to node A with an edge
        '''
        for node in self.__graph_dict:
            for neighbour in self.__graph_dict[node]:
                if node not in self.__graph_dict[neighbour]:
                    self.__graph_dict[neighbour].append(node)
    
    # function to get the graph dictionary
    def get_graph_dict(self):
        return self.__graph_dict


def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def collision(p1, p2, img):
    dist = distance(p1, p2)
    num_steps = int(dist)
    x_vals = np.linspace(p1[0], p2[0], num_steps)
    y_vals = np.linspace(p1[1], p2[1], num_steps)
    for x, y in zip(x_vals, y_vals):
        if img[int(y), int(x)] == 0:
            return True
    return False

def create_edges(points, img):
    graph = Graph()
    for point in points:
        # sort the points by distance from the current point if they are not the same point and the distance is less than 10
        sorted_points = sorted(points, key=lambda p: distance(point, p))
        sorted_points = [p for p in sorted_points if p != point and distance(point, p) < 100]
        
        # check for collisions between the current point and each other point
        for p in sorted_points:
            if not collision(point, p, img):
                if point not in graph.get_graph_dict():
                    graph.add_node(point)
                graph.add_edge((point, p))
    return graph

with open('foreground_centroids.txt', 'r') as f:
    points = [tuple(map(float, line.split())) for line in f]
img = cv2.imread('map_framed.png', 0)
graph = create_edges(points, img)
graph_dict = graph.get_graph_dict() 
# plot the points and edges
plt.imshow(img, cmap='gray')
for point in graph_dict:
    for p in graph_dict[point]:
        plt.plot([point[0], p[0]], [point[1], p[1]], 'r-')
plt.scatter(*zip(*points), c='b')
plt.show()

# Graph class to represent the graph

# depth-first search function
def dfs(graph, node, visited=None):
    if visited is None:
        visited = []
    if node not in visited:
        visited.append(node)
        for neighbour in graph.get(node, []):
            dfs(graph, neighbour, visited)
    return visited

# function to get the order to visit nodes
def get_node_order(graph, start_node):
    visited = dfs(graph.get_graph_dict(), start_node)
    return visited
graph.make_undirected()
graph_dict = graph.get_graph_dict()
order = get_node_order(graph,(39.0, 39.0))
print(order)
# plot the points and edges according to the order of visitation write the indices of the points on the plot
plt.imshow(img, cmap='gray')
for i in range(len(order)-1):
    plt.plot([order[i][0], order[i+1][0]], [order[i][1], order[i+1][1]], 'r-')
    plt.text(order[i][0], order[i][1], str(i))
plt.scatter(*zip(*points), c='b')
plt.show()
