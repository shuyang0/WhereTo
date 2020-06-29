import os, csv, json

from flask import Flask, session, render_template, request, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dijkstra import readData, dijkstra, stopDict

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
		path_id,bus_path,totalDur = dijkstra(start_id, end_id)
		mins = totalDur // 60
		secs = totalDur % 60
		stop_coord = []
		for stop in path_id:
			stop_coord.append([stopDict[stop]['name'],stopDict[stop]['lat'], stopDict[stop]['lng']])
		return render_template("go.html", mins = mins, secs = secs, stop_coord = stop_coord, bus_path = bus_path, same = False)
