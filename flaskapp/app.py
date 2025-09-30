# flask requirements
from flask import Flask, render_template, request, redirect, url_for
import hashlib

# database requirements
from flaskapp import database as db



# ===== Flask Initialization =====

app = Flask(__name__)



# ===== Routes =====

@app.route("/")
def render_index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    password = request.form.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if db.validate_password(hashed_password):
        print("Password is valid!")
    else:
        print("Invalid password.")
        
    return render_template("home.html")