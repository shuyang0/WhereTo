import os, csv

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from heapq import heapify, heappush, heappop 

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



#bus stop class
class Stop:
	def __init__(self, id, name, dur):
		self.id = id
		self.name = name
		self.dur = dur

#route class not in use yet
class Route:
	def __init__(self, start, end, dur):
		self.start = start
		self.end = end
		self.dur = dur

# class MinHeap:
# 	def __init__(self):
# 		self.data = [0]
# 		self.size = 0

# 	def parent(self, i):
# 		return i//2

# 	def left(self, i):
# 		return i*2

# 	def right(self, i):
# 		return i*2+1
	
# 	def push(self, d):
# 		self.size += 1
# 		data[self.size] = d
# 		shiftup(self.size)

# 	def pop(self):
# 		value = self.data[1]
# 		data[1] = data[self,size]
# 		self.size -= 1
# 		shiftdown(1)
# 		return value

# 	def shiftup(self, i):
# 		while i > 1 && data[parent(i)] > data[i]:
# 			swap(data[i], data[parent(i)])
# 			i = parent(i)

# 	def shiftdown(self, i):




#generate list of bus stop objects
stops = []
with open("stopdata.csv") as f:
	data = csv.reader(f)
	for row in data:
		stops.append(Stop(row[0], row[1], row[2]))

#routes are represented using adj list
routes = {}
with open("routedata.csv") as f:
	data = csv.reader(f)
	for start,end,dur,buses in data:
		if start in routes:
			routes[start].append((end,dur,buses))
		else:
			routes[start] = [(end, dur,buses)]

@app.route("/")
def home():
	return render_template("home.html", stops = stops)

@app.route("/go",  methods =['POST'])
def go():
	start = request.form.get("start")
	end = request.form.get("end")
	stop_time = {}
	stop_time[start] = 0
	heap = []
	heapify(heap)
	heappush(heap, (0, start))
	while len(heap) > 0:
		dist, curr = heappop(heap)
		if dist == stop_time[curr]:
			if curr == end: break
			for neigh in routes[curr]:
				if (neigh[0] not in stop_time) or (stop_time[neigh[0]] > stop_time[curr] + int(neigh[1])):
					stop_time[neigh[0]] = stop_time[curr] + int(neigh[1])
					heappush(heap, (stop_time[neigh[0]], neigh[0]))
	mins = stop_time[end]//60
	secs = stop_time[end]%60
	return render_template("go.html", start = start, end = end, mins = mins, secs = secs)
