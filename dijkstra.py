import csv
from pqdict import minpq

class Stop:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.neighbours = []

class Edge:
    def __init__(self, stop1_id, stop2_id, dur):
        self.stop1_id = stop1_id
        self.stop2_id = stop2_id
        self.dur = dur 

graph = []
stopNamesDict = {}
stopDurationsDict = {}
pathDurationsDict = {}
pathServicesDict = {} 

def readData():
    with open("stopdata.csv") as f:
        data = csv.reader(f)
        next(data)
        for stop_id, stop_name, stop_dur in data:
            stop_id, stop_dur = int(stop_id), int(stop_dur)
            graph.append(Stop(stop_id, stop_name))
            stopNamesDict[stop_id] = stop_name
            stopDurationsDict[stop_id] = stop_dur

    with open("routedata.csv") as f:
        data = csv.reader(f)
        next(data)
        for stop1_name, stop1_id, stop2_name, stop2_id, path_dur, services in data:
            stop1_id, stop2_id, path_dur = int(stop1_id), int(stop2_id), int(path_dur)
            graph[stop1_id].neighbours.append(Edge(stop1_id, stop2_id, path_dur))
            pathDurationsDict[(stop1_id, stop2_id)] = path_dur
            pathServicesDict[(stop1_id, stop2_id)] = services.split()

def getPath(start_id, end_id, parent):
    totalDur = 0
    path = []
    path_id = []
    path.append(stopNamesDict[end_id])
    path_id.append(end_id)

    while end_id != start_id:
        totalDur += pathDurationsDict[(parent[end_id], end_id)] + stopDurationsDict[parent[end_id]]
        end_id = parent[end_id]
        path.append(stopNamesDict[end_id])
        path_id.append(end_id)

    if len(path) > 1:
        totalDur -= stopDurationsDict[end_id]

    path.reverse()
    path_id.reverse()
    return path, path_id, totalDur

def dijkstra(start_id, end_id):
    distTo = []
    parent = []
    pq = minpq()
    
    for i in range(len(graph)):
        distTo.append(float("inf"))
        parent.append(None)
    distTo[start_id] = 0
    pq.additem(start_id, 0)

    while len(pq) > 0:
        curr_id, curr_dist = pq.popitem()
        if curr_dist == distTo[curr_id]:
            if curr_id == end_id:
                break
            for edge in graph[curr_id].neighbours:
                if distTo[edge.stop2_id] > distTo[curr_id] + edge.dur:
                    distTo[edge.stop2_id] = distTo[curr_id] + edge.dur
                    parent[edge.stop2_id] = curr_id
                    try: 
                        pq.additem(edge.stop2_id, distTo[edge.stop2_id])
                    except: 
                        pq.updateitem(edge.stop2_id, distTo[edge.stop2_id])
    
    path, path_id, totalDur = getPath(start_id, end_id, parent)
    bus_path = getBus(path_id, start_id, end_id)
    return totalDur, bus_path

class Bus_Vert:
    def __init__(self, stop_id, bus):
        self.stop_id = stop_id
        self.bus = bus

    def __eq__(self, other):
        return self.stop_id == other.stop_id and self.bus == other.bus

    def __hash__(self):
        return hash(str(self.stop_id) + self.bus)

def getBus(path_id, start_id, end_id):
    pair_id = []
    bus_graph = {}
    for i in range(len(path_id) - 1):
        pair_id.append((path_id[i], path_id[i + 1]))
    for i in range(len(pair_id)):
        stop1_id, stop2_id = pair_id[i][0], pair_id[i][1]
        for bus in pathServicesDict[(stop1_id, stop2_id)]:
            bus_graph[Bus_Vert(stop1_id, bus)] = [stop2_id]
            for j in range(i + 1, len(pair_id)):
                if bus in pathServicesDict[pair_id[j][0], pair_id[j][1]]:
                    bus_graph[Bus_Vert(stop1_id, bus)].append(pair_id[j][1]) # break?

    dist = {}
    parent = {}
    pq = minpq()
    
    for val in bus_graph:
        if val.stop_id == start_id:
            pq.additem(val, 0)
    for stop_id in path_id:
        dist[stop_id] = (float("inf"))
        parent[stop_id] = []
    dist[start_id] = 0

    while len(pq) > 0:
        curr, curr_dist = pq.popitem()
        if curr_dist == dist[curr.stop_id]:
            for dest in bus_graph[curr]:
                if dist[dest] > dist[curr.stop_id] + 1:
                    dist[dest] = dist[curr.stop_id] + 1
                    parent[dest].append(curr)
                    for val in bus_graph:
                        if val.stop_id == dest:
                            pq.additem(val, dist[dest])
                elif dist[dest] == dist[curr.stop_id] + 1:
                    parent[dest].append(curr)

    bus_path = []
    while end_id != start_id:
        curr_buses = []
        for val in parent[end_id]:
            temp_id = val.stop_id
            if val.bus not in curr_buses:
                curr_buses.append(val.bus)
        bus_path.append([stopNamesDict[end_id], curr_buses, []])
        end_id = temp_id
    bus_path.reverse()
    i = 0
    j = 0
    
    while j < len(path_id) and i < len(bus_path):
        if stopNamesDict[path_id[j]] != bus_path[i][0]:
            bus_path[i][2].append(stopNamesDict[path_id[j]])
            j += 1
        else:
            bus_path[i][2].append(stopNamesDict[path_id[j]])
            i += 1

    for segment in bus_path:
        segment.append(len(segment[2])-1)

    return bus_path