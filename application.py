import os, csv, json

from flask import Flask, session, render_template, request, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dijkstra import readData, dijkstra_bus, dijkstra_walk, stopDict, routeDict, nodeDict

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

readData()

# Default mode is bus + walking
@app.route("/")
def home():
	buildingArr = []
	stopArr = []
	for node in nodeDict:
		if nodeDict[node]['type'] == 'Building':
			buildingArr.append([node, nodeDict[node]['name'], nodeDict[node]['lat'], nodeDict[node]['lng']])
		if nodeDict[node]['type'] == 'Bus Stop':
			stopArr.append([node, nodeDict[node]['name'], nodeDict[node]['lat'], nodeDict[node]['lng']])
	return render_template("home.html", nodeDict=nodeDict, buildingArr = buildingArr, stopArr = stopArr)

@app.route("/walk")
def walk():
	buildingArr = []
	stopArr = []
	for node in nodeDict:
		if nodeDict[node]['type'] == 'Building':
			buildingArr.append([node, nodeDict[node]['name'], nodeDict[node]['lat'], nodeDict[node]['lng']])
		if nodeDict[node]['type'] == 'Bus Stop':
			stopArr.append([node, nodeDict[node]['name'], nodeDict[node]['lat'], nodeDict[node]['lng']])
	return render_template("walk.html", nodeDict=nodeDict, buildingArr = buildingArr, stopArr = stopArr)

@app.route("/bus")
def bus():
	stopArr = []
	for stop in stopDict:
		stopArr.append([stop, stopDict[stop]['name'], stopDict[stop]['lat'], stopDict[stop]['lng']])
	return render_template("bus.html", stopDict=stopDict, stopArr=stopArr)

@app.route("/go",  methods =['POST'])
def go():
	return render_template("go.html")


@app.route("/go_bus",  methods =['POST'])
def go_bus():
	start_id = request.form.get("start")
	end_id = request.form.get("end")
	if start_id == end_id:
		coord = [stopDict[start_id]['name'], stopDict[start_id]['lat'], stopDict[start_id]['lng']]
		return render_template("go_bus.html", coord=coord,  same=True)
	else:
		bus_route, segments = dijkstra_bus(start_id, end_id)

		stop_coord = []
		for stop_id in bus_route:
			stop_coord.append([stopDict[stop_id]['name'], stopDict[stop_id]['lat'], stopDict[stop_id]['lng']])
			path_coord = [[stopDict[start_id]['lng'], stopDict[start_id]['lat']]]
		for i in range(len(bus_route)-1):
			curr_coords = routeDict[(bus_route[i], bus_route[i+1])]['coord']
			for curr_coord in curr_coords[1:]:
				path_coord.append([float(curr_coord.split('/')[1]), float(curr_coord.split('/')[0])])

		totalMins = 0
		for segment in segments:
			dur = segment[0][1]
			mins = dur // 60
			secs = dur % 60
			if secs >= 30:
				mins += 1
			totalMins += mins
			segment[0][1] = mins

		return render_template("go_bus.html", mins=totalMins, segments = segments, same=False, stopDict=stopDict, stop_coord=stop_coord, path_coord=path_coord)

@app.route("/go_walk",  methods=['POST'])
def go_walk():
	start_id = request.form.get("start")
	end_id = request.form.get("end")
	if start_id == end_id:
		coord = [nodeDict[start_id]['name'], nodeDict[start_id]['lat'], nodeDict[start_id]['lng']]
		return render_template("go_walk.html", coord=coord,  same=True)
	else:
		walk_route, dur = dijkstra_walk(start_id, end_id)

		node_coord = []
		for node_id in walk_route:
			node_coord.append([nodeDict[node_id]['name'], nodeDict[node_id]['lat'], nodeDict[node_id]['lng']])

		mins = dur // 60
		secs = dur % 60
		if secs >= 30:
			mins += 1

		return render_template("go_walk.html", mins=int(mins), same=False, nodeDict=nodeDict, node_coord=node_coord)
