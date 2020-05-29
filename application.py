import os, csv

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dijkstra import *

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

@app.route("/")
def home():
    return render_template("home.html", stops = createGraph())	

@app.route("/go",  methods =['POST'])
def go():
	start_id = int(request.form.get("start"))
	end_id = int(request.form.get("end"))
	searchPath(start_id, end_id)
	path, totalDur = shortestPath(start_id, end_id)
	mins = totalDur // 60
	secs = totalDur % 60
	# return str(path)
	return render_template("go.html", start = start_id, end = end_id, mins = mins, secs = secs)
