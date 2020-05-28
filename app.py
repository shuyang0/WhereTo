import os, csv

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

stops = []

class Stop:
	def __init__(self, id, name, dur):
		self.id = id
		self.name = name
		self.dur=dur

with open("stopdata.csv") as f:
	data = csv.reader(f)
	for row in data:
		stops.append(Stop(row[0], row[2], row[2]))
 

@app.route("/")
def home():
    return render_template("home.html", stops = stops)
