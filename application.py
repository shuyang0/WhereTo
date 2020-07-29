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

@app.route("/")
def home():
	stopArr = []
	for stop in stopDict:
		stopArr.append([stop, stopDict[stop]['name'], stopDict[stop]['lat'], stopDict[stop]['lng']])
	return render_template("home.html", stopDict = stopDict, stopArr = stopArr)

@app.route("/go",  methods =['POST'])
def go():
	start_id = request.form.get("start")
	end_id = request.form.get("end")
	if start_id == end_id:
		coord = [stopDict[start_id]['name'], stopDict[start_id]['lat'], stopDict[start_id]['lng']]
		return render_template("go.html", coord = coord,  same = True)
	else:
		path_id,bus_path,totalDur = dijkstra_bus(start_id, end_id)
		mins = totalDur // 60
		secs = totalDur % 60
		if secs >= 30:
			mins += 1
		stop_coord = []
		for stop in path_id:
			stop_coord.append([stopDict[stop]['name'],stopDict[stop]['lat'], stopDict[stop]['lng']])
		path_coord = [[stopDict[start_id]['lng'],stopDict[start_id]['lat']]]
		for i in range(len(path_id)-1):
			curr_coords = routeDict[(path_id[i], path_id[i+1])]['coord']
			for curr_coord in curr_coords[1:]:
				path_coord.append([float(curr_coord.split('/')[1]),float(curr_coord.split('/')[0])])

		return render_template("go.html", mins = mins, stop_coord = stop_coord, path_coord = path_coord, bus_path = bus_path, same = False)
