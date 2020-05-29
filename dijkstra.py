import csv
from queue import PriorityQueue
from pqdict import minpq

class Stop:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.neighbours = []

class Edge:
    def __init__(self, stop1, stop2, dur):
        self.stop1 = stop1
        self.stop2 = stop2
        self.dur = dur

stopNamesDict = {}
pathDurationsDict = {}
stopDurationsDict = {}

def createGraph():
    stops = []
    with open("stopdata.csv") as f:
        data = csv.reader(f)
        next(data)
        for row in data:
            stops.append(Stop(int(row[0]), row[1]))
            stopNamesDict[int(row[0])] = row[1]
            stopDurationsDict[int(row[0])] = int(row[2])

    with open("routedata.csv") as f:
        data = csv.reader(f)
        next(data)
        for row in data:
            stops[int(row[1])].neighbours.append(Edge(int(row[1]), int(row[3]), int(row[4])))
            pathDurationsDict[(int(row[1]), int(row[3]))] = int(row[4])

    return stops

stops = createGraph()
distTo = []
parent = []
pq = minpq()

for i in range(len(stops)):
    distTo.append(float("inf"))
    parent.append(None)

def relax(edge):
    stop1 = edge.stop1
    stop2 = edge.stop2
    dur = edge.dur
    if distTo[stop2] > distTo[stop1] + dur:
        distTo[stop2] = distTo[stop1] + dur
        parent[stop2] = stop1

        if stop2 in pq:
            pq.updateitem(stop2, distTo[stop2])
        else:
            pq.additem(stop2, distTo[stop2])


def searchPath(startID, endID):
    distTo[startID] = 0
    pq[startID] = 0

    while len(pq) > 0:
        stopID = pq.popitem()[0]

        if stopID == endID:
            break

        for edge in stops[stopID].neighbours:
            relax(edge)

def shortestPath(startID, endID):
    totalDur = 0
    end = endID
    path = []
    path.append(stopNamesDict[end])
    while end != startID:
        totalDur += pathDurationsDict[(parent[end], end)] + stopDurationsDict[parent[end]]
        end = parent[end]
        path.append(stopNamesDict[end])
    totalDur -= stopDurationsDict[end]
    path.reverse()
    return path, totalDur

searchPath(2, 22)
print(shortestPath(2, 22))
