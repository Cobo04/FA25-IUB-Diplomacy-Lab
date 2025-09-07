# flask requirements
from flask import Flask, render_template

# database requirements
from flaskapp import database as db



# ===== Flask Initialization =====

app = Flask(__name__)



# ===== Routes =====

@app.route("/")
def render_index():
    return render_template("index.html")